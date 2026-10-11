"""Lift the music bed by +8 dB where nobody talks (the four silent exercise clips, 3.27-26.6 s).

usage: music_lift.py <music.wav>  (in place)
"""
import sys
import wave

import numpy as np

w = wave.open(sys.argv[1])
p = w.getparams()
a = np.frombuffer(w.readframes(p.nframes), np.int16).astype(float).reshape(-1, p.nchannels)
t = np.arange(len(a)) / p.framerate
up = 10 ** (8 / 20)
g = np.interp(t, [0, 3.0, 3.45, 26.15, 26.55, 99], [1, 1, up, up, 1, 1])
o = wave.open(sys.argv[1], "w")
o.setparams(p)
o.writeframes(np.clip(a * g[:, None], -32768, 32767).astype(np.int16).tobytes())
o.close()
