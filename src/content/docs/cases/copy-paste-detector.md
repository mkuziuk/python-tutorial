---
title: "Дело 02. Детектор текстовых совпадений"
description: "Пошагово строим инструмент, который режет тексты на n-граммы, сравнивает множества и ранжирует подозрительные совпадения."
concepts:
  - tuple
  - n-grams
  - set
  - dict
  - sorting
  - functions
  - control flow
  - comprehensions
  - unittest
difficulty: "начальный+"
projectId: "case-02"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> найти пары архивных описаний, которые слишком похожи на утечку или подмену.</p>
  <p><strong>Инструменты</strong> кортежи, n-граммы, множества, словари, сортировка, функции и аккуратный отчет в терминале.</p>
  <p><strong>Результат</strong> консольный детектор, который показывает рейтинг подозрительных совпадений.</p>
  <p><strong>Маршрут</strong> начальный+ · 90–120 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-02.zip">case-02.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../copy-paste-detector-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/control-flow/">условия и циклы</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/tuple/">tuple</a> · <a href="../../field-guide/set/">set</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/sorting/">sorting</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/comprehensions/">включения</a> · <a href="../../field-guide/rich/">Rich</a> · <a href="../../field-guide/testing/">unittest</a></p>
</div>

## Проблема

После анонимной записки редактор просматривает соседние материалы архива. В черновике экскурсии почти дословно повторяются фрагменты закрытой описи, хотя эта опись еще не должна была покинуть рабочую папку. Еще одна пара отчетов тоже подозрительно похожа, но относится к учебному стенду: инструменту предстоит отделить возможную утечку от обычного повторного использования текста.

Вопрос дела: какие пары действительно похожи на копирование или утечку, а какие просто описывают одну тему похожими словами?

Наша задача не "поймать нарушителя", а сделать рабочий инструмент первичной проверки. Программа прочитает несколько отчетов, сравнит каждую пару и поднимет наверх те пары, где совпадает много соседних слов.

Скачайте архив [case-02.zip](../../downloads/case-02.zip) или откройте папку `projects/case-02/` в репозитории.

В learner-наборе:

- `copy_paste_detector.py` - пустой стартовый файл, который мы будем дорабатывать;
- `requirements.txt` - точная версия Rich для красивой таблицы;
- `data/report_*.txt` - полные отчеты из архива;
- `check_result.txt` - форма ожидаемого результата.

Полное решение вынесено отдельно: [Разбор полного решения](../copy-paste-detector-solution/).

### Подготовка окружения

Нужен Python 3.13 или новее. Перед началом проверьте `py -3 --version` на Windows или `python3 --version` на macOS и Linux.

Windows PowerShell:

```powershell
cd path\to\case-02
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS или Linux:

```bash
cd path/to/case-02
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Запустите пустой стартовый файл:

```bash
python copy_paste_detector.py
```

Он пока ничего не выводит: это чистая заготовка. Дальше мы вручную превратим ее в детектор.

## Стратегия

Один общий абзац еще не доказывает заимствование: в текстах одной темы часто встречаются одинаковые слова. Поэтому будем сравнивать не отдельные слова, а соседние группы слов.

Такая группа называется n-граммой. Если `n = 4`, то из [списка](../../field-guide/list/) слов:

```python
["каждое", "утро", "группа", "открывает", "журнал"]
```

получаются две 4-граммы:

```python
("каждое", "утро", "группа", "открывает")
("утро", "группа", "открывает", "журнал")
```

Обратите внимание на круглые скобки. N-грамму удобно хранить как [`tuple`](../../field-guide/tuple/): порядок слов важен, а сама группа не должна меняться после создания.

План инструмента:

1. прочитать все `report_*.txt`;
2. превратить каждый текст в список нормализованных слов;
3. собрать n-граммы как кортежи;
4. положить n-граммы каждого отчета в [`set`](../../field-guide/set/);
5. сравнить каждую пару через пересечение множеств;
6. сохранить результат пары в [`dict`](../../field-guide/dict/);
7. [отсортировать](../../field-guide/sorting/) результаты по убыванию подозрительности.

## Сборка инструмента

Откройте пустой `copy_paste_detector.py`. Сначала добавьте путь к данным, размер n-граммы и консоль:

