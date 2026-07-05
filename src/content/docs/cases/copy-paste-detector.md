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
difficulty: "начальный+"
projectId: "case-02"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> найти пары архивных описаний, которые слишком похожи на утечку или подмену.</p>
  <p><strong>Инструменты</strong> кортежи, n-граммы, множества, словари, сортировка, функции и аккуратный отчет в терминале.</p>
  <p><strong>Результат</strong> консольный детектор, который показывает рейтинг подозрительных совпадений.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-02.zip">case-02.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../copy-paste-detector-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/tuple/">tuple</a> · <a href="../../field-guide/set/">set</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/sorting/">sorting</a> · <a href="../../field-guide/rich/">Rich</a></p>
</div>

## Проблема

После анонимной записки редактор просматривает соседние материалы архива. В подборке коротких фрагментов появляется новая странность: два описания закрытых экспонатов почти дословно всплывают в чужих черновиках, хотя эти тексты еще не должны были покинуть рабочую папку.

Вопрос дела: какие пары действительно похожи на копирование или утечку, а какие просто описывают одну тему похожими словами?

Наша задача не "поймать нарушителя", а сделать рабочий инструмент первичной проверки. Программа прочитает несколько фрагментов, сравнит каждую пару и поднимет наверх те пары, где совпадает много соседних слов.

Скачайте архив [case-02.zip](../../downloads/case-02.zip) или откройте папку `projects/case-02/` в репозитории.

В learner-наборе:

- `copy_paste_detector.py` - стартовый файл, который мы будем дорабатывать;
- `requirements.txt` - точная версия Rich для красивой таблицы;
- `data/fragment_*.txt` - безопасные синтетические фрагменты;
- `check_result.txt` - форма ожидаемого результата.

Полное решение вынесено отдельно: [Разбор полного решения](../copy-paste-detector-solution/).

### Подготовка окружения

Нужен Python 3.14 или новее.

Windows PowerShell:

```powershell
cd path\to\case-02
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS или Linux:

```bash
cd path/to/case-02
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Проверьте стартовый файл:

```bash
python copy_paste_detector.py
```

Пока он только загружает материалы и показывает короткую сводку. Дальше мы превратим его в детектор.

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

1. прочитать все `fragment_*.txt`;
2. превратить каждый текст в список нормализованных слов;
3. собрать n-граммы как кортежи;
4. положить n-граммы каждого фрагмента в [`set`](../../field-guide/set/);
5. сравнить каждую пару через пересечение множеств;
6. сохранить результат пары в [`dict`](../../field-guide/dict/);
7. [отсортировать](../../field-guide/sorting/) результаты по убыванию подозрительности.

## Сборка инструмента

Откройте `copy_paste_detector.py`. В начале уже есть `Path`, `Console`, путь к данным и функция чтения файла.

### Нормализуем слова

Нам не нужны запятые, точки и регистр. Сделаем простую функцию: буквы оставляем, все остальное превращаем в пробел. На входе у нее текст, на выходе `list[str]`; если этот шаг пропустить, совпадения будут зависеть от запятых и заглавных букв.

```python
def normalize_words(text: str) -> list[str]:
    cleaned: list[str] = []

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


def make_ngrams(words: list[str], size: int = NGRAM_SIZE) -> list[tuple[str, ...]]:
    if size < 1:
        raise ValueError("N-gram size must be positive")

    ngrams: list[tuple[str, ...]] = []

    for index in range(len(words) - size + 1):
        ngram = tuple(words[index : index + size])
        ngrams.append(ngram)

    return ngrams
```

Тип `tuple[str, ...]` значит "кортеж из строк, длина может быть разной". В нашем проекте длина обычно равна четырем, но запись остается удобной для любого `size`.

### Профиль фрагмента

Для каждого файла соберем небольшой словарь. В нем будет название, количество слов, количество n-грамм и множество самих n-грамм. Такой профиль отделяет чтение текста от сравнения: остальные функции уже не знают, откуда пришел файл.

```python
DISPLAY_NAMES = {
    "fragment_atrium_report": "Опись Северного стола",
    "fragment_greenhouse_note": "Черновик экскурсии",
    "fragment_river_walk": "Карта подвального коридора",
    "fragment_sensor_lab": "Дневник ночного сигнала",
    "fragment_school_blog": "Отчет охраны",
}


def display_name(path: Path) -> str:
    return DISPLAY_NAMES.get(path.stem, path.stem.replace("_", " ").title())
```

