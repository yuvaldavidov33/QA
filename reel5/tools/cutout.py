"""Person cutouts for the text-behind-subject effect (U^2-Net human seg, rembg's GitHub release).

Writes RGBA PNGs (frame with the person kept, background transparent) for a frame range,
so the page can stack: video frame -> big text -> person cutout.
Masks are averaged with their neighbors over time to stop edge flicker, then feathered.

usage: cutout.py <frames dir> <u2net_human_seg.onnx> <out dir> <first frame> <last frame>
"""
import sys
from pathlib import Path

import cv2
import numpy as np

frames, model, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
a, b = int(sys.argv[4]), int(sys.argv[5])
out.mkdir(parents=True, exist_ok=True)
net = cv2.dnn.readNetFromONNX(model)
MEAN, STD = np.array([0.485, 0.456, 0.406]), np.array([0.229, 0.224, 0.225])

masks = {}
for i in range(a - 1, b + 2):
    im = cv2.imread(str(frames / f"{i:05d}.jpg"))
    if im is None:
        continue
    x = cv2.resize(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), (320, 320), interpolation=cv2.INTER_AREA) / 255.0
    x = ((x / x.max() - MEAN) / STD).transpose(2, 0, 1)[None].astype(np.float32)
    net.setInput(x)
    m = net.forward()[0, 0]
    m = (m - m.min()) / (m.max() - m.min() + 1e-9)
    masks[i] = m
    print("mask", i, flush=True)

for i in range(a, b + 1):
    im = cv2.imread(str(frames / f"{i:05d}.jpg"))
    near = [masks[k] for k in (i - 1, i, i + 1) if k in masks]
    m = (masks[i] * 2 + sum(near) - masks[i]) / (len(near) + 1)
    m = cv2.resize(m, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_CUBIC)
    m = np.clip((m - 0.35) / 0.4, 0, 1)  # tighten the soft edge
    m = cv2.GaussianBlur(m, (0, 0), 2.0)
    rgba = np.dstack([im, (m * 255).astype(np.uint8)])
    cv2.imwrite(str(out / f"{i:05d}.png"), rgba, [cv2.IMWRITE_PNG_COMPRESSION, 3])
print("wrote", b - a + 1, "cutouts")