```python
from pathlib import Path

from rich.console import Console

# Путь строится от файла скрипта и не зависит от текущей папки терминала.
DATA_DIR = Path(__file__).with_name("data")
NGRAM_SIZE = 4
TOP_EXAMPLES = 3
console = Console()
```

Сначала добавьте чтение файла:

```python
def read_text(path):
    return path.read_text(encoding="utf-8")
```

### Нормализуем слова

Нам не нужны запятые, точки и регистр. Сделаем простую функцию: буквы оставляем, все остальное превращаем в пробел. На входе у нее текст, на выходе список слов; если этот шаг пропустить, совпадения будут зависеть от запятых и заглавных букв.

```python
def normalize_words(text):
    cleaned = []

    for char in text.lower():
        if char.isalpha():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return "".join(cleaned).split()
```

`isalpha()` работает и с русскими буквами. После `"".join(cleaned)` у нас получается очищенная строка, а `.split()` режет ее на слова.

### Собираем n-граммы

Теперь нужна функция, которая двигает окно размера `size` по списку слов. Она возвращает список кортежей, потому что дальше эти кортежи можно положить во множество и быстро сравнивать.

```python
NGRAM_SIZE = 4


def make_ngrams(words, size=NGRAM_SIZE):
    if size < 1:
        raise ValueError("N-gram size must be positive")

    ngrams = []

    # Последнее окно начинается в len(words) - size; +1 включает эту позицию.
    for index in range(len(words) - size + 1):
        ngram = tuple(words[index : index + size])
        ngrams.append(ngram)

    return ngrams
```

Кортеж хранит соседние слова в фиксированном порядке. В нашем проекте длина обычно равна четырем, но сама функция остается удобной для любого `size`.

### Профиль отчета

Для каждого файла соберем небольшой словарь. В нем будет название, количество слов, количество n-грамм и множество самих n-грамм. Такой профиль отделяет чтение текста от сравнения: остальные функции уже не знают, откуда пришел файл.

```python
DISPLAY_NAMES = {
    "report_north_table": "Опись Северного стола",
    "report_tour_draft": "Черновик экскурсии",
    "report_basement_route": "Служебный маршрут подвального коридора",
    "report_alarm_stand": "Отчет учебного стенда",
    "report_guard_note": "Отчет охраны",
}


def display_name(path):
    return DISPLAY_NAMES.get(path.stem, path.stem.replace("_", " ").title())
```

Теперь профиль:

```python
def build_profile(path, ngram_size=NGRAM_SIZE):
    text = read_text(path)
    words = normalize_words(text)
    ngrams = set(make_ngrams(words, ngram_size))

    return {
        "path": path,
        "title": display_name(path),
        "word_count": len(words),
        "ngram_count": len(ngrams),
        "ngrams": ngrams,
    }
```

Здесь `set(...)` важен: множество хранит только уникальные n-граммы и умеет быстро находить пересечения.

### Считаем подозрительность

Для пары отчетов нам нужны две оценки. `overlap_score()` принимает два множества n-грамм и возвращает одно число от `0.0` до `1.0`, чтобы результат можно было сортировать.

Первая - containment: какая доля меньшего текста нашлась в большем. Это полезно, если один отчет почти целиком повторяет часть длинного.

Вторая - Jaccard: какая доля общих n-грамм есть среди всех n-грамм пары.

```python


def overlap_score(left, right):
    if not left or not right:
        return 0.0

    shared = left & right
    if not shared:
        return 0.0

    # Первая доля ищет вложение в меньший текст, вторая штрафует лишние n-граммы.
    containment = len(shared) / min(len(left), len(right))
    jaccard = len(shared) / len(left | right)
    return round(containment * 0.7 + jaccard * 0.3, 3)
```

`left & right` возвращает n-граммы, которые есть в обоих множествах. `left | right` возвращает все уникальные n-граммы из двух текстов.

### Сравниваем пару профилей

Результат сравнения тоже удобно держать в словаре: это одна запись будущего отчета, где есть пара, оценка, количество совпадений и несколько примеров.

```python
def compare_profiles(left, right):
    left_ngrams = left["ngrams"]
    right_ngrams = right["ngrams"]
    shared_ngrams = sorted(left_ngrams & right_ngrams)

    return {
        "pair": (left["title"], right["title"]),
        "score": overlap_score(left_ngrams, right_ngrams),
        "shared_count": len(shared_ngrams),
        "examples": shared_ngrams[:3],
    }
```

