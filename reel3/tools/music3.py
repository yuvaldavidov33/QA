"""Phonk-style gym track for reel3 (client asked for a different song): 140 BPM, cowbell melody, distorted
sliding 808, hard kick, half-time clap/snare on 3, 8th hats with rolls, risers into the reel's big moments.
Ducked under the voice. Everything is generated; no samples.
usage: music3.py <voice.wav (mono 48k)> <out.wav> <duration> [lift,times]
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 140
BEAT = 60 / BPM
STEP = BEAT / 4
rng = np.random.default_rng(3)

voice_path, out_path = sys.argv[1], sys.argv[2]
DUR = float(sys.argv[3])
LIFTS = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
N = int(DUR * SR)
mix = {k: np.zeros(N + SR * 3) for k in ("drums", "bass", "bell", "fx")}


def add(track, at, snd):
    i = int(at * SR)
    if i < 0:
        snd, i = snd[-i:], 0
    buf = mix[track]
    end = min(len(buf), i + len(snd))
    buf[i:end] += snd[: end - i]


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def onepole_lp(x, cutoff):
    cutoff = np.broadcast_to(cutoff, x.shape)
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def kick():
    t = t_(0.42)
    f = 50 + 110 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.11)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.003) * 0.3
    return np.tanh(1.6 * (body + click)) * 0.9


def clap():
    t = t_(0.3)
    n = rng.standard_normal(len(t))
    bursts = sum(np.exp(-np.maximum(t - d, 0) / 0.012) * (t >= d) for d in (0, 0.011, 0.022))
    tail = np.exp(-t / 0.09)
    hp = n - onepole_lp(n, 1200)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04) * 0.4
    return (hp * (0.6 * bursts + 0.5 * tail) + tone) * 0.55


def hat(open_=False):
    t = t_(0.14 if open_ else 0.04)
    n = rng.standard_normal(len(t))
    hp = n - onepole_lp(n, 7000)
    return hp * np.exp(-t / (0.05 if open_ else 0.009)) * (0.22 if open_ else 0.18)


def bass808(freq, dur):
    t = t_(dur)
    f = freq * (1 + 0.6 * np.exp(-t / 0.02))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.9)
    y *= np.minimum(1, (dur - t) / 0.03)
    y = y + 0.35 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR) * np.exp(-t / 0.9)
    return np.tanh(2.8 * y) * 0.55


def rolling_bass(freq, dur):
    t = t_(dur)
    y = onepole_lp(saw(freq, t) + 0.5 * saw(freq * 1.005, t), 700)
    return np.tanh(2.5 * y) * np.exp(-t / 0.12) * 0.5


def saw(freq, t):
    return 2 * ((freq * t) % 1) - 1


def pad(freqs, dur):
    t = t_(dur)
    y = sum(saw(f * d, t) for f in freqs for d in (0.996, 1.004))
    y = onepole_lp(y / (2 * len(freqs)), 900)
    env = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.4)
    return y * env * 0.5


def pluck(freq):
    t = t_(0.5)
    y = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t)) * np.exp(-t / 0.14)
    return y * 0.16


def crash():
    t = t_(1.2)
    n = rng.standard_normal(len(t))
    return (n - onepole_lp(n, 5000)) * np.exp(-t / 0.35) * 0.3


def riser(dur):
    t = t_(dur)
    n = rng.standard_normal(len(t))
    y = onepole_lp(n, 300 + 6000 * (t / dur) ** 2)
    return y * (t / dur) ** 2 * 0.5





def snare():
    t = t_(0.25)
    n = rng.standard_normal(len(t))
    hp = n - onepole_lp(n, 1500)
    tone = np.sin(2 * np.pi * 200 * t) * np.exp(-t / 0.05)
    return np.tanh(2 * (hp * np.exp(-t / 0.09) * 0.6 + tone * 0.4)) * 0.55


def hard_kick():
    t = t_(0.35)
    f = 48 + 160 * np.exp(-t / 0.025)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    return np.tanh(3.0 * y) * 0.8


def cowbell(f):
    """Phonk cowbell: two detuned square-ish partials, band-limited, short metallic decay."""
    t = t_(0.32)
    sq = lambda fr: np.tanh(6 * np.sin(2 * np.pi * fr * t))
    y = sq(f) + 0.8 * sq(f * 1.48)
    y = y - onepole_lp(y, 500)          # high-pass
    y = onepole_lp(y, 4200)             # tame the top
    env = np.minimum(1, t / 0.002) * (0.65 * np.exp(-t / 0.045) + 0.35 * np.exp(-t / 0.16))
    return y * env * 0.2


def dist808(f0, f1, dur):
    t = t_(dur)
    glide = np.clip(t / 0.06, 0, 1)
    f = (f0 + (f1 - f0) * glide) * (1 + 0.5 * np.exp(-t / 0.015))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    y = np.tanh(4.5 * y) * np.exp(-t / 1.2) * np.minimum(1, (dur - t) / 0.02)
    return onepole_lp(y, 2200) * 0.5


A = 440.0
semi = lambda n: A * 2 ** (n / 12)
# 2-bar cowbell riff in A minor (16th steps: (step, semitone from A4) ), classic phonk bounce
RIFF = [(0, 0), (3, 0), (6, 3), (8, 0), (10, 7), (12, 5), (14, 3),
        (16, 0), (19, 0), (22, 3), (24, 0), (26, -2), (28, -4), (30, -5)]
BASS = [(0, 55.0, 55.0, 6), (6, 55.0, 65.41, 4), (10, 49.0, 49.0, 6),  # (step, from, to, length in steps)
        (16, 43.65, 43.65, 6), (22, 43.65, 49.0, 4), (26, 41.2, 41.2, 6)]
BAR = 4 * BEAT
kicks = []
two, at = 0, 0.0
while at < DUR:
    intro = at < 1.5
    for st in (0, 10, 16, 26):  # kick pattern over 2 bars
        add("drums", at + st * STEP, hard_kick())
        kicks.append(at + st * STEP)
    if not intro:
        for st in (8, 24):  # half-time snare on 3
            add("drums", at + st * STEP, snare())
            add("drums", at + st * STEP, clap() * 0.7)
        for st, f0, f1, ln in BASS:
            add("bass", at + st * STEP, dist808(f0, f1, ln * STEP))
    for st in range(0, 32, 2):
        roll = st in (14, 30) and two % 2 == 1
        if roll:
            for r in range(4):
                add("drums", at + st * STEP + r * STEP / 2, hat() * 0.7)
        else:
            add("drums", at + st * STEP, hat(open_=(st % 8 == 4)) * (1.0 if st % 4 == 0 else 0.7))
    for st, n in RIFF:
        add("bell", at + st * STEP, cowbell(semi(n)) * (1.0 if st % 4 == 0 else 0.8))
    two += 1
    at += 2 * BAR

for lift in LIFTS:
    for k in range(8):
        add("drums", lift - BEAT * 2 + k * (BEAT * 2 / 8), snare() * (0.3 + 0.7 * k / 8))
    add("fx", lift - 1.4, riser(1.4) * 0.9)
    add("fx", lift, crash())
    add("drums", lift, hard_kick() * 1.1)

drums, bass, bell, fx = (mix[k][:N] for k in ("drums", "bass", "bell", "fx"))
t = np.arange(N) / SR
pump = np.ones(N)
for k in kicks:
    i = int(k * SR)
    seg = t_(BEAT)
    j = min(N, i + len(seg))
    if i < N:
        pump[i:j] = np.minimum(pump[i:j], 1 - 0.35 * np.exp(-seg[: j - i] / 0.08))
music = drums * 0.85 + bass * pump * 1.0 + bell * 1.7 + fx * 0.55
intro_cut = np.where(t < 1.5, 1500 + 7000 * (t / 1.5) ** 2, 12000)
music = onepole_lp(music, intro_cut)

w = wave.open(voice_path)
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.sqrt(onepole_lp(v ** 2, 6))
venv /= venv.max() + 1e-9
music *= 1 - 0.45 * np.clip(venv * 3, 0, 1)
music *= np.minimum(1, (DUR - t) / 0.6)

music = np.tanh(music * 1.3) / 1.3
target_rms = 10 ** (-33 / 20)
music *= target_rms / (np.sqrt((music ** 2).mean()) + 1e-9)
pcm = (np.clip(np.stack([music, music], 1), -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as o:
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
print(f"{BPM} bpm phonk, peak {20 * np.log10(np.abs(music).max()):.1f} dBFS")
