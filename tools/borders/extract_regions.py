# Извлекает из Natural Earth admin-1 (1:10M) Крым, Севастополь, Донецкую, Луганскую,
# Запорожскую и Херсонскую области. Запуск: python extract_regions.py admin1_10m.geojson regions.geojson
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(sys.argv[1], encoding='utf-8'))
want = {'UA-43','UA-40','UA-14','UA-09','UA-23','UA-65'}
out = []
for f in d['features']:
    p = f['properties']
    if p.get('adm0_a3') == 'UKR' or p.get('iso_3166_2','').startswith('UA-'):
        code = p.get('iso_3166_2')
        mark = '*' if code in want else ' '
        g = f['geometry']; n = sum(len(r) for poly in ([g['coordinates']] if g['type']=='Polygon' else g['coordinates']) for r in poly)
        print(mark, code, p.get('name'), p.get('name_ru'), p.get('adm0_a3'), 'pts', n)
        if code in want: out.append({'type':'Feature','properties':{'code':code,'name':p.get('name')},'geometry':g})
json.dump({'type':'FeatureCollection','features':out}, open(sys.argv[2],'w',encoding='utf-8'))
print('extracted', len(out))
