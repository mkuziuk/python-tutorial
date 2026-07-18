---
title: Материалы
description: Архивы, данные, тетради Jupyter и команды для обеих частей курса.
---

На этой странице собраны самостоятельные рабочие наборы двух арок. В Части I это стартовые скрипты, данные и примеры формы результата; в Части II — тетрадь для самостоятельной работы, README, зафиксированные зависимости и необходимые локальные данные. Каждый ZIP можно запустить отдельно, даже если учебные понятия продолжают предыдущее расследование.

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

Два маленьких примера показывают переход между арками.

Сначала проверим, сколько содержательных строк прочитано из одного текстового файла. На входе находится `data/report.txt`, а после команды должны появиться список строк `lines`, отфильтрованный список `non_empty` и число непустых строк в терминале:

```python
from pathlib import Path

lines = Path("data/report.txt").read_text(encoding="utf-8").splitlines()  # подставьте файл расследования
non_empty = [line for line in lines if line.strip()]
print(f"Непустых строк: {len(non_empty)}")
```

Строка `Непустых строк: ...` подтверждает, что путь найден, файл прочитан и пустые строки отброшены. Конкретное число зависит от файла расследования; его нужно сверить с примером главы или `check_result.*`. Получив проверяемую коллекцию, можно переходить к подсчёту частот, поиску совпадений или другому анализу главы.

В ML-расследовании следующая форма данных — матрица признаков `X` и вектор правильных ответов `y`. Создадим два учебных объекта с двумя признаками и проверим, что каждому объекту соответствует ровно один ответ:

```python
import numpy as np

X = np.array([[5.1, 3.5], [6.7, 3.1]])  # 2 объекта × 2 признака
y = np.array([0, 1])                    # по одному ответу на объект

assert X.shape == (2, 2)
assert y.shape == (2,)
```

Если обе проверки завершаются без `AssertionError`, `X` имеет форму «2 объекта × 2 признака», а `y` содержит 2 ответа. Здесь **вектор** — просто упорядоченный одномерный список чисел, а **матрица** — прямоугольная таблица чисел. Проверив соответствие строк и ответов, можно безопасно переходить к разбиению данных; остальные обозначения собраны в [коротком математическом словаре](../field-guide/numpy/#math-vocabulary).

## Как открыть терминал в папке расследования

После загрузки распакуйте ZIP и откройте папку `case-0N`:

- **Windows:** в Проводнике щёлкните правой кнопкой по свободному месту внутри папки и выберите **Открыть в терминале**;
- **macOS:** в Finder щёлкните по папке правой кнопкой и выберите **Службы → Новый терминал по адресу папки**;
- **Linux:** в файловом менеджере щёлкните правой кнопкой внутри папки и выберите **Открыть в терминале**.

Формулировка пункта зависит от системы и файлового менеджера. Терминал должен открыться в папке, где видны `requirements.txt`, стартовый файл и `data/`. Все команды ниже выполняются уже там и начинаются с создания `.venv`.

## Часть I · Архив

В каждом архиве первой части лежат README, данные, пустой стартовый скрипт, `requirements.txt` и `check_result.txt` с формой ожидаемого результата. Студент сверяет вывод программы с `check_result.txt`, а тесты остаются внутренним инструментом сопровождающих и в учебный ZIP не входят. Полные решения открываются отдельно в главах разбора.

## Расследование 01. Кто оставил предупреждение?

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-01/</code></p>
  <p><strong>Уровень:</strong> начальный+</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-01.zip">case-01.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/anonymous-letter/">сборка инструмента</a> · <a href="../cases/anonymous-letter-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый `anonymous_letter.py`
- `data/anonymous.txt`
- `data/author_morozova.txt`, `data/author_sokolov.txt`, `data/author_korolev.txt`
- `check_result.txt`

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python anonymous_letter.py
```

macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python anonymous_letter.py
```

После активации обычно появится `(.venv)`. Внешних библиотек нет. Первый запуск пустого скрипта ничего не выводит; по мере сборки программы сверяйте текстовый отчёт и JSON с `check_result.txt`.

## Расследование 02. Детектор текстовых совпадений

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-02/</code></p>
  <p><strong>Уровень:</strong> начальный+</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-02.zip">case-02.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/copy-paste-detector/">сборка инструмента</a> · <a href="../cases/copy-paste-detector-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый `copy_paste_detector.py`;
- папка `data/` с отчётами и заметками;
- `check_result.txt` с примером формы отчёта.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python copy_paste_detector.py
```

macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python copy_paste_detector.py
```

Метка `(.venv)` обычно показывает активацию. Внешних библиотек нет. Пустой стартовый файл сначала не печатает результат; готовый текстовый отчёт сверяйте с `check_result.txt`.

## Расследование 03. Фишинговое письмо или нет?

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-03/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-03.zip">case-03.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/phishing-email/">сборка инструмента</a> · <a href="../cases/phishing-email-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый `phishing_email.py`;
- письма `.eml` в `data/`;
- `check_result.txt` с примером отчёта по риск-сигналам.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python phishing_email.py
```

macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python phishing_email.py
```

Метка `(.venv)` обычно показывает активацию. Внешних библиотек нет. После сборки программы сравните уровни риска и сохранённый отчёт с ориентирами в `check_result.txt`.

## Расследование 04. Последнее доказательство

<div class="materials-panel">
  <p><strong>Проект:</strong> <code>projects/case-04/</code></p>
  <p><strong>Уровень:</strong> средний</p>
  <p><strong>Архив:</strong> <a href="../downloads/case-04.zip">case-04.zip</a></p>
  <p><strong>Глава:</strong> <a href="../cases/final-evidence/">сборка инструмента</a> · <a href="../cases/final-evidence-solution/">разбор решения</a></p>
</div>

Ключевые файлы:

- пустой стартовый `final_evidence.py`;
- три канонических отчёта I-01–I-03 в `data/artifacts/`;
- `final_evidence.json` с утренними проверками;
- `suspect_dossiers.json` с вымышленными локальными досье;
- `check_result.txt` с формой итогового отчёта.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python final_evidence.py
```

macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python final_evidence.py
```

Метка `(.venv)` обычно показывает активацию. Внешних библиотек нет. Итоговое число улик, лидера рейтинга и путь сохранённого JSON сверяйте с `check_result.txt`.

## Часть II · Бюро

Для расследований в тетрадях Jupyter нужен Python 3.12 или 3.13. Локально распакуйте ZIP и откройте терминал в папке расследования способом, описанным выше.

macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab
```

Вместо `py -3.12` можно использовать `py -3.13`. Появление `(.venv)` подтверждает активацию. Затем откройте `case-0N.ipynb` и выполните **Restart Kernel and Run All**. Ссылка Colab запускает ту же тетрадь для самостоятельной работы; начальная ячейка получает ZIP и проверяет контрольную сумму.

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
