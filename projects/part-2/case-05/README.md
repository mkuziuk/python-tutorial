# Дело II-05. Знакомый почерк

Вместо монтажа удачных распознаваний вы восстановите проверяемый протокол для
встроенного набора Digits: сравните k-NN и RBF SVM, объявите маленький grid
заранее и разберёте ошибки каждого класса на единственном внешнем holdout.

Ориентир времени: **4–5 часов**. Нужен Python 3.12 или 3.13.

## Что внутри

- `case-05.ipynb` — учебная тетрадь;
- `data/SOURCE.md`, `LICENSE.txt`, `dataset_manifest.json`, `CHECKSUMS.md` —
  карточка встроенного `load_digits()`;
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

Digits входит в scikit-learn: сеть и предыдущие дела не нужны.

## Google Colab

[Открыть learner notebook в Colab](https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-05/case-05.ipynb)

Bootstrap проверяет SHA-256 архива до распаковки. После загрузки notebook
дополнительно проверяет content hash встроенных массивов `X` и `y`.

## Результат

Тетрадь создаёт `artifacts/model_lock.json` и `artifacts/audit_memo.md`.
Блокировка фиксирует модель до дела II-06; внешний test нельзя использовать для
расширения grid. Перед сдачей выполните **Restart Kernel → Run All**.
