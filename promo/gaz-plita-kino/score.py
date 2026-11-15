"""Soundtrack for "Oyimga sovgʻa": recorded music + real sound effects + narration.

- Music: Mixkit "A New Life" (music_src/543.mp3, Mixkit Stock Music Free License).
  The track's big entry (~24 s) is aligned with the title card; the CTA crossfades
  (beat-matched) into the track's own ending so it finishes naturally.
- SFX (Mixkit Sound Effects Free License): gas ignition, gas burner hum, frying in a pan.
- Voice: vo_wav/*.wav, gently EQ'd (warmth, de-essed, softened top end), lightly compressed,
  with a small room so it sits in the scene; music ducks ~9 dB under it.
Writes out/mix.wav (48 kHz stereo).
"""
import json
import os
import subprocess
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
TL = json.load(open(os.path.join(HERE, "timeline.json")))
DUR = TL["dur"]
N = int(SR * DUR)
SH = TL["shots"]
rng = np.random.default_rng(5)


def read(path, ch=2):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return x.reshape(-1, ch) if ch > 1 else x


def eq(x, bands):
    """FFT EQ. bands: list of (kind, f, gain_db) with kind in lowshelf/highshelf/peak/hp."""
    X = np.fft.rfft(x, axis=0)
    f = np.fft.rfftfreq(x.shape[0], 1 / SR)
    g = np.ones_like(f)
    for kind, fc, db in bands:
        a = 10 ** (db / 20)
        if kind == "hp":
            g *= 1 - 1 / (1 + (f / fc) ** 4)
        elif kind == "lowshelf":
            g *= 1 + (a - 1) / (1 + (f / fc) ** 2)
        elif kind == "highshelf":
            g *= 1 + (a - 1) / (1 + (fc / np.maximum(f, 1)) ** 2)
        elif kind == "peak":
            q = 1.2
            g *= 1 + (a - 1) / (1 + ((f - fc) / (fc / q)) ** 2)
    X *= g[:, None] if x.ndim > 1 else g
    return np.fft.irfft(X, x.shape[0], axis=0)


def reverb(x, seconds, wet, seed=1):
    r = np.random.default_rng(seed)
    n_ir = int(seconds * SR)
    t = np.arange(n_ir) / SR
    out = np.zeros_like(x)
    for c in range(x.shape[1]):
        ir = r.normal(0, 1, n_ir) * np.exp(-t * (6.9 / seconds))
        ir = eq(ir[:, None], [("highshelf", 5000, -8)])[:, 0]
        ir /= np.sqrt(np.sum(ir ** 2))
        L = x.shape[0] + n_ir
        n = 1 << (L - 1).bit_length()
        out[:, c] = np.fft.irfft(np.fft.rfft(x[:, c], n) * np.fft.rfft(ir, n), n)[: x.shape[0]]
    return x * (1 - wet) + out * wet


