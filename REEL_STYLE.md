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

## Reel 3 notes (`reel3/`, "מבצע חגים") — read these first for the next reel
Tools that work in this sandbox (npm/PyPI/storage.googleapis.com/raw.githubusercontent.com are blocked; GitHub
release downloads and `git clone` of GitHub repos work):
- Face track: `reel3/tools/face_track.py` (OpenCV DNN, model via `git clone -b dnn_samples_face_detector_20180220_uint8
  https://github.com/opencv/opencv_3rdparty` + `opencv_face_detector.pbtxt` from opencv/opencv samples).
- Word timing: sherpa-onnx v1.12.20 linux binaries + Whisper small (GitHub releases), transcribe overlapping 2.5 s
  windows, then `reel3/tools/words.py` (segments + anchors). Slow on 2 CPUs: run in background, 2 processes.
- Person cutouts for text-behind-subject: `reel3/tools/cutout.py` (U²-Net human seg from rembg's GitHub release).
- Render: `reel3/tools/render.py` (headless Chrome at /opt/pw-browsers, frame by frame, same index.html), then mix.
- Builder: `reel3/tools/build3.py`; copy and rewrite content per video.

What the client approved / asked for on reel 3 (defaults for the next reel):
- Ask before building: propose cards/animations per sentence, wait for approval.
- Plural wording when the speech is plural ("שלחו לי הודעה").
- Key words in **royal blue #3a64f0** (not red). ₪ in white.
- Opening hook: plain centered text, each phrase enters whole (no word-by-word), not behind the head.
- Big text behind the trainer (cutout) is liked for one mid-reel phrase, beside the head, no duplicate caption below.
- Cards must move smoothly: glide + fade (`sine.out`), no 3D tilt flips; no snap-zoom while a card is on screen.
- Wide top card (not a full-screen page) when the trainer should stay visible; full-screen pages (star page,
  motion-graphics page) are fine for the offer and for list-like content.
- The client sends reference reels to copy exactly ("בול אחד לאחד"): analyze frame by frame (timings, layout, easing)
  before building. Copy the motion, never their logo or their song.
- CTA: low-opacity Instagram DM notification with the client's round profile picture (`reel3/avatar.png`,
  account idoamarr, "IDO AMAR | סטודיו לאימוני כוח"), "שלחו לי הודעה", then "ונשמור לכם מקום" under it.
- SFX at 0.35. Music: the client is picky. Clean (no distortion), low, slow hip-hop bed was the last request
  (`reel3/tools/music6.py`). Always also deliver a no-music version (voice + SFX) so a song can be added in Instagram.
- Deliver: commit `reelN/reel_final.mp4` to `claude/workout-video-animations-sx06ew`, give the raw GitHub link and
  update the claude.ai artifact page.

## Reel 4 notes (`reel4/`, "למה אנשים לא מתמידים") — the latest approved reel; start the next one from here
Builder `reel4/tools/build4.py`, renderer `reel4/tools/render.py` (writes `reel_final.mp4` and `reel_no_music.mp4`).
What the client approved / asked for:
- Opening text = the full first sentence exactly as spoken, in two whole phrases (no shortened wording).
- Problem → solution as two full-screen dark pages of blocks (glass rows, red ✕ / royal-blue ✓, a live mini-animation
  per block: draining battery, friends fading, wobbling ?, six people lighting up, plan sheet, kg counter, graph).
  No page titles on these pages, no subtitles the client did not say.
- Solution page = block cascade copied from the client's reference (`d3e71928-….mov` on `main`), measured frame by
  frame: each block opens below centre from a narrow strip, rises into its slot while the whole board moves up one
  fixed step; flat, NO tilt / roll / 3D. Each block starts on its spoken words.
- Zooms must be smooth: one slow push per section, origin from a heavily smoothed face track (~0.5 s); no stacked
  punch + snap (read as shaking). Always look up word times by the right occurrence (`t(word, nth)`).
- Big text behind the trainer for one mid-reel phrase is still liked ("אחרי חודש / מפסיקים").
- CTA: low-opacity Instagram DM notification with the round profile picture; wording as spoken ("שלחו לנו הודעה").
- A real side angle needs a second camera; faking it from the front shot was rejected. Ask for a side clip instead.
- When the client sends a reference, measure it (positions/timing per frame) and copy the motion exactly; do not
  add extra effects of your own.

## Reel 5 notes (`reel5/`, "4 תרגילי ישבן")
- Talking head + silent B-roll clips: one wide top card per clip (number, name, live stick-figure rig of the move),
  soft whip-in on each cut, music lifted +8 dB where nobody talks (`reel5/tools/music_lift.py`).
- Text behind the subject works on B-roll too (big "4" behind the athlete's kicking leg).
