# Reel 5 — "4 תרגילי ישבן"

Same approved style as `reel4/` (see `../REEL_STYLE.md`). Final render: `reel_final.mp4`; `reel_no_music.mp4` is
voice + SFX only (for adding a song from Instagram's library).

- Source: `0ebad599-8718-499f-bd5f-274be874028f.mov` on `main` (720×1280, 29.73 s, 29.97 fps). Not committed here.
- Structure: the trainer talks 0–3.27 s and 26.6–29.73 s; between them four **silent** exercise clips
  (cuts at 3.27 / 8.9 / 16.7 / 20.77 / 26.6 s, ffmpeg scene detection).
- Plan approved by the client before building:
  - Opening "הכנתי לך ארבעה תרגילים / ממוקדי ישבן במיוחד בשבילך" as whole phrases, "ארבעה" and "ישבן" in royal blue.
  - Fix 1 (client): on "ממוקדי ישבן" a full-screen page with the client's anatomy image (`anatomy.jpg`; Fix 6: replaced with the client's woman version with the "IA Studio" band): zoom-blur in, a blue
    target locks on the glutes, they light up red from grey, slow push in, the phrase at the top; zooms forward into clip 1.
  - "4 תרגילי ישבן" behind the athlete on the first clip (person cutout): the big blue 4 counts 1→4 and her kicking
    leg sweeps in front of it.
  - One wide top card per exercise (number, name, live stick-figure doing the move with the glute dot lighting at the
    squeeze, 4-step progress bar). Glide + fade in, leaves upward before the next cut. Soft whip-in on every cut.
  - Light-leak back to the trainer; captions "לעוד תרגילים / שורפים ומחטבים" (both key words blue).
  - CTA: Instagram follow notification with the round profile picture (idoamarr), "תעקבי אחרי העמוד", the blue
    "מעקב" button is tapped and turns to "במעקב".
- On-screen name "קיק בק" (the script said "קיק באג"); the other names as written by the client.
- Fix 2 (client): sumo squat figure knees open outward; deadlift figure has the rear foot on a bench, standing on one leg.
- Fix 3 (client, "a completely different tune"): `tools/music7.py`, new clean upbeat 120 BPM groove (soft kick, claps,
  plucked bass, marimba hook in A minor), drop on the first clip, quiet and ducked under the voice. SFX at 0.35.
- Fix 7 (client): every exercise card shows "3 סטים · 8-12 חזרות" under the name, all white (client changed it from blue numbers).
- Fix 4 (client): kick-back figure's standing leg straight. Fix 5 (client, "a trendy sports song"): `tools/music8.py`,
  130 BPM Brazilian-phonk style gym beat (pitched cowbell riff, funk kick pattern, gliding 808), kept clean.

Rebuild: frames `ffmpeg -i in.mov -vf "scale=1440:2560:flags=lanczos,unsharp=5:5:0.7:5:5:0" -q:v 2 -start_number 1 work/frames/%05d.jpg`,
`python3 tools/face_track.py work/in.mov opencv_face_detector.pbtxt opencv_face_detector_uint8.pb tools/face.json`,
`python3 tools/words.py voice16.wav tools/words.json`,
`python3 tools/cutout.py work/frames u2net_human_seg.onnx work/cutout 99 170`,
`python3 tools/build5.py tools/face.json tools/words.json index.html in.mov 99 170`, `python3 tools/sfx.py sfx.json sfx.wav`,
`python3 tools/music8.py voice48.wav music.wav 30.0 3.267 26.6 8.9,16.7,20.767`,
`python3 tools/render.py . work/frames work/in.mov reel_final.mp4 30` (writes `reel_final.mp4` and `reel_no_music.mp4`).
