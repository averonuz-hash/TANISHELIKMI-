# AVERON — MIDEA MF0116 promo video (9:16, 20 s)

**Final video:** `AVERON_MIDEA_MF0116_promo_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, -14 LUFS, ready for Instagram Reels / TikTok / YouTube Shorts / Telegram).

## Storyboard

| Time | Scene | On-screen text (Uzbek) |
|---|---|---|
| 0–2 s | Logo slam on a blue disk, rings and sparkles, then a blue swipe | **AVERON** · YANGI TAKLIF! · maishiy texnika doʻkoni |
| 2–7 s | White automatic washing machine flies in, turning slowly on a clean white background, drum spinning with water and clothes | **MIDEA MF0116** · Avtomatik kir yuvish mashinasi |
| 7–10.5 s | Feature chips slide in | Zamonaviy dizayn · Avtomatik rejimlar · Oson boshqaruv |
| 10.5–14 s | Price counts up and slams in on the beat | NAQD PULGA · **3 199 000 soʻm** |
| 14–17 s | Installment price zooms in | 12 OYGA MUDDATLI TOʻLOV · **379 000 soʻm / oyiga** |
| 17–20 s | Call to action on a blue brand background with a pulsing phone button | HOZIROQ QOʻNGʻIROQ QILING! · **50-772-25-00** · both prices · AVERON |

Music: an original 120 BPM electro-pop track (A minor) synthesized by `music.py`, so it is royalty-free. Impacts land on the scene cuts at 2, 11, 14 and 17 s, with a riser into the call to action.

## Rebuild / edit

```bash
python3 music.py                 # -> out/music.wav
node render.js                   # -> out/video_silent.mp4  (needs Playwright + Chromium + ffmpeg)
ffmpeg -y -i out/video_silent.mp4 -i out/music.wav -c:v copy \
  -af "loudnorm=I=-14:TP=-1.0:LRA=9" -ar 48000 -c:a aac -b:a 192k -shortest \
  -movflags +faststart AVERON_MIDEA_MF0116_promo_9x16.mp4
```

- Change text, prices, colors, or timings in `scene.html` (the `S` scene table and the `BLUE/RED/YEL` constants).
- Open `scene.html` in a browser for a live looping preview.
- `node render.js --stills 4,12,19` saves single frames to `out/` for a quick check.
- **To use a real product photo:** save a cut-out PNG with a transparent background as `product.png` next to `scene.html`, then run `node render.js --photo`. The photo replaces the drawn machine.

## Prompts for AI video generators (Runway / Pika / Kling)

AI generators often misspell on-screen text and numbers. Generate the **product shot only**, without text, and add the prices in an editor (CapCut and similar), or use the video above.

**Product shot (English, recommended):**
> Vertical 9:16 commercial product shot. A sleek modern white front-loading automatic washing machine with a chrome round door and glass porthole, slowly rotating 360° on a turntable against a seamless pure white studio background. Soft bright high-key lighting, subtle reflection on a glossy white floor, gentle rim light, clothes tumbling with water visible through the door glass. Smooth slow camera push-in, premium minimalist advertising aesthetic, ultra sharp, 4K. No text, no logos.

**Negative prompt:** text, letters, watermark, logo, blurry, distorted door, extra doors, dark background, people, clutter.

**Oʻzbekcha (qisqa):**
> Vertikal 9:16 reklama videosi. Zamonaviy oq avtomatik kir yuvish mashinasi toza oq fonda sekin aylanmoqda, yorqin studiya yoritilishi, eshik oynasi orqali kiyimlar aylanayotgani koʻrinadi. Matnsiz, logotipsiz.

**Text overlays to add in the editor:** `MIDEA MF0116` → `3 199 000 soʻm` (naqd) → `379 000 soʻm / oyiga · 12 oy` → `HOZIROQ QOʻNGʻIROQ QILING! 50-772-25-00` → `AVERON`.
