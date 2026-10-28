# Геометрия границ «по законодательству РФ»

Скрипты, которыми собран объект `BORDER_VIEWS.ru` в `index.html`: полигоны России и Украины, где Республика Крым, Севастополь, ДНР, ЛНР, Запорожская и Херсонская области (в административных границах) отнесены к России. Остальные страны берутся из базовой карты без изменений. Второй режим («международно признанные») — это базовая карта как есть.

## Источники (общественное достояние)

- Базовая карта стран 1:110M — [johan/world.geo.json](https://github.com/johan/world.geo.json) (Natural Earth).
- Административное деление 1:10M — [ne_10m_admin_1_states_provinces.geojson](https://github.com/nvkelso/natural-earth-vector/tree/master/geojson) (Natural Earth).

## Пересборка

```bash
curl -L -o world110.geojson https://cdn.jsdelivr.net/gh/johan/world.geo.json@master/countries.geo.json
curl -L -o admin1_10m.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_1_states_provinces.geojson
python extract_regions.py admin1_10m.geojson regions.geojson
npm install polygon-clipping@0.15.7
node build_ru_view.js world110.geojson regions.geojson ru_view.json
```

Содержимое `ru_view.json` вставляется в `index.html` как значение `BORDER_VIEWS.ru`.

Что делает `build_ru_view.js`:

1. объединяет шесть регионов и упрощает их границу (Дуглас — Пекер, 0,03°);
2. закрывает щель в русле Днепра у Херсона (в данных 1:10M оно вырезано как вода);
3. оставляет Украине основной массив её полигона, а всё прочее — перенесённые регионы и узкие обрезки на стыке масштабов 1:110M и 1:10M — присоединяет к России, поэтому общая граница двух стран совпадает без зазоров;
4. округляет координаты до 0,001°.
