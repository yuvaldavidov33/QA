"""Synthesize an original 86 BPM half-time hip-hop bed (A minor) for the reel.

Intro is filtered pads + a riser into the first snap zoom, then the full beat,
ducked under the voice. Everything is generated; no samples.
usage: music.py <voice.wav (mono 48k)> <out.wav> <drop_time> <duration>
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 86
BEAT = 60 / BPM
STEP = BEAT / 4
rng = np.random.default_rng(3)

voice_path, out_path = sys.argv[1], sys.argv[2]
DROP, DUR = float(sys.argv[3]), float(sys.argv[4])
N = int(DUR * SR)
mix = {k: np.zeros(N + SR * 3) for k in ("drums", "bass", "pad", "pluck", "fx")}


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
    f = 45 + 105 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
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
    return np.tanh(2.2 * y) * 0.55


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


def riser(dur):
    t = t_(dur)
    n = rng.standard_normal(len(t))
    y = onepole_lp(n, 300 + 6000 * (t / dur) ** 2)
    return y * (t / dur) ** 2 * 0.5


A2, C3, E3, F2, G2, B2, D3 = 110.0, 130.81, 164.81, 87.31, 98.0, 123.47, 146.83
CHORDS = [  # (pad voicing an octave up, 808 root, arp notes)
    ([A2 * 2, C3 * 2, E3 * 2], 55.0, [A2 * 4, E3 * 2, C3 * 4, E3 * 2]),
    ([F2 * 2, A2 * 2, C3 * 2], 43.65, [A2 * 4, F2 * 4, C3 * 4, F2 * 4]),
    ([G2 * 2, C3 * 2, E3 * 2], 65.41, [G2 * 4, C3 * 4, E3 * 4, C3 * 4]),
    ([G2 * 2, B2 * 2, D3 * 2], 49.0, [G2 * 4, B2 * 4, D3 * 4, B2 * 4]),
]
BAR = 4 * BEAT

# Bars are anchored so a downbeat lands exactly on the drop.
first_bar = DROP - BAR * int(np.ceil(DROP / BAR))
bar_i = 0
at = first_bar
while at < DUR:
    padv, root, arp = CHORDS[bar_i % 4]
    add("pad", at, pad(padv, BAR + 0.1))
    if at >= DROP - 1e-6:
        # Half-time groove: kick on 1 and the "and" of 2, clap on 3.
        for step in (0, 6, 10):
            add("drums", at + step * STEP, kick())
        add("drums", at + 8 * STEP, clap())
        for s in range(16):
            roll = bar_i % 2 == 1 and s >= 14
            if roll:
                for r in range(3):
                    add("drums", at + s * STEP + r * STEP / 3, hat() * 0.8)
            else:
                add("drums", at + s * STEP, hat(open_=s in (6, 14)) * (1.0 if s % 2 == 0 else 0.6))
        add("bass", at, bass808(root, 6 * STEP))
        add("bass", at + 6 * STEP, bass808(root, 4 * STEP))
        add("bass", at + 10 * STEP, bass808(root * (1.5 if bar_i % 2 else 1), 6 * STEP))
        for s, f in enumerate(arp * 2):
            add("pluck", at + s * 2 * STEP, pluck(f))
    bar_i += 1
    at += BAR

add("fx", DROP - 2.0, riser(2.0))
add("drums", DROP, kick() * 1.2)

drums, bass, padt, pl, fx = (mix[k][:N] for k in ("drums", "bass", "pad", "pluck", "fx"))
t = np.arange(N) / SR
# Intro pad is muffled, then opens on the drop.
intro_cut = np.where(t < DROP, 500 + 1500 * np.clip(t / DROP, 0, 1) ** 2, 9000)
padt = onepole_lp(padt, intro_cut)
music = drums * 0.9 + bass * 0.4 + padt * 1.1 + pl * 1.6 + fx * 0.8

# Duck under the voice.
w = wave.open(voice_path)
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.sqrt(onepole_lp(v ** 2, 6))
venv /= venv.max() + 1e-9
duck = 1 - 0.45 * np.clip(venv * 3, 0, 1)
music *= duck
music *= np.minimum(1, (DUR - t) / 0.8)  # fade out at the end

music = np.tanh(music * 1.2) / 1.2
target_rms = 10 ** (-30 / 20)  # well under the voice (~-21 dB mean)
music *= target_rms / (np.sqrt((music ** 2).mean()) + 1e-9)
pcm = (np.clip(np.stack([music, music], 1), -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as o:
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
print(f"{BPM} bpm, drop at {DROP}s, peak {20 * np.log10(np.abs(music).max()):.1f} dBFS")
