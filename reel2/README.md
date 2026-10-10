# Reel v2: reference-style edit

- `index.html` — composition: dynamic face-centered zooms (slow pushes, spring punch-ins, snaps), blur-in hook, 2–4 word captions, content graphics.
- Source video is not committed (size). Build it: `ffmpeg -i ../reel/in.mov -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.7:5:5:0" -c:v libx264 -crf 14 -c:a copy quick.mp4`
  or AI-upscale with `tools/upscale.py` (Real-ESRGAN realesr-general-x4v3), then `python3 tools/build2.py tools/face.json tools/words.json index.html <video>`.
- `tools/words.py` — word times estimated from audio pauses (no ASR available).
