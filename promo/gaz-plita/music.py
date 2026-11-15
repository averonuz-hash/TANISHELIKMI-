"""Original energetic background track for the AVERON gas-stove promo (synthesized, royalty-free).

120 BPM, C major (C - G - Am - F), 24 s. Starts with gas-ignition sound effects (clicks + whoosh),
the beat drops at 1.0 s; hits on every product change (3, 7, 11, 15 s) and the call to action (19 s),
a whoosh on each whip transition and a bright "ding" when each price lands.
Writes out/music.wav (44.1 kHz stereo).
"""
import os
import wave
import numpy as np

SR = 44100
DUR = 24.0
BPM = 120
BEAT = 60 / BPM
N = int(SR * DUR)
rng = np.random.default_rng(11)
INTRO_END = 1.0

L = np.zeros(N)
R = np.zeros(N)


def t_arr(sec):
    return np.arange(int(sec * SR)) / SR


def add(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i : i + len(sig)] += sig * np.sqrt((1 - pan) / 2) * 1.414
    R[i : i + len(sig)] += sig * np.sqrt((1 + pan) / 2) * 1.414


def env(n, a=0.002, d=0.2, sr=SR):
    t = np.arange(n) / sr
    e = np.minimum(1, t / a) * np.exp(-t / d)
    return e


def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def lowpass(x, cutoff):
    # simple one-pole low-pass
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def highpass(x, cutoff):
    return x - lowpass(x, cutoff)


# ---------------- drums ----------------
def kick():
    t = t_arr(0.45)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7)
    s += 0.6 * np.exp(-t * 300) * rng.uniform(-1, 1, len(t))  # click
    return np.tanh(s * 1.6)


def clap():
    t = t_arr(0.3)
    n = rng.uniform(-1, 1, len(t))
    e = np.zeros(len(t))
    for off in (0, 0.011, 0.022):
        e += (t >= off) * np.exp(-np.maximum(t - off, 0) * 60)
    e += 0.6 * np.exp(-t * 14)
    return highpass(n * e, 900) * 0.8


def hat(open_=False):
    t = t_arr(0.25 if open_ else 0.06)
    n = highpass(rng.uniform(-1, 1, len(t)), 7000)
    return n * np.exp(-t * (12 if open_ else 70))


def impact():
    t = t_arr(2.0)
    boom = np.sin(2 * np.pi * np.cumsum(30 + 80 * np.exp(-t * 8)) / SR) * np.exp(-t * 2.2)
    noise = lowpass(rng.uniform(-1, 1, len(t)), 2500) * np.exp(-t * 3.0)
    return np.tanh((boom * 1.2 + noise * 0.9) * 1.5)


def riser(length):
    t = t_arr(length)
    n = rng.uniform(-1, 1, len(t))
    # sweep: progressively brighter noise + rising tone
    k = t / length
    bright = highpass(n, 2000) * k + lowpass(n, 1500) * (1 - k)
    tone = np.sin(2 * np.pi * np.cumsum(200 + 1400 * k ** 2) / SR) * 0.25
    return (bright * 0.5 + tone) * k ** 1.5


def whoosh():
    t = t_arr(0.5)
    n = rng.uniform(-1, 1, len(t))
    e = np.sin(np.pi * t / 0.5) ** 2
    return lowpass(n, 3000) * e * 0.7


# ---------------- synths ----------------
def saw(f, t, detune=0.0):
    ph = (f * (1 + detune)) * t
    return 2 * (ph - np.floor(ph + 0.5))


def supersaw(freq, length, voices=5, spread=0.012):
    t = t_arr(length)
    s = np.zeros(len(t))
    for v in range(voices):
        d = (v - (voices - 1) / 2) * spread / voices
        s += saw(freq, t + rng.uniform(0, 1 / freq), d)
    return s / voices


def stab(notes, length=0.22):
    s = sum(supersaw(hz(m), length) for m in notes) / len(notes)
    s = lowpass(s, 4200)
    return s * env(len(s), 0.003, 0.12)


def pad(notes, length):
    s = sum(supersaw(hz(m), length, voices=7, spread=0.02) for m in notes) / len(notes)
    s = lowpass(s, 1800)
    t = t_arr(length)
    e = np.minimum(1, t / 0.08) * np.minimum(1, (length - t) / 0.15)
    return s * e


def bass(midi, length):
    t = t_arr(length)
    f = hz(midi)
    s = np.tanh(2.2 * (np.sin(2 * np.pi * f * t) + 0.35 * saw(f, t)))
    return lowpass(s, 900) * env(len(t), 0.004, 0.25)


def pluck(midi, length=0.2):
    t = t_arr(length)
    f = hz(midi)
    s = saw(f, t) * 0.6 + np.sin(2 * np.pi * f * 2 * t) * 0.4
    return lowpass(s, 5000) * env(len(t), 0.002, 0.07)


# chord per bar (bar = 2 s): Am F C G, repeated
CHORDS = [
    (60, 64, 67),  # C
    (59, 62, 67),  # G/B
    (57, 60, 64),  # Am
    (57, 60, 65),  # F
]
ROOTS = [36, 43, 45, 41]
ARP = [0, 1, 2, 1, 2, 0, 2, 1]

