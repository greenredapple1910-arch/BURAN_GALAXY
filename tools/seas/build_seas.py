"""Сборка таблицы морей и океанов для «Сейчас над» (index.html, константа SEAS).

Источник: Natural Earth 1:50m geography_marine_polys (общественное достояние),
названия — поле name_ru с правками ниже. Контуры упрощаются (Дуглас — Пекер),
координаты округляются до 0,1° и пишутся приращениями: [lon0, lat0, dlon1, dlat1, ...]
в десятых долях градуса. Порядок — от малых акваторий к большим: первая найденная
и есть ответ (Саргассово море раньше Атлантики).

Запуск:  python tools/seas/build_seas.py [путь_к_geojson] > seas.js
"""
import json, math, sys, urllib.request

SRC = ('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/'
       'geojson/ne_50m_geography_marine_polys.geojson')
TOL = 0.25          # допуск упрощения, градусы
Q = 10              # 0,1°

FIX = {  # name -> русское название (где name_ru неполное или неудачное)
    'Celebes Sea': 'Море Сулавеси', 'Bahía de Campeche': 'Залив Кампече',
    'James Bay': 'Залив Джеймс', 'Gulf of Carpentaria': 'Залив Карпентария',
    'Bay of Plenty': 'Залив Пленти', 'Gulf of Tonkin': 'Тонкинский залив',
    'Bay of Fundy': 'Залив Фанди', 'Río de la Plata': 'Залив Ла-Плата',
    'Melville Bay': 'Залив Мелвилл', 'Gulf of Maine': 'Залив Мэн',
    'Golfo San Jorge': 'Залив Сан-Хорхе', 'Viscount Melville Sound': 'Пролив Вайкаунт-Мелвилл',
    'Ungava Bay': 'Залив Унгава', 'Bismarck Sea': 'Море Бисмарка',
    'Inner Seas': 'Гебридское море', 'Bristol Bay': 'Бристольский залив (Аляска)',
    'Baffin Bay': 'Море Баффина', 'Gulf of Mannar': 'Манарский залив',
}
SKIP = {'river'}
# акватории, которых нет в Natural Earth 1:50m (контуры грубые: сушу внутри перекрывают страны)
EXTRA = {
    'Азовское море': [(34.8, 45.9), (35.2, 45.35), (36.5, 45.4), (37.0, 45.3), (38.0, 46.0), (38.6, 46.6),
                      (39.3, 47.2), (38.4, 47.1), (37.0, 46.9), (35.9, 46.6), (35.2, 46.2)],
    'Мраморное море': [(26.7, 40.4), (27.5, 40.3), (28.5, 40.35), (29.2, 40.4), (29.9, 40.7), (29.0, 41.05),
                       (28.0, 41.0), (27.4, 40.95), (26.9, 40.7)],
    'Восточно-Сибирское море': [(140.0, 72.5), (140.5, 76.8), (150.0, 77.5), (160.0, 77.2), (180.0, 74.0),
                                (180.0, 71.0), (178.0, 70.9), (176.0, 69.6), (170.0, 69.8), (160.0, 69.6),
                                (154.0, 70.8), (150.0, 71.5), (145.0, 72.3)],
}


def dp(pts, tol):
    """Дуглас — Пекер для открытой ломаной."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]; bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / L if L > 1e-12 else math.hypot(px - ax, py - ay)
            if d > best:
                best, bi = d, i
        if bi >= 0 and best > tol:
            keep[bi] = True
            stack.append((a, bi)); stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]


def ring_simplify(r):
    r = [(float(x), float(y)) for x, y in r]
    if r[0] == r[-1]:
        r = r[:-1]
    if len(r) < 3:
        return None
    # замкнутое кольцо делим на две половины, чтобы концы не «съедались»
    h = len(r) // 2
    a = dp(r[:h + 1], TOL); b = dp(r[h:] + [r[0]], TOL)
    out = a[:-1] + b[:-1]
    q = []
    for x, y in out:
        p = (round(x * Q), round(y * Q))
        if not q or q[-1] != p:
            q.append(p)
    return q if len(q) >= 3 else None


def area(q):
    s = 0.0
    for i in range(len(q)):
        x1, y1 = q[i]; x2, y2 = q[(i + 1) % len(q)]
        s += (x1 * y2 - x2 * y1)
    lat = sum(y for _, y in q) / len(q) / Q
    return abs(s) / 2 / Q / Q * math.cos(math.radians(lat))


def main():
    if len(sys.argv) > 1:
        g = json.load(open(sys.argv[1], encoding='utf-8'))
    else:
        g = json.load(urllib.request.urlopen(SRC))
    feats = []
    npts = 0
    for f in g['features']:
        p = f['properties']
        if p.get('featurecla') in SKIP:
            continue
        name = FIX.get(p['name']) or p.get('name_ru') or p['name']
        geo = f['geometry']
        polys = geo['coordinates'] if geo['type'] == 'MultiPolygon' else [geo['coordinates']]
        rings, A = [], 0.0
        for poly in polys:
            for k, r in enumerate(poly):
                q = ring_simplify(r)
                if not q:
                    continue
                a = area(q)
                if k == 0 and a < 0.02:   # крошечные острова акватории не нужны
                    continue
                A += a if k == 0 else -a
                flat = [q[0][0], q[0][1]]
                for i in range(1, len(q)):
                    flat += [q[i][0] - q[i - 1][0], q[i][1] - q[i - 1][1]]
                rings.append(flat)
                npts += len(q)
        if rings:
            feats.append((A, name, rings))
    for name, ring in EXTRA.items():
        q = [(round(x * Q), round(y * Q)) for x, y in ring]
        flat = [q[0][0], q[0][1]]
        for i in range(1, len(q)):
            flat += [q[i][0] - q[i - 1][0], q[i][1] - q[i - 1][1]]
        feats.append((area(q), name, [flat]))
        npts += len(q)
    feats.sort(key=lambda t: t[0])
    body = ',\n'.join(json.dumps([n, r], ensure_ascii=False, separators=(',', ':')) for _, n, r in feats)
    sys.stdout.reconfigure(encoding='utf-8')
    print('/* Моря и океаны: Natural Earth 1:50m marine polys (public domain), tools/seas/build_seas.py; '
          + str(len(feats)) + ' акваторий, ' + str(npts) + ' точек */')
    print('const SEAS=[\n' + body + '\n];')


if __name__ == '__main__':
    main()
