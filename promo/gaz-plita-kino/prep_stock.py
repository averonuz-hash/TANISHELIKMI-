"""Cut, slow down, crop to 9:16 and upscale the Mixkit stock clips into 2160x3840 JPEG frames
(out/frames/<shot>/0001.jpg ...) at the video frame rate, padded by a few frames for transitions."""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, "timeline.json")))
FPS = TL["fps"]
PAD = 0.5  # seconds of extra footage on each side for crossfades

manifest = {}
for name, st in TL["stock"].items():
    a, b = TL["shots"][name]
    dur = b - a + 2 * PAD
    src = os.path.join(HERE, "stock_src", st["clip"] + ".mp4")
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(","))
    if w > h:   # landscape: crop a 9:16 window around cx
        cw = int(h * 9 / 16) // 2 * 2
        x = max(0, min(w - cw, int(w * st["cx"] - cw / 2)))
        crop = f"crop={cw}:{h}:{x}:0,"
    else:
        crop = ""
    out = os.path.join(HERE, "out", "frames", name)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))
    speed = st["speed"]
    start = max(0.0, st["src"] - PAD * speed)
    vf = (f"setpts=PTS/{speed},{crop}scale=2160:3840:flags=lanczos,"
          f"unsharp=5:5:0.35:5:5:0.0,fps={FPS}")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{start:.3f}", "-i", src,
                    "-t", f"{dur + 0.2:.3f}", "-vf", vf, "-q:v", "2",
                    os.path.join(out, "%04d.jpg")], check=True)
    n = len(os.listdir(out))
    manifest[name] = {"frames": n, "lead": (st["src"] - start) / speed}
    print(f"{name}: {st['clip']} {n} frames ({n / FPS:.2f}s, need {dur:.2f}s)")
json.dump(manifest, open(os.path.join(HERE, "out", "frames", "manifest.json"), "w"), indent=1)
