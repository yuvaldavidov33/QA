"""(music7) New bed for reel 5 after the client asked for a completely different tune: bright, clean, upbeat
120 BPM workout groove (soft four-on-the-floor kick, clap on 2 and 4, off-beat hats, plucked bass, a marimba-like
melodic hook in A minor over Am-F-C-G). No pads, no distortion, nothing above ~8 kHz. The drop lands on the first
exercise clip; the bed is quiet and ducked under the voice while the trainer talks, fuller during the silent clips.

usage: music7.py <voice.wav (mono 48k)> <out.wav> <duration> <talk_end> <talk_again> [cut times, comma separated]
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 120
BEAT = 60 / BPM
STEP = BEAT / 4
BAR = 4 * BEAT
rng = np.random.default_rng(11)

voice_path, out_path = sys.argv[1], sys.argv[2]
DUR, TALK_END, TALK_AGAIN = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
CUTS = [float(x) for x in sys.argv[6].split(",")] if len(sys.argv) > 6 else []
N = int(DUR * SR)
tracks = {k: np.zeros(N + SR * 3) for k in ("kick", "perc", "bass", "lead", "chord", "fx")}


def add(track, at, snd, pan=0.0):
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
    """One-pole low-pass."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a) * x[i] + a * s
        y[i] = s
    return y


def kick():
    t = t_(0.3)
    f = 52 + 120 * np.exp(-t / 0.025)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    return y * np.minimum(1, t / 0.0015) * 0.8


def clap():
    t = t_(0.25)
    n = rng.standard_normal(len(t))
    hp = lp(n - lp(n, 1100), 6500)
    bursts = sum(np.exp(-np.maximum(t - d, 0) / 0.01) * (t >= d) for d in (0, 0.012, 0.024))
    return hp * (0.55 * bursts + 0.35 * np.exp(-t / 0.08)) * 0.42


def hat(open_=False):
    t = t_(0.16 if open_ else 0.04)
    n = rng.standard_normal(len(t))
    hp = lp(n - lp(n, 6500), 9000)
    return hp * np.exp(-t / (0.06 if open_ else 0.01)) * (0.16 if open_ else 0.09)


def shaker():
    t = t_(0.05)
    n = rng.standard_normal(len(t))
    return lp(n - lp(n, 4500), 8000) * np.sin(np.pi * t / 0.05) * 0.05


def pluck_bass(freq, dur=0.22):
    t = t_(dur)
    y = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t) + 0.12 * np.sin(6 * np.pi * freq * t)
    return y * np.exp(-t / 0.11) * np.minimum(1, t / 0.003) * np.minimum(1, (dur - t) / 0.01) * 0.5


def marimba(freq):
    t = t_(0.7)
    y = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.28) + 0.45 * np.sin(2 * np.pi * 4 * freq * t) * np.exp(-t / 0.05)
    y += 0.2 * np.sin(2 * np.pi * 2.01 * freq * t) * np.exp(-t / 0.12)
    return y * np.minimum(1, t / 0.002) * 0.22


def stab(freqs):
    t = t_(0.18)
    y = sum(np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) for f in freqs) / len(freqs)
    return y * np.exp(-t / 0.06) * np.minimum(1, t / 0.003) * 0.2


def riser(dur):
    t = t_(dur)
    n = rng.standard_normal(len(t))
    return lp(n, 2500) * (t / dur) ** 2.5 * 0.25


def swell():
    t = t_(1.0)
    n = rng.standard_normal(len(t))
    return lp(n, 3000) * np.exp(-t / 0.3) * np.minimum(1, t / 0.01) * 0.28


