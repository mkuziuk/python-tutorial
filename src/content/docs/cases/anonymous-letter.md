---
title: "Дело 01. Кто оставил предупреждение?"
description: "Пошагово строим инструмент стилометрии: окружение, regex, профили текста и аккуратный терминальный отчет."
concepts:
  - str
  - list
  - dict
  - set
  - regex
  - Counter
  - Rich
  - functions
difficulty: "начальный+"
projectId: "case-01"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> найти источник предупреждения, чтобы восстановить детали скрытой полуночной правки.</p>
  <p><strong>Инструменты</strong> виртуальная среда, строки, регулярные выражения, словари, множества, `Counter`, Rich.</p>
  <p><strong>Результат</strong> консольный инструмент с понятной таблицей кандидатов.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-01.zip">case-01.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../anonymous-letter-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/str/">str</a> · <a href="../../field-guide/regex/">regex</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/set/">set</a> · <a href="../../field-guide/counter/">Counter</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/rich/">Rich</a></p>
</div>

## Завязка

В небольшой редакции готовят публичный показ оцифрованного архива. Ночью перед контрольной сверкой в общей папке появляется файл `anonymous.txt`. В нем нет угроз и громких обвинений, но есть холодное предупреждение: часть черновиков уже тронули, а следующая подмена будет выглядеть как обычная ошибка.

В команде три человека, которые часто работают с архивом: Алина Морозова, Илья Соколов и Никита Королев. У каждого есть два известных рабочих текстовых фрагмента. Вопрос дела не в том, кого обвинить. Нужно понять, кто оставил предупреждение: этот человек может знать, какой файл изменили, когда это случилось и где след исчезнет первым.

Наша задача - построить инструмент первичной проверки. Он достанет слова, посчитает привычки письма и покажет, с кем команда должна поговорить в первую очередь.

## Материалы дела

Скачайте архив [case-01.zip](../../downloads/case-01.zip) или откройте папку `projects/case-01/` в репозитории.

Внутри learner-набора:

- `anonymous_letter.py` - пустой стартовый файл, который мы будем наращивать;
- `requirements.txt` - внешняя библиотека для красивого отчета;
- `data/anonymous.txt` - анонимная записка;
- `data/author_morozova.txt`, `data/author_sokolov.txt`, `data/author_korolev.txt` - образцы кандидатов;
- `check_result.txt` - форма ожидаемого результата.

Полное решение вынесено отдельно: [Разбор полного решения](../anonymous-letter-solution/).

## Подготовка окружения

Перед проектом создадим виртуальную среду. Это отдельная папка с Python и библиотеками только для этого дела. Так мы не ломаем системный Python и не смешиваем зависимости разных проектов.

### Windows PowerShell

```powershell
cd path\to\case-01
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Если PowerShell не разрешает запуск `Activate.ps1`, выполните в этом же окне:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS или Linux

```bash
cd path/to/case-01
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Что здесь происходит:

- `venv` создает изолированное окружение;
- `pip` устанавливает библиотеки в это окружение;
- `requirements.txt` фиксирует точную версию зависимости;
- `rich==15.0.0` нужен только для красивой таблицы в терминале.

Проверьте пустой стартовый файл:

```bash
python anonymous_letter.py
```

Он пока ничего не выводит: это нормально. Откройте `anonymous_letter.py` и начните с путей, консоли и чтения текста:

```python
from pathlib import Path

from rich.console import Console

DATA_DIR = Path(__file__).with_name("data")
console = Console()


def read_text(path):
    return path.read_text(encoding="utf-8")
```

Дальше мы превратим пустой файл в инструмент.

## Стратегия

Мы не будем пытаться "почувствовать стиль". Программа измерит признаки и сложит их в обычные структуры Python: [списки](../../field-guide/list/), [словари](../../field-guide/dict/), [множества](../../field-guide/set/) и [`Counter`](../../field-guide/counter/).

1. список слов;
2. количество уникальных слов;
3. среднюю длину слова;
4. частые слова;
5. привычки пунктуации;
6. похожесть анонимного текста на каждый образец.

