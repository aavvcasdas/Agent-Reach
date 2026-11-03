// Day10: repair-shop pilot. Silent storyboard by default; voiced output requires measured cues.
// Reuses Day8 room/props, Day9 finite-action rig and Day2 subtitles. No new character assets.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { createHash } from 'node:crypto';
import { createCanvas, loadImage, bg, panel6, text6, day3RiceBowl, resolveFfmpeg } from '../day8制作/render_day8.mjs';
import { loadMotionAssets, drawAction, travel, cacheStats } from '../day9制作/motion_v2.mjs';
import { createDay2Subtitle } from '../字幕/day2_style_sub.mjs';
import { repairBoard, commissionPaper, sendKeySeal, repairTv } from './repair_props.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const arg = (s) => argv.includes(s) ? argv[argv.indexOf(s) + 1] : null;
const voice = arg('--voice'), alignment = arg('--alignment'), subtitleFile = arg('--subtitle-file');
const measured = alignment ? JSON.parse(fs.readFileSync(alignment, 'utf8')) : null;
if (voice) {
  if (measured?.measured !== true || !subtitleFile) throw Error('有声版必须提供实测cue与字幕');
  if (createHash('sha256').update(fs.readFileSync(voice)).digest('hex') !== measured.source_sha256) throw Error('音源SHA256与实测时间轴不一致');
}
const lines = fs.readFileSync(path.join(ROOT, 'Day10/Day10配音台词.txt'), 'utf8').trim().split(/\n+/);
let clock = 0;
const cues = measured ? measured.cues.map((c, i) => { if (c.text !== lines[i]) throw Error('时间轴文本不匹配'); return { ...c, line: i + 1 }; })
  : lines.map((text, i) => { const duration = Math.max(.8, [...text.replace(/[^\p{L}\p{N}]/gu, '')].length / 4.3); const c = { line: i + 1, text, start: +clock.toFixed(3), end: +(clock + duration).toFixed(3) }; clock += duration + .18; return c; });
const duration = cues.at(-1).end + .2, FPS = 30, S = 1.5, W = 1280, H = 720;
const clamp = x => Math.min(1, Math.max(0, x));
const mix = (a, b, p) => a + (b - a) * p;
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const spans = [
  [1, 1, '开场翻车', '电视里科考站变成食堂，本鲸震惊'],
  [2, 5, '钻到电视后', '本鲸指向电视，笨鱼在电视后探头'],
  [6, 11, '食堂细节', '卫星锅下的饭碗与草莓拌饭标签'],
  [12, 17, '抵债纸条', '笨鱼递纸，本鲸读纸条'],
  [18, 23, '第一次修好', '挪开饭盆，摆正卫星锅，换回标本标签'],
  [24, 30, '别刷碗', '别刷屏写成别刷碗，本鲸纠正后擦掉'],
  [31, 34, '只修不发', '发送键封印，修坏墙出现'],
  [35, 40, '开单规则', '委托单出现，本鲸收尾并记一口饭'],
  [41, 41, '嘴硬收尾', '本鲸叉腰，绝不摸鱼'],
].map(([from, to, title, action], i) => ({ id: `C${String(i + 1).padStart(2, '0')}`, from, to, title, action, start: cues[from - 1].start, end: cues[to - 1].end }));
const subs = measured ? JSON.parse(fs.readFileSync(subtitleFile, 'utf8')).screens
  : cues.flatMap(c => { const parts = c.text.match(/[^，。！？；：]+[，。！？；：]?/g) || [c.text]; let n = 0; const total = parts.join('').length; return parts.map(text => { const st = c.start + (c.end - c.start) * n / total; n += text.length; return { line: c.line, text, start: st, end: c.start + (c.end - c.start) * n / total }; }); });
