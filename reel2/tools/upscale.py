"""Upscale a video with Real-ESRGAN realesr-general-x4v3 (SRVGGNetCompact), CPU.

Frames are upscaled x4, then resized to the target size and piped to ffmpeg.
usage: upscale.py <in.mov> <weights.pth> <out.mp4> <width> <height> [first_n_frames]
"""
import subprocess
import sys

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


class SRVGGNetCompact(nn.Module):
    def __init__(self, num_feat=64, num_conv=32, upscale=4):
        super().__init__()
        self.upscale = upscale
        self.body = nn.ModuleList([nn.Conv2d(3, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)])
        for _ in range(num_conv):
            self.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1))
            self.body.append(nn.PReLU(num_parameters=num_feat))
        self.body.append(nn.Conv2d(num_feat, 3 * upscale * upscale, 3, 1, 1))
        self.upsampler = nn.PixelShuffle(upscale)

    def forward(self, x):
        out = x
        for layer in self.body:
            out = layer(out)
        out = self.upsampler(out)
        return out + F.interpolate(x, scale_factor=self.upscale, mode="nearest")


src, weights, out, W, H = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
limit = int(sys.argv[6]) if len(sys.argv) > 6 else None

model = SRVGGNetCompact()
state = torch.load(weights, map_location="cpu")
model.load_state_dict(state.get("params", state), strict=True)
model.eval()
torch.set_num_threads(4)

cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS)
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
enc = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps),
     "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", out],
    stdin=subprocess.PIPE,
)
i = 0
with torch.inference_mode(), torch.autocast("cpu", dtype=torch.bfloat16):
    while True:
        ok, frame = cap.read()
        if not ok or (limit and i >= limit):
            break
        x = torch.from_numpy(frame[:, :, ::-1].astype(np.float32) / 255).permute(2, 0, 1)[None]
        y = model(x).float().clamp(0, 1)[0].permute(1, 2, 0).numpy()[:, :, ::-1]
        y = cv2.resize((y * 255).round().astype(np.uint8), (W, H), interpolation=cv2.INTER_AREA)
        enc.stdin.write(y.tobytes())
        i += 1
        if i % 25 == 0:
            print(f"{i}/{total}", flush=True)
enc.stdin.close()
enc.wait()
print("done", i)