Профиль текста будет обычным [словарем](../../field-guide/dict/): ключи называют признаки, а значения хранят числа, частоты и счетчики.

```python
profile = {
    "name": "Алина Морозова",
    "word_count": 78,
    "unique_words": 59,
    "average_word_length": 5.62,
    "common_words": [("след", 2), ("пауза", 2)],
    "punctuation": Counter({".": 7, ",": 5}),
}
```

## Почему не `.split()`

Наивный способ достать слова выглядит так:

```python
text = "След есть. След рядом!"
print(text.lower().split())
```

Результат:

```text
['след', 'есть.', 'след', 'рядом!']
```

Точки и восклицательные знаки остались приклеенными к словам. Для подсчета частот это плохо: `есть` и `есть.` станут разными словами.

## Маленькое введение в regex

[Регулярное выражение](../../field-guide/regex/) - это шаблон для поиска фрагментов текста. Нам нужен шаблон "найди подряд идущие русские буквы".

```python
import re

WORD_RE = re.compile(r"[а-яё]+", re.IGNORECASE)
```

Разберем по частям:

- `r"..."` - raw string: Python не пытается заранее обработать обратные слеши;
- `[а-яё]` - один символ из диапазона русских букв, включая `ё`;
- `+` - один или больше таких символов подряд;
- `re.IGNORECASE` - не различать строчные и заглавные буквы.

Теперь можно получить слова чище:

```python
def normalize_words(text):
    return WORD_RE.findall(text.lower())
```

Добавьте `import re`, `WORD_RE` и функцию `normalize_words()` в `anonymous_letter.py`. Эта функция получает одну [строку](../../field-guide/str/) и возвращает список слов: дальше весь анализ работает уже не с исходным текстом, а с чистыми словами. Если оставить пунктуацию внутри слов, `Counter` будет считать `след` и `след.` разными признаками.

## Профиль текста

Теперь добавим частоты и пунктуацию.

```python
from collections import Counter

PUNCTUATION = ".,;:!?"


def punctuation_profile(text):
    return Counter(char for char in text if char in PUNCTUATION)
```

Функция [`Counter`](../../field-guide/counter/) похожа на словарь, но специально создана для подсчета. В `punctuation_profile()` она превращает поток символов в карту "знак -> сколько раз встретился".

```python
def build_profile(name, text):
    words = normalize_words(text)
    if not words:
        raise ValueError(f"Text for {name!r} does not contain Russian words")

    total_letters = sum(len(word) for word in words)
    return {
        "name": name,
        "word_count": len(words),
        "unique_words": len(set(words)),
        "average_word_length": total_letters / len(words),
        "common_words": Counter(words).most_common(12),
        "punctuation": punctuation_profile(text),
    }
```

`build_profile()` - центральная функция подготовки данных: на входе имя и текст, на выходе один профиль, который удобно сравнивать с другими профилями. Здесь появляются главные структуры данных дела:

- `list` хранит слова в порядке появления;
- `set(words)` оставляет только уникальные слова;
- `dict` собирает разные признаки в один профиль;
- `Counter` считает слова и знаки.

## Сравнение профилей

Частые слова сравним через пересечение [множеств](../../field-guide/set/). Это дешевый способ спросить: "какие признаки есть у обоих текстов?"

```python
def jaccard(left, right):
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)
```

`left & right` - что есть в обоих множествах. `left | right` - все элементы из обоих множеств.

Пунктуацию сравним по долям: если один автор ставит много запятых, а другой почти не ставит, расстояние увеличится.

```python
def punctuation_similarity(left, right):
    left_total = sum(left.values()) or 1
    right_total = sum(right.values()) or 1
    distance = 0.0

    for mark in PUNCTUATION:
        distance += abs((left[mark] / left_total) - (right[mark] / right_total))

    return max(0.0, 1.0 - distance / 2)
```

Общая оценка будет смесью трех сигналов:

