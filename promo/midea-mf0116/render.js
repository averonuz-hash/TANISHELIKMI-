// Render scene.html to frames and pipe them into ffmpeg.
// Usage:
//   node render.js                     -> out/video_silent.mp4 (30 fps, 1080x1920)
//   node render.js --stills 1,3,8      -> out/still_<t>.png for quick checks
//   node render.js --photo             -> use product.png instead of the drawn machine
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30;
const args = process.argv.slice(2);
const photo = args.includes('--photo');
const stillsArg = args.indexOf('--stills');
const outDir = path.join(__dirname, 'out');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  const url = 'file://' + path.join(__dirname, 'scene.html') + (photo ? '?photo=1' : '');
  await page.goto(url);
  await page.evaluate(() => window.ready);

  const grab = async t => {
    const b64 = await page.evaluate(t => { window.drawFrame(t); return document.getElementById('c').toDataURL('image/png').split(',')[1]; }, t);
    return Buffer.from(b64, 'base64');
  };

  if (stillsArg >= 0) {
    for (const t of args[stillsArg + 1].split(',').map(Number)) {
      fs.writeFileSync(path.join(outDir, `still_${t}.png`), await grab(t));
    }
    await browser.close();
    return;
  }

  const dur = await page.evaluate(() => window.DUR);
  const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p',
    path.join(outDir, 'video_silent.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });

  const n = Math.round(dur * FPS);
  for (let i = 0; i < n; i++) {
    const buf = await grab(i / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 60 === 0) process.stdout.write(`frame ${i}/${n}\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('done');
})();
