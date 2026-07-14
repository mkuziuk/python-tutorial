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
  - ветвления и циклы
  - comprehensions
  - unittest
difficulty: "начальный+"
projectId: "case-02"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> найти пары архивных описаний с одинаковыми последовательностями слов и составить рейтинг по степени совпадения n-грамм.</p>
  <p><strong>Инструменты</strong> кортежи, n-граммы, множества, словари, сортировка, функции и понятный отчёт в терминале.</p>
  <p><strong>Результат</strong> консольный детектор, который показывает рейтинг подозрительных совпадений.</p>
  <p><strong>Маршрут</strong> начальный+ · 90–120 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-02.zip">case-02.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../copy-paste-detector-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/control-flow/">условия и циклы</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/tuple/">tuple</a> · <a href="../../field-guide/set/">set</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/sorting/">sorting</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/comprehensions/">включения</a> · <a href="../../field-guide/rich/">Rich</a> · <a href="../../field-guide/testing/">unittest</a></p>
</div>

## Проблема

После анонимной записки редактор просматривает соседние материалы архива. В черновике экскурсии почти дословно повторяются фрагменты закрытой описи, хотя эта опись ещё не должна была покинуть рабочую папку. Ещё одна пара отчётов тоже подозрительно похожа, но относится к учебному стенду: инструменту предстоит отделить возможную утечку от обычного повторного использования текста.

Вопрос дела: какие пары действительно похожи на копирование или утечку, а какие просто описывают одну тему похожими словами?

Наша задача — не «поймать нарушителя», а создать рабочий инструмент первичной проверки. Программа прочитает несколько отчётов, сравнит каждую пару и поставит выше пары с большим количеством совпадающих последовательностей слов.

Скачайте архив [case-02.zip](../../downloads/case-02.zip) или откройте папку `projects/case-02/` в репозитории.

В учебном наборе:

- `copy_paste_detector.py` — пустой стартовый файл;
- `requirements.txt` — точная версия Rich для удобной таблицы;
- `data/report_*.txt` — полные отчёты из архива;
- `check_result.txt` — форма ожидаемого результата.

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

Запустите стартовый файл:

```bash
python copy_paste_detector.py
```

Пока программа ничего не выводит: это только заготовка. Дальше мы шаг за шагом соберём детектор.

## Стратегия

Один общий абзац ещё не доказывает заимствование: в текстах одной темы часто встречаются одинаковые слова. Поэтому будем сравнивать не отдельные слова, а соседние группы слов.

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
4. положить n-граммы каждого отчёта в [`set`](../../field-guide/set/);
5. сравнить каждую пару через пересечение множеств;
6. сохранить результат пары в [`dict`](../../field-guide/dict/);
7. [отсортировать](../../field-guide/sorting/) результаты по убыванию подозрительности.

## Сборка инструмента

Откройте `copy_paste_detector.py`. Сначала добавьте путь к данным, размер n-граммы и консоль:

```python
from pathlib import Path

from rich.console import Console

# Путь строится от файла скрипта и не зависит от текущей папки терминала.
DATA_DIR = Path(__file__).with_name("data")
# Четыре слова — выбранная для дела чувствительность, а не универсальный стандарт плагиата.
NGRAM_SIZE = 4
# В отчёт попадут только несколько примеров; сама оценка использует все совпадения.
TOP_EXAMPLES = 3
console = Console()
```

Сначала добавьте чтение файла:

```python
def read_text(path):
    # Явная кодировка исключает зависимость результата от настроек операционной системы.
    return path.read_text(encoding="utf-8")
```

### Нормализуем слова

Запятые, точки и регистр здесь не нужны. Оставим буквы, а остальные символы заменим пробелами. Функция получает текст и возвращает список слов; без этого шага совпадения зависели бы от пунктуации и заглавных букв.

```python
def normalize_words(text):
    cleaned = []

    # Заменяем разделители пробелами, чтобы слова по обе стороны знака не склеились.
    for char in text.lower():
        # isalpha() принимает буквы разных алфавитов; для этого набора это осознанная граница нормализации.
        if char.isalpha():
            cleaned.append(char)
        else:
            cleaned.append(" ")

    return "".join(cleaned).split()
```

`isalpha()` работает и с русскими буквами. `"".join(cleaned)` собирает очищенную строку, а `.split()` делит её на слова.

