"""Cinematic score + voice-over mix for "Oyimga sovgʻa" (synthesized, royalty-free).

Reads timeline.json and vo_wav/*.wav, writes out/mix.wav (48 kHz stereo):
  0-12 s   soft piano + warm pad, gas-ignition SFX, swell into the title
  11.9 s   low "braam" + boom on the title card
  13-20 s  string ostinato + toms, one chord per product shot
  20-28 s  full: drums, strings, pad
  28.6 s   tender piano for "Oyijonim... bu sizga!"
  31.5 s+  uplifting end: major chords, light drums, final hit
The music ducks ~9 dB under the narration.
"""
import json
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
TL = json.load(open(os.path.join(HERE, "timeline.json")))
DUR = TL["dur"]
N = int(SR * DUR)
SH = TL["shots"]
rng = np.random.default_rng(3)

M = np.zeros((N, 2))      # music bus
SFX = np.zeros((N, 2))    # effects (not ducked as much)


def t_arr(sec):
    return np.arange(int(sec * SR)) / SR


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(bus, sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i] * gain
    bus[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2) * 1.414
    bus[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2) * 1.414


def lowpass(x, fc):
    # FFT brick-ish low-pass with a soft knee (fast for long signals)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def highpass(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def saw(f, t):
    ph = f * t
    return 2 * (ph - np.floor(ph + 0.5))


# ---------------- instruments ----------------
def piano(m, dur=2.5, vel=1.0):
    t = t_arr(dur)
    f = hz(m)
    s = np.zeros(len(t))
    for k, a in ((1, 1), (2, .45), (3, .22), (4, .12), (5, .06)):
        s += a * np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k * k)) * np.exp(-t * (1.2 + k * 0.9))
    s += 0.05 * rng.uniform(-1, 1, len(t)) * np.exp(-t * 120)          # hammer
    return s * np.minimum(1, t / 0.004) * vel * 0.5


def pad(notes, dur, bright=1200, attack=0.8):
    t = t_arr(dur)
    s = np.zeros(len(t))
    for m in notes:
        for d in (-0.006, 0, 0.007):
            s += saw(hz(m) * (1 + d), t + rng.uniform(0, 1))
    s = lowpass(s / (len(notes) * 3), bright)
    e = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / 0.8)
    return s * e


def strings_stac(m, dur=0.22):
    t = t_arr(dur)
    s = sum(saw(hz(m) * (1 + d), t) for d in (-0.004, 0.004)) / 2
    return lowpass(s, 2600) * np.minimum(1, t / 0.01) * np.exp(-t * 9)


def braam():
    t = t_arr(4.0)
    s = np.zeros(len(t))
    for m in (24, 31, 36, 43):                    # C1 G1 C2 G2
        for d in (-0.01, 0, 0.012):
            s += saw(hz(m) * (1 + d), t)
    s /= 12
    # opening filter: crossfade dark -> bright -> dark
    dark, bright = lowpass(s, 180), lowpass(s, 1400)
    k = np.minimum(1, t / 0.25) * np.exp(-t * 0.9)
    s = dark * (1 - k) + bright * k
    sub = np.sin(2 * np.pi * np.cumsum(32 + 30 * np.exp(-t * 5)) / SR) * np.exp(-t * 1.2)
    env = np.minimum(1, t / 0.02) * np.exp(-t * 0.75)
    return np.tanh((s * 1.6 + sub) * env * 1.4)


def boom():
    t = t_arr(2.5)
    s = np.sin(2 * np.pi * np.cumsum(28 + 70 * np.exp(-t * 9)) / SR) * np.exp(-t * 2.0)
    n = lowpass(rng.uniform(-1, 1, len(t)), 900) * np.exp(-t * 4)
    return np.tanh((s + n * 0.6) * 1.8)


def kick():
    t = t_arr(0.5)
    s = np.sin(2 * np.pi * np.cumsum(45 + 120 * np.exp(-t * 30)) / SR) * np.exp(-t * 6)
    return np.tanh(s * 1.8)


def snare():
    t = t_arr(0.4)
    n = highpass(rng.uniform(-1, 1, len(t)), 1500) * np.exp(-t * 14)
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    return n * 0.7 + tone * 0.5


