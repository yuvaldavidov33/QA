"""Dark hip-hop beat matched to the client's reference clip (b3d2041e-….mp4 on main), measured from its audio:
~101 BPM (8th-note hats every 0.297 s with 16th doubles), a deep sustained 808 sitting on D1 (~37 Hz) almost
without gaps, doubled snare hits, no melody instruments. Original composition; nothing taken from the clip.
Ducked under the voice. usage: music5.py <voice.wav (mono 48k)> <out.wav> <duration> [lift,times]
"""
import sys
import wave

import numpy as np

SR = 48000
BPM = 101
BEAT = 60 / BPM
STEP = BEAT / 4
rng = np.random.default_rng(3)

voice_path, out_path = sys.argv[1], sys.argv[2]
DUR = float(sys.argv[3])
LIFTS = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else []
N = int(DUR * SR)
mix = {k: np.zeros(N + SR * 3) for k in ("drums", "bass", "snr", "fx")}


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
    return onepole_lp(rng.standard_normal(len(t)) * np.exp(-t / decay), lp) * 0.08


def kick_hh():
    t = t_(0.35)
    f = 45 + 135 * np.exp(-t / 0.022)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.1)
    click = rng.standard_normal(len(t)) * np.exp(-t / 0.0025) * 0.3
    return np.tanh(2.2 * (y + click)) * 0.8


def snare_hh():
    t = t_(0.28)
    n = rng.standard_normal(len(t))
    hp = n - onepole_lp(n, 1800)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    return np.tanh(1.8 * (hp * np.exp(-t / 0.085) * 0.65 + body * 0.4)) * 0.6


def hat_hh(open_=False):
    t = t_(0.12 if open_ else 0.035)
    n = rng.standard_normal(len(t))
    hp = n - onepole_lp(n, 8000)
    return hp * np.exp(-t / (0.045 if open_ else 0.008)) * 0.2


def deep808(notes, dur):
    """One long 808 line: list of (time, freq) targets with short glides; sustained, almost no gaps."""
    t = t_(dur)
    f = np.full(len(t), notes[0][1])
    for (t0, f0), (t1, f1) in zip(notes, notes[1:] + [(dur, notes[-1][1])]):
        i0, i1 = int(t0 * SR), int(t1 * SR)
        g = np.clip((t[i0:i1] - t0) / 0.07, 0, 1)
        f[i0:i1] = f0 if i0 == 0 else (prev + (f0 - prev) * g)
        prev = f0
    y = np.sin(2 * np.pi * np.cumsum(f) / SR)
    y = y + 0.25 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR)  # 2nd harmonic so phones hear it
    return np.tanh(2.2 * y) * 0.55


D1, F1, C1, A0 = 36.71, 43.65, 32.70, 27.5
BAR = 4 * BEAT
kicks, line = [], []
bar_i, at = 0, 0.0
while at < DUR:
    # 808 line (2-bar phrase): D... slide F... back D, C pickup
    if bar_i % 2 == 0:
        line += [(at, D1), (at + 10 * STEP, D1 * 1.0)]
    else:
        line += [(at, D1), (at + 6 * STEP, F1), (at + 12 * STEP, C1 * 2 if False else D1), (at + 14 * STEP, C1 * 1.0)]
    for st in ((0, 10) if bar_i % 2 == 0 else (0, 6, 11)):
        add("drums", at + st * STEP, kick_hh())
        kicks.append(at + st * STEP)
    for st in (4, 12):  # snare on 2 and 4, doubled with a 16th ghost on 4
        add("snr", at + st * STEP, snare_hh())
    add("snr", at + 13 * STEP, snare_hh() * 0.55)
    for st in range(0, 16, 2):
        add("drums", at + st * STEP, hat_hh(open_=(st == 14 and bar_i % 2 == 1)) * (1.0 if st % 4 == 0 else 0.75))
        if st in (6, 10) or (bar_i % 2 == 1 and st == 14):
            add("drums", at + (st + 1) * STEP, hat_hh() * 0.6)
    bar_i += 1
    at += BAR

add("bass", 0.0, deep808(line, DUR + 1))
for lift in LIFTS:
    add("fx", lift - 1.0, riser(1.0) * 0.5)
    add("fx", lift, crash() * 0.6)

drums, bass, snr, fx = (mix[k][:N] for k in ("drums", "bass", "snr", "fx"))
t = np.arange(N) / SR
snr = snr + fft_conv(snr, reverb_ir(0.9, 0.25, 6000)) * 1.2
duck_k = np.ones(N)
for k in kicks:  # bass ducks briefly under each kick so both punch
    i = int(k * SR)
    seg = t_(0.18)
    j = min(N, i + len(seg))
    if i < N:
        duck_k[i:j] = np.minimum(duck_k[i:j], 1 - 0.6 * np.exp(-seg[: j - i] / 0.05))
music = drums * 0.85 + bass * duck_k * 1.1 + snr * 0.95 + fx * 0.45

w = wave.open(voice_path)
v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
v = np.pad(v, (0, max(0, N - len(v))))[:N]
venv = np.sqrt(onepole_lp(v ** 2, 6))
venv /= venv.max() + 1e-9
music *= 1 - 0.4 * np.clip(venv * 3, 0, 1)
music *= np.minimum(1, (DUR - t) / 0.7) * np.minimum(1, t / 0.05)

music = np.tanh(music * 1.2) / 1.2
target_rms = 10 ** (-32 / 20)
music *= target_rms / (np.sqrt((music ** 2).mean()) + 1e-9)
pcm = (np.clip(np.stack([music, music], 1), -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as o:
    o.setnchannels(2)
    o.setsampwidth(2)
    o.setframerate(SR)
    o.writeframes(pcm.tobytes())
print(f"{BPM} bpm dark hip-hop, peak {20 * np.log10(np.abs(music).max()):.1f} dBFS")
