"""Synthesize the reel's sound effects (no samples, all generated) into one WAV.

usage: sfx.py <sfx.json> <out.wav>
"""
import json
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def env(n, attack, release):
    a, r = int(attack * SR), int(release * SR)
    e = np.ones(n)
    e[:a] = np.linspace(0, 1, a) ** 2
    e[n - r:] *= np.linspace(1, 0, r) ** 2
    return e


def sweep_noise(dur, f0, f1, q=3.0):
    """Noise through a resonant band-pass whose center sweeps f0 -> f1 (a whoosh)."""
    n = int(dur * SR)
    x = rng.standard_normal(n)
    f = np.geomspace(f0, f1, n)
    y = np.zeros(n)
    s1 = s2 = 0.0
    for i in range(n):  # state-variable filter
        g = 2 * np.sin(np.pi * f[i] / SR)
        hp = x[i] - s1 / q - s2
        s1 += g * hp
        s2 += g * s1
        y[i] = s1
    return y / (np.abs(y).max() + 1e-9)


def whoosh(dur=0.42, f0=350, f1=3200, gain=0.32):
    y = sweep_noise(dur, f0, f1)
    return gain * y * env(len(y), dur * 0.65, dur * 0.3)


def tone(freq, dur, decay, gain, drop=1.0):
    t = np.arange(int(dur * SR)) / SR
    f = freq * drop ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return gain * np.sin(ph) * np.exp(-t / decay) * env(len(t), 0.002, 0.01)


def mix(*parts):
    n = max(len(p) for p in parts)
    return sum(np.pad(p, (0, n - len(p))) for p in parts)


SOUNDS = {
    "whoosh": lambda: whoosh(),
    "whoosh_soft": lambda: whoosh(0.35, 500, 2600, 0.18),
    "whoosh_out": lambda: whoosh(0.32, 2800, 300, 0.22),
    "pop": lambda: tone(880, 0.09, 0.03, 0.42, drop=0.45),
    "tick": lambda: tone(1500, 0.05, 0.012, 0.22, drop=0.7),
    "ding": lambda: mix(tone(1320, 0.5, 0.16, 0.18), tone(1980, 0.5, 0.11, 0.09)),
    "thump": lambda: mix(tone(110, 0.22, 0.07, 0.55, drop=0.5), whoosh(0.16, 2500, 600, 0.12)),
    "scratch": lambda: whoosh(0.18, 4000, 1800, 0.16),
}

spec = json.load(open(sys.argv[1]))
out = np.zeros(int(spec["duration"] * SR) + SR)
cache = {}
for name, at in spec["events"]:
    if name not in cache:
        cache[name] = SOUNDS[name]()
    snd = cache[name]
    i = int(at * SR)
    out[i:i + len(snd)] += snd[: len(out) - i]
out = out[: int(spec["duration"] * SR)]
peak = np.abs(out).max()
if peak > 0.5:
    out *= 0.5 / peak  # keep SFX well under the voice
pcm = (np.stack([out, out], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"{len(spec['events'])} cues, peak {20 * np.log10(np.abs(out).max() + 1e-9):.1f} dBFS")