K, C, HO, HC = kick(), clap(), hat(True), hat(False)

bars = int(DUR / (4 * BEAT))
for bar in range(bars):
    b0 = bar * 4 * BEAT
    ch = CHORDS[bar % 4]
    root = ROOTS[bar % 4]
    intro = b0 + 4 * BEAT <= INTRO_END
    break_bar = 10.0 <= b0 + 0.01 < 11.0  # none at 120 bpm, kept for clarity
    for beat in range(4):
        t0 = b0 + beat * BEAT
        intro = t0 < INTRO_END
        # four-on-the-floor (intro: kick only on 1 and 3 for build)
        if not intro or beat in (0, 2):
            add(K, t0, gain=0.95)
        if not intro and beat in (1, 3):
            add(C, t0, pan=0.0, gain=0.55)
        if not intro:
            add(HO, t0 + BEAT / 2, pan=0.25, gain=0.22)
            add(HC, t0 + BEAT / 4, pan=-0.3, gain=0.12)
            add(HC, t0 + 3 * BEAT / 4, pan=-0.3, gain=0.12)
        # off-beat bass (sidechain feel)
        add(bass(root, BEAT / 2 - 0.02), t0 + BEAT / 2, gain=0.55)
        if not intro:
            add(bass(root + 12, BEAT / 4 - 0.02), t0 + 3 * BEAT / 4, gain=0.25)
    # chord stabs: syncopated pattern (in 1/8ths)
    for step in (0, 3, 6):
        add(stab(ch), b0 + step * BEAT / 2, pan=-0.35, gain=0.32)
        add(stab(tuple(n + 12 for n in ch)), b0 + step * BEAT / 2, pan=0.35, gain=0.18)
    # pad underneath
    add(pad(ch, 4 * BEAT), b0, gain=0.10 if not intro else 0.16)
    # 16th arp
    if True:
        for i in range(16):
            if b0 + i * BEAT / 4 < INTRO_END:
                continue
            n = ch[ARP[i % 8]] + 12 + (12 if i % 4 == 3 else 0)
            add(pluck(n), b0 + i * BEAT / 4, pan=0.5 if i % 2 else -0.5, gain=0.12)

# ---- gas ignition SFX (hook) ----
def click():
    t = t_arr(0.05)
    n = rng.uniform(-1, 1, len(t)) * np.exp(-t * 180)
    return highpass(n, 2500) * 1.2 + np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 250) * 0.5


def whoomp():
    t = t_arr(0.9)
    n = lowpass(rng.uniform(-1, 1, len(t)), 1200)
    e = np.minimum(1, t / 0.03) * np.exp(-t * 3.2)
    body = np.sin(2 * np.pi * np.cumsum(55 + 40 * np.exp(-t * 6)) / SR) * np.exp(-t * 4)
    return np.tanh((n * 1.4 + body) * e * 1.5)


def hiss(length):
    t = t_arr(length)
    n = highpass(lowpass(rng.uniform(-1, 1, len(t)), 6000), 1500)
    return n * np.minimum(1, t / 0.1) * np.minimum(1, (length - t) / 0.2)


def ding():
    t = t_arr(0.9)
    s = sum(np.sin(2 * np.pi * f * t) * a for f, a in ((1568, 1), (2093, .6), (3136, .3)))
    return s * np.exp(-t * 5) * np.minimum(1, t / 0.003)


for at in (0.10, 0.18, 0.27):
    add(click(), at, pan=0.3, gain=0.5)
add(whoomp(), 0.38, gain=0.8)
add(hiss(0.62), 0.38, gain=0.12)
add(riser(0.6), 0.4, gain=0.35)

for at, g in ((1.0, 0.95), (3.0, 0.8), (7.0, 0.7), (11.0, 0.7), (15.0, 0.7), (19.0, 0.95)):
    add(impact(), at, gain=g)
for at in (6.65, 10.65, 14.65, 18.65):          # whip transitions between products
    add(whoosh(), at, pan=-0.3, gain=0.7)
for at in (4.0, 8.0, 12.0, 16.0):               # price slams
    add(ding(), at, gain=0.22)
add(riser(1.5), 17.5, gain=0.45)                # build into the call to action
for i, m in enumerate((72, 76, 79, 84)):
    add(pluck(m, 0.4), 20.0 + i * 0.08, gain=0.25)

mix = np.stack([L, R], axis=1)
# gentle compression/limit + fades
mix = np.tanh(mix * 1.1) * 0.9
fade_in = np.minimum(1, np.arange(N) / (0.02 * SR))
fade_out = np.minimum(1, (N - np.arange(N)) / (0.8 * SR))
mix *= (fade_in * fade_out)[:, None]
mix /= np.max(np.abs(mix)) / 0.89

os.makedirs(os.path.join(os.path.dirname(__file__), "out"), exist_ok=True)
out = os.path.join(os.path.dirname(__file__), "out", "music.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out)
