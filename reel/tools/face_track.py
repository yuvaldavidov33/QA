"""Track the face center per frame with MediaPipe FaceDetector.

Per frame: keep only detections whose center lies in the top half of the
frame, take the highest-scoring one, then smooth the track. Output is in
percent of the frame (not pixels).

usage: face_track.py <video> <model.tflite> <out.json>
"""
import json
import sys

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

video, model, out = sys.argv[1:4]

detector = vision.FaceDetector.create_from_options(
    vision.FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=model),
        running_mode=vision.RunningMode.VIDEO,
        min_detection_confidence=0.3,
    )
)

cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS)
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Faces are small in a full-body shot, so the detector also gets the top half
# upscaled 2x; boxes are mapped back to full-frame coordinates.
raw = []
i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    ts = int(i * 1000 / fps)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    top = cv2.resize(rgb[: H // 2], (W * 2, H))
    res = detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(top)), ts)
    best = None
    for d in res.detections:
        b = d.bounding_box
        cx = (b.origin_x + b.width / 2) / 2
        cy = (b.origin_y + b.height / 2) / 2
        if cy >= H / 2:
            continue
        s = d.categories[0].score
        if best is None or s > best[0]:
            best = (s, cx, cy, b.width / 2, b.height / 2)
    raw.append(None if best is None else {"t": i / fps, "score": best[0], "x": best[1] / W * 100,
                                          "y": best[2] / H * 100, "w": best[3] / W * 100, "h": best[4] / H * 100})
    i += 1

n = len(raw)
found = [k for k, r in enumerate(raw) if r]
xs = np.interp(range(n), found, [raw[k]["x"] for k in found])
ys = np.interp(range(n), found, [raw[k]["y"] for k in found])

# Reject single-frame jumps (a hand read as a face), then smooth.
def despike(a, win=7, tol=4.0):
    med = np.array([np.median(a[max(0, k - win): k + win + 1]) for k in range(len(a))])
    return np.where(np.abs(a - med) > tol, med, a)

def smooth(a, sigma=4.0):
    r = int(sigma * 3)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    return np.convolve(np.pad(a, r, mode="edge"), k, mode="valid")

xs, ys = smooth(despike(xs)), smooth(despike(ys))
json.dump({"fps": fps, "width": W, "height": H, "detected": len(found), "frames": n,
           "track": [{"t": round(k / fps, 4), "x": round(float(xs[k]), 2), "y": round(float(ys[k]), 2)} for k in range(n)],
           "raw": raw}, open(out, "w"))
print(f"{W}x{H} @ {fps}fps, face found in {len(found)}/{n} frames")