if (!measured) fs.writeFileSync(path.join(HERE, 'sample_timing.json'), JSON.stringify({ measured: false, purpose: 'silent_storyboard_only', source: 'Day10/Day10配音台词.txt', rate_estimate: 4.3, duration, cues, subtitles: subs, shots: spans }, null, 2));
const sub = createDay2Subtitle({ fontOf: (s, w) => `${w} ${s}px NotoSansSC`, measureCtx: createCanvas(1, 1).getContext('2d') });
function box(g, x, y, w, h, fill = '#17364D', stroke = '#7AA9BA', r = 10) { panel6(g, x, y, w, h, fill, stroke, r); }
function txt(g, s, x, y, size = 23, color = '#E8F4F2') { text6(g, s, x, y, size, color); }
function tag(g, s, x, y, w = 160) { box(g, x - w / 2, y - 26, w, 40, '#E9F2E7', '#7DA9AC', 12); txt(g, s, x, y + 2, 20, '#294A56'); }
function act(g, action, x, y, u, t, start, len, extra = {}) { return drawAction(g, { action, x, y, u, time: t, start, duration: Math.max(.3, len), ...extra }); }
function shotAt(t) { return spans.find(s => t >= s.start && t < s.end) || spans.at(-1); }
function frame(g, t) {
  g.setTransform(S, 0, 0, S, 0, 0); g.clearRect(0, 0, W, H);
  const sh = shotAt(t), n = cues.find(c => t >= c.start && t < c.end)?.line || cues.at(-1).line;
  const lt = t - sh.start, len = sh.end - sh.start, p = clamp(lt / Math.max(.01, len));
  bg(g, 0);
  // Fixed set: repair wall on the left, television on the right, commission desk in front.
  const wallItems = n >= 33 ? ['食堂摘要', '别刷碗'] : [];
  repairBoard(g, 36, 150, 210, 230, wallItems, t);
  const tvMode = n <= 17 ? 'canteen' : n <= 24 ? 'work' : n <= 26 ? 'spam' : 'fixed';
  repairTv(g, 560, 110, 640, 360, tvMode, t);
  box(g, 250, 520, 620, 26, '#796047', '#B6A07C', 6);
  if (n >= 31) sendKeySeal(g, 430, 500, 1, t);
  if (n >= 35) commissionPaper(g, 650, 480, 150, 110, '委托单', ['坏掉的话', '只修不发'], -0.05);
  if (n >= 39) day3RiceBowl(g, 760, 505, 1.1, 0.6, t);
  // Actors: 本鲸 supervises; 笨鱼 works near the TV. Labels keep the two whales readable.
  if (sh.id === 'C01') {
    act(g, 'shock', 320, 580, 34, t, sh.start, len);
    act(g, 'idle', 900, 580, 20, 0, 0, 10, { label: '笨鱼' });
    tag(g, '开饭了？', 330, 190, 170);
  } else if (sh.id === 'C02') {
    act(g, 'point', 300, 580, 33, t, sh.start, len);
    act(g, 'look', 900, 580, 20, t, sh.start, len, { label: '笨鱼' });
  } else if (sh.id === 'C03') {
    act(g, 'protest', 320, 580, 33, t, sh.start, len);
    act(g, 'eat', 900, 580, 20, t, sh.start, len, { label: '笨鱼' });
    if (n >= 8) tag(g, '这是锅！', 330, 190, 160);
  } else if (sh.id === 'C04') {
    act(g, 'read', 300, 580, 33, t, sh.start, len, { paper: true });
    act(g, 'point', 880, 580, 20, t, sh.start, len, { label: '笨鱼' });
    commissionPaper(g, 430, 470, 150, 110, '总结', ['吃了口粮', '要干活抵债'], 0.04);
  } else if (sh.id === 'C05') {
    act(g, 'look', 320, 580, 33, t, sh.start, len);
    act(g, 'type', 880, 580, 20, t, sh.start, len, { label: '笨鱼' });
    if (n >= 22) tag(g, '修好一半', 330, 190, 170);
  } else if (sh.id === 'C06') {
    act(g, n >= 27 ? 'stop' : 'protest', 320, 580, 33, t, n >= 27 ? cues[26].start : sh.start, n >= 27 ? cues[27].end - cues[26].start : cues[26].end - sh.start);
    act(g, 'read', 880, 580, 20, t, sh.start, len, { label: '笨鱼' });
    if (n === 27) tag(g, '是屏！', 330, 190, 140);
  } else if (sh.id === 'C07') {
    act(g, 'point', 320, 580, 33, t, sh.start, len);
    act(g, 'idle', 880, 580, 20, 0, 0, 10, { label: '笨鱼' });
    if (n >= 32) tag(g, '只修不发', 430, 430, 170);
  } else if (sh.id === 'C08') {
    act(g, 'read', 320, 580, 33, t, sh.start, len, { paper: true });
    act(g, 'look', 880, 580, 20, t, sh.start, len, { label: '笨鱼' });
    if (n >= 39) tag(g, '记一口饭', 760, 430, 170);
  } else {
    act(g, 'proud', 360, 580, 34, t, sh.start, len);
    act(g, 'idle', 880, 580, 20, 0, 0, 10, { label: '笨鱼' });
    tag(g, '本鲸在监工！', 360, 190, 190);
  }
  txt(g, '非官方同人 · AI生成 · 剧情演绎', 1058, 34, 15, '#B6CFD2');
  const hit = subs.find(s => t >= s.start && t < s.end);
  if (hit) sub.draw(g, { lines: sub.wrap(hit.text), speaker: '本鲸', vis: 1, W, H });
}

