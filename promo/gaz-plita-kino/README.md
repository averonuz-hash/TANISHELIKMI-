# AVERON — "Oyimga sovgʻa" (kino uslubidagi reklama, 9:16, 43 s)

**Tayyor video:** `AVERON_OYIMGA_SOVGA_kino_9x16.mp4` (1080×1920, 30 fps, H.264 + AAC, -14 LUFS). Ovozli (oʻzbekcha dublyaj) va subtitrli.

Kichkina qiz oyisiga sovgʻa tanlagani haqida qisqa kino. Doʻkonda olingan haqiqiy rasmlar (`photos/`, `../gaz-plita` dan retush qilingan) ishlatilgan.

## Syujet

| Vaqt | Kadr | Ovoz (qiz bola) |
|---|---|---|
| 0–5 s | Qorongʻida gaz konforkasi yonadi, koʻk anamorfik blik, bugʻ | "Har kuni ertalab uyimizda birinchi boʻlib oshxonada olov yonadi." |
| 5–9 s | Makro: plita ruchkalari, fokus siljiydi, iliq yorugʻlik | "Oyijonim bizga eng mazali taomlarni pishiradi." |
| 9–12 s | Qorongʻida oltin eshik, ustidan yorugʻlik oʻtadi | "Bu yil men ham unga eng yaxshi sovgʻani topdim..." |
| 12–13 s | Sarlavha: AVERON TAQDIM ETADI · **OYIMGA SOVGʻA** ("braam" zarbasi) | — |
| 13–20 s | 4 ta plita, har biri nomi va oltin rangli narxi bilan | "Oltin eshikli Lifetech... Zamonaviy kulrang... Nafis, och rangli... Yoki tejamkor Ferre!" |
| 20–29 s | 4 model narxlari bilan · **2.099.999 soʻmdan** · naqd yoki 12 oyga | "Narxi atigi 2.099.999 soʻmdan. Naqd yoki 12 oyga boʻlib toʻlang!" |
| 29–31.5 s | Oltin eshikli plita, iliq nur, oltin zarrachalar: **"Oyijonim, bu sizga!"** | "Oyijonim... bu sizga!" |
| 31.5–43 s | Yakuniy kadr: AVERON, 4 ta narx, 3·6·9·12 oyga toʻlov, **50-772-25-00** · **77-200-85-04**, "Sifat va qulay narx" | "Hammasi AVERON doʻkonida. Qoʻngʻiroq qiling: 50-772-25-00." "AVERON — sifat va qulay narx!" |

Narxlar: Lifetech LT-110 2.099.999 · LT-305 2.399.999 · LT-265 2.399.999 · Ferre BT60-F31 2.499.999 soʻm (12 oyga: 249.999 / 289.999 / 289.999 / 299.999).

## Ovoz haqida

Dublyaj **sunʼiy intellekt ovozi** bilan qilingan: Microsoft Edge neyron TTS, `uz-UZ-MadinaNeural`. Qiz bola ovoziga oʻxshashi uchun toni koʻtarilgan (+18 Hz) va biroz sekinlashtirilgan. Bu jonli inson yozuvi emas.
Haqiqiy qiz bola ovozini yozib olsangiz, har bir satrni `vo_wav/01.wav ... 11.wav` nomi bilan almashtiring (matnlar `voiceover.json` da), soʻng `score.py` va ffmpeg buyrugʻini qayta ishga tushiring.

## Qayta yaratish

```bash
pip install edge-tts
SSL_CERT_FILE=/path/to/ca.crt python3 tts.py          # voiceover.json -> vo/*.mp3 (proksi boʻlmasa SSL_CERT_FILE shart emas)
# jimlikni kesish (har bir satr uchun):
for f in vo/*.mp3; do b=$(basename $f .mp3); ffmpeg -y -i $f -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse" -ar 48000 -ac 1 vo_wav/$b.wav; done
# vo_wav/lengths.json ni yangilash (har bir satr davomiyligi, soniyada) — README pastidagi python qatoriga qarang
python3 score.py                 # musiqa + ovoz -> out/mix.wav
node render.js                   # -> out/video_silent.mp4
ffmpeg -y -i out/video_silent.mp4 -i out/mix.wav -c:v copy -af "loudnorm=I=-14:TP=-1.0:LRA=11" \
  -ar 48000 -c:a aac -b:a 192k -shortest -movflags +faststart AVERON_OYIMGA_SOVGA_kino_9x16.mp4
```

`lengths.json` ni yangilash:

```bash
python3 -c "import json,subprocess,glob,os; json.dump({os.path.basename(f)[:-4]: float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout) for f in sorted(glob.glob('vo_wav/*.wav'))}, open('vo_wav/lengths.json','w'), indent=1)"
```

- Ovoz satrlari va subtitrlar: `voiceover.json`. Satrlarning boshlanish vaqtlari va kadrlar: `timeline.json`.
- Narx va nomlar: `scene.html` dagi `PRODUCTS`.
