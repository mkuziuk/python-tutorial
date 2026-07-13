# Дело II-04. Карта дорогих ошибок

Поставщик «Компаса» сообщает высокий общий `R²` и обещает оценку жилья в
новых районах. В этом деле вы проверите, меняется ли вывод, когда вместо
случайных строк holdout содержит целые невиданные географические ячейки.

Ориентир времени: **4–5 часов**. Нужен Python 3.12 или 3.13.

## Что внутри

- `case-04.ipynb` — учебная тетрадь с упражнениями;
- `data/california_housing.csv` — фиксированный offline-снимок;
- `data/SOURCE.md`, `LICENSE.txt`, `dataset_manifest.json`, `CHECKSUMS.sha256` —
  происхождение и контроль целостности;
- `requirements.txt` и `requirements-colab.txt` — закреплённые зависимости;
- `check_result.md` — форма ожидаемого результата;
- `solution/case-04-solution.ipynb` — эталон в репозитории, не в learner ZIP.

## Локальный запуск

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
jupyter lab case-04.ipynb
```

Запускайте тетрадь из каталога дела. Bootstrap также умеет найти каталог из
корня репозитория. Данные не скачиваются и не требуют предыдущих дел.

## Google Colab

[Открыть learner notebook в Colab](https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-04/case-04.ipynb)

В Colab bootstrap скачивает `part-2-case-04.zip` и соседний `.zip.sha256`,
проверяет архив до распаковки и сохраняет ту же структуру путей.

## Результат

После выполнения появится `artifacts/audit_memo.md`. В записке должны быть
отдельно названы установленный факт, поддержанная интерпретация, что не
доказано, ограничения и рекомендуемое действие. Перед сдачей выполните
**Restart Kernel → Run All** и сверьтесь с `check_result.md`.