await loadMotionAssets({ createCanvas, loadImage });
const out = path.resolve(arg('--out') || path.join(ROOT, 'Day10/成片/Day10_售后部开张_无声分镜.mp4'));
const canvas = createCanvas(W * S, H * S), g = canvas.getContext('2d');
const totalFrames = Math.ceil(duration * FPS);
if (argv.includes('--test')) {
  const covered = new Set();
  for (const sh of spans) for (let i = sh.from; i <= sh.to; i++) covered.add(i);
  if (covered.size !== lines.length) throw Error('分镜未覆盖全部台词');
  for (const sh of spans) { frame(g, mix(sh.start, sh.end, .5)); }
  console.log({ shots: spans.length, lines: lines.length, duration, frames: totalFrames, cache: cacheStats() });
} else if (argv.includes('--stills')) {
  const dir = path.join(HERE, '抽帧'); fs.mkdirSync(dir, { recursive: true });
  for (const sh of spans) for (const [i, p] of [.08, .35, .65, .95].entries()) {
    frame(g, mix(sh.start, sh.end, p));
    fs.writeFileSync(path.join(dir, `${sh.id}_${i}.jpg`), canvas.toBuffer('image/jpeg'));
  }
  console.log('stills', spans.length * 4, dir);
} else {
  if (!voice || !measured) throw Error('整片需要 --voice / --alignment / --subtitle-file；无声分镜请用 --stills 或 --test');
  fs.mkdirSync(path.dirname(out), { recursive: true });
  const ff = spawn(resolveFfmpeg(), ['-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', `${W * S}x${H * S}`, '-r', String(FPS), '-i', '-',
    '-i', path.resolve(voice), '-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', '-t', String(totalFrames / FPS),
    '-c:v', 'libx264', '-preset', 'veryfast', '-tune', 'animation', '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: ['pipe', 'ignore', 'pipe'] });
  let err = ''; ff.stderr.on('data', d => err += d); ff.stdin.on('error', () => {});
  const done = new Promise((resolve, reject) => { ff.on('error', reject); ff.on('close', c => c === 0 ? resolve() : reject(Error(err.slice(-2000)))); });
  for (let f = 0; f < totalFrames; f++) {
    frame(g, f / FPS); const raw = canvas.data();
    if (!ff.stdin.write(Buffer.from(raw.buffer, raw.byteOffset, raw.byteLength))) await Promise.race([new Promise(r => ff.stdin.once('drain', r)), done]);
    if (f % 180 === 0) console.log(`${f}/${totalFrames}`);
  }
  ff.stdin.end(); await done; console.log('DONE', out, fs.statSync(out).size, cacheStats());
}