A2, F2, C3, G2 = 110.0, 87.31, 130.81, 98.0
CHORDS = [(A2, (220.0, 261.63, 329.63)), (F2, (174.61, 220.0, 261.63)), (C3, (196.0, 261.63, 329.63)), (G2, (196.0, 246.94, 293.66))]
A4, C5, D5, E5, G5 = 440.0, 523.25, 587.33, 659.25, 783.99
HOOK = [(0, E5), (3, D5), (6, C5), (8, A4), (10, C5), (14, D5), (16, E5), (19, G5), (22, E5), (24, D5), (26, C5), (28, A4)]

t0 = TALK_END - 2 * BAR  # a downbeat (and the drop) lands on the first exercise clip
bar_i, at = 0, t0
kicks = []
while at < DUR:
    drop = at >= TALK_END - 0.01 and at < TALK_AGAIN - 0.01
    root, triad = CHORDS[bar_i % 4]
    for b in range(4):
        bt = at + b * BEAT
        if drop or b in (0, 2):
            add("kick", bt, kick() * (1.0 if drop else 0.6))
            kicks.append(bt)
        if b in (1, 3):
            add("perc", bt, clap() * (1.0 if drop else 0.6))
        add("perc", bt + BEAT / 2, hat(open_=drop) * 1.0)
        for s in range(4):
            add("perc", bt + s * STEP, shaker() * (1.0 if s % 2 else 0.6))
        # bass: off-beat plucks, octave jump on the last off-beat of the bar
        add("bass", bt + BEAT / 2, pluck_bass(root * (2 if b == 3 else 1)) * (1.0 if drop else 0.7))
        if b in (1, 3):
            add("chord", bt + BEAT / 2 + STEP, stab(triad))
    # melodic hook over two bars; plays from the start, a dotted-8th echo adds width
    phase = (bar_i % 2) * 16
    for st, f in HOOK:
        if phase <= st < phase + 16:
            when = at + (st - phase) * STEP
            add("lead", when, marimba(f))
            add("lead", when + 3 * STEP, marimba(f) * 0.3)
    bar_i += 1
    at += BAR

for c in CUTS:
    add("fx", c - 0.8, riser(0.8))
    add("fx", c, swell())

kk, pc, bs, ld, ch, fx = (tracks[k][:N] for k in ("kick", "perc", "bass", "lead", "chord", "fx"))
t = np.arange(N) / SR
side = np.ones(N)  # bass and chords breathe with the kick (gentle sidechain)
for k in kicks:
    i = int(k * SR)
    seg = t_(0.2)
    j = min(N, i + len(seg))
    if 0 <= i < N:
        side[i:j] = np.minimum(side[i:j], 1 - 0.45 * np.exp(-seg[: j - i] / 0.07))
music = kk * 0.9 + pc * 0.8 + bs * side * 1.0 + ld * 0.85 + ch * side * 0.7 + fx * 0.5

# Talk sections quiet (about 10 dB down) and ducked under the voice; full during the silent clips.
sec = np.interp(t, [0, TALK_END - 0.3, TALK_END, TALK_AGAIN - 0.4, TALK_AGAIN, 99], [0.32, 0.32, 1, 1, 0.32, 0.32])
w = wave.open(voice_path)
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.sqrt(lp(v ** 2, 6))
venv /= venv.max() + 1e-9
music *= sec * (1 - 0.35 * np.clip(venv * 3, 0, 1))
music *= np.minimum(1, (DUR - t) / 0.8) * np.minimum(1, t / 0.05)
music = lp(music, 8000)

clips = (t > TALK_END + 0.5) & (t < TALK_AGAIN - 0.5)
music *= 10 ** (-23 / 20) / (np.sqrt((music[clips] ** 2).mean()) + 1e-9)
# light stereo: echo of the lead slightly to one side
L = music.copy()
R = music.copy()
d = int(0.012 * SR)
R[d:] = 0.85 * music[d:] + 0.15 * music[:-d]
pcm = (np.clip(np.stack([L, R], 1), -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as o:
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
print(f"{BPM} bpm clean upbeat groove, peak {20 * np.log10(np.abs(music).max()):.1f} dBFS")
