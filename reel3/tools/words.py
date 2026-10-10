"""Estimate per-word start times for reel3 ("מבצע חגים").

Segments come from pauses (silencedetect -27/-24 dB) and were assigned words by
transcribing overlapping 2.5 s windows with Whisper small (sherpa-onnx, offline).
Inside each segment: letter-proportional placement, snapped to the nearest energy
dip within +-0.1 s. A few words get hand anchors where the windows pin them down.

usage: words.py <audio.wav 16 kHz mono> <out words.json>
"""
import json
import sys
import wave

import numpy as np

w = wave.open(sys.argv[1])
a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
db = 20 * np.log10(np.array([np.sqrt(np.mean(a[i:i + 320] ** 2)) for i in range(0, len(a) - 320, 160)]) + 1e-6)

SEGS = [
    (0.22, 1.04, "החגים נגמרו"),
    (1.20, 1.98, "חוזרים לשגרה"),
    (2.22, 3.97, "וזה הזמן לחזור גם לאימונים"),
    (4.13, 6.32, "אם כבר הרבה זמן אתם אומרים לעצמכם שהגיע הזמן"),
    (6.45, 7.21, "להתחיל להתאמן"),
    (7.37, 8.36, "עכשיו זה סיבה טובה להתחיל"),
    (8.65, 10.05, "אימוני כוח בקבוצות קטנות"),
    (10.37, 11.10, "עד 6 מתאמנים באימון"),
    (11.22, 12.30, "אני בונה לכל מתאמן תכנית אישית"),
    (13.00, 13.80, "מלווה אתכם לאורך"),
    (13.93, 14.26, "כל הדרך"),
    (14.57, 16.12, "לכבוד החזרה לשגרה יצאתי במבצע"),
    (16.28, 18.42, "של 199 ש״ח לחודש הראשון"),
    (18.61, 19.70, "רוצים גם אתם להצטרף"),
    (19.83, 20.06, "למשפחה"),
    (20.19, 20.87, "שלחו לי הודעה"),
    (21.02, 21.74, "ונשמור לכם מקום"),
]
# Spoken length in letters for words written as digits or abbreviations.
SPOKEN = {"6": 4, "199": 12, "ש״ח": 5}
# Hand anchors (word, nth occurrence) -> start time, from the window transcriptions.
ANCHOR = {("לשגרה", 1): 1.60, ("199", 1): 16.62, ("ש״ח", 1): 17.30, ("לחודש", 1): 17.72}

out, seen = [], {}
for s, e, txt in SEGS:
    ws = txt.split()
    L = [SPOKEN.get(x, len(x)) for x in ws]
    tot, acc = sum(L), 0
    for wd, l in zip(ws, L):
        seen[wd] = seen.get(wd, 0) + 1
        t = s + (e - s) * acc / tot
        if acc:
            lo, hi = int((t - 0.1) * 100), int((t + 0.1) * 100)
            t = (lo + int(np.argmin(db[lo:hi]))) / 100 + 0.02
        t = ANCHOR.get((wd, seen[wd]), t)
        if acc and t < out[-1]["t"] + 0.12:  # keep words in order after snapping
            t = out[-1]["t"] + 0.12
        out.append({"w": wd, "t": round(t, 2)})
        acc += l
    out[-1]["segEnd"] = e
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False)
print(" | ".join(f"{x['w']} {x['t']}" for x in out))
