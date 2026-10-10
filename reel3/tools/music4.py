"""Moody Toronto-style hip-hop beat for reel3 (client: "drake style hip hop beat"): original composition,
68 BPM half-time feel (136 grid), muffled electric-piano chords through a low-pass, long deep 808, punchy kick,
crisp clap/snare on 3 with a reverb tail, sparse hats with triplet rolls, rim ghosts. Ducked under the voice.
Everything is generated; no samples.
usage: music4.py <voice.wav (mono 48k)> <out.wav> <duration> [lift,times]
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 136
BEAT = 60 / BPM
STEP = BEAT / 4
rng = np.random.default_rng(3)

voice_path, out_path = sys.argv[1], sys.argv[2]
DUR = float(sys.argv[3])
LIFTS = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
N = int(DUR * SR)
mix = {k: np.zeros(N + SR * 3) for k in ("drums", "bass", "keys", "snr", "fx")}


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





def fft_conv(x, ir):
    n = len(x) + len(ir)
    m = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]


def reverb_ir(dur, decay, lp):
    t = t_(dur)
    n = rng.standard_normal(len(t)) * np.exp(-t / decay)
    return onepole_lp(n, lp) * 0.08


def epiano(freqs, dur):
    """FM electric piano: bell-ish attack, warm sustain, gentle tremolo."""
    t = t_(dur)
    y = 0
    for f in freqs:
        idx = 1.6 * np.exp(-t / 0.35) + 0.3
        y = y + np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t)) * np.exp(-t / 2.2)
    y *= (1 + 0.18 * np.sin(2 * np.pi * 4.5 * t)) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.25)
    return y / len(freqs) * 0.5


def punch_kick():
    t = t_(0.3)
    f = 52 + 120 * np.exp(-t / 0.02)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.002) * 0.25
    return np.tanh(2.0 * (y + click)) * 0.75


def snare_clap():
    t = t_(0.3)
    n = rng.standard_normal(len(t))
    hp = n - onepole_lp(n, 2000)
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.04)
    bursts = sum(np.exp(-np.maximum(t - d, 0) / 0.01) * (t >= d) for d in (0, 0.009, 0.018))
    return (hp * (0.5 * bursts + 0.45 * np.exp(-t / 0.08)) + 0.35 * tone) * 0.6


def rim():
    t = t_(0.06)
    y = np.sin(2 * np.pi * 1700 * t) * np.exp(-t / 0.008) + np.sin(2 * np.pi * 820 * t) * np.exp(-t / 0.012)
    return y * 0.12


def sub808(f0, f1, dur):
    t = t_(dur)
    g = np.clip((t - 0.0) / 0.08, 0, 1)
    f = (f0 + (f1 - f0) * g) * (1 + 0.35 * np.exp(-t / 0.02))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    y = np.tanh(1.6 * y) * np.exp(-t / 2.5) * np.minimum(1, (dur - t) / 0.03) * np.minimum(1, t / 0.003)
    return y * 0.55


n2f = lambda n: 440.0 * 2 ** ((n - 69) / 12)
# Original progression in F minor: Fm9 | Dbmaj9 | Bbm9 | C7sus->C7  (MIDI voicings), 808 roots
PROG = [([53, 56, 60, 63, 67], 41), ([49, 53, 56, 60, 63], 37), ([46, 49, 53, 56, 60], 34), ([48, 53, 55, 58, 64], 36)]
BAR = 4 * BEAT
kicks = []
bar_i, at = 0, 0.0
while at < DUR:
    chord, root = PROG[bar_i % 4]
    add("keys", at, epiano([n2f(n) for n in chord], BAR + 0.05))
    rf = n2f(root)
    # 808 + kick: 1, "a" of 2, "and" of 3 (half-time bounce)
    for st, ln, slide in ((0, 7, 1.0), (7, 3, 1.0), (10, 6, 1.0 if bar_i % 2 == 0 else 2 ** (3 / 12))):
        add("drums", at + st * STEP, punch_kick())
        kicks.append(at + st * STEP)
        if at >= 1.7:  # 808 drops in after the first bar
            add("bass", at + st * STEP, sub808(rf, rf * slide, ln * STEP))
    if at >= 1.7:
        add("snr", at + 8 * STEP, snare_clap())
    for st in range(0, 16, 2):
        if bar_i % 2 == 1 and st == 12:
            for r in range(6):  # triplet roll
                add("drums", at + st * STEP + r * (4 * STEP) / 6, hat() * (0.45 + 0.08 * r))
            break
        add("drums", at + st * STEP, hat() * (0.7 if st % 4 == 0 else 0.5))
    for st in (3, 13):
        add("drums", at + st * STEP, rim())
    bar_i += 1
    at += BAR

for lift in LIFTS:
    add("fx", lift - 1.2, riser(1.2) * 0.6)
    add("fx", lift, crash() * 0.7)

drums, bass, keys, snr, fx = (mix[k][:N] for k in ("drums", "bass", "keys", "snr", "fx"))
t = np.arange(N) / SR
keys = onepole_lp(keys, 1400)                       # muffled, "underwater" keys
keys = keys + fft_conv(keys, reverb_ir(2.2, 0.7, 3000)) * 1.2
snr = snr + fft_conv(snr, reverb_ir(1.2, 0.35, 6000)) * 1.5
pump = np.ones(N)
for k in kicks:
    i = int(k * SR)
    seg = t_(BEAT)
    j = min(N, i + len(seg))
    if i < N:
        pump[i:j] = np.minimum(pump[i:j], 1 - 0.3 * np.exp(-seg[: j - i] / 0.12))
music = drums * 0.9 + bass * 1.5 + keys * pump * 0.45 + snr * 1.0 + fx * 0.5

w = wave.open(voice_path)
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.sqrt(onepole_lp(v ** 2, 6))
venv /= venv.max() + 1e-9
music *= 1 - 0.45 * np.clip(venv * 3, 0, 1)
music *= np.minimum(1, (DUR - t) / 0.8) * np.minimum(1, t / 0.15)

music = np.tanh(music * 1.2) / 1.2
target_rms = 10 ** (-33 / 20)
music *= target_rms / (np.sqrt((music ** 2).mean()) + 1e-9)
pcm = (np.clip(np.stack([music, music], 1), -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as o:
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
print(f"{BPM} bpm (half-time) hip-hop, peak {20 * np.log10(np.abs(music).max()):.1f} dBFS")
