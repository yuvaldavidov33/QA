# Reel: spring punch-in zooms

- `index.html` — HyperFrames composition, 1080×1920, source `in.mov` (720×1280).
- `tools/face_track.py` — MediaPipe 0.10.35 FaceDetector face track → `tools/face.json` (percent of frame, smoothed).
- `tools/build.py` — regenerates `index.html` from `tools/face.json` and the zoom word list.
- `preview_10s_540x960.mp4` — first 10 s preview render.

Render: `npx hyperframes render -o out.mp4`
