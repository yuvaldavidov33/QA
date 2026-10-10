# Reel v3: "מבצע חגים" (holiday offer)

Same approved style as `reel2/` (see `../REEL_STYLE.md`). Final render: `reel_final.mp4`.

- Source: `1522cba7-c65d-4ac2-88d9-76cc4d9a6c8e.mov` on `main` (720×1280, 22.3 s). Not committed here.
- `tools/face_track.py` — OpenCV DNN face detector (res10 SSD, from opencv/opencv_3rdparty via git) because
  storage.googleapis.com and PyPI were blocked in this session.
- `tools/words.py` — pause segments + Whisper small (sherpa-onnx GitHub release) on overlapping 2.5 s windows
  to assign words to segments; letter-proportional inside.
- `tools/build3.py` — writes `index.html` and `sfx.json`. Cards: "אתחיל מחר" ✕ → "עכשיו!" ✓, small groups with 6
  people + "עד 6", personal plan checklist, road to the flag, 199₪ price roll, CTA "שלחו לי הודעה".
- `tools/render.py` — renders the composition in headless Chrome frame by frame (npm registry was unreachable,
  so no `npx hyperframes`), then mixes voice + `music.wav` + `sfx.wav`×0.55 (+2.6 dB, limiter; −17.7 LUFS).

Rebuild: extract frames `ffmpeg -i in.mov -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.7:5:5:0" -q:v 2 -start_number 1 work/frames/%05d.jpg`,
then `python3 tools/build3.py tools/face.json tools/words.json index.html quick.mp4`, `python3 tools/sfx.py sfx.json sfx.wav`,
`python3 tools/music.py voice48.wav music.wav 3.53 22.3 16.62`, `python3 tools/render.py . work/frames in.mov reel_final.mp4 30`.
