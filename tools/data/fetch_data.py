#!/usr/bin/env python3
"""Снимок данных для BURAN GALAXY: TLE CelesTrak и компактный каталог SATCAT.

Запускается GitHub Action (.github/workflows/data.yml) каждые 3 часа и публикует файлы
в ветку data. Карта берёт данные оттуда, поэтому посетители не нагружают CelesTrak:
сервер отдаёт каждую группу одному адресу не чаще раза за обновление (≈2 ч) и блокирует
адреса с большим числом ошибок.

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

    meta = {'t': files.get('active.tle', ''), 'files': files,
            'source': 'CelesTrak (T. S. Kelso), https://celestrak.org'}
    save('meta.json', json.dumps(meta, ensure_ascii=False, indent=1))
    save('README.md', '# Данные BURAN GALAXY\n\nСнимок TLE и каталога SATCAT с [CelesTrak](https://celestrak.org) '
         '(T. S. Kelso). Ветку обновляет GitHub Action каждые 3 часа; история не хранится.\n')
    if not files.get('active.tle'):
        sys.exit('нет основного списка active.tle')


if __name__ == '__main__':
    main()