def place(bus, sig, at, gain=1.0):
    i = int(at * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    n = min(len(sig), N - i)
    if n > 0:
        bus[i:i + n] += sig[:n] * gain


def onset_env(x, hop=480):
    m = x.mean(axis=1) if x.ndim > 1 else x
    fr = len(m) // hop
    e = np.log(np.array([np.sum(m[i * hop:(i + 1) * hop] ** 2) for i in range(fr)]) + 1e-9)
    return np.maximum(0, np.diff(e, prepend=e[0])), hop / SR


# ---------------- music ----------------
mus = read(os.path.join(HERE, "music_src", "543.mp3"))
on, dt = onset_env(mus)
# 1) the big entry near 24 s -> aligned to just after the title card appears
w0, w1 = int(23.4 / dt), int(24.6 / dt)
entry = (w0 + int(np.argmax(on[w0:w1]))) * dt
TITLE_HIT = SH["title"][0] + 0.12
offset = entry - TITLE_HIT                       # track time = video time + offset
# 2) beat-matched jump into the track's ending for the CTA
XF_AT, XF_LEN = SH["cta"][0] - 0.6, 1.2          # crossfade window in video time
src_a = XF_AT + offset                            # where we leave the track
best, best_d = -1, 33.0
seg_a = on[int(src_a / dt): int((src_a + 3.0) / dt)]
for d in np.arange(31.5, 34.5, dt):
    i = int((src_a + d) / dt)
    seg_b = on[i:i + len(seg_a)]
    if len(seg_b) < len(seg_a):
        continue
    c = float(np.dot(seg_a - seg_a.mean(), seg_b - seg_b.mean()))
    if c > best:
        best, best_d = c, d
jump = best_d
print(f"music: entry {entry:.2f}s -> video {TITLE_HIT:.2f}s (offset {offset:.2f}); CTA jump +{jump:.2f}s")

M = np.zeros((N, 2))
tv = np.arange(N) / SR
idx_a = ((tv + offset) * SR).astype(int)
idx_b = ((tv + offset + jump) * SR).astype(int)
A = np.where((idx_a >= 0)[:, None] & (idx_a < len(mus))[:, None], mus[np.clip(idx_a, 0, len(mus) - 1)], 0)
B = np.where((idx_b >= 0)[:, None] & (idx_b < len(mus))[:, None], mus[np.clip(idx_b, 0, len(mus) - 1)], 0)
k = np.clip((tv - XF_AT) / XF_LEN, 0, 1)[:, None]
k = 0.5 - 0.5 * np.cos(np.pi * k)                 # equal-power-ish
M = A * np.sqrt(1 - k) + B * np.sqrt(k)
# soften during the intimate "Oyijonim... bu sizga" moment, swell into the title
dip = 1 - 0.35 * np.clip(1 - np.abs(tv - (TL["vo"]["09"] + 0.7)) / 1.2, 0, 1)
M *= dip[:, None]
M *= np.clip(tv / 1.2, 0, 1)[:, None]             # fade in from black

# ---------------- sound effects ----------------
SFX = np.zeros((N, 2))
ign = read(os.path.join(HERE, "sfx_src", "1801.wav"))
hum = read(os.path.join(HERE, "sfx_src", "1797.wav"))
fry = read(os.path.join(HERE, "sfx_src", "133.wav"))


def loop(x, seconds, xf=0.25):
    """Seamless loop by overlapping copies with cosine crossfades."""
    n, f = int(seconds * SR), int(xf * SR)
    out = np.zeros((n, 2))
    step = len(x) - f
    ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, f))[:, None]
    pos = 0
    while pos < n:
        y = x.copy()
        y[:f] *= ramp
        y[-f:] *= ramp[::-1]
        m = min(len(y), n - pos)
        out[pos:pos + m] += y[:m]
        pos += step
    e = np.ones((n, 1))
    e[:f] = ramp
    e[-f:] = ramp[::-1]
    return out * e


fa, fb = SH["flame"]
place(SFX, ign, 0.35, 1.0)
place(SFX, loop(hum, fb - 0.3 + 0.6), 0.45, 0.55)
place(SFX, loop(fry, fb - 0.8 + 0.6), 0.9, 0.85)
place(SFX, loop(fry, 2.4) * 0.6, SH["food"][0] - 0.1, 0.35)     # simmering sauce
SFX = reverb(SFX, 0.6, 0.15, seed=3)

# ---------------- narration ----------------
VOX = np.zeros((N, 2))
for vid, at in TL["vo"].items():
    v = read(os.path.join(HERE, "vo_wav", f"{vid}.wav"), ch=1)[:, None]
    v = eq(v, [("hp", 80, 0), ("lowshelf", 220, 2.0), ("peak", 3200, 1.0), ("peak", 6800, -3.5), ("highshelf", 11000, -4.0)])
    pk = np.max(np.abs(v)) + 1e-9
    v = np.tanh(v / pk * 1.4) / np.tanh(1.4) * 0.75            # soft compression
    place(VOX, np.repeat(v, 2, axis=1), at, 1.0)
VOX = reverb(VOX, 0.45, 0.07, seed=7)
# faint room tone under the whole film so the voice never sits on digital silence
room = eq(rng.normal(0, 1, (N, 2)), [("hp", 120, 0), ("highshelf", 3000, -18)])
VOX += room / np.max(np.abs(room)) * 10 ** (-58 / 20)

# ---------------- ducking + mix ----------------
env = np.abs(VOX[:, 0])
win = int(0.03 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
env = np.clip(env / (np.percentile(env[env > 1e-4], 90) + 1e-9), 0, 1)
duck = np.zeros(N)
g, a_att, a_rel = 0.0, np.exp(-32 / (0.03 * SR)), np.exp(-32 / (0.40 * SR))
for i in range(0, N, 32):
    target = env[i]
    a = a_att if target > g else a_rel
    g = target + (g - target) * a
    duck[i:i + 32] = g
music_gain = (1 - 0.65 * duck)[:, None]          # about -9 dB under the voice

mus_rms = np.sqrt(np.mean(M[int(14 * SR):int(28 * SR)] ** 2)) + 1e-9
mix = M / mus_rms * 0.16 * music_gain + SFX * 1.3 + VOX * 0.9
end_fade = np.clip((DUR - tv) / 0.8, 0, 1)[:, None]
mix *= end_fade
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) / 0.9

os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
out = os.path.join(HERE, "out", "mix.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("wrote", out)