```python
def compare_profiles(anonymous, candidate):
    anonymous_words = {word for word, _ in anonymous["common_words"]}
    candidate_words = {word for word, _ in candidate["common_words"]}
    word_overlap = jaccard(anonymous_words, candidate_words)

    average_delta = abs(
        float(anonymous["average_word_length"]) - float(candidate["average_word_length"])
    )
    length_score = max(0.0, 1.0 - average_delta / 3)

    punctuation_score = punctuation_similarity(
        anonymous["punctuation"],
        candidate["punctuation"],
    )

    return round(word_overlap * 0.45 + length_score * 0.25 + punctuation_score * 0.30, 3)
```

Эти веса не священные. Это первая рабочая версия прибора: вклад каждого признака виден прямо в формуле, поэтому ученик может менять числа и наблюдать, как меняется рейтинг.

## Загрузка кандидатов

Добавим имена и чтение файлов. `rank_candidates()` отвечает только за порядок работы: загрузить анонимное письмо, построить профиль каждого кандидата, сравнить и вернуть список пар `(имя, оценка)`.

```python
AUTHOR_NAMES = {
    "author_morozova": "Алина Морозова",
    "author_sokolov": "Илья Соколов",
    "author_korolev": "Никита Королев",
}


def display_name(path):
    return AUTHOR_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def rank_candidates(data_dir=DATA_DIR):
    anonymous = build_profile("Анонимное письмо", read_text(data_dir / "anonymous.txt"))
    results = []

    for path in sorted(data_dir.glob("author_*.txt")):
        profile = build_profile(display_name(path), read_text(path))
        results.append((str(profile["name"]), compare_profiles(anonymous, profile)))

    return sorted(results, key=lambda item: item[1], reverse=True)
```

## Отчет с Rich

Библиотека [Rich](../../field-guide/rich/) не участвует в анализе. Она только делает вывод читаемым: если убрать `render_results()`, ранжирование кандидатов продолжит работать.

```python
from rich.table import Table


def render_results(results):
    table = Table(title="Вероятные авторы")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Кандидат")
    table.add_column("Сходство", justify="right")

    for position, (name, score) in enumerate(results, start=1):
        table.add_row(str(position), name, f"{score:.2f}")

    console.print(table)
    winner, score = results[0]
    console.print(
        f"\n[bold]Главная версия:[/bold] {winner} "
        f"([cyan]{score:.2f}[/cyan]). Это повод проверить текст вручную, а не окончательный приговор."
    )
```

В конце `main()` должен запускать ранжирование и печатать отчет:

```python
def main():
    render_results(rank_candidates())
```

## Запуск

```bash
python anonymous_letter.py
```

Ожидаемая форма результата:

```text
Вероятные авторы
1  Алина Морозова  0.69
2  Никита Королев  0.53
3  Илья Соколов    0.40
```

Если первым стоит Алина Морозова, инструмент работает как задумано. Если числа немного отличаются, проверьте веса в `compare_profiles()`.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) - современная версия Python 3, виртуальная среда и установка зависимостей.
- [Строки `str`](../../field-guide/str/) - исходный текст и нормализация.
- [Regex](../../field-guide/regex/) - поиск русских слов без приклеенной пунктуации.
- [Списки `list`](../../field-guide/list/) - последовательность найденных слов.
- [Словари `dict`](../../field-guide/dict/) - профиль текста как набор признаков.
- [Множества `set`](../../field-guide/set/) - уникальные слова и пересечение признаков.
- [Counter](../../field-guide/counter/) - частоты слов и пунктуации.
- [Rich](../../field-guide/rich/) - читаемая таблица результата.
- [Функции](../../field-guide/functions/) - отдельные проверяемые шаги: нормализация, профиль, сравнение и отчет.

## Усложняем проект

1. Добавьте n-граммы: сравнивайте не отдельные слова, а пары соседних слов.
2. Считайте любимые первые слова предложений.
3. Добавьте стоп-слова и проверьте, меняется ли победитель.
4. Сохраните отчет в JSON.
5. Сделайте класс `AuthorProfile`, чтобы подготовиться к большему делу про систему расследований.

Когда закончите, откройте [разбор полного решения](../anonymous-letter-solution/).
