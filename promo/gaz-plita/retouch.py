"""Retouch the store photos: remove the photographer's reflection from the mirror oven doors
(OpenCV inpainting + soft blend), then save cropped, colour-tuned product shots for the video.

Polygons are in "display" coordinates of a 1500x2000 frame; source photos are 3000x4000.
"""
import os
import sys
import cv2
import numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "source")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")
os.makedirs(OUT, exist_ok=True)

PHOTOS = {
    # name: (file, [mask polygons], door rect for soft-blur (x0,y0,x1,y1), crop (x0,y0,x1,y1))
    "lt110": ("lifetech_lt110.jpg",
              [[(545, 670), (915, 670), (912, 915), (545, 915)]],
              (110, 560, 1170, 905), (0, 160, 1500, 1660)),
    "lt305": ("lifetech_lt305.jpg",
              [[(430, 742), (830, 742), (812, 950), (800, 1118), (365, 1118), (378, 955)],
               [(1190, 690), (1290, 690), (1290, 750), (1190, 750)]],   # orange hand-written sticker
              (110, 600, 1390, 1320), (0, 150, 1500, 1650)),
    "ferre": ("ferre_bt60f31.jpg",
              [[(290, 935), (770, 935), (770, 1105), (290, 1105)],
               [(575, 1050), (670, 1050), (670, 1090), (575, 1090)],
               [(820, 1055), (895, 1055), (895, 1260), (820, 1260)]],     # blue protective tape
              (420, 940, 1080, 1265), (0, 220, 1500, 1720)),
    "lt265": ("lifetech_lt265.jpg",
              [[(490, 855), (900, 855), (925, 1160), (395, 1160), (420, 975)]],
              (190, 730, 1460, 1380), (0, 230, 1500, 1730)),
}


def build(name):
    f, polys, door, crop = PHOTOS[name]
    img = cv2.imread(os.path.join(SRC, f))
    h, w = img.shape[:2]
    k = w / 1500.0
    mask = np.zeros((h, w), np.uint8)
    for p in polys:
        cv2.fillPoly(mask, [np.array([(int(x * k), int(y * k)) for x, y in p], np.int32)], 255)
    # fill each masked row by interpolating between the mirror pixels just left and right of it,
    # so the reflected floor/tile lines continue naturally (no smearing from the handle above)
    fill = img.astype(np.float32).copy()
    ys = np.where(mask.any(axis=1))[0]
    pad, smp = int(10 * k), int(30 * k)
    for y in ys:
        xs = np.where(mask[y] > 0)[0]
        xl, xr = max(xs.min() - pad, smp), min(xs.max() + pad, w - smp - 1)
        cl = np.median(img[y, xl - smp:xl].astype(np.float32), axis=0)
        cr = np.median(img[y, xr:xr + smp].astype(np.float32), axis=0)
        u = np.linspace(0, 1, xr - xl)[:, None]
        fill[y, xl:xr] = cl * (1 - u) + cr * u
    fill = cv2.GaussianBlur(fill, (0, 0), sigmaX=3, sigmaY=10)
    # a touch of grain so the patch matches the photo
    fill += np.random.default_rng(1).normal(0, 2.0, fill.shape)
    fill = np.clip(fill, 0, 255)
    # soften the filled area so it reads as a smooth reflection, then feather-blend
    soft = cv2.GaussianBlur(cv2.dilate(mask, np.ones((15, 15), np.uint8)).astype(np.float32) / 255, (0, 0), 10)[..., None]
    out = (img * (1 - soft) + fill * soft).astype(np.uint8)
    # gentle overall softening of the mirror door so the retouch blends in
    x0, y0, x1, y1 = [int(v * k) for v in door]
    dm = np.zeros((h, w), np.float32); dm[y0:y1, x0:x1] = 1
    dm = cv2.GaussianBlur(dm, (0, 0), 30)[..., None] * 0.55
    out = (out * (1 - dm) + cv2.GaussianBlur(out, (0, 0), 6) * dm).astype(np.uint8)
    # crop + light grade (a little contrast and warmth, like a product shoot)
    cx0, cy0, cx1, cy1 = [int(v * k) for v in crop]
    out = out[cy0:cy1, cx0:cx1]
    out = cv2.convertScaleAbs(out, alpha=1.08, beta=4)
    out = cv2.resize(out, (1500, 1500), interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join(OUT, f"{name}.jpg"), out, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return out


if __name__ == "__main__":
    for n in PHOTOS:
        build(n)
        print("ok", n)
