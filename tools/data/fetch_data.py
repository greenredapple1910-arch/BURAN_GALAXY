#!/usr/bin/env python3
"""Снимок данных для BURAN GALAXY: TLE CelesTrak, компактный каталог SATCAT
и ближайшие запуски (Launch Library 2, The Space Devs).

Запускается GitHub Action (.github/workflows/data.yml) каждые 3 часа и публикует файлы
в ветку data. Карта берёт данные оттуда, поэтому посетители не нагружают CelesTrak:
сервер отдаёт каждую группу одному адресу не чаще раза за обновление (≈2 ч) и блокирует
адреса с большим числом ошибок. Launch Library 2 без ключа пускает ~15 запросов в час
на адрес — снимок делает два запроса раз в 3 часа.

    python3 tools/data/fetch_data.py out

Если какая-то загрузка не удалась, в каталоге out остаётся файл из прошлого снимка.
Только стандартная библиотека Python 3.
"""
import calendar
import csv
import io
import json
import os
import sys
import time
import urllib.request

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
UA = 'BURAN-GALAXY-data/1.0 (+https://github.com/greenredapple1910-arch/BURAN_GALAXY)'
GP = 'https://celestrak.org/NORAD/elements/gp.php?{}&FORMAT=tle'
SATCAT = 'https://celestrak.org/pub/satcat.csv'
PLAN = {
    'active.tle': ['GROUP=active'],
    'visual.tle': ['GROUP=visual'],
    'debris.tle': ['GROUP=fengyun-1c-debris', 'GROUP=cosmos-2251-debris',
                   'GROUP=iridium-33-debris', 'GROUP=cosmos-1408-debris'],
}
LL2 = 'https://ll.thespacedevs.com/2.3.0/launches/{}/?mode=normal&limit={}'
STAMP = '%Y-%m-%dT%H:%M:%SZ'


def now():
    return time.strftime(STAMP, time.gmtime())


def age_h(stamp):
    try:
        return (time.time() - calendar.timegm(time.strptime(stamp, STAMP))) / 3600
    except (TypeError, ValueError):
        return 1e9


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read().decode('utf-8', 'replace')


def save(name, text):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def _num(v):
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def compact_launch(x):
    """Запуск Launch Library 2 → только то, что показывает карта."""
    m = x.get('mission') or {}
    pad = x.get('pad') or {}
    loc = pad.get('location') or {}
    cfg = (x.get('rocket') or {}).get('configuration') or {}
    lsp = x.get('launch_service_provider') or {}
    st = x.get('status') or {}
    orb = m.get('orbit') or {}
    vids = (x.get('vid_urls') or []) + (m.get('vid_urls') or [])
    vids.sort(key=lambda v: (v.get('priority') or 99))
    fams = cfg.get('families') or []
    return {
        'id': x.get('id'), 'name': x.get('name'), 'net': x.get('net'),
        'prec': (x.get('net_precision') or {}).get('abbrev'),
        'ws': x.get('window_start'), 'we': x.get('window_end'),
        'st': st.get('abbrev'), 'stn': st.get('name'),
        'lsp': lsp.get('name'), 'lspa': lsp.get('abbrev'), 'lspt': (lsp.get('type') or {}).get('name'),
        'rocket': cfg.get('full_name') or cfg.get('name'), 'fam': fams[0].get('name') if fams else None,
        'mission': m.get('name'), 'mtype': m.get('type'), 'mdesc': (m.get('description') or '')[:700],
        'orbit': orb.get('abbrev'), 'orbitN': orb.get('name'),
        'pad': pad.get('name'), 'loc': loc.get('name'), 'lat': _num(pad.get('latitude')), 'lon': _num(pad.get('longitude')),
        'cc': (pad.get('country') or {}).get('alpha_3_code'),
        'vid': vids[0].get('url') if vids else None, 'wl': bool(x.get('webcast_live')),
        'prog': [p.get('name') for p in (x.get('program') or []) if p.get('name')],
        'fail': x.get('failreason') or '',
    }