Теперь профиль:

```python
def build_profile(path: Path, ngram_size: int = NGRAM_SIZE) -> dict[str, object]:
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

Для пары фрагментов нам нужны две оценки. `overlap_score()` принимает два множества n-грамм и возвращает одно число от `0.0` до `1.0`, чтобы результат можно было сортировать.

Первая - containment: какая доля меньшего текста нашлась в большем. Это полезно, если один фрагмент почти целиком скопирован из длинного.

Вторая - Jaccard: какая доля общих n-грамм есть среди всех n-грамм пары.

```python
Ngram = tuple[str, ...]


def overlap_score(left: set[Ngram], right: set[Ngram]) -> float:
    if not left or not right:
        return 0.0

    shared = left & right
    if not shared:
        return 0.0

    containment = len(shared) / min(len(left), len(right))
    jaccard = len(shared) / len(left | right)
    return round(containment * 0.7 + jaccard * 0.3, 3)
```

`left & right` возвращает n-граммы, которые есть в обоих множествах. `left | right` возвращает все уникальные n-граммы из двух текстов.

### Сравниваем пару профилей

Результат сравнения тоже удобно держать в словаре: это одна запись будущего отчета, где есть пара, оценка, количество совпадений и несколько примеров.

```python
def compare_profiles(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
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

Чтобы сравнить каждый фрагмент с каждым, подключим `combinations`.

```python
from itertools import combinations
```

Загрузка профилей:

```python
def load_profiles(data_dir: Path = DATA_DIR, ngram_size: int = NGRAM_SIZE) -> list[dict[str, object]]:
    paths = sorted(data_dir.glob("fragment_*.txt"))
    if not paths:
        raise FileNotFoundError(f"No fragment_*.txt files found in {data_dir}")

    return [build_profile(path, ngram_size) for path in paths]
```

Рейтинг:

```python
def rank_overlaps(data_dir: Path = DATA_DIR, ngram_size: int = NGRAM_SIZE) -> list[dict[str, object]]:
    profiles = load_profiles(data_dir, ngram_size)
    results: list[dict[str, object]] = []

    for left, right in combinations(profiles, 2):
        result = compare_profiles(left, right)
        if result["shared_count"] > 0:
            results.append(result)

    return sorted(
        results,
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
def format_ngram(ngram: Ngram) -> str:
    return " ".join(ngram)


def render_results(results: list[dict[str, object]], limit: int = 5) -> None:
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
def main() -> None:
    render_results(rank_overlaps())
```

## Проверка

Запустите:

```bash
python copy_paste_detector.py
```

Ожидаемая форма результата:

```text
Подозрительные совпадения
1  Опись Северного стола / Черновик экскурсии       0.45+  ...
2  Отчет охраны / Дневник ночного сигнала           0.30+  ...
```

Числа могут немного отличаться, если вы поменяли размер n-граммы или формулу в `overlap_score()`. Важно, чтобы наверху оказались пары с реальными общими фразами, а не любые тексты на похожую тему.

Если таблица пустая, проверьте три места:

- `DATA_DIR` указывает на папку `data`;
- файлы называются `fragment_*.txt`;
- `make_ngrams()` возвращает кортежи, а не строки.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) - Python 3.14+, виртуальная среда и зависимости.
- [Списки `list`](../../field-guide/list/) - слова и последовательность n-грамм.
- [Словари `dict`](../../field-guide/dict/) - профиль текста и результат сравнения.
- [Множества `set`](../../field-guide/set/) - быстрые пересечения n-грамм.
- [Кортежи `tuple`](../../field-guide/tuple/) - неизменяемые группы соседних слов.
- [Сортировка](../../field-guide/sorting/) - рейтинг пар по подозрительности.
- [Rich](../../field-guide/rich/) - аккуратная таблица без смешивания вывода и анализа.
- Функции - маленькие проверяемые шаги вместо одного большого скрипта.

## Усложняем проект

1. Добавьте настройку `NGRAM_SIZE` через аргумент командной строки.
2. Показывайте не одну, а три совпавшие n-граммы для каждой пары.
3. Игнорируйте слишком частые служебные слова перед сборкой n-грамм.
4. Сохраняйте рейтинг в CSV для редактора.
5. Добавьте режим сравнения одного нового файла со всей папкой известных фрагментов.

Когда закончите, откройте [разбор полного решения](../copy-paste-detector-solution/).
