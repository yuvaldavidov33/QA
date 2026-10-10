# Reel style guide (studio reels)

Read this before making a new reel. It records what the client approved on the first reel
(`reel2/`, final render `reel2/reel_final.mp4`). Reuse `reel2/tools/*` and adapt the content.

## Inputs the client provides
- The talking-head video (vertical). Usually WhatsApp-compressed (720×1280); uploaded to this repo via
  GitHub web "Upload files", ends up on `main`.
- The script text, sentence by sentence (no ASR available: huggingface.co is blocked here).

## Pipeline (all in `reel2/tools/`)
1. `face_track.py` — MediaPipe 0.10.35 FaceDetector (venv, `pip install mediapipe==0.10.35 opencv-python-headless`,
   needs `apt-get install libgles2 libegl1`, model `blaze_face_short_range.tflite` from storage.googleapis.com).
   Top-half filter, highest score, smoothed, percent of frame.
2. `words.py` — word start times from pause-delimited segments (silencedetect) + letter-proportional placement
   snapped to energy dips. Segments and text are hard-coded; edit per video.
3. `upscale.py` — Real-ESRGAN `realesr-general-x4v3.pth` (GitHub release), bf16 autocast on CPU, to 1440×2560,
   then mux original audio back. Slow (~1 h for 18 s); run in background, render with a lanczos+unsharp copy meanwhile.
4. `build2.py` — writes `index.html` (HyperFrames, 1080×1920). Content (chunks, keywords, graphics, zoom keyframes)
   is hard-coded for reel 1; rewrite those parts for the new script.
5. `sfx.py` — synthesized SFX from `sfx.json` cues written by `build2.py`.
6. `music.py` — synthesized 140 BPM half-time trap bed, drums + 808 only.
7. Render: `npx hyperframes render -q high -o out.mp4`; commit as `reelN/reel_final.mp4` with `-movflags +faststart`;
   give the client the GitHub raw link for download and a claude.ai artifact page for viewing.

## Approved look
- Output 1080×1920 (Reels). Keep CTA above the bottom Instagram UI (bottom ≥ 440px).
- **Hook** (first sentence): big Karantina 700, words resolve from blur one by one, max 3 lines, split into
  two beats when long (second beat replaces the first, alone). Key word red.
- **Captions**: Heebo 900, 74px, white with shadow, 2–4 words per chunk, centered at y≈1240px, pop in with back.out.
  Key words colored: red default; client chose green for "6", cyan for "דואגים". On-screen wording may differ
  from speech when the client asks.
- **Cards**: dark glass, rounded, Heebo 800. Enter from below with a 3D tilt + blur and **settle perfectly
  straight** (no final tilt). Exit drops down with blur. Each card hidden from t=0 until its own entrance.
  Badges: red ✕ with strike line, green ✓ with ding; "?" flipping to ✓.
- **Background stays sharp** behind cards (client rejected background blur/dim).
- **CTA**: cyan pill "שלחי לי הודעה", then "פה למטה", then bouncing ↓, stacked in that order.
- **Zoom**: centered on the face (percent origin from the face track), max ~1.32 on a 1440 source.
  Mix of slow pushes, spring punch-ins `p => (1-(1+7*p)*Math.exp(-7*p)) / (1-8*Math.exp(-7))`, and on key phrases a
  sharp snap-in (0.2 s, brief motion blur) followed by a glide back to 100% before the next sentence.
- **Sound**: SFX at data-volume 0.55 (whoosh in/out on cards, scratch on strike, tick/pop/ding, low thump on snaps).
  Music: 140 BPM half-time trap, drums + 808 only (no pads/keys — client found them sleepy), beat from frame 0,
  ~14 dB under the voice with ducking. Client wants to hear the voice clearly; music is background.
- Video keeps its sound: `data-has-audio="true"`, no `muted`.

## Working with the client
- Hebrew, phone-only (iPhone). Explain steps simply. Check the phone silent switch when "no sound".
- Show a plan/list before building when the client asks; then deliver via the artifact page and the raw download link.
