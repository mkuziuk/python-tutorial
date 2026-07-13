# Дело II-06. Экзамен для «Компаса»

Финальный аудит проверяет почти идеальный vendor benchmark. Вы обнаружите
связанные captures по обе стороны row-wise split, замените его на
`StratifiedGroupKFold`, а затем один раз откроете запечатанный scanner batch C.

Ориентир времени: **6–8 часов**. Нужен Python 3.12 или 3.13.

> Все изображения в `digits_compass.csv.gz` — документированные учебные
> синтетические преобразования. Это не реальные сканеры, не реальный поставщик
> и не production benchmark.

## Что внутри

- `case-06.ipynb` — учебная тетрадь;
- `data/digits_compass.csv.gz` — фиксированная синтетическая производная;
- `data/generate_synthetic_captures.py` — детерминированный генератор;
- `data/SOURCE.md`, `LICENSE.txt`, `generation_report.json`, `CHECKSUMS.sha256`;
- `requirements.txt`, `requirements-colab.txt`, `check_result.md`;
- `solution/case-06-solution.ipynb` — эталон только в репозитории.

## Локальный запуск

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
jupyter lab case-06.ipynb
```

Набор уже включён и не требует выполнения II-05: замороженная конфигурация
модели записана в тетради. Генератор нужен сопровождающим, а не для Run All.

## Google Colab

[Открыть learner notebook в Colab](https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-06/case-06.ipynb)

Bootstrap скачивает ZIP и `.zip.sha256`, проверяет архив и только затем
распаковывает локальную копию данных.

## Результат

Тетрадь создаёт `artifacts/model_card.md` и
`artifacts/procurement_memo.md`. Каноническое действие — приостановить закупку
до независимой task-specific проверки. Найденный дефект benchmark не является
доказательством личного умысла или мошенничества.

Перед сдачей выполните **Restart Kernel → Run All** и проверьте все пункты
`check_result.md`.
