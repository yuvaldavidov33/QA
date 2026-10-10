"""Track the face center per frame with OpenCV DNN (res10 SSD, TensorFlow uint8) face detector; storage.googleapis.com is blocked so MediaPipe models are unavailable.

Per frame: keep only detections whose center lies in the top half of the
frame, take the highest-scoring one, then smooth the track. Output is in
percent of the frame (not pixels).

usage: face_track.py <video> <opencv_face_detector.pbtxt> <opencv_face_detector_uint8.pb> <out.json>
"""
import json
import sys

import cv2
import numpy as np

video, proto, model, out = sys.argv[1:5]
net = cv2.dnn.readNetFromTensorflow(model, proto)

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
    top = frame[: H // 2]
    net.setInput(cv2.dnn.blobFromImage(cv2.resize(top, (300, 300)), 1.0, (300, 300), (104, 177, 123)))
    det = net.forward()[0, 0]
    best = None
    for d in det:
        s = float(d[2])
        if s < 0.4:
            continue
        x1, y1, x2, y2 = float(d[3]) * W, float(d[4]) * (H // 2), float(d[5]) * W, float(d[6]) * (H // 2)
        if best is None or s > best[0]:
            best = (s, (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1)
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
