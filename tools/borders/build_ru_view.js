// Сборка геометрии «границы по законодательству РФ» для BURAN GALAXY.
// Вход: базовая карта (johan/world.geo.json, Natural Earth 1:110M) и
// границы Крыма, Севастополя, Донецкой, Луганской, Запорожской и
// Херсонской областей (Natural Earth admin-1 1:10M). Выход: компактные
// MultiPolygon для RUS и UKR, совместимые с базовой картой.
const fs = require('fs');
const pc = require('polygon-clipping');
const [worldPath, oblPath, outPath] = process.argv.slice(2);

const world = JSON.parse(fs.readFileSync(worldPath, 'utf8'));
const obl = JSON.parse(fs.readFileSync(oblPath, 'utf8'));
const toMP = g => (g.type === 'Polygon' ? [g.coordinates] : g.coordinates);
const feat = id => world.features.find(f => f.id === id);

function rdp(pts, eps) {
  if (pts.length < 4) return pts.slice();
  const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length - 1] = 1;
  const stack = [[0, pts.length - 1]];
  while (stack.length) {
    const [a, b] = stack.pop();
    const [ax, ay] = pts[a], [bx, by] = pts[b];
    const dx = bx - ax, dy = by - ay, L = Math.hypot(dx, dy) || 1e-12;
    let md = -1, mi = -1;
    for (let i = a + 1; i < b; i++) {
      const d = Math.abs(dy * pts[i][0] - dx * pts[i][1] + bx * ay - by * ax) / L;
      if (d > md) { md = d; mi = i; }
    }
    if (md > eps) { keep[mi] = 1; stack.push([a, mi], [mi, b]); }
  }
  return pts.filter((_, i) => keep[i]);
}
function simplifyMP(mp, eps) {
  return mp.map(poly => poly.map(r => {
    const open = r.slice(0, -1); let s = rdp(open, eps);
    if (s.length < 3) s = open;
    return s.concat([s[0]]);
  })).filter(poly => poly[0].length >= 4);
}
const area = r => { let s = 0; for (let i = 0, j = r.length - 1; i < r.length; j = i++) s += r[j][0] * r[i][1] - r[i][0] * r[j][1]; return Math.abs(s / 2); };
const pts = mp => mp.reduce((n, p) => n + p.reduce((m, r) => m + r.length, 0), 0);
const round = mp => mp.map(p => p.map(r => r.map(([x, y]) => [Math.round(x * 1000) / 1000, Math.round(y * 1000) / 1000])));

let T = pc.union(...obl.features.map(f => toMP(f.geometry)));
console.log('regions union: polys', T.length, 'points', pts(T));
T = pc.union(simplifyMP(T, 0.03));
console.log('simplified: polys', T.length, 'points', pts(T));

const UKR = toMP(feat('UKR').geometry), RUS = toMP(feat('RUS').geometry);
// в границах областей 1:10M русло Днепра у Херсона вырезано как вода;
// административно оно входит в Херсонскую область — закрываем щель
const DNIPRO_DELTA = [[[[32.45, 46.45], [32.95, 46.45], [32.95, 46.72], [32.45, 46.72], [32.45, 46.45]]]];
T = pc.union(T, pc.intersection(DNIPRO_DELTA, UKR));
// у Украины остаётся основной массив; всё прочее из её прежнего полигона
// (перенесённые регионы и узкие обрезки на стыке масштабов) — к России
const diff = pc.difference(UKR, T).sort((a, b) => area(b[0]) - area(a[0]));
let newU = [diff[0]];
const P = pc.difference(UKR, newU);
const dropped = diff.slice(1).map(p => area(p[0]).toFixed(3));
let newR = pc.union(RUS, P);
console.log('transferred area (deg²):', P.reduce((s, p) => s + area(p[0]), 0).toFixed(2), 'pieces', P.length);
console.log('slivers moved to Russia:', dropped.join(', ') || 'none');
console.log('UKR polys', newU.length, 'points', pts(newU), '| RUS polys', newR.length, 'points', pts(newR));

const out = { RUS: { type: 'MultiPolygon', coordinates: round(newR) }, UKR: { type: 'MultiPolygon', coordinates: round(newU) } };
fs.writeFileSync(outPath, JSON.stringify(out));
console.log('written', outPath, fs.statSync(outPath).size, 'bytes');
