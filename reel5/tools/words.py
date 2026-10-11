"""Estimate per-word start times for reel5 ("4 תרגילי ישבן").

Segments come from pauses (silencedetect -24 dB); words from the client's script.
Speech is only at the start and the end; the four exercise clips are silent.
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
    (0.24, 2.34, "הכנתי לך ארבעה תרגילים ממוקדי ישבן במיוחד"),
    (2.40, 2.84, "בשבילך"),
    (26.54, 27.17, "לעוד תרגילים"),
    (27.25, 28.90, "שורפים ומחטבים תעקבי אחרי העמוד"),
]
SPOKEN = {}
ANCHOR = {}

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