def tom(f0=110):
    t = t_arr(0.8)
    return np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.6 * np.exp(-t * 12))) / SR) * np.exp(-t * 4.5)


def swell(length):            # reverse-cymbal style rise
    t = t_arr(length)
    n = highpass(rng.uniform(-1, 1, len(t)), 3000)
    return n * (t / length) ** 3


def click():
    t = t_arr(0.05)
    return highpass(rng.uniform(-1, 1, len(t)) * np.exp(-t * 180), 2500) * 1.2


def whoomp():
    t = t_arr(1.2)
    n = lowpass(rng.uniform(-1, 1, len(t)), 1000)
    body = np.sin(2 * np.pi * np.cumsum(50 + 40 * np.exp(-t * 6)) / SR) * np.exp(-t * 3)
    return np.tanh((n * 1.3 + body) * np.minimum(1, t / 0.04) * np.exp(-t * 2.6) * 1.5)


def hiss(length):
    t = t_arr(length)
    n = highpass(lowpass(rng.uniform(-1, 1, len(t)), 5000), 1200)
    return n * np.minimum(1, t / 0.3) * np.minimum(1, (length - t) / 0.6)


# chords (MIDI): Am F C G and major end C G Am F
AM, F, C, G = (57, 60, 64), (53, 57, 60), (55, 60, 64), (55, 59, 62)

# ---------------- 0 - 12 s: intro ----------------
for at in (0.30, 0.42):
    add(SFX, click(), at, pan=0.25, gain=0.45)
add(SFX, whoomp(), 0.58, gain=0.7)
add(SFX, hiss(5.0), 0.6, gain=0.06)
prog = [AM, F, C, G]
for i, at in enumerate((1.0, 4.0, 7.0, 10.0)):
    ch = prog[i % 4]
    add(M, pad([n - 12 for n in ch] + [ch[0] - 24], 3.4 if at < 10 else 2.0, bright=900), at, gain=0.35)
    for j, m in enumerate((ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1])):
        add(M, piano(m + 12, 2.2, 0.8 if j else 1.0), at + j * 0.5, pan=-0.2 + 0.08 * j, gain=0.55)
add(M, swell(2.6), SH["title"][0] - 2.6, gain=0.35)

# ---------------- title ----------------
add(SFX, braam(), SH["title"][0], gain=0.95)
add(SFX, boom(), SH["title"][0], gain=0.7)

# ---------------- product shots: ostinato + toms ----------------
p0, p1 = SH["lt110"][0], SH["ferre"][1]
for k, name in enumerate(("lt110", "lt305", "lt265", "ferre")):
    a, b = SH[name]
    ch = prog[k]
    add(M, pad([n - 12 for n in ch], b - a + 0.3, bright=1500, attack=0.2), a, gain=0.32)
    add(SFX, tom(95 - k * 8), a, gain=0.55)
    add(M, boom(), a, gain=0.25)
    i = 0
    tt = a
    while tt < b:
        m = (ch[0] - 12, ch[0], ch[2] - 12, ch[0])[i % 4]
        add(M, strings_stac(m), tt, pan=-0.3 if i % 2 else 0.3, gain=0.4)
        if i % 2 == 0:
            add(M, kick(), tt, gain=0.5)
        tt += 0.25
        i += 1
add(M, swell(1.6), SH["grid"][0] - 1.6, gain=0.35)

# ---------------- grid: full ----------------
a, b = SH["grid"]
add(SFX, boom(), a, gain=0.6)
beat = 0.5
k = 0
tt = a
while tt < b - 0.3:
    bar = int((tt - a) / 2.0)
    ch = prog[bar % 4]
    pos = int(round((tt - a) / beat)) % 4
    add(M, kick(), tt, gain=0.55)
    if pos in (1, 3):
        add(M, snare(), tt, gain=0.35)
    for sub in range(2):
        m = (ch[0] - 12, ch[0])[sub]
        add(M, strings_stac(m), tt + sub * 0.25, pan=-0.3 if sub else 0.3, gain=0.32)
    if pos == 0:
        add(M, pad([n - 12 for n in ch] + [ch[0] - 24], 2.1, bright=2200, attack=0.1), tt, gain=0.3)
        add(M, piano(ch[2] + 12, 1.8), tt, gain=0.4)
    tt += beat