def fetch_launches(files):
    try:
        up = json.loads(get(LL2.format('upcoming', 60) + '&hide_recent_previous=true'))
        time.sleep(2)
        prev = json.loads(get(LL2.format('previous', 15)))
    except Exception as e:  # 429 — лимит запросов; остаётся прошлый снимок
        print('skip launches', e)
        return
    data = {'t': now(), 'source': 'Launch Library 2 — The Space Devs (https://thespacedevs.com)',
            'upcoming': [compact_launch(x) for x in up.get('results', [])],
            'previous': [compact_launch(x) for x in prev.get('results', [])]}
    if not data['upcoming']:
        print('skip launches: empty')
        return
    save('launches.json', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    files['launches.json'] = now()
    print('ok launches.json', len(data['upcoming']), len(data['previous']))


def main():
    os.makedirs(OUT, exist_ok=True)
    meta_path = os.path.join(OUT, 'meta.json')
    try:
        with open(meta_path, encoding='utf-8') as f:
            files = json.load(f).get('files', {})
    except (OSError, ValueError):
        files = {}

    for name, queries in PLAN.items():
        parts = []
        for q in queries:
            try:
                t = get(GP.format(q))
            except Exception as e:  # 403 — данные ещё не обновились с прошлой загрузки
                print('skip', q, e)
                parts = None
                break
            if not any(line.startswith('1 ') for line in t.splitlines()[:6]):
                print('skip', q, t[:100].replace('\n', ' '))
                parts = None
                break
            parts.append(t.strip())
            time.sleep(2)
        if parts:
            save(name, '\n'.join(parts) + '\n')
            files[name] = now()
            print('ok', name)

    # каталог SATCAT обновляется раз в сутки — берём не чаще раза в 20 часов
    if age_h(files.get('satcat.json')) > 20:
        try:
            rows = csv.DictReader(io.StringIO(get(SATCAT)))
            out = []
            for r in rows:
                if r['DECAY_DATE'] or r['ORBIT_CENTER'] != 'EA':
                    continue
                try:
                    per, apo, peri = float(r['PERIOD']), float(r['APOGEE']), float(r['PERIGEE'])
                    incl = float(r['INCLINATION'] or 0)
                except ValueError:
                    continue
                if per <= 0 or apo <= 0 or peri < -50:
                    continue
                out.append([int(r['NORAD_CAT_ID']), r['OBJECT_NAME'], r['OBJECT_ID'], r['OBJECT_TYPE'],
                            r['OWNER'], r['LAUNCH_DATE'], r['LAUNCH_SITE'], per, incl, apo, peri,
                            float(r['RCS']) if r['RCS'] else None, r['OPS_STATUS_CODE']])
            save('satcat.json', json.dumps(out, ensure_ascii=False, separators=(',', ':')))
            files['satcat.json'] = now()
            print('ok satcat.json', len(out))
        except Exception as e:
            print('skip satcat', e)

    fetch_launches(files)

    meta = {'t': files.get('active.tle', ''), 'files': files,
            'source': 'CelesTrak (T. S. Kelso), https://celestrak.org; '
                      'Launch Library 2 — The Space Devs, https://thespacedevs.com'}
    save('meta.json', json.dumps(meta, ensure_ascii=False, indent=1))
    save('README.md', '# Данные BURAN GALAXY\n\nСнимок TLE и каталога SATCAT с [CelesTrak](https://celestrak.org) '
         '(T. S. Kelso) и ближайших запусков из [Launch Library 2](https://thespacedevs.com) (The Space Devs). '
         'Ветку обновляет GitHub Action каждые 3 часа; история не хранится.\n')
    if not files.get('active.tle'):
        sys.exit('нет основного списка active.tle')


if __name__ == '__main__':
    main()
