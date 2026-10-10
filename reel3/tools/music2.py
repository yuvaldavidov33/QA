"""Upbeat workout track for reel3 (client: "שיר קצבי טוב"): 126 BPM four-on-the-floor, offbeat pumping bass,
short synth stabs (no pads), claps + snare on 2 and 4, rolling hats, snare-roll + riser builds into the reel's
big moments. Ducked under the voice. Everything is generated; no samples.
usage: music2.py <voice.wav (mono 48k)> <out.wav> <duration> [lift,times]
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 126
BEAT = 60 / BPM
STEP = BEAT / 4
rng = np.random.default_rng(3)

voice_path, out_path = sys.argv[1], sys.argv[2]
DUR = float(sys.argv[3])
LIFTS = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
N = int(DUR * SR)
mix = {k: np.zeros(N + SR * 3) for k in ("drums", "bass", "stab", "fx")}


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
    t = t_(0.22)
    n = rng.standard_normal(len(t))
    hp = n - onepole_lp(n, 1800)
    tone = np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.05)
    return (hp * np.exp(-t / 0.07) * 0.5 + tone * 0.35) * 0.6


def shaker():
    t = t_(0.05)
    n = rng.standard_normal(len(t))
    return (n - onepole_lp(n, 9000)) * np.exp(-t / 0.012) * 0.09


def pump_bass(freq, dur):
    t = t_(dur)
    y = saw(freq, t) + 0.6 * saw(freq * 1.007, t) + 0.8 * np.sin(2 * np.pi * freq / 2 * t)
    y = onepole_lp(y, 900 + 1400 * np.exp(-t / 0.05))
    env = np.minimum(1, t / 0.004) * np.exp(-t / 0.16) * np.minimum(1, (dur - t) / 0.01)
    return np.tanh(1.8 * y * env) * 0.42


def stab(freqs):
    t = t_(0.2)
    y = sum(saw(f * d, t) for f in freqs for d in (0.995, 1.005)) / (2 * len(freqs))
    y = onepole_lp(y, 2600 * np.exp(-t / 0.06) + 500)
    return y * np.exp(-t / 0.07) * 0.5


A1, F1, C2, G1 = 55.0, 43.65, 65.41, 49.0
CHORDS = [  # bass root, stab voicing (A minor: Am F C G)
    (A1 * 2, [220.0, 261.63, 329.63]),
    (F1 * 2, [174.61, 220.0, 261.63]),
    (C2 * 2, [196.0, 261.63, 329.63]),
    (G1 * 2, [196.0, 246.94, 293.66]),
]
BAR = 4 * BEAT
kicks = []
bar_i, at = 0, 0.0
while at < DUR:
    root, chord = CHORDS[bar_i % 4]
    intro = at < 2.0  # first bar: kick + hats only, filtered, so the hook lands clean
    for b in range(4):
        add("drums", at + b * BEAT, kick())
        kicks.append(at + b * BEAT)
    if not intro:
        for b in (1, 3):
            add("drums", at + b * BEAT, clap() * 0.9)
            add("drums", at + b * BEAT, snare() * 0.7)
        for b in range(4):
            add("drums", at + b * BEAT + 2 * STEP, hat(open_=True) * 1.1)
            add("bass", at + b * BEAT + 2 * STEP, pump_bass(root, 2 * STEP * 0.95))
            add("bass", at + b * BEAT + 3 * STEP, pump_bass(root, STEP * 0.9) * 0.7)
        for st in (0, 3, 6, 10, 12):
            add("stab", at + st * STEP, stab(chord) * (1.0 if st in (0, 6) else 0.75))
    for st in range(16):
        add("drums", at + st * STEP, hat() * (0.9 if st % 2 else 0.55))
        add("drums", at + st * STEP, shaker())
    bar_i += 1
    at += BAR

for lift in LIFTS:  # snare roll + riser into each big moment, crash on it
    n = 8
    for k in range(n):
        add("drums", lift - BEAT * 2 + k * (BEAT * 2 / n), snare() * (0.35 + 0.65 * k / n))
    add("fx", lift - 1.4, riser(1.4) * 0.9)
    add("fx", lift, crash())
    add("drums", lift, kick() * 1.15)

drums, bass, stb, fx = (mix[k][:N] for k in ("drums", "bass", "stab", "fx"))
t = np.arange(N) / SR
pump = np.ones(N)
for k in kicks:
    i = int(k * SR)
    seg = t_(BEAT)
    j = min(N, i + len(seg))
    if i < N:
        pump[i:j] = np.minimum(pump[i:j], 1 - 0.55 * np.exp(-seg[: j - i] / 0.09))
music = drums * 0.85 + bass * pump * 0.95 + onepole_lp(stb, 5000) * pump * 0.55 + fx * 0.6
intro_cut = np.where(t < 2.0, 1800 + 6000 * (t / 2.0) ** 2, 12000)
music = onepole_lp(music, intro_cut)

# Duck under the voice.
w = wave.open(voice_path)
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.sqrt(onepole_lp(v ** 2, 6))
venv /= venv.max() + 1e-9
music *= 1 - 0.45 * np.clip(venv * 3, 0, 1)
music *= np.minimum(1, (DUR - t) / 0.6)

music = np.tanh(music * 1.3) / 1.3
target_rms = 10 ** (-33 / 20)  # a bit more present than reel 2, still well under the voice
music *= target_rms / (np.sqrt((music ** 2).mean()) + 1e-9)
pcm = (np.clip(np.stack([music, music], 1), -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as o:
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
print(f"{BPM} bpm, peak {20 * np.log10(np.abs(music).max()):.1f} dBFS")
