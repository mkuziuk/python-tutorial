# Python-расследования

Русский проектный учебник по Python и классическому машинному обучению: каждая глава строит работающий инструмент для расследования, а теория появляется там, где она нужна проекту.

Сайт: [https://mkuziuk.github.io/python-tutorial/](https://mkuziuk.github.io/python-tutorial/)

## Что внутри

- `src/content/docs/` — страницы Starlight: расследования, справочник, материалы и карта навыков двух частей.
- `projects/case-01/` … `projects/case-06/` — шесть проектов части I с данными, стартовыми файлами, решениями и тестами.
- `projects/part-2/case-01/` … `projects/part-2/case-06/` — шесть автономных проектов части II в тетрадях Jupyter с локальными данными и готовыми решениями.
- `src/data/course.json` — общий публичный манифест курса для Astro и проверяющих скриптов.
- `PLOT.md` и `PLOT_PART_2.md` — раздельные каноны двух сюжетных арок.
- `.github/workflows/deploy.yml` — развёртывание на GitHub Pages через официальный Astro Action.

## Локальный запуск

Для части I требуется Python 3.13 или новее; часть II проверяется на Python 3.12 и 3.13. Проверьте версию перед началом: `python3 --version` на macOS и Linux или `py -3 --version` на Windows. Зависимости зафиксированы в `requirements.txt` внутри соответствующей части и каждого расследования.

```bash
pnpm install
pnpm dev
```

## Проверки

```bash
pnpm build
pnpm test:python
pnpm test:notebooks
pnpm test:manifest
pnpm test:part1-artifacts
pnpm test:part1-solutions
pnpm test:archives
pnpm test:links
pnpm verify
```

`test:part1-artifacts` проверяет цепочку JSON I-01 → I-06, а `test:part1-solutions` сверяет страницы разборов с каноническими Python-файлами. `test:notebooks` проверяет генерацию тетрадей для самостоятельной работы и исполняет решения части II из чистых временных наборов. `test:manifest` сверяет манифест с маршрутами, проектами и данными. `test:archives` проверяет скачиваемые ZIP-наборы обеих частей; пересобрать их можно командой `pnpm build:archives`. `test:links` проверяет внутренние ссылки и якоря в уже собранной папке `dist/`; `verify` запускает полный цикл.

Политика кода:

- часть I ориентирована на Python 3.13+, часть II — на Python 3.12–3.13;
- новые проекты не используют устаревшие API и не добавляют сторонние библиотеки без явной причины;
- если библиотека нужна, она добавляется в актуальной версии и с коротким объяснением, где она используется.

## GitHub Pages

Если репозиторий будет опубликован как `https://<user>.github.io/<repo>/`, задайте переменные окружения для сборки:

```bash
SITE_URL=https://<user>.github.io
BASE_PATH=/repo
```

Для репозитория вида `<user>.github.io` достаточно `SITE_URL=https://<user>.github.io`.

В публичный репозиторий должны попадать только оригинальные материалы из `site/`; локальные PDF-файлы из родительской папки не нужны для сборки и не должны коммититься.
