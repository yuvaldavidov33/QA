"""(music8) Trendy gym-reel bed after the client asked for "a trendy sports song": Brazilian-phonk style workout
beat, 130 BPM (the sound of current gym edits): pitched cowbell riff in F# minor, punchy kick on a funk pattern,
claps, 16th hats with rolls, gliding 808. Original composition. Kept clean on purpose (the client disliked
harsh distortion before): only a light tanh on the 808, master low-passed at 9 kHz.
Quiet, filtered and ducked under the voice while the trainer talks; full drop on the first exercise clip.

usage: music8.py <voice.wav (mono 48k)> <out.wav> <duration> <talk_end> <talk_again> [cut times, comma separated]
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 130
BEAT = 60 / BPM
STEP = BEAT / 4
BAR = 4 * BEAT
rng = np.random.default_rng(21)

voice_path, out_path = sys.argv[1], sys.argv[2]
DUR, TALK_END, TALK_AGAIN = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
CUTS = [float(x) for x in sys.argv[6].split(",")] if len(sys.argv) > 6 else []
N = int(DUR * SR)
tracks = {k: np.zeros(N + SR * 3) for k in ("kick", "perc", "bass", "bell", "fx")}


def add(track, at, snd):
    i = int(round(at * SR))
    if i < 0:
        snd, i = snd[-i:], 0
    buf = tracks[track]
    end = min(len(buf), i + len(snd))
    if end > i:
        buf[i:end] += snd[: end - i]


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def lp(x, cutoff):
    """One-pole low-pass (cutoff may be an array)."""
    a = np.exp(-2 * np.pi * np.broadcast_to(cutoff, x.shape) / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def kick():
    t = t_(0.28)
    f = 48 + 150 * np.exp(-t / 0.02)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.1)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.002) * 0.15
    return np.tanh(1.3 * (y + click)) * 0.85


def clap():
    t = t_(0.22)
    n = rng.standard_normal(len(t))
    hp = lp(n - lp(n, 1200), 7000)
    bursts = sum(np.exp(-np.maximum(t - d, 0) / 0.009) * (t >= d) for d in (0, 0.01, 0.02))
    return hp * (0.6 * bursts + 0.35 * np.exp(-t / 0.07)) * 0.5


def hat(open_=False):
    t = t_(0.12 if open_ else 0.03)
    n = rng.standard_normal(len(t))
    hp = lp(n - lp(n, 7000), 9500)
    return hp * np.exp(-t / (0.045 if open_ else 0.008)) * (0.14 if open_ else 0.1)


def square(f, t):
    return np.sign(np.sin(2 * np.pi * f * t))


def cowbell(freq, dur=0.2):
    """Pitched 808-style cowbell: two detuned squares (ratio ~1.48), band-limited, fast decay."""
    t = t_(dur)
    y = square(freq, t) + 0.8 * square(freq * 1.48, t)
    y = lp(y - lp(y, freq * 0.6), 4500)
    env = np.exp(-t / 0.075) * 0.85 + 0.15 * np.exp(-t / 0.02)
    return y * env * np.minimum(1, t / 0.001) * 0.16


def bass808(notes, dur):
    """Gliding 808 line: (time, freq, length) notes, short glide into each, light saturation only."""
    out = np.zeros(int(dur * SR) + SR)
    prev = None
    for at, f, ln in notes:
        t = t_(ln)
        fr = np.full(len(t), f)
        if prev is not None and prev != f:
            g = np.clip(t / 0.06, 0, 1)
            fr = prev + (f - prev) * g
        y = np.sin(2 * np.pi * np.cumsum(fr * (1 + 0.5 * np.exp(-t / 0.012))) / SR)
        y = np.tanh(1.6 * y) * np.exp(-t / 0.6) * np.minimum(1, (ln - t) / 0.02) * np.minimum(1, t / 0.002)
        i = int(at * SR)
        j = min(len(out), i + len(y))
        if 0 <= i < len(out):
            out[i:j] += y[: j - i]
        prev = f
    return out[: int(dur * SR)] * 0.55


def riser(dur):
    t = t_(dur)
    n = rng.standard_normal(len(t))
    return lp(n, 300 + 4000 * (t / dur) ** 2) * (t / dur) ** 2 * 0.35


def impact():
    t = t_(0.9)
    f = 40 + 60 * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    n = rng.standard_normal(len(t))
    return y * 0.6 + lp(n, 3000) * np.exp(-t / 0.15) * 0.15


# F# minor riff (pitched cowbell), 2 bars of 16 steps
Fs5, A5, B5, Cs6, E5, D5, Gs5 = 739.99, 880.0, 987.77, 1108.73, 659.25, 587.33, 830.61
RIFF = [(0, Fs5), (2, Fs5), (3, A5), (6, Fs5), (8, Cs6), (10, B5), (11, A5), (14, Gs5),
        (16, Fs5), (18, Fs5), (19, A5), (22, Fs5), (24, E5), (26, D5), (27, E5), (30, Fs5)]
ROOTS = [46.25, 46.25, 36.71, 41.20]  # F#1, F#1, D1, E1 per bar
KICKS = [0, 3, 6, 10, 12]  # funk-style pattern
t0 = TALK_END - 2 * BAR  # downbeat (drop) on the first exercise clip
notes, kicks = [], []
bar_i, at = 0, t0
while at < DUR:
    drop = TALK_END - 0.01 <= at < TALK_AGAIN - 0.01
    root = ROOTS[bar_i % 4]
    for st in KICKS:
        k_at = at + st * STEP
        if drop or st in (0, 6):
            add("kick", k_at, kick() * (1.0 if drop else 0.55))
            kicks.append(k_at)
        if drop:
            f = root * (2 if (st == 12 and bar_i % 2 == 1) else 1)
            notes.append((k_at, f, 2.5 * STEP if st != 12 else 4 * STEP))
    for st in (4, 12):
        add("perc", at + st * STEP, clap() * (1.0 if drop else 0.5))
    if drop:
        add("perc", at + 15 * STEP, clap() * 0.35)
        for st in range(16):
            roll = bar_i % 4 == 3 and st >= 12
            add("perc", at + st * STEP, hat(open_=(st == 14 and bar_i % 2 == 0)) * (1.0 if st % 2 == 0 else 0.6))
            if roll:
                add("perc", at + st * STEP + STEP / 2, hat() * 0.55)
    else:
        for st in range(0, 16, 4):
            add("perc", at + st * STEP + 2 * STEP, hat() * 0.6)
    phase = (bar_i % 2) * 16
    for st, f in RIFF:
        if phase <= st < phase + 16:
            add("bell", at + (st - phase) * STEP, cowbell(f))
    bar_i += 1
    at += BAR

for c in CUTS + [TALK_END]:
    add("fx", c - 0.9, riser(0.9))
    add("fx", c, impact())

kk, pc, bl, fx = (tracks[k][:N] for k in ("kick", "perc", "bell", "fx"))
bs = bass808(notes, DUR)
t = np.arange(N) / SR
side = np.ones(N)
for k in kicks:
    i = int(k * SR)
    seg = t_(0.12)
    j = min(N, i + len(seg))
    if 0 <= i < N:
        side[i:j] = np.minimum(side[i:j], 1 - 0.5 * np.exp(-seg[: j - i] / 0.04))
# Cowbell filtered (muffled) while the trainer talks, opens up on the drop.
talk = np.interp(t, [0, TALK_END - 0.2, TALK_END, TALK_AGAIN - 0.3, TALK_AGAIN, 99], [1, 1, 0, 0, 1, 1])
bl = lp(bl, 1400 + 7000 * (1 - talk))
music = kk * 0.95 + pc * 0.8 + bs * side * 1.0 + bl * 1.0 + fx * 0.5

sec = 0.3 + 0.7 * (1 - talk)
w = wave.open(voice_path)
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.sqrt(lp(v ** 2, 6))
venv /= venv.max() + 1e-9
music *= sec * (1 - 0.35 * np.clip(venv * 3, 0, 1))
music *= np.minimum(1, (DUR - t) / 0.8) * np.minimum(1, t / 0.05)
music = lp(music, 9000)

clips = (t > TALK_END + 0.5) & (t < TALK_AGAIN - 0.5)
music *= 10 ** (-22 / 20) / (np.sqrt((music[clips] ** 2).mean()) + 1e-9)
L = music.copy()
R = music.copy()
d = int(0.011 * SR)
R[d:] = 0.85 * music[d:] + 0.15 * music[:-d]
pcm = (np.clip(np.stack([L, R], 1), -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as o:
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
print(f"{BPM} bpm phonk-style workout bed, peak {20 * np.log10(np.abs(music).max()):.1f} dBFS")
