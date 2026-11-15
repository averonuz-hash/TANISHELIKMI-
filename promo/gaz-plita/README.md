# AVERON — Gaz plitalar reklama videosi (9:16, 24 s)

**Tayyor video:** `AVERON_GAZ_PLITALAR_promo_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, -14 LUFS). Instagram Reels, TikTok, YouTube Shorts va Telegram uchun tayyor.

Videoda doʻkonda olingan **haqiqiy rasmlar** ishlatilgan (`source/`). Oynali eshiklardagi suratga olgan odamning aksi `retouch.py` bilan olib tashlangan (`photos/`).

## Modellar va narxlar

Narxlar doʻkon talabi boʻyicha **x.x99.999** koʻrinishida (oylik toʻlov **xx9.999**). Yorliqdagi narx eng yaqin shunday qiymatga yaxlitlangan.

| Model | Rangi | Yorliqda | Videoda, naqd | 12 oyga, oyiga |
|---|---|---|---|---|
| Lifetech LT-110 | Qora korpus, oltin rang oynali eshik | 2 087 250 | **2.099.999 soʻm** | **249.999 soʻm** |
| Lifetech LT-305 | Toʻq kulrang, oynali eshik | 2 365 550 | **2.399.999 soʻm** | **289.999 soʻm** |
| Lifetech LT-265 | Och kulrang, oynali eshik | 2 380 500 | **2.399.999 soʻm** | **289.999 soʻm** |
| Ferre BT60-F31 | Toʻq jigarrang, shisha eshik | 2 472 500 | **2.499.999 soʻm** | **299.999 soʻm** |

Narxni oʻzgartirish uchun `scene.html` dagi `PRODUCTS` roʻyxatidagi `price` va `m12` qiymatlarini tahrirlang.

## Sahnalar

| Vaqt | Sahna |
|---|---|
| 0–1 s | Gaz konforkasi yonadi (uchqun chiqillashi va alanga "vush" ovozi): "Oshxonangiz uchun YANGI GAZ PLITA!" |
| 1–3 s | Ritmga mos 4 ta rasm almashadi: **AVERON** doʻkonida · **GAZ PLITALAR** · narxi **2.099.999 soʻmdan** · 3·6·9·12 oyga muddatli toʻlov |
| 3–19 s | Har bir model 4 soniyadan: haqiqiy rasm sekin yaqinlashadi, ustidan yorugʻlik oʻtadi, haqiqiy detal belgilanadi (Duxovka 40–275 °C / Energiya sinfi A), naqd narx sanab chiqib "ding" bilan tushadi, keyin 12 oylik toʻlov. Pastda telefonlar yozilgan yugurma qator |
| 19–24 s | 4 model narxlari bilan, muddatli toʻlov, **50-772-25-00** · **77-200-85-04**, "AVERON — sifat va qulay narx!" |

Musiqa: `music.py` dasturida yaratilgan original 120 BPM energik trek (C major) va ovoz effektlari. Mualliflik huquqi muammosi yoʻq.

## Qayta yaratish / tahrirlash

```bash
pip install opencv-python-headless
python3 retouch.py               # source/*.jpg -> photos/*.jpg (aksni olib tashlash, kesish)
python3 music.py                 # -> out/music.wav
node render.js                   # -> out/video_silent.mp4  (Playwright + Chromium + ffmpeg kerak)
ffmpeg -y -i out/video_silent.mp4 -i out/music.wav -c:v copy \
  -af "loudnorm=I=-14:TP=-1.0:LRA=9" -ar 48000 -c:a aac -b:a 192k -shortest \
  -movflags +faststart AVERON_GAZ_PLITALAR_promo_9x16.mp4
```

- Narx, model va matnlar `scene.html` dagi `PRODUCTS` roʻyxatida, telefonlar `PHONES` da.
- `node render.js --stills 5,21` buyrugʻi bitta kadrni `out/` papkasiga saqlaydi (tez tekshirish uchun).
- Yangi model qoʻshish: rasmni `source/` ga qoʻying, `retouch.py` dagi `PHOTOS` ga aks tushgan joy koordinatalari bilan qoʻshing va `PRODUCTS` ga yozing.
