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
- Word timing: `tools/words.json` hand-timed from pauses (silencedetect −27 dB) and Whisper small (sherpa-onnx int8)
  on sliding 1.5 s windows. Whisper does not hear "קצת אחרת" or "הודעה" clearly; their times sit inside the
  pause-bounded segments.
- Music: `tools/music6.py` (the clean low bed approved on reel3). SFX at 0.35.

Rebuild: frames `ffmpeg -i in.mov -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.7:5:5:0" -q:v 2 -start_number 1 work/frames/%05d.jpg`,
`python3 tools/cutout.py work/frames u2net_human_seg.onnx work/cutout 188 238`,
`python3 tools/build4.py tools/face.json tools/words.json index.html in.mov 188 238`, `python3 tools/sfx.py sfx.json sfx.wav`,
`python3 tools/music6.py voice48.wav music.wav 21.0 9.77`, `python3 tools/render.py . work/frames in.mov reel_final.mp4 30`
(writes `reel_final.mp4` and `reel_no_music.mp4`).
