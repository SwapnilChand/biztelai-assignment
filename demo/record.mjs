// Records the app in a headless Chromium over CDP (Page.startScreencast).
// usage: node record.mjs <cdp port> <outdir> <width> <height> <mobile 0|1> <url> <script.json>
// script.json: [["ask", "question"], ["chip", "label"], ["open", n], ["scroll", y], ["wait", ms], ["mark", "caption"]]
import fs from 'fs';
const [,, port, out, W, H, mobile, url, scriptFile] = process.argv;
const steps = JSON.parse(fs.readFileSync(scriptFile, 'utf8'));
const B = `http://127.0.0.1:${port}`;
const t = await (await fetch(B + '/json/new?about:blank', { method: 'PUT' })).json();
const ws = new WebSocket(t.webSocketDebuggerUrl); let id = 0; const pend = {}; const events = [];
fs.mkdirSync(out, { recursive: true });
let n = 0; const frames = []; const marks = []; const t0 = Date.now();
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pend[d.id]) { pend[d.id](d); delete pend[d.id]; return; }
  if (d.method === 'Page.screencastFrame') {
    const f = `${out}/f${String(n++).padStart(5, '0')}.jpg`;
    fs.writeFileSync(f, Buffer.from(d.params.data, 'base64'));
    frames.push([f, d.params.metadata.timestamp]);
    send('Page.screencastFrameAck', { sessionId: d.params.sessionId });
  } else events.push(d.method);
};
await new Promise((r) => (ws.onopen = r));
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pend[i] = r; ws.send(JSON.stringify({ id: i, method, params })); });
const sl = (ms) => new Promise((r) => setTimeout(r, ms));
const ev = async (expr) => (await send('Runtime.evaluate', { expression: `(async()=>{${expr}})()`, awaitPromise: true, returnByValue: true, userGesture: true })).result?.result?.value;
await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: +W, height: +H, deviceScaleFactor: mobile === '1' ? 2 : 1, mobile: mobile === '1' });
if (mobile === '1') await send('Emulation.setTouchEmulationEnabled', { enabled: true });
await send('Page.navigate', { url });
for (let i = 0; i < 60 && !events.includes('Page.loadEventFired'); i++) await sl(200);
if (process.env.ZOOM) await ev(`document.documentElement.style.zoom='${process.env.ZOOM}'`);
await send('Page.startScreencast', { format: 'jpeg', quality: 85, everyNthFrame: 1 });
await sl(300);
const clickAt = async (sel, idx = 0) => {
  const r = await ev(`const e=document.querySelectorAll(${JSON.stringify(sel)})[${idx}]; e.scrollIntoView({block:'center'}); await new Promise(r=>setTimeout(r,400)); const b=e.getBoundingClientRect(); return [b.x+Math.min(b.width/2,60), b.y+b.height/2];`);
  for (const type of ['mousePressed', 'mouseReleased']) await send('Input.dispatchMouseEvent', { type, x: r[0], y: r[1], button: 'left', clickCount: 1 });
};
for (const [cmd, arg] of steps) {
  if (cmd === 'mark') marks.push([(Date.now() - t0) / 1000, arg]);
  if (cmd === 'wait') await sl(arg);
  if (cmd === 'ask') {
    await clickAt('#q');
    for (const ch of arg) { await send('Input.insertText', { text: ch }); await sl(28); }
    await sl(500);
    await clickAt('#send');
    for (let i = 0; i < 300; i++) { await sl(200); if (await ev(`return !document.querySelector('.thinking')`)) break; }
    await sl(400);
    await ev(`document.querySelector('.qa').scrollIntoView({behavior:'smooth',block:'start'})`);
  }
  if (cmd === 'chip') {
    const i = await ev(`return [...document.querySelectorAll('.chip')].findIndex(c=>c.textContent===${JSON.stringify(arg)})`);
    await clickAt('.chip', i);
    for (let k = 0; k < 300; k++) { await sl(200); if (await ev(`return !document.querySelector('.thinking') && !!document.querySelector('.qa')`)) break; }
    await sl(400);
    await ev(`document.querySelector('.qa').scrollIntoView({behavior:'smooth',block:'start'})`);
  }
  if (cmd === 'open') { await clickAt('.qa summary', arg); await sl(300); }
  if (cmd === 'scroll') await ev(`window.scrollBy({top:${arg},behavior:'smooth'})`);
}
await sl(500);
const tEnd = Date.now() / 1000;
await send('Page.stopScreencast');
// ffconcat with real frame durations so the video keeps real time
let list = 'ffconcat version 1.0\n';
for (let i = 0; i < frames.length; i++) {
  const dur = i + 1 < frames.length ? frames[i + 1][1] - frames[i][1] : Math.max(0.5, tEnd - frames[i][1]);
  list += `file '${frames[i][0]}'\nduration ${dur.toFixed(3)}\n`;
}
list += `file '${frames.at(-1)[0]}'\n`;
fs.writeFileSync(`${out}/list.txt`, list);
fs.writeFileSync(`${out}/marks.json`, JSON.stringify({ start: frames[0][1], marks: marks.map(([s, c]) => [s - (frames[0][1] - t0 / 1000), c]) }));
await send('Target.closeTarget', { targetId: t.id }).catch(() => {});
console.log(frames.length, 'frames', ((frames.at(-1)[1] - frames[0][1])).toFixed(1), 's');
process.exit(0);