Если редактор спросит "почему эта пара подозрительная?", поле `examples` покажет несколько совпавших n-грамм.

### Ранжируем все пары

Чтобы сравнить каждый отчет с каждым, подключим `combinations`.

```python
from itertools import combinations
```

Загрузка профилей:

```python
def load_profiles(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    paths = sorted(data_dir.glob("report_*.txt"))
    if not paths:
        raise FileNotFoundError(f"No report_*.txt files found in {data_dir}")

    return [build_profile(path, ngram_size) for path in paths]
```

Рейтинг:

```python
def rank_overlaps(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    profiles = load_profiles(data_dir, ngram_size)
    results = []

    # combinations(..., 2) выдаёт каждую пару один раз и не сравнивает файл с собой.
    for left, right in combinations(profiles, 2):
        result = compare_profiles(left, right)
        if result["shared_count"] > 0:
            results.append(result)

    return sorted(
        results,
        # Кортеж задаёт два ключа: сначала балл, затем число совпадений.
        key=lambda item: (item["score"], item["shared_count"]),
        reverse=True,
    )
```

Сортировка получает ключ из двух значений: сначала оценка, потом количество общих n-грамм. Так пары с одинаковой оценкой будут упорядочены стабильнее.

### Печатаем отчет

[Rich](../../field-guide/rich/) нужен только для вывода. Анализ остается на стандартной библиотеке.

```python
from rich.table import Table
```

```python
def format_ngram(ngram):
    return " ".join(ngram)


def render_results(results, limit=5):
    table = Table(title="Подозрительные совпадения")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Пара")
    table.add_column("Оценка", justify="right")
    table.add_column("Общих n-грамм", justify="right")
    table.add_column("Пример")

    for position, result in enumerate(results[:limit], start=1):
        left, right = result["pair"]
        examples = result["examples"]
        example = format_ngram(examples[0]) if examples else "нет общих n-грамм"
        table.add_row(
            str(position),
            f"{left} / {right}",
            f"{result['score']:.3f}",
            str(result["shared_count"]),
            example,
        )

    console.print(table)
```

В конце `main()` должен запускать рейтинг и печатать таблицу:

```python
def main():
    render_results(rank_overlaps())


if __name__ == "__main__":
    main()
```

Проверка `__name__` запускает `main()` при команде ниже, но не запускает отчет автоматически, если файл импортируют для проверки отдельных функций.

## Проверка

Запустите:

```bash
python copy_paste_detector.py
```

После таблицы запустите тесты из учебного набора:

```bash
python -m unittest discover -s tests
```

Ожидаемая форма результата:

```text
Подозрительные совпадения
1  Опись Северного стола / Черновик экскурсии       0.27  ...
2  Отчет учебного стенда / Отчет охраны              0.18  ...
```

Числа могут немного отличаться, если вы поменяли размер n-граммы или формулу в `overlap_score()`. Важно, чтобы наверху оказались пары с реальными общими фразами, а не любые тексты на похожую тему.

Если таблица пустая, проверьте три места:

- `DATA_DIR` указывает на папку `data`;
- файлы называются `report_*.txt`;
- `make_ngrams()` возвращает кортежи, а не строки.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) - Python 3.13+, виртуальная среда и зависимости.
- [Списки `list`](../../field-guide/list/) - слова и последовательность n-грамм.
- [Словари `dict`](../../field-guide/dict/) - профиль текста и результат сравнения.
- [Множества `set`](../../field-guide/set/) - быстрые пересечения n-грамм.
- [Кортежи `tuple`](../../field-guide/tuple/) - неизменяемые группы соседних слов.
- [Сортировка](../../field-guide/sorting/) - рейтинг пар по подозрительности.
- [Rich](../../field-guide/rich/) - аккуратная таблица без смешивания вывода и анализа.
- [Функции](../../field-guide/functions/) - маленькие проверяемые шаги вместо одного большого скрипта.

## Усложняем проект

1. Добавьте настройку `NGRAM_SIZE` через аргумент командной строки.
2. Показывайте не одну, а три совпавшие n-граммы для каждой пары.
3. Игнорируйте слишком частые служебные слова перед сборкой n-грамм.
4. Сохраняйте рейтинг в CSV для редактора.
5. Добавьте режим сравнения одного нового файла со всей папкой известных отчетов.

Когда закончите, откройте [разбор полного решения](../copy-paste-detector-solution/).
