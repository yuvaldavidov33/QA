"""Estimate per-word start times from speech segments (no ASR available):
letter-proportional placement inside each pause-delimited segment, snapped to
the nearest energy dip within +-0.1 s."""
import json, wave, numpy as np
w = wave.open('work/audio.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
db = 20 * np.log10(np.array([np.sqrt(np.mean(a[i:i+320]**2)) for i in range(0, len(a) - 320, 160)]) + 1e-6)
SEGS = [
  (0.27, 2.93, "אם אתם לא אוהבים חדרי כושר אבל רוצים להתחזק תקשיבו לי"),
  (3.27, 5.79, "אצלנו אין מאות אנשים או מכשירים שאתם לא יודעים מה לעשות איתם"),
  (6.12, 7.48, "עד 6 אנשים בקבוצה"),
  (7.61, 9.88, "תכנית אישית ומאמן שמלווה אתכם לאורך כל הדרך"),
  (10.50, 13.16, "אתם לא צריכים לדעת איזה תרגיל לעשות כמה משקל או כמה חזרות"),
  (13.35, 16.11, "אתם מגיעים מקבלים תכנית שמתאימה לכם ואנחנו דואגים לכל השאר"),
  (16.33, 18.12, "רוצה להצטרף שלחי לי הודעה פה למטה"),
]
out = []
for s, e, txt in SEGS:
    ws = txt.split(); L = [len(x) if x != "6" else 2 for x in ws]; tot = sum(L); acc = 0
    for wd, l in zip(ws, L):
        t = s + (e - s) * acc / tot
        if acc:
            lo, hi = int((t - 0.1) * 100), int((t + 0.1) * 100)
            t = (lo + int(np.argmin(db[lo:hi]))) / 100 + 0.02
        out.append({"w": wd, "t": round(t, 2)}); acc += l
    out[-1]["segEnd"] = e
json.dump(out, open('work/words.json', 'w'), ensure_ascii=False)
print(' | '.join(f"{x['w']} {x['t']}" for x in out))
