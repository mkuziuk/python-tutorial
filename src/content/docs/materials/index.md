---
title: Материалы
description: Архивы, данные, тетради Jupyter и команды для обеих частей курса.
---

На этой странице собраны самостоятельные рабочие наборы двух арок. В Части I это скрипты, данные и тесты; в Части II — тетрадь для самостоятельной работы, README, зафиксированные зависимости и необходимые локальные данные. Каждый ZIP можно запустить отдельно, даже если учебные понятия продолжают предыдущее расследование.

Если нужно быстро вспомнить Python, pandas, метрики или другой инструмент, возвращайтесь в [Справочник](../field-guide/): ссылки на нужные страницы также есть в начале каждого расследования.

## Быстрый выбор справки

Необязательно читать справочник подряд. Начните с действия, которое сейчас мешает продолжить:

| Нужно сделать | Открыть сначала | Минимальный результат |
| --- | --- | --- |
| прочитать текстовый файл и пройти по строкам | [Файлы](../field-guide/file-io/) и [циклы](../field-guide/control-flow/) | получить `list[str]` и обработать каждую строку |
| посчитать частоты или собрать запись по ключам | [Counter](../field-guide/counter/) и [dict](../field-guide/dict/) | получить воспроизводимую таблицу частот или словарь фактов |
| безопасно работать с путями и JSON | [pathlib](../field-guide/pathlib/) и [JSON](../field-guide/json/) | прочитать вход и сохранить проверяемый отчёт |
| понять форму ML-данных | [математический словарь и NumPy](../field-guide/numpy/#math-vocabulary), затем [pandas](../field-guide/pandas/) | назвать, что означает каждая строка, колонка и ось |
| отделить обучение от проверки | [Постановка ML-задачи](../field-guide/ml-framing/) и [утечка](../field-guide/leakage-pipelines/) | зафиксировать `X`, `y`, обучающую и тестовую выборки до обучения |
| выбрать и объяснить метрику | [Классификационные метрики](../field-guide/classification-metrics/) или [регрессия](../field-guide/regression/) | посчитать показатель и назвать его знаменатель или единицы |
| проверить новые источники, районы или партии | [Групповая валидация](../field-guide/grouped-validation/) | определить независимую единицу и исключить пересечение групп |

Два маленьких примера показывают переход между арками. В Python-расследовании один файл превращается в коллекцию, которую можно проверить:

```python
from pathlib import Path

lines = Path("data/report.txt").read_text(encoding="utf-8").splitlines()  # подставьте файл расследования
non_empty = [line for line in lines if line.strip()]
print(f"Непустых строк: {len(non_empty)}")
```

В ML-расследовании несколько объектов превращаются в матрицу признаков `X`, а ожидаемые ответы — в вектор `y`:

```python
import numpy as np

X = np.array([[5.1, 3.5], [6.7, 3.1]])  # 2 объекта × 2 признака
y = np.array([0, 1])                    # по одному ответу на объект

assert X.shape == (2, 2)
assert y.shape == (2,)
```

Здесь **вектор** — просто упорядоченный одномерный список чисел, а **матрица** — прямоугольная таблица чисел. Геометрический смысл появится только там, где он нужен алгоритму; остальные обозначения собраны в [коротком математическом словаре](../field-guide/numpy/#math-vocabulary).

## Часть I · Архив

В каждом архиве первой части лежат README, данные, стартовый скрипт с ориентирами, `requirements.txt`, пример формы вывода и `tests/` для самопроверки. Полные решения открываются отдельно в главах разбора.

## Расследование 01. Кто оставил предупреждение?

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-01/</code></p>
  <p><strong>Уровень:</strong> начальный+</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-01.zip">case-01.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/anonymous-letter/">сборка инструмента</a> · <a href="../cases/anonymous-letter-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- стартовый `anonymous_letter.py` с комментариями-ориентирами
- `data/anonymous.txt`
- `data/author_morozova.txt`, `data/author_sokolov.txt`, `data/author_korolev.txt`
- `check_result.txt`

```bash
cd case-01
python -m pip install -r requirements.txt
python anonymous_letter.py
python -m unittest discover -s tests
```

## Расследование 02. Детектор текстовых совпадений

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-02/</code></p>
  <p><strong>Уровень:</strong> начальный+</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-02.zip">case-02.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/copy-paste-detector/">сборка инструмента</a> · <a href="../cases/copy-paste-detector-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- стартовый скрипт детектора с комментариями-ориентирами;
- папка `data/` с отчётами и заметками;
- `check_result.txt` с примером формы отчёта.

```bash
cd case-02
python -m pip install -r requirements.txt
python copy_paste_detector.py
python -m unittest discover -s tests
```

## Расследование 03. Фишинговое письмо или нет?

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-03/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-03.zip">case-03.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/phishing-email/">сборка инструмента</a> · <a href="../cases/phishing-email-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- стартовый скрипт анализатора писем с комментариями-ориентирами;
- письма `.eml` в `data/`;
- `check_result.txt` с примером отчёта по риск-сигналам.

```bash
cd case-03
python -m pip install -r requirements.txt
python phishing_email.py
python -m unittest discover -s tests
```

## Расследование 04. Ночной сигнал архива

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-04/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-04.zip">case-04.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/secret-folder-archive/">сборка инструмента</a> · <a href="../cases/secret-folder-archive-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- стартовый скрипт индексатора с комментариями-ориентирами;
- папка `data/secret_folder/` с архивными заметками и копиями;
- `check_result.txt` с формой отчёта по манифесту.

```bash
cd case-04
python -m pip install -r requirements.txt
python secret_folder_archive.py
python -m unittest discover -s tests
```

## Расследование 05. Доска расследования

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-05/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-05.zip">case-05.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/investigation-system/">сборка инструмента</a> · <a href="../cases/investigation-system-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- четыре канонических отчёта I-01–I-04 в `data/artifacts/`;
- `data/relationships.json` с людьми, гипотезами и связями;
- `check_result.txt` с формой `05-case-board.json`.

```bash
cd case-05
python -m pip install -r requirements.txt
python investigation_system.py
python -m unittest discover -s tests
```

## Расследование 06. Вердикт перед открытием

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-06/</code></p>
  <p><strong>Уровень:</strong> продвинутый</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-06.zip">case-06.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/final-verdict/">сборка инструмента</a> · <a href="../cases/final-verdict-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- стартовый `final_verdict.py` с комментариями-ориентирами;
- `data/artifacts/05-case-board.json` из предыдущего расследования;
- `data/morning_updates.json` только с новыми утренними материалами;
- `check_result.txt` с формой финального отчёта;
- `tests/` для проверки хронологии, баллов и вердикта.

```bash
cd case-06
python -m pip install -r requirements.txt
python final_verdict.py
python -m unittest discover -s tests
```

## Часть II · Бюро

Для расследований в тетрадях Jupyter нужен Python 3.12 или 3.13. Локально распакуйте ZIP, откройте папку расследования и выполните:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab
```

В Windows используйте `py -3.12 -m venv .venv` (или `py -3.13 -m venv .venv`) и `.\.venv\Scripts\Activate.ps1`. Затем откройте `case-0N.ipynb` и выполните **Restart Kernel and Run All**. Ссылка Colab запускает ту же тетрадь для самостоятельной работы; начальная ячейка получает ZIP и проверяет контрольную сумму.

Начинайте с тетради для самостоятельной работы в корне архива. `check_result.md` задаёт не единственное правильное число, а обязательную форму проверки: схему разбиения, диапазоны метрик, диагностические графики и структуру вывода. Папка `solution/` остаётся в репозитории для разбора и не входит в самостоятельный ZIP.

### II-01 · Ирисовый экзамен

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/part-2/case-01/</code></p>
  <p><strong>Данные:</strong> <a href="../datasets/iris.csv" download><code>iris.csv</code></a> · <a href="../datasets/iris.csv.sha256">SHA-256</a> · зафиксированная локальная копия <code>sklearn-iris</code></p>
  <p><strong>Архив:</strong> <a href="../downloads/part-2-case-01.zip">part-2-case-01.zip</a></p>
  <p><strong>Notebook:</strong> <code>case-01.ipynb</code> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-01/case-01.ipynb">Open in Colab</a></p>
  <p><strong>Главы:</strong> <a href="../bureau/iris-exam/">брифинг</a> · <a href="../bureau/iris-exam-solution/">дебриф</a></p>
</div>

### II-02 · Пассажиры после факта

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/part-2/case-02/</code></p>
  <p><strong>Данные:</strong> <a href="../datasets/titanic.csv" download><code>titanic.csv</code></a> · <a href="../datasets/titanic.csv.sha256">SHA-256</a> · локальный snapshot <code>openml-titanic-40945-frozen</code></p>
  <p><strong>Архив:</strong> <a href="../downloads/part-2-case-02.zip">part-2-case-02.zip</a></p>
  <p><strong>Notebook:</strong> <code>case-02.ipynb</code> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-02/case-02.ipynb">Open in Colab</a></p>
  <p><strong>Главы:</strong> <a href="../bureau/passengers-after-the-fact/">брифинг</a> · <a href="../bureau/passengers-after-the-fact-solution/">дебриф</a></p>
</div>

### II-03 · Цена одной ошибки

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/part-2/case-03/</code></p>
  <p><strong>Данные:</strong> <a href="../datasets/titanic.csv" download><code>titanic.csv</code></a> · <a href="../datasets/titanic.csv.sha256">SHA-256</a> · тот же зафиксированный снимок Titanic; конвейер обработки без утечки включён в тетрадь, предыдущее расследование не требуется на диске</p>
  <p><strong>Архив:</strong> <a href="../downloads/part-2-case-03.zip">part-2-case-03.zip</a></p>
  <p><strong>Notebook:</strong> <code>case-03.ipynb</code> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-03/case-03.ipynb">Open in Colab</a></p>
  <p><strong>Главы:</strong> <a href="../bureau/cost-of-one-error/">брифинг</a> · <a href="../bureau/cost-of-one-error-solution/">дебриф</a></p>
</div>

### II-04 · Карта дорогих ошибок

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/part-2/case-04/</code></p>
  <p><strong>Данные:</strong> <a href="../datasets/california_housing.csv" download><code>california_housing.csv</code></a> · <a href="../datasets/california_housing.csv.sha256">SHA-256</a> · локальный snapshot <code>sklearn-california-housing-1990-frozen-v1</code></p>
  <p><strong>Архив:</strong> <a href="../downloads/part-2-case-04.zip">part-2-case-04.zip</a></p>
  <p><strong>Notebook:</strong> <code>case-04.ipynb</code> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-04/case-04.ipynb">Open in Colab</a></p>
  <p><strong>Главы:</strong> <a href="../bureau/map-of-costly-errors/">брифинг</a> · <a href="../bureau/map-of-costly-errors-solution/">дебриф</a></p>
</div>

### II-05 · Знакомый почерк

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/part-2/case-05/</code></p>
  <p><strong>Данные:</strong> <a href="../datasets/digits.csv" download><code>digits.csv</code></a> · <a href="../datasets/digits.csv.sha256">SHA-256</a> · зафиксированная локальная копия <code>sklearn-digits-8x8-v1</code></p>
  <p><strong>Архив:</strong> <a href="../downloads/part-2-case-05.zip">part-2-case-05.zip</a></p>
  <p><strong>Notebook:</strong> <code>case-05.ipynb</code> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-05/case-05.ipynb">Open in Colab</a></p>
  <p><strong>Главы:</strong> <a href="../bureau/familiar-handwriting/">брифинг</a> · <a href="../bureau/familiar-handwriting-solution/">дебриф</a></p>
</div>

### II-06 · Экзамен для «Компаса»

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/part-2/case-06/</code></p>
  <p><strong>Данные:</strong> <a href="../datasets/compass_digits_synthetic_captures.csv.gz" download><code>compass_digits_synthetic_captures.csv.gz</code></a> · <a href="../datasets/compass_digits_synthetic_captures.csv.gz.sha256">SHA-256</a> · документированный синтетический стресс-тест <code>compass-digits-synthetic-captures-v1</code></p>
  <p><strong>Архив:</strong> <a href="../downloads/part-2-case-06.zip">part-2-case-06.zip</a></p>
  <p><strong>Notebook:</strong> <code>case-06.ipynb</code> · <a href="https://colab.research.google.com/github/mkuziuk/python-tutorial/blob/main/projects/part-2/case-06/case-06.ipynb">Open in Colab</a></p>
  <p><strong>Главы:</strong> <a href="../bureau/compass-exam/">брифинг</a> · <a href="../bureau/compass-exam-solution/">финальный дебриф</a></p>
</div>

Сначала выполните задания в `case-0N.ipynb` и запишите выводы. Затем откройте тетрадь из `solution/` и сравните код, схему разбиения, метрики и выводы.