add(M, swell(1.2), SH["hero"][0] - 1.2, gain=0.3)

# ---------------- hero: tender ----------------
a, b = SH["hero"]
for j, (ch, at) in enumerate(((F, a), (C, a + 1.5))):
    add(M, pad([n - 12 for n in ch], 1.8, bright=800, attack=0.4), at, gain=0.35)
    for q, m in enumerate((ch[0] + 12, ch[1] + 12, ch[2] + 12)):
        add(M, piano(m, 2.4, 0.7), at + q * 0.35, pan=0.15 * (q - 1), gain=0.5)

# ---------------- end card: uplifting ----------------
a, b = SH["cta"]
add(SFX, boom(), a, gain=0.5)
end_prog = [C, G, AM, F]
tt, i = a, 0
while tt < 41.0:
    ch = end_prog[i % 4]
    add(M, pad([n - 12 for n in ch] + [ch[0] - 24], 2.1, bright=1800, attack=0.15), tt, gain=0.3)
    for q in range(4):
        add(M, kick(), tt + q * 0.5, gain=0.4)
        if q in (1, 3):
            add(M, snare(), tt + q * 0.5, gain=0.22)
        add(M, piano(ch[q % 3] + 12 + (12 if q == 3 else 0), 1.6, 0.8), tt + q * 0.5, pan=0.2 * (q - 1.5), gain=0.4)
    tt += 2.0
    i += 1
# final chord hit (C major) under "Sifat va qulay narx"
add(SFX, boom(), 41.0, gain=0.55)
add(M, pad([48, 55, 60, 64, 67], 2.0, bright=2400, attack=0.02), 41.0, gain=0.45)
for m in (72, 76, 79, 84):
    add(M, piano(m, 2.0), 41.0, gain=0.35)


# ---------------- reverb ----------------
def reverb(x, seconds=2.2, wet=0.22):
    ir_len = int(seconds * SR)
    t = np.arange(ir_len) / SR
    out = np.zeros_like(x)
    for c in range(2):
        ir = rng.normal(0, 1, ir_len) * np.exp(-t * 3.2)
        ir = lowpass(ir, 6000)
        ir /= np.sqrt(np.sum(ir ** 2))
        L = len(x) + ir_len
        n = 1 << (L - 1).bit_length()
        y = np.fft.irfft(np.fft.rfft(x[:, c], n) * np.fft.rfft(ir, n), n)[: len(x)]
        out[:, c] = y
    return x * (1 - wet) + out * wet * 1.6


M = reverb(M, 2.6, 0.30)
SFX = reverb(SFX, 2.0, 0.18)


# ---------------- voice-over ----------------
def read_wav(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


VOX = np.zeros(N)
for vid, at in TL["vo"].items():
    v = read_wav(os.path.join(HERE, "vo_wav", f"{vid}.wav"))
    v = highpass(v, 85)
    v = np.tanh(v / (np.max(np.abs(v)) + 1e-9) * 1.6) * 0.8     # gentle compression
    i = int(at * SR)
    VOX[i:i + len(v)] += v[: N - i]
# a little room around the voice
vx = np.stack([VOX, VOX], axis=1)
vx = reverb(vx, 0.7, 0.10)

# ducking envelope from the voice
env = np.abs(VOX)
win = int(0.03 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
env = env / (env.max() + 1e-9)
duck = np.zeros(N)
a_att, a_rel, g = np.exp(-1 / (0.02 * SR)), np.exp(-1 / (0.35 * SR)), 0.0
for i in range(0, N, 32):                      # block-wise smoothing (fast enough)
    target = min(1.0, env[i] * 4)
    a = a_att if target > g else a_rel
    g = target + (g - target) * (a ** 32)
    duck[i:i + 32] = g
music_gain = 1 - 0.62 * duck[:, None]           # about -8.5 dB under the voice
sfx_gain = 1 - 0.40 * duck[:, None]

mix = M * 0.55 * music_gain + SFX * 0.6 * sfx_gain + vx * 1.0
fade = np.minimum(1, (N - np.arange(N)) / (1.5 * SR))[:, None]
mix = np.tanh(mix * fade * 1.05)
mix /= np.max(np.abs(mix)) / 0.9

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
out = os.path.join(HERE, "out", "mix.wav")
import wave
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out)
