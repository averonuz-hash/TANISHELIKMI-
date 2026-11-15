// Render scene.html (2160x3840) to video.
// Usage:
//   node render.js                    -> out/video_silent.mp4, rendered by 3 parallel workers
//   node render.js --workers 4
//   node render.js --stills 2,14,30   -> out/still_<t>.jpg (full 4K) for quick checks
//   (internal) node render.js --from 0 --to 400 --out out/part0.mp4
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

const args = process.argv.slice(2);
const arg = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const outDir = path.join(__dirname, 'out');
fs.mkdirSync(outDir, { recursive: true });

function serve() {
  const types = { '.html': 'text/html', '.jpg': 'image/jpeg', '.png': 'image/png', '.js': 'text/javascript', '.json': 'application/json' };
  const server = http.createServer((req, res) => {
    const p = path.join(__dirname, decodeURIComponent(req.url.split('?')[0]));
    if (!p.startsWith(__dirname) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' });
    fs.createReadStream(p).pipe(res);
  }).listen(0, '127.0.0.1');
  return new Promise(r => server.once('listening', () => r(server)));
}

async function openPage() {
  const server = await serve();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 540, height: 960 } });
  page.on('pageerror', e => console.error('pageerror', e));
  await page.goto(`http://127.0.0.1:${server.address().port}/scene.html`);
  await page.evaluate(() => window.ready);
  const grab = async (t, type = 'image/jpeg') => {
    const b64 = await page.evaluate(async ([t, type]) => {
      await window.renderAt(t);
      return document.getElementById('c').toDataURL(type, 0.95).split(',')[1];
    }, [t, type]);
    return Buffer.from(b64, 'base64');
  };
  const info = await page.evaluate(() => ({ dur: window.DUR, fps: window.FPS }));
  return { grab, info, close: async () => { await browser.close(); server.close(); } };
}

function run(cmd, a) { return new Promise((res, rej) => { const p = spawn(cmd, a, { stdio: 'inherit' }); p.on('close', c => c ? rej(new Error(cmd + ' ' + c)) : res()); }); }

(async () => {
  if (args.includes('--stills')) {
    const { grab, close } = await openPage();
    for (const t of arg('--stills').split(',').map(Number)) fs.writeFileSync(path.join(outDir, `still_${t}.jpg`), await grab(t));
    await close();
    return;
  }

  if (args.includes('--from')) {            // worker: render a frame range to one segment
    const from = +arg('--from'), to = +arg('--to'), out = arg('--out');
    const { grab, info, close } = await openPage();
    const ff = spawn('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error',
      '-f', 'image2pipe', '-framerate', String(info.fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
      '-profile:v', 'high', '-level', '5.2', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = from; i < to; i++) {
      const buf = await grab(i / info.fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if ((i - from) % 60 === 0) console.log(`[${from}-${to}] frame ${i}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    await close();
    return;
  }

  // driver: split into ranges, render in parallel, concatenate
  const workers = +arg('--workers', 3);
  const probe = await openPage(); const { dur, fps } = probe.info; await probe.close();
  const n = Math.round(dur * fps), step = Math.ceil(n / workers);
  const parts = [];
  const jobs = [];
  for (let w = 0; w < workers; w++) {
    const from = w * step, to = Math.min(n, (w + 1) * step);
    if (from >= to) break;
    const out = path.join(outDir, `part${w}.mp4`);
    parts.push(out);
    jobs.push(run('node', [__filename, '--from', String(from), '--to', String(to), '--out', out]));
  }
  await Promise.all(jobs);
  const list = path.join(outDir, 'parts.txt');
  fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
  await run('ffmpeg', ['-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', path.join(outDir, 'video_silent.mp4')]);
  console.log('done');
})();