### Собираем n-граммы

Теперь нужна функция, которая двигает окно размера `size` по списку слов. Она возвращает список кортежей, потому что дальше эти кортежи можно положить во множество и быстро сравнивать.

```python
NGRAM_SIZE = 4


def make_ngrams(words, size=NGRAM_SIZE):
    # Проверяем параметр сразу, чтобы отрицательный диапазон не выглядел как корректный пустой результат.
    if size < 1:
        raise ValueError("N-gram size must be positive")

    # Если слов меньше size, цикл не выполнится и функция честно вернёт пустой список.
    ngrams = []

    # Последнее окно начинается в len(words) - size; +1 включает эту позицию.
    for index in range(len(words) - size + 1):
        ngram = tuple(words[index : index + size])
        ngrams.append(ngram)

    return ngrams
```

Кортеж хранит соседние слова в фиксированном порядке. В нашем проекте длина обычно равна четырём, но функция работает с любым допустимым `size`.

### Профиль отчёта

Для каждого файла соберём небольшой словарь: название, количество слов и n-грамм, а также множество самих n-грамм. Такой профиль отделяет чтение текста от сравнения: остальным функциям уже не важно, откуда получен файл.

```python
DISPLAY_NAMES = {
    "report_north_table": "Опись Северного стола",
    "report_tour_draft": "Черновик экскурсии",
    "report_basement_route": "Служебный маршрут подвального коридора",
    "report_alarm_stand": "Отчёт учебного стенда",
    "report_guard_note": "Отчёт охраны",
}


def display_name(path):
    # Словарь улучшает подписи известных файлов, а fallback не ломает работу с новым отчётом.
    return DISPLAY_NAMES.get(path.stem, path.stem.replace("_", " ").title())
```

Теперь профиль:

```python
def build_profile(path, ngram_size=NGRAM_SIZE):
    text = read_text(path)
    words = normalize_words(text)
    # set хранит каждую уникальную n-грамму один раз.
    ngrams = set(make_ngrams(words, ngram_size))

    return {
        "path": path,
        "title": display_name(path),
        "word_count": len(words),
        # Это число уникальных фрагментов: повтор одной фразы внутри отчёта не увеличивает счётчик.
        "ngram_count": len(ngrams),
        "ngrams": ngrams,
    }
```

Здесь `set(...)` важен: множество хранит только уникальные n-граммы и умеет быстро находить пересечения.

### Считаем подозрительность

Для пары отчётов нужны две оценки. `overlap_score()` принимает два множества n-грамм и возвращает число от `0.0` до `1.0`, пригодное для сортировки.

Первая — доля вхождения (containment): какая часть меньшего текста нашлась в большем. Эта оценка помогает заметить, что один отчёт почти целиком повторяет часть более длинного.

Вторая — коэффициент Жаккара (Jaccard): доля общих n-грамм среди всех n-грамм пары.

```python


def overlap_score(left, right):
    # При пустом множестве сходство равно 0.
    if not left or not right:
        return 0.0

    # Пересечение множеств оставляет только фрагменты, которые встретились в обоих отчётах.
    shared = left & right
    if not shared:
        return 0.0

    # containment измеряет долю n-грамм меньшего текста, найденных в другом тексте.
    # Jaccard снижает оценку, если в текстах много несовпадающих n-грамм.
    # shared не может быть больше меньшего множества, поэтому containment всегда лежит в диапазоне 0–1.
    containment = len(shared) / min(len(left), len(right))
    # Jaccard симметрично штрафует лишние фрагменты в обоих текстах.
    jaccard = len(shared) / len(left | right)
    # Округляем score; при равном score пары дополнительно сортируются по shared_count.
    return round(containment * 0.7 + jaccard * 0.3, 3)
```

`left & right` возвращает n-граммы, которые есть в обоих множествах. `left | right` возвращает все уникальные n-граммы из двух текстов.

### Сравниваем пару профилей

Результат сравнения тоже удобно хранить в словаре: одна запись будущего отчёта содержит пару, оценку, количество совпадений и несколько примеров.

