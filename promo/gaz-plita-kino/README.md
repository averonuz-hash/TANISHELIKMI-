# AVERON — "Oyimga sovgʻa" (kino uslubidagi reklama, 4K 9:16, 43 s)

**Tayyor video:** `AVERON_OYIMGA_SOVGA_4K.mp4` (2160×3840, 30 fps, H.264 + AAC, -14 LUFS). Oʻzbekcha dublyaj va subtitrlar bor.

Kichkina qiz oyisiga sovgʻa tanlagani haqida qisqa kino. Hikoya qismida **haqiqiy video kadrlar** (Mixkit), plitalar qismida doʻkonda olingan **haqiqiy rasmlar** (retush qilingan, 3000×3000), **jonli yozilgan musiqa** va **haqiqiy ovoz effektlari** ishlatilgan.

## Syujet

| Vaqt | Kadr | Ovoz (qiz bola) |
|---|---|---|
| 0–5 s | Koʻk gaz alangasi ustida tovada omlet (gaz yoqilishi, jizillash ovozi) | "Har kuni ertalab uyimizda birinchi boʻlib oshxonada olov yonadi." |
| 5–9 s | Sousdagi kotletlar, ona va qizning qoʻllari xamir qoryapti | "Oyijonim bizga eng mazali taomlarni pishiradi." |
| 9–12 s | Qiz oʻylanib turibdi, keyin sovgʻa oʻralyapti | "Bu yil men ham unga eng yaxshi sovgʻani topdim..." |
| 12–13 s | AVERON TAQDIM ETADI · **OYIMGA SOVGʻA** (musiqa toʻliq kuch bilan kiradi) | — |
| 13–20 s | 4 ta plita, nomi va oltin rangli narxi bilan | "Oltin eshikli Lifetech... Zamonaviy kulrang... Nafis, och rangli... Yoki tejamkor Ferre!" |
| 20–29 s | 4 model narxlari bilan · **2.099.999 soʻmdan** · naqd yoki 12 oyga | "Narxi atigi 2.099.999 soʻmdan. Naqd yoki 12 oyga boʻlib toʻlang!" |
| 29–31.5 s | Ona va qiz kulib turibdi, keyin oltin eshikli plita: **"Oyijonim, bu sizga!"** | "Oyijonim... bu sizga!" |
| 31.5–43 s | AVERON, 4 narx, 3·6·9·12 oyga toʻlov, **50-772-25-00** · **77-200-85-04**, "Sifat va qulay narx" | "Hammasi AVERON doʻkonida. Qoʻngʻiroq qiling: 50-772-25-00." "AVERON — sifat va qulay narx!" |

## Manbalar va litsenziyalar

| Material | Manba | Litsenziya |
|---|---|---|
| Video: 42910 (tovada omlet, gaz alangasi), 3806 (sousdagi kotletlar), 101169 (xamir qorish), 101172 (qiz bola), 101672 (sovgʻa oʻrash), 101179 (ona va qiz) | mixkit.co | Mixkit Stock Video **Free** License: tijoriy loyiha va reklamada ruxsat etiladi, muallifni koʻrsatish shart emas |
| Musiqa: "A New Life" (543) | mixkit.co | Mixkit Stock Music Free License: internet va ijtimoiy tarmoq reklamalarida ruxsat etiladi (**TV, radio va DVD da emas**) |
| Ovoz effektlari: 1801 (gaz yoqilishi), 1797 (gaz gʻuvillashi), 133 (tovada qovurish) | mixkit.co | Mixkit Sound Effects Free License |
| Plita rasmlari | AVERON doʻkonida olingan rasmlar (`../gaz-plita/source`) | doʻkonniki |
| Ovoz | Microsoft Edge neyron TTS `uz-UZ-MadinaNeural` (toni +12 Hz) | — |

Mixkit "Restricted" litsenziyali kadrlar (faqat shaxsiy loyihalar uchun) ataylab ishlatilmagan. **Videoni TV yoki radioda koʻrsatish uchun musiqani almashtirish kerak.**

## Ovoz haqida

Dublyaj sunʼiy intellekt ovozi bilan qilingan. Uni imkon qadar tabiiy qilish uchun quyidagilar bajarilgan:
- ton faqat biroz koʻtarilgan;
- iliqlik qoʻshilgan, "s", "sh" tovushlari yumshatilgan, yuqori chastotalar silliqlangan;
- yengil kompressiya va kichik xona akustikasi berilgan;
- butun video ostida juda past xona shovqini bor.

Baribir 100% jonli inson ovozi emas. Eng tabiiy natija uchun qiz boladan `voiceover.json` dagi satrlarni oʻqib berishini soʻrab yozib oling, `vo_wav/01.wav ... 11.wav` fayllarini almashtiring va qayta yigʻing.

## Qayta yaratish

```bash
./fetch_assets.sh                # Mixkit videolarini yuklab olish (gitda yoʻq, juda katta)
pip install edge-tts opencv-python-headless
SSL_CERT_FILE=/path/to/ca.crt python3 tts.py     # (ixtiyoriy) ovozni qayta sintez qilish -> vo/*.mp3
# vo/*.mp3 -> vo_wav/*.wav (jimlikni kesish) va vo_wav/lengths.json: avvalgi versiyadagi buyruqlar
python3 ../gaz-plita/retouch.py --size 3000 --out photos   # 4K plita rasmlari
python3 prep_stock.py            # videolarni 9:16 ga kesish, sekinlashtirish, 2160x3840 kadrlar
python3 score.py                 # musiqa + effektlar + ovoz -> out/mix.wav
node render.js --workers 3       # -> out/video_silent.mp4 (4K)
ffmpeg -y -i out/video_silent.mp4 -i out/mix.wav -c:v libx264 -preset slow -b:v 15M -maxrate 20M -bufsize 30M \
  -pix_fmt yuv420p -profile:v high -level 5.2 -af "loudnorm=I=-14:TP=-1.0:LRA=11" -ar 48000 -c:a aac -b:a 256k \
  -shortest -movflags +faststart AVERON_OYIMGA_SOVGA_4K.mp4
```

- Ovoz satrlari va subtitrlar: `voiceover.json`. Satrlar vaqti, kadrlar va videolarning qaysi qismi olinishi: `timeline.json`.
- Narx va nomlar: `scene.html` dagi `PRODUCTS`.
- `node render.js --stills 2,14,30` buyrugʻi alohida 4K kadrlarni `out/` papkasiga saqlaydi.
