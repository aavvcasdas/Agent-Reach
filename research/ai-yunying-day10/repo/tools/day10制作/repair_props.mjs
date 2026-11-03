// Day10+ shared props for the "repair shop" arc.
// Reuses Day8 drawing primitives so the room, bowls and subtitle style stay identical.
import { panel6, text6, day3RiceBowl } from '../day8制作/render_day8.mjs';

function box(g, x, y, w, h, fill = '#17364D', stroke = '#7AA9BA', r = 10) {
  panel6(g, x, y, w, h, fill, stroke, r);
}
function txt(g, s, x, y, size = 22, color = '#E8F4F2') {
  text6(g, s, x, y, size, color);
}
function line(g, x, y, xx, yy, color = '#A8C3D2', width = 3) {
  g.beginPath(); g.moveTo(x, y); g.lineTo(xx, yy);
  g.strokeStyle = color; g.lineWidth = width; g.lineCap = 'round'; g.stroke();
}

/** A wall board that collects failed repairs. No numbers, no metrics. */
export function repairBoard(g, x, y, w, h, items = [], t = 0) {
  box(g, x, y, w, h, '#24384A', '#7FA0AB', 12);
  txt(g, '修坏墙', x + w / 2, y + 26, 22, '#E7D9B8');
  line(g, x + 14, y + 40, x + w - 14, y + 40, '#5E7A86', 2);
  const shown = items.slice(0, 3);
  shown.forEach((s, i) => {
    const yy = y + 62 + i * 46;
    const rot = (i % 2 ? -1 : 1) * 0.03;
    g.save(); g.translate(x + w / 2, yy + 14); g.rotate(rot);
    box(g, -w * 0.38, -16, w * 0.76, 34, '#EFE8D6', '#B7AE93', 4);
    txt(g, s, 0, 7, 17, '#4A5A63');
    g.restore();
  });
  if (!shown.length) txt(g, '还空着', x + w / 2, y + h / 2 + 10, 18, '#9FB6BE');
}

/** A single commission slip. Text only; never renders account data. */
export function commissionPaper(g, x, y, w, h, title, lines = [], rot = 0) {
  g.save(); g.translate(x, y); g.rotate(rot);
  box(g, -w / 2, -h / 2, w, h, '#F2E8D2', '#AAB9C2', 5);
  txt(g, title, 0, -h / 2 + 24, 19, '#3C5566');
  line(g, -w * 0.34, -h / 2 + 36, w * 0.34, -h / 2 + 36, '#9FB0B5', 2);
  lines.slice(0, 4).forEach((s, i) => txt(g, s, 0, -h / 2 + 60 + i * 24, 17, '#4A606B'));
  g.restore();
}

/** The send key stays visibly sealed: the arc's permission boundary as a prop. */
export function sendKeySeal(g, x, y, s = 1, t = 0) {
  g.save(); g.translate(x, y); g.scale(s, s);
  box(g, -70, -26, 140, 52, '#2B3B4E', '#8FA9B5', 10);
  txt(g, '发送键', 0, 6, 20, '#CFE2E8');
  g.rotate(-0.12);
  box(g, -78, -12, 156, 24, '#C9A24B', '#F2D28C', 4);
  txt(g, '只修不发', 0, 5, 16, '#3B2F14');
  g.restore();
}

/** Simplified TV summary used for before/after gags. Not a copy of any third-party video. */
export function repairTv(g, x, y, w, h, mode = 'canteen', t = 0) {
  g.save();
  g.shadowColor = '#07121FCC'; g.shadowBlur = 12;
  box(g, x - 12, y - 12, w + 24, h + 34, '#1D2934', '#91ABB3', 14);
  g.restore();
  g.save();
  g.beginPath(); g.roundRect(x, y, w, h, 8); g.clip();
  g.translate(x, y); g.scale(w / 640, h / 360);
  const sky = g.createLinearGradient(0, 0, 0, 360);
  sky.addColorStop(0, '#457C9D'); sky.addColorStop(1, '#B9DAE0');
  g.fillStyle = sky; g.fillRect(0, 0, 640, 360);
  for (let i = 0; i < 4; i++) {
    g.beginPath(); g.moveTo(i * 200 - 60, 220);
    g.lineTo(i * 200 + 70, 60 + (i % 2) * 30); g.lineTo(i * 200 + 220, 230);
    g.closePath(); g.fillStyle = i % 2 ? '#B6D4DB' : '#E4F1ED'; g.fill();
  }
  g.fillStyle = '#DDECEB'; g.fillRect(0, 224, 640, 136);
  box(g, 250, 70, 150, 44, '#D9DCCB', '#8CABA4', 5);
  txt(g, mode === 'canteen' ? '南极食堂' : '南极科考站', 325, 98, 18, '#36505A');
  // satellite dish
  g.save(); g.translate(430, 210);
  line(g, 0, 15, -18, 76, '#7E9EA9', 8);
  g.save(); g.rotate(-0.23);
  g.beginPath(); g.ellipse(0, 0, 70, 30, 0, 0, Math.PI); g.closePath();
  g.fillStyle = '#AACDD7'; g.fill(); g.strokeStyle = '#426A81'; g.lineWidth = 4; g.stroke();
  g.restore(); g.restore();
  if (mode === 'canteen') {
    day3RiceBowl(g, 430, 300, 1.2, 0.8, t);
    box(g, 120, 250, 120, 60, '#EFE8D6', '#B7AE93', 5);
    txt(g, '草莓拌饭', 180, 285, 18, '#7A4A55');
  } else if (mode === 'spam') {
    box(g, 150, 150, 340, 90, '#E9F2E7', '#7DA9AC', 10);
    txt(g, '别刷碗', 320, 205, 34, '#315564');
  } else if (mode === 'fixed') {
    box(g, 150, 150, 340, 90, '#E9F2E7', '#7DA9AC', 10);
    txt(g, '别刷屏', 320, 205, 34, '#AD5264');
    box(g, 120, 250, 120, 60, '#DCE9E4', '#9DB8B2', 5);
    txt(g, '冰心标本', 180, 285, 18, '#3E5E69');
  } else {
    box(g, 120, 250, 120, 60, '#DCE9E4', '#9DB8B2', 5);
    txt(g, '冰心标本', 180, 285, 18, '#3E5E69');
  }
  g.restore();
  box(g, x, y, w, 26, '#123347', '#426779', 0);
  txt(g, '观影摘要 · 场景示意（非原片）', x + w / 2, y + 18, 15, '#E1ECE6');
  line(g, x + w * 0.44, y + h + 14, x + w * 0.56, y + h + 14, '#627F88', 4);
}