```python
def compare_profiles(left, right):
    # compare_profiles() сравнивает множества n-грамм из готовых профилей.
    left_ngrams = left["ngrams"]
    right_ngrams = right["ngrams"]
    # Сортировка делает примеры воспроизводимыми при любом порядке элементов множества.
    shared_ngrams = sorted(left_ngrams & right_ngrams)

    # Результат пары хранит и оценку, и данные для объяснения этой оценки в таблице.
    return {
        "pair": (left["title"], right["title"]),
        "score": overlap_score(left_ngrams, right_ngrams),
        "shared_count": len(shared_ngrams),
        # examples содержит первые три n-граммы после сортировки.
        "examples": shared_ngrams[:3],
    }
```

Если редактор спросит: «Почему эта пара подозрительна?», поле `examples` покажет несколько совпавших n-грамм.

### Ранжируем все пары

Чтобы сравнить каждый отчёт со всеми остальными, подключим `combinations`.

```python
from itertools import combinations
```

Загрузка профилей:

```python
def load_profiles(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    # glob("report_*.txt") выбирает только файлы отчётов и исключает остальные txt-файлы.
    paths = sorted(data_dir.glob("report_*.txt"))
    if not paths:
        raise FileNotFoundError(f"No report_*.txt files found in {data_dir}")

    return [build_profile(path, ngram_size) for path in paths]
```

Рейтинг:

```python
def rank_overlaps(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    # Каждый файл нормализуем один раз, а затем переиспользуем профиль во всех попарных сравнениях.
    profiles = load_profiles(data_dir, ngram_size)
    results = []

    # combinations(profiles, 2) создаёт каждую неупорядоченную пару один раз.
    for left, right in combinations(profiles, 2):
        result = compare_profiles(left, right)
        # Пары без общих n-грамм не добавляем в отчёт.
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

### Печатаем отчёт

[Rich](../../field-guide/rich/) нужен только для вывода. Анализ остаётся на стандартной библиотеке.

```python
from rich.table import Table
```

```python
def format_ngram(ngram):
    # N-грамма хранится как кортеж слов; join() объединяет их в строку для вывода.
    return " ".join(ngram)


def render_results(results, limit=5):
    table = Table(title="Подозрительные совпадения")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Пара")
    table.add_column("Оценка", justify="right")
    table.add_column("Общих n-грамм", justify="right")
    table.add_column("Пример")

    # render_results() показывает первые limit элементов полного списка results.
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
    # render_results() форматирует уже отсортированный список results.
    render_results(rank_overlaps())


if __name__ == "__main__":
    main()
```

Проверка `__name__` запускает `main()` по команде ниже, но не запускает отчёт автоматически при импорте файла для проверки отдельных функций.

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
2  Отчёт учебного стенда / Отчёт охраны              0.18  ...
```

Числа могут немного отличаться, если вы поменяли размер n-граммы или формулу в `overlap_score()`. Важно, чтобы наверху оказались пары с реальными общими фразами, а не любые тексты на похожую тему.

Если таблица пустая, проверьте три места:

- `DATA_DIR` указывает на папку `data`;
- файлы называются `report_*.txt`;
- `make_ngrams()` возвращает кортежи, а не строки.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) — Python 3.13+, виртуальная среда и зависимости.
- [Списки `list`](../../field-guide/list/) — слова и последовательность n-грамм.
- [Словари `dict`](../../field-guide/dict/) — профиль текста и результат сравнения.
- [Множества `set`](../../field-guide/set/) — быстрые пересечения n-грамм.
- [Кортежи `tuple`](../../field-guide/tuple/) — неизменяемые группы соседних слов.
- [Сортировка](../../field-guide/sorting/) — рейтинг пар по подозрительности.
- [Rich](../../field-guide/rich/) — аккуратная таблица без смешивания вывода и анализа.
- [Функции](../../field-guide/functions/) — небольшие проверяемые шаги вместо одного большого скрипта.

## Усложняем проект

1. Добавьте настройку `NGRAM_SIZE` через аргумент командной строки.
2. Показывайте не одну, а три совпавшие n-граммы для каждой пары.
3. Игнорируйте слишком частые служебные слова перед сборкой n-грамм.
4. Сохраняйте рейтинг в CSV для редактора.
5. Добавьте режим сравнения одного нового файла со всей папкой известных отчётов.

Когда закончите, откройте [разбор полного решения](../copy-paste-detector-solution/).
