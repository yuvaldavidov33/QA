# Reel v4: "למה אנשים לא מתמידים" (why people quit training)

Same approved style as `reel3/` (see `../REEL_STYLE.md`). Final render: `reel_final.mp4`; `reel_no_music.mp4` is
voice + SFX only, for adding a song from Instagram's library.

- Source: `26fd5922-e90c-43ad-9bd0-971800f0b77a.mov` on `main` (720×1280, 19.87 s, 29.95 fps). Not committed here.
- Plan approved by the client before building:
  - Opening: plain centered text, each phrase enters whole: "למה רוב האנשים" / "לא **מתמידים** באימונים?" (royal blue).
  - Reasons on a full-screen page (client chose full page): zoom-blur in, title "למה מפסיקים?", three rows glide in as
    spoken with red ✕: "מתחילים חזק מדי" (battery shoots to 100% then drains to 8% red and flickers),
    "מתאמנים לבד" (friends around him fade away), "לא יודעים מה בדיוק לעשות" (question marks pop, big ? wobbles).
    Light-leak flash back to the video on "ואז".
  - "אחרי חודש / מפסיקים" as big text behind the trainer (cutouts frames 188-238), a calendar ticks 1→30 and drops.
  - "בדיוק בגלל זה / בנינו את הסטודיו / בצורה קצת **אחרת**" captions, punch-in on "בנינו", snap-in on "אחרת",
    then the solution page "אצלנו זה אחרת" with blue ✓ rows: "עד 6 מתאמנים" (six people light up, counter to 6),
    "תכנית אישית לכל מתאמן" (plan sheet writes itself), "מעקב משקלים" (40→60 ק״ג), "והתקדמות" (glowing graph draws).
    Hard cut back on "אם" with the approved over-exposed settle.
  - CTA: low-opacity Instagram DM notification with the round profile picture, "שלחו לנו הודעה" (plural, as spoken).
    The last frame holds to 21.0 s so the notification stays readable.
- Fix 1 (client): opening wording is the full sentence as spoken: "בואו אני אגיד לכם / למה רוב האנשים", then
  "לא מצליחים / **להתמיד** באימונים".
- Fix 2 (client): a fake side angle on "לא מצליחים להתמיד באימונים" was tried and removed; a real profile shot needs a
  second camera (the client may film one). The wording fix stays.
- Fix 3-5 (client): the "אצלנו זה אחרת" page copies the block cascade of the client's reference (`d3e71928-….mov` on
  `main`), measured frame by frame from the yellow block outlines (1248 px frame scaled to 1920): flat, no tilt or roll.
  Each new block opens below centre (centre y≈1190) from a narrow strip to full width with a slight overshoot and rises
  ~70 px into its slot, while the whole board (title, earlier blocks, grid, dust) moves up: the new block's centre goes
  1190 → 1040 in 0.25 s (ease in-out) → 930 by 0.6 s (ease out) → speeds up to 805 as the next block arrives.
  Fixed pitch 385 px between blocks; blocks far above the focus go soft. Each block starts on its spoken words.
- Fix 6 (client): "בדיוק בגלל זה" shook: the zoom keys used the first "בדיוק" (inside "לא יודעים בדיוק") so a push had a
  negative duration, then a punch and a snap followed. Now one smooth push 1.03 → 1.14 from the reasons page to the
  solution page, and the zoom origin uses a heavier (~0.5 s) smoothing of the face track. Measured: no frame-to-frame
  jump above 1.2 px (at 270 px width) between 6.3 and 9.7 s.
- Fix 8 (client): subtitle "ונשרפים מהר" removed from the first reason.
- Fix 7 (client): page titles "למה מפסיקים?" and "אצלנו זה אחרת" removed; reasons rows re-centred.
- Fix 9 (client, trial): the blue blocks page replaced by the 3D app carousel of the client's reference
  (`422f8911-….mov` on `main`, measured at 60 fps): a whip blur cut, the shot slides so the trainer stands on the right
  (1.75x, fixed origin on the face), background grey and soft, person cutout in colour (frames 291-488) over a ring of
  thick navy tiles on the left (60° apart, radius 380) that turns right-to-left in 0.42 s eased steps so each block's
  tile reaches the front on its words, drifting between steps; the block text (same wording) resolves above the ring.
  Builder `tools/build4c.py` (`... 188 238 291 488`). The previous blocks version is kept as
  `reel_final_blocks.mp4` / `reel_no_music_blocks.mp4`.
- Word timing: `tools/words.json` hand-timed from pauses (silencedetect −27 dB) and Whisper small (sherpa-onnx int8)
  on sliding 1.5 s windows. Whisper does not hear "קצת אחרת" or "הודעה" clearly; their times sit inside the
  pause-bounded segments.
- Music: `tools/music6.py` (the clean low bed approved on reel3). SFX at 0.35.

Rebuild: frames `ffmpeg -i in.mov -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.7:5:5:0" -q:v 2 -start_number 1 work/frames/%05d.jpg`,
`python3 tools/cutout.py work/frames u2net_human_seg.onnx work/cutout 188 238`,
`python3 tools/build4.py tools/face.json tools/words.json index.html in.mov 188 238`, `python3 tools/sfx.py sfx.json sfx.wav`,
`python3 tools/music6.py voice48.wav music.wav 21.0 9.77`, `python3 tools/render.py . work/frames in.mov reel_final.mp4 30`
(writes `reel_final.mp4` and `reel_no_music.mp4`).
