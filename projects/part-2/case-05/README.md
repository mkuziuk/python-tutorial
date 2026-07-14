# Расследование II-05. Знакомый почерк

Вместо монтажа удачных распознаваний вы восстановите проверяемый протокол для
замороженного CSV-снимка Digits: сравните k-NN и RBF SVM, заранее объявите небольшую сетку параметров
и разберите ошибки каждого класса на единственной внешней тестовой выборке.

Ориентир времени: **4–5 часов**. Нужен Python 3.12 или 3.13.

## Что внутри

- `case-05.ipynb` — учебная тетрадь;
- `data/digits.csv` — замороженный снимок набора;
- `data/SOURCE.md`, `LICENSE.txt`, `dataset_manifest.json`, `CHECKSUMS.sha256` —
  происхождение, лицензия, схема и контрольная сумма;
- `requirements.txt` и `requirements-colab.txt`;
- `check_result.md`;
- `solution/case-05-solution.ipynb` — эталон только в репозитории.

## Локальный запуск

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
jupyter lab case-05.ipynb
```

CSV уже вложен в архив: сеть и предыдущие расследования не нужны.

## Google Colab

[Открыть тетрадь для самостоятельной работы в Colab](https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-05/case-05.ipynb)

Начальная ячейка проверяет SHA-256 архива до распаковки. После загрузки тетрадь
дополнительно проверяет SHA-256 `digits.csv` до чтения в `DataFrame`.

## Результат

Тетрадь создаёт `artifacts/model_lock.json` и `artifacts/audit_memo.md`.
Блокировка фиксирует модель до расследования II-06; внешнюю тестовую выборку нельзя использовать для
расширения сетки параметров. Перед сдачей выполните **Restart Kernel → Run All**.
