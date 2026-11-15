# AVERON — Brando Smart TV 43″ reklama videosi (9:16, 20 s)

**Tayyor video:** `AVERON_BRANDO_TV43_promo_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, -14 LUFS). Instagram Reels, TikTok, YouTube Shorts va Telegram uchun tayyor.

## Sahnalar

| Vaqt | Sahna | Ekrandagi matn |
|---|---|---|
| 0–2.5 s | AVERON logotipi, keyin katta qizil yozuv | **AVERON** doʻkonida · **ULKAN CHEGIRMA!** |
| 2.5–7 s | Televizor uchib kirib, ekrani yonadi va sekin aylanadi; fonda doʻkon devoridagi televizorlar | **SMART TV BRANDO** · 43″ dyuym · Zamonaviy oila uchun **ENG YAXSHI TANLOV!** |
| 7–10 s | Devorda turli oʻlchamdagi televizorlar paydo boʻladi | Doʻkonimizda **BARCHA OʻLCHAMDAGI** televizorlar mavjud! |
| 10–13.5 s | Narx sanab chiqadi va ritmga zarb bilan tushadi | NAQD PULGA ATIGI · **2 155 999 soʻm** · ULKAN CHEGIRMA belgisi |
| 13.5–16.5 s | Muddatli toʻlov narxi kattalashib chiqadi | YOKI OYIGA · **279 999 soʻmdan** · 12 OYGA BOʻLIB TOʻLANG! |
| 16.5–20 s | Koʻk fonda qoʻngʻiroqqa chaqiruv | KELIB KOʻRING, NARXGA ISHONING! · **50-772-25-00** · **77-200-85-04** · AVERON — sifat va qulay narx! |

Musiqa: `music.py` dasturida yaratilgan original 120 BPM energik trek (D minor). Mualliflik huquqi muammosi yoʻq. Zarblar sahna almashinuvlariga (2.5, 10.5, 13.5, 16.5 s) toʻgʻri keladi.

## Qayta yaratish / tahrirlash

```bash
python3 music.py                 # -> out/music.wav
node render.js                   # -> out/video_silent.mp4  (Playwright + Chromium + ffmpeg kerak)
ffmpeg -y -i out/video_silent.mp4 -i out/music.wav -c:v copy \
  -af "loudnorm=I=-14:TP=-1.0:LRA=9" -ar 48000 -c:a aac -b:a 192k -shortest \
  -movflags +faststart AVERON_BRANDO_TV43_promo_9x16.mp4
```

- Matn, narx, telefon raqamlari (`PHONES`) va vaqtlar (`S` jadvali) `scene.html` faylida.
- `scene.html` ni brauzerda ochsangiz, video jonli koʻrinishda aylanib turadi.
- **Haqiqiy televizor rasmi:** shaffof fonli PNG ni `product.png` nomi bilan `scene.html` yoniga qoʻying va `node render.js --photo` ni ishga tushiring. Keyin yuqoridagi ffmpeg buyrugʻi bilan musiqani qayta qoʻshing.

## AI video generatorlar uchun prompt (Runway / Kling)

AI generatorlar narx va oʻzbekcha harflarni (oʻ, gʻ) koʻpincha xato yozadi. Shuning uchun ular bilan faqat **matnsiz** fon videosini yarating, narxlarni esa CapCut kabi muharrirda qoʻshing (yoki yuqoridagi tayyor videodan foydalaning).

**Prompt (inglizcha, tavsiya etiladi):**
> Vertical 9:16 retail advertisement shot. Bright modern electronics store interior, a wall of many flat-screen TVs in different sizes all showing vivid colorful sunset landscapes. The camera slowly pushes in toward one slim black 43-inch smart TV on a stand in the center, its screen glowing with a vibrant mountain-lake sunset. Clean white and blue store design, glossy floor reflections, bright commercial lighting, energetic mood, shallow depth of field, ultra sharp, 4K. No text, no logos, no people.

**Negative prompt:** text, letters, numbers, watermark, logo, brand names, distorted screens, curved TV, dark store, people, clutter, blur.

**Oʻzbekcha (qisqa):**
> Vertikal 9:16 reklama videosi. Yorqin zamonaviy elektronika doʻkoni, devorda turli oʻlchamdagi koʻplab televizorlar rang-barang manzaralarni koʻrsatmoqda. Kamera markazdagi 43 dyuymli qora Smart TV ga sekin yaqinlashadi. Matnsiz, logotipsiz.

**Muharrirda qoʻshiladigan matnlar:** `ULKAN CHEGIRMA!` → `SMART TV BRANDO 43″` → `Naqd pulga atigi 2 155 999 soʻm` → `Yoki oyiga 279 999 soʻmdan — 12 oyga boʻlib toʻlang!` → `Kelib koʻring, narxga ishoning!` → `50-772-25-00 · 77-200-85-04` → `AVERON — sifat va qulay narx!`
