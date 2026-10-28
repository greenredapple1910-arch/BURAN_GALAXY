# BURAN GALAXY — живая 3D-карта Солнечной системы

> [!WARNING]
> **Не открывается GitHub Pages?** У части провайдеров (в том числе российских) адреса `*.github.io` недоступны: страница бесконечно грузится или выдаёт ошибку соединения. Сам сайт при этом работает.
>
> **Откройте карту через зеркало:** [**raw.githack.com/…/BURAN_GALAXY/main/index.html**](https://raw.githack.com/greenredapple1910-arch/BURAN_GALAXY/main/index.html). Это тот же `index.html` из этого репозитория. При первом заходе нажмите «Open the page» на промежуточной странице.
>
> Основной адрес: https://greenredapple1910-arch.github.io/BURAN_GALAXY/

**Открытая интерактивная карта Солнечной системы в реальном времени.** Планеты, спутники, зонды, кометы и тысячи спутников Земли — по данным NASA, NOAA и CelesTrak. Интерфейс в стиле Bloomberg-терминала, графика в духе Universe Sandbox. Один HTML-файл, без сборки и установки.

![Интерфейс: ночная Европа в огнях городов, досье Земли, космическая погода](docs/screenshots/ui-earth.jpg)

## Запуск

- **Онлайн:** https://greenredapple1910-arch.github.io/BURAN_GALAXY/
- **Зеркало, если GitHub Pages недоступен:** https://raw.githack.com/greenredapple1910-arch/BURAN_GALAXY/main/index.html (на промежуточной странице нажмите «Open the page»).
- **Локально:** скачайте репозиторий и откройте `index.html` двойным щелчком.
- **Через локальный сервер** (так стабильнее работают живые данные):

  ```bash
  python -m http.server 8000
  ```

  затем откройте <http://localhost:8000>.

При первом запуске нужен интернет: библиотеки, текстуры и живые данные загружаются с CDN и открытых API.

## Что внутри

| | |
|---|---|
| ![Луна в HD с местами посадок](docs/screenshots/ui-moon.jpg) | ![Сатурн с кольцами по фотографиям](docs/screenshots/saturn.jpg) |
| ![Реальные спутники Starlink по TLE](docs/screenshots/starlink.jpg) | ![Гелиосфера и пояс Койпера](docs/screenshots/heliosphere.jpg) |

**Живые данные**
- **Спутники в реальном времени:** МКС, Тяньгун, Хаббл, Chandra — по свежим TLE CelesTrak и модели SGP4, с наземной трассой и подсказкой, над какой страной аппарат сейчас.
- **Группировки целиком:** Starlink (более 10 тыс.), OneWeb, GPS, ГЛОНАСС, Galileo, BeiDou, геостационар и космический мусор — свыше 15 тыс. объектов.
- **Космическая погода NOAA:** солнечный ветер, межпланетное поле, индекс Kp (по нему светятся полярные сияния на глобусе), рентгеновский поток GOES.
- **NEO WATCH:** сближения астероидов с Землёй на неделю (NASA NeoWs).

**Объекты**
- Солнце, 8 планет и Плутон по кеплеровым элементам JPL; 24 крупных спутника; реальная фаза Луны.
- Земля как с орбиты: огни городов, облака, атмосфера; ориентация по звёздному времени, поэтому день, ночь и сезоны совпадают с действительностью. При приближении проявляются границы 180 государств с досье (ВВП, население, столица).
- Границы государств по умолчанию — по законодательству РФ: Республика Крым, Севастополь, ДНР, ЛНР, Запорожская и Херсонская области в составе России. В «⚙ Настройках» можно переключиться на международно признанные границы.
- Луна в HD (мозаика LRO 11469×5734) с 26 местами посадок, 3D-моделями модулей и луноходов, траекториями Земля → Луна.
- Зонды дальнего космоса, флот у Марса, телескопы JWST, Хаббл, Euclid; наземные обсерватории.
- Кометы с хвостами и межзвёздные объекты 1I/ʻОумуамуа, 2I/Борисов, 3I/ATLAS.
- Пояс астероидов с люками Кирквуда, троянцы Юпитера, пояс Койпера, гелиосфера.
- Небесная сфера: реальный Млечный Путь, созвездия, яркие звёзды, галактики, чёрные дыры Sgr A* и M87*, экзопланетные системы.

**Инструменты**
- Командная строка `/` с автодополнением: «Марс», «Япония», `ДАТА 1969-07-20 20:17`, `ТУР`, `LIVE`.
- Кинотур, машина времени (21 событие от «Спутника-1» до 2134 года), запланированные миссии с обратным отсчётом.
- Сравнение небесных тел, линейка расстояний (Ctrl+щелчок), снимок PNG, ссылки на вид.
- Управление временем: ускорение до 30 суток в секунду и обратный ход.

![Комета NEOWISE с ионным и пылевым хвостом, июль 2020](docs/screenshots/comet.jpg)

## Управление

| Действие | Мышь / клавиша |
|---|---|
| Вращать / приблизить / сдвинуть | ЛКМ / колесо / ПКМ (на телефоне: один палец / два пальца) |
| Досье объекта / подлёт | щелчок / двойной щелчок |
| Поиск и команды | `/` |
| Обзор всей системы | `H` |
| Медленнее / быстрее (ниже ×1 — назад) | `,` / `.` |
| Пауза | `Пробел` |
| Кинотур / машина времени / NEO / сравнение | `T` / `Y` / `N` / `C` |
| Каталог / скрыть интерфейс | `L` / `U` |
| Слои карты | `1`–`6`, `8`, `9`, `0` или меню «◧ СЛОИ» |
| Справка | `?` |

Ссылка вида `index.html#o=saturn&t=2061-07-28T00:00Z` открывает выбранный объект на нужную дату.

## Как включить GitHub Pages

Settings → Pages → Build and deployment → Source: **Deploy from a branch**, Branch: **main**, папка **/ (root)**. Через минуту карта будет доступна по адресу `https://greenredapple1910-arch.github.io/BURAN_GALAXY/`.

## Устройство проекта

Всё приложение — один файл `index.html`, без сборщиков и зависимостей в репозитории:

1. **Данные** — планеты, спутники, зонды, страны, миссии, места посадок, обсерватории, история версий (`VERSIONS`).
2. **Ядро («часть 2»)** — сцена Three.js r128, орбитальная механика, интерфейс. Наружу открыт объект `window.BURAN` и точки расширения `BURAN.hooks`: `pos`, `post`, `vis`, `live`, `select`, `click`, `key`, `input`, `ticker`, `resize`.
3. **Модули v0.4 («часть 3»)** — живые данные, кометы, пояса, небо, командная строка, тур, Bloom.
4. **Модуль v0.5 («часть 4»)** — упрощённый интерфейс, настройки, касания, ссылки на вид.

Новую функцию проще всего добавить отдельным `<script>` в конце файла через `BURAN.hooks`, не трогая ядро:

```js
BURAN.hooks.post.push((dt) => { /* вызывается каждый кадр после расчёта позиций */ });
BURAN.hooks.live.push((rec, rows) => rows.push(['Моя метрика', () => '42']));
```

## Источники данных и благодарности

- Орбиты планет — элементы JPL (Standish); точность — доли градуса на 1800–2050 гг. Орбиты комет, астероидов и зондов — приближённые.
- TLE — [CelesTrak](https://celestrak.org) (T. S. Kelso), расчёт — [satellite.js](https://github.com/shashwatak/satellite-js) (MIT).
- Космическая погода — [NOAA SWPC](https://www.swpc.noaa.gov) (общественное достояние).
- Сближения астероидов — [NASA NeoWs](https://api.nasa.gov) (публичный ключ `DEMO_KEY`, до 30 запросов в час).
- Границы государств — [Natural Earth](https://www.naturalearthdata.com) через [world.geo.json](https://github.com/johan/world.geo.json) (общественное достояние); границы регионов для режима «по законодательству РФ» — Natural Earth admin-1 1:10M, скрипты сборки в [tools/borders](tools/borders).
- Текстуры Земли — NASA Blue Marble и Black Marble (через примеры [three-globe](https://github.com/vasturiano/three-globe) и three.js); HD-карта Луны — NASA LRO (через пример [globe.gl](https://github.com/vasturiano/globe.gl)).
- Текстуры планет — © James Hastings-Trew, [Planet Pixel Emporium](http://planetpixelemporium.com), через [threex.planets](https://github.com/jeromeetienne/threex.planets); используются по условиям автора и загружаются с CDN, в репозитории не хранятся.
- 3D-движок — [three.js](https://threejs.org) r128 (MIT).

Все внешние ресурсы подгружаются во время работы и не входят в репозиторий; их лицензии действуют отдельно от лицензии проекта.

## Участие

Пул-реквесты и идеи приветствуются: новые миссии, переводы интерфейса, уточнение данных, оптимизация. Перед отправкой откройте `index.html` и убедитесь, что в консоли браузера нет ошибок. Историю изменений см. в [CHANGELOG.md](CHANGELOG.md) или в самом приложении (бейдж версии в правом верхнем углу).

## Лицензия

Код проекта распространяется по лицензии [MIT](LICENSE).

---

## English summary

**BURAN GALAXY** is an open-source, real-time 3D map of the Solar System in a single HTML file: planets and moons from JPL orbital elements, a photoreal Earth with city lights and a true day/night terminator, an HD Moon with 26 landing sites, live satellites (ISS, Tiangong, Hubble and 15,000+ objects including Starlink, GNSS constellations and debris) propagated from CelesTrak TLEs with SGP4, NOAA space weather with Kp-driven aurorae, NASA near-Earth asteroid approaches, comets with tails, interstellar objects, asteroid and Kuiper belts, the heliosphere and a real celestial sphere. The interface is in Russian and styled after a Bloomberg terminal. Open `index.html` in a browser (internet connection required for libraries, textures and live data). Licensed under MIT.

Live: https://greenredapple1910-arch.github.io/BURAN_GALAXY/ · Mirror (if `*.github.io` is blocked on your network): https://raw.githack.com/greenredapple1910-arch/BURAN_GALAXY/main/index.html
