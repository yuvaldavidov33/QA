# Reel v3: "מבצע חגים" (holiday offer)

Same approved style as `reel2/` (see `../REEL_STYLE.md`). Final render: `reel_final.mp4`.

- Source: `1522cba7-c65d-4ac2-88d9-76cc4d9a6c8e.mov` on `main` (720×1280, 22.3 s). Not committed here.
- `tools/face_track.py` — OpenCV DNN face detector (res10 SSD, from opencv/opencv_3rdparty via git) because
  storage.googleapis.com and PyPI were blocked in this session.
- `tools/words.py` — pause segments + Whisper small (sherpa-onnx GitHub release) on overlapping 2.5 s windows
  to assign words to segments; letter-proportional inside.
- `tools/build3.py` — writes `index.html` and `sfx.json`. Cards: "אתחיל מחר" ✕ → "עכשיו!" ✓, small groups with 6
  people + "עד 6", personal plan checklist, CTA "שלחו לי הודעה".
- Fix 1 (client): "לכבוד החזרה / לשגרה" as big text behind the trainer, copied from the client's reference reel
  (`fd6defd5-….mp4` on `main`): letters resolve from the left, shallow 3D drift, whip-out to the right.
  `tools/cutout.py` makes per-frame person cutouts (U²-Net human seg, rembg GitHub release) laid over the text.
- Fix 3 (client): the offer copies the client's second reference (`17664b08-….mov` on `main`): "יצאתי במבצע" streams
  in from the left, the whole shot slides off to the right with motion blur onto a black star page, "199₪" lands
  letter by letter with "לחודש הראשון" under it, slow drift, hard cut back on "רוצים" opening over-exposed
  (+35%, slightly soft) and settling in 0.2 s, matched to the client's 1 s transition clip (same file name, a7c1c6a).
- Fix 5 (client): "מלווה אתכם לאורך כל הדרך" copies the client's third reference (`32372936-….mp4` on `main`):
  (fix 9: now a wide card across the top, the trainer stays in view) a dark grid card with one long glowing line, a red dot running along it, words resolving from grey
  blur above it, "כל הדרך" glitching in red; the line is alive (waves, tilts, crackling edge, breathing glow,
  a bright pulse riding with the dot); hard cut back on "לכבוד".
- Fix 8 (client): 8.6-12.45 s is a motion-graphics sequence copied from the client's fourth reference
  (`1b9a93f9-….mp4` on `main`): "אימוני כוח" pops on the video, zoom-blur through to a dark page, "בקבוצות קטנות"
  streams across on a red glow, a red band types "עד 6 מתאמנים באימון" with a cursor, the band tips into a 3D
  "תכנית אישית" card with two filling rings (dumbbell, group) and "לכל מתאמן", light-leak flash back to the video.
  It replaces the small-groups and plan cards.
- Fix 10 (client): hook word "לשגרה" re-timed to 1.60 s (was 0.6 s late) and colored royal blue; CTA is now a
  low-opacity Instagram DM notification with the client's round profile picture (`avatar.png`, cropped from their
  profile screenshot), "שלחו לי הודעה", and "ונשמור לכם מקום" under it (replaces the pill, "פה למטה" and arrow).
  Caption key words "לאימונים" and "עכשיו" are royal blue too (fix 11).
- Fix 12 (client): opening is text behind the trainer too (fix 13: swapped and lowered so his head/arms cover it as he moves):
  "החגים / נגמרו" right, "חוזרים / לשגרה" left (royal
  blue), each phrase enters whole (no word-by-word), both whip out before "וזה הזמן"; cutouts now cover frames
  1-72 as well (`data-cut-ranges`). Opening push softened to 1.07. ₪ on the star page is white.
- Fix 14 (client): opening back to plain centered text (each phrase enters whole); the "אתחיל מחר / עכשיו!" cards
  glide in smoothly (no 3D tilt) and the snap zoom on "עכשיו" is gone; SFX volume 0.55 → 0.35; new upbeat music
  `tools/music2.py` (126 BPM four-on-the-floor, offbeat pumping bass, short stabs, rolls + risers into 9.3/12.9/15.9/18.65):
  `python3 tools/music2.py voice48.wav music.wav 22.3 9.3,12.9,15.9,18.65`.
  Fix 15: client wanted a different song, now `tools/music3.py` (phonk: 140 BPM, cowbell riff, distorted sliding 808,
  hard kick, half-time snare), same arguments.
  Fix 16: client asked for a Drake-style hip-hop beat, now `tools/music4.py` (original composition: 68 BPM half-time,
  muffled FM electric-piano chords Fm9-Dbmaj9-Bbm9-C7 with reverb, long deep 808, clap/snare on 3, triplet hat rolls).
- `tools/render.py` — renders the composition in headless Chrome frame by frame (npm registry was unreachable,
  so no `npx hyperframes`), then mixes voice + `music.wav` + `sfx.wav`×0.55 (+2.6 dB, limiter; −17.7 LUFS).

Rebuild: extract frames `ffmpeg -i in.mov -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.7:5:5:0" -q:v 2 -start_number 1 work/frames/%05d.jpg`,
then `python3 tools/cutout.py work/frames u2net_human_seg.onnx work/cutout 1 72` and `... 425 497`,
`python3 tools/build3.py tools/face.json tools/words.json index.html quick.mp4 425 497`, `python3 tools/sfx.py sfx.json sfx.wav`,
`python3 tools/music.py voice48.wav music.wav 3.53 22.3 16.62`, `python3 tools/render.py . work/frames in.mov reel_final.mp4 30`.
