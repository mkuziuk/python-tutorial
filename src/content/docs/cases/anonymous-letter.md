---
title: "Дело 01. Кто оставил предупреждение?"
description: "Пошагово строим инструмент стилометрии: окружение, regex, профили текста и понятный отчёт в терминале."
concepts:
  - str
  - list
  - dict
  - set
  - regex
  - Counter
  - Rich
  - functions
  - ветвления и циклы
  - comprehensions
  - работа с файлами
  - unittest
difficulty: "начальный+"
projectId: "case-01"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> найти источник предупреждения, чтобы восстановить детали скрытой полуночной правки.</p>
  <p><strong>Инструменты</strong> виртуальная среда, строки, регулярные выражения, словари, множества, `Counter`, Rich.</p>
  <p><strong>Результат</strong> консольный инструмент с понятной таблицей кандидатов.</p>
  <p><strong>Маршрут</strong> начальный+ · 90–120 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-01.zip">case-01.zip</a> · <a href="../../materials/">материалы всех дел</a> · <a href="../anonymous-letter-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/control-flow/">условия и циклы</a> · <a href="../../field-guide/str/">str</a> · <a href="../../field-guide/regex/">regex</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/set/">set</a> · <a href="../../field-guide/counter/">Counter</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/comprehensions/">включения</a> · <a href="../../field-guide/file-io/">файлы</a> · <a href="../../field-guide/rich/">Rich</a> · <a href="../../field-guide/testing/">unittest</a></p>
</div>

## Завязка

В небольшой редакции готовят публичный показ оцифрованного архива. Ночью перед контрольной сверкой в общей папке появляется файл `anonymous.txt`. В нем нет угроз и громких обвинений, но есть холодное предупреждение: часть черновиков уже тронули, а следующая подмена будет выглядеть как обычная ошибка.

В команде три человека, которые часто работают с архивом: Алина Морозова, Илья Соколов и Никита Королев. У каждого есть два известных рабочих текстовых фрагмента. Вопрос дела не в том, кого обвинить. Нужно понять, кто оставил предупреждение: этот человек может знать, какой файл изменили, когда это случилось и где след исчезнет первым.

Наша задача — построить инструмент первичной проверки. Он выделит слова, измерит особенности письма и подскажет, с кем команде стоит поговорить в первую очередь.

## Материалы дела

Скачайте архив [case-01.zip](../../downloads/case-01.zip) или откройте папку `projects/case-01/` в репозитории.

В учебном наборе:

- `anonymous_letter.py` — пустой стартовый файл;
- `requirements.txt` — внешняя библиотека для удобного чтения отчёта;
- `data/anonymous.txt` — анонимная записка;
- `data/author_morozova.txt`, `data/author_sokolov.txt`, `data/author_korolev.txt` — образцы текстов кандидатов;
- `check_result.txt` — форма ожидаемого результата.

Полное решение вынесено отдельно: [Разбор полного решения](../anonymous-letter-solution/).

## Подготовка окружения

Перед началом создайте виртуальную среду — отдельную папку с Python и библиотеками только для этого дела. Так зависимости проекта не смешаются с системным Python и другими проектами. Нужен Python 3.13 или новее; проверьте версию командой `py -3 --version` в Windows или `python3 --version` в macOS и Linux.

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

- `venv` создаёт изолированное окружение;
- `pip` устанавливает библиотеки в это окружение;
- `requirements.txt` фиксирует точную версию зависимости;
- `rich==15.0.0` нужен только для красивой таблицы в терминале.

Запустите стартовый файл:

```bash
python anonymous_letter.py
```

Пока программа ничего не выводит: это нормально. Откройте `anonymous_letter.py` и начните с путей, консоли и чтения текста:

```python
# Собирайте программу по шагам и после каждого этапа запускайте указанную проверку.
# Сначала добейтесь правильной обработки одного текста, затем переходите к сравнению.
# Промежуточный вывод поможет заметить шаг, на котором результат начал расходиться.
from collections import Counter
from pathlib import Path

from rich.console import Console

# Путь считаем от самого скрипта: запуск из другой папки не должен менять набор данных.
DATA_DIR = Path(__file__).with_name("data")
# Один объект Console переиспользуем во всём уроке, чтобы вывод оставался единообразным.
console = Console()


def read_text(path):
    # Явная UTF-8 кодировка делает чтение одинаковым на Windows, macOS и Linux.
    return path.read_text(encoding="utf-8")
```

Дальше мы шаг за шагом соберём инструмент.

## Стратегия

Мы не будем пытаться «почувствовать стиль». Программа измерит признаки и сохранит их в обычных структурах Python: [списках](../../field-guide/list/), [словарях](../../field-guide/dict/), [множествах](../../field-guide/set/) и [`Counter`](../../field-guide/counter/).

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
    # word_count — количество слов с повторами, unique_words — без повторов.
    "word_count": 78,
    "unique_words": 59,
    # Средняя длина измеряется в буквах на слово, а не в символах исходного текста.
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

Точки и восклицательные знаки остались приклеенными к словам. Для подсчёта частот это плохо: `есть` и `есть.` станут разными словами.

## Маленькое введение в regex

[Регулярное выражение](../../field-guide/regex/) — это шаблон для поиска фрагментов текста. Здесь нужен шаблон «найди подряд идущие русские буквы».

```python
import re

# Шаблон выделяет только цепочки русских букв, включая «ё».
# Компилируем его один раз: одна и та же граница слова применяется ко всем текстам.
WORD_RE = re.compile(r"[а-яё]+", re.IGNORECASE)
```

Разберем по частям:

- `r"..."` — необработанная строка (raw string): Python не пытается заранее обработать обратные слеши;
- `[а-яё]` — один символ из диапазона русских букв, включая `ё`;
- `+` — один или больше таких символов подряд;
- `re.IGNORECASE` — не различать строчные и заглавные буквы.

Теперь можно получить слова чище:

```python
def normalize_words(text):
    # Список сохраняет повторы: они нужны и для частот, и для средней длины слов.
    return WORD_RE.findall(text.lower())
```

Добавьте `import re`, `WORD_RE` и функцию `normalize_words()` в `anonymous_letter.py`. Эта функция получает одну [строку](../../field-guide/str/) и возвращает список слов: дальше весь анализ работает уже не с исходным текстом, а с чистыми словами. Если оставить пунктуацию внутри слов, `Counter` будет считать `след` и `след.` разными признаками.

## Профиль текста

Теперь добавим частоты и пунктуацию.

```python
PUNCTUATION = ".,;:!?"


def punctuation_profile(text):
    # Counter получает только нужные знаки и сам подсчитывает их частоты.
    # Считаем абсолютные количества здесь; к долям перейдём только при сравнении профилей.
    return Counter(char for char in text if char in PUNCTUATION)
```

Функция [`Counter`](../../field-guide/counter/) похожа на словарь, но предназначена именно для подсчёта. В `punctuation_profile()` она превращает поток символов в соответствие «знак → количество вхождений».

```python
def build_profile(name, text):
    words = normalize_words(text)
    # Останавливаемся до деления: у пустого текста нельзя определить среднюю длину слова.
    if not words:
        raise ValueError(f"Text for {name!r} does not contain Russian words")

    # Длину измеряем в буквах, поэтому пробелы и знаки препинания в среднее не попадают.
    total_letters = sum(len(word) for word in words)
    # Берём 12 самых частых слов, чтобы единичная редкая лексика не влияла сильнее устойчивых привычек.
    return {
        "name": name,
        "word_count": len(words),
        "unique_words": len(set(words)),
        "average_word_length": total_letters / len(words),
        "common_words": Counter(words).most_common(12),
        "punctuation": punctuation_profile(text),
    }
```

`build_profile()` — центральная функция подготовки данных. Она получает имя и текст, а возвращает профиль, который удобно сравнивать с другими. Здесь появляются главные структуры данных дела:

- `list` хранит слова в порядке появления;
- `set(words)` оставляет только уникальные слова;
- `dict` собирает разные признаки в один профиль;
- `Counter` считает слова и знаки.

## Сравнение профилей

Частые слова сравним через пересечение [множеств](../../field-guide/set/). Это простой способ ответить на вопрос: «Какие признаки есть у обоих текстов?»

```python
def jaccard(left, right):
    # Если признака нет в обоих текстах, считаем отсутствие полным совпадением, а не ошибкой.
    if not left and not right:
        return 1.0
    # «&» даёт общие слова, а «|» — все слова из обоих множеств.
    return len(left & right) / len(left | right)
```

`left & right` возвращает элементы из обоих множеств, а `left | right` — все элементы двух множеств.

Пунктуацию сравним по долям: если один автор ставит много запятых, а другой почти не ставит, расстояние увеличится.

```python
def punctuation_similarity(left, right):
    # Единица защищает от деления на ноль, а / 2 приводит результат к диапазону 0–1.
    # Нормируем на объём каждого текста, чтобы длинный текст не получал преимущество автоматически.
    left_total = sum(left.values()) or 1
    right_total = sum(right.values()) or 1
    distance = 0.0

    # Перебираем фиксированный алфавит знаков, поэтому отсутствующий знак Counter вернёт как ноль.
    for mark in PUNCTUATION:
        distance += abs((left[mark] / left_total) - (right[mark] / right_total))

    return max(0.0, 1.0 - distance / 2)
```

Общая оценка будет смесью трёх сигналов:

```python
def compare_profiles(anonymous, candidate):
    # В формулу входит состав частых слов; количества использовались только при отборе двенадцати.
    anonymous_words = {word for word, _ in anonymous["common_words"]}
    candidate_words = {word for word, _ in candidate["common_words"]}
    word_overlap = jaccard(anonymous_words, candidate_words)

    # average_delta измеряется в буквах на слово и сравнивает одинаково определённые признаки.
    average_delta = abs(
        float(anonymous["average_word_length"]) - float(candidate["average_word_length"])
    )
    # Если средняя длина слова отличается на три буквы или больше, length_score равен 0.
    length_score = max(0.0, 1.0 - average_delta / 3)

    punctuation_score = punctuation_similarity(
        anonymous["punctuation"],
        candidate["punctuation"],
    )

    # Веса складываются в 1: это эвристика сходства, а не вероятность авторства.
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
    # Словарь даёт читабельные имена, а запасной вариант позволяет добавить новый файл без правки кода.
    return AUTHOR_NAMES.get(path.stem, path.stem.replace("_", " ").title())


def rank_candidates(data_dir=DATA_DIR):
    # Профиль анонимного текста строим один раз и используем при сравнении со всеми авторами.
    anonymous = build_profile("Анонимное письмо", read_text(data_dir / "anonymous.txt"))
    results = []

    # Шаблон не захватывает anonymous.txt, а сортировка фиксирует порядок обхода.
    for path in sorted(data_dir.glob("author_*.txt")):
        profile = build_profile(display_name(path), read_text(path))
        # После сравнения полные профили больше не нужны, поэтому сохраняем только имя и итоговый балл.
        results.append((str(profile["name"]), compare_profiles(anonymous, profile)))

    # sorted() стабилен: при равных баллах сохранится зафиксированный выше порядок файлов.
    return sorted(results, key=lambda item: item[1], reverse=True)
```

## Отчёт с Rich

Библиотека [Rich](../../field-guide/rich/) не участвует в анализе. Она только делает вывод читаемым: если убрать `render_results()`, ранжирование кандидатов продолжит работать.

```python
from rich.table import Table


def render_results(results):
    # Отрисовка отделена от расчёта: тесты проверяют результаты без захвата терминала.
    table = Table(title="Вероятные авторы")
    table.add_column("Место", justify="right", style="cyan")
    table.add_column("Кандидат")
    table.add_column("Сходство", justify="right")

    # Нумерация начинается с единицы, потому что это место в пользовательском рейтинге.
    for position, (name, score) in enumerate(results, start=1):
        table.add_row(str(position), name, f"{score:.2f}")

    console.print(table)
    # Хотя бы один кандидат — контракт учебного набора; иначе здесь нужен отдельный пустой отчёт.
    winner, score = results[0]
    console.print(
        f"\n[bold]Главная версия:[/bold] {winner} "
        f"([cyan]{score:.2f}[/cyan]). Это повод проверить текст вручную, а не окончательный приговор."
    )
```

В конце `main()` должен запускать ранжирование и печатать отчёт:

```python
def main():
    # main связывает расчёт и вывод, не пряча дополнительную обработку между ними.
    render_results(rank_candidates())


if __name__ == "__main__":
    main()
```

Последние две строки — точка входа: без них Python определит `main()`, но не вызовет его при запуске файла.

## Запуск

```bash
python anonymous_letter.py
```

Затем запустите тесты из учебного набора:

```bash
python -m unittest discover -s tests
```

В скачанном ZIP тесты проверяют собранный вами корневой скрипт.

Ожидаемая форма результата:

```text
Вероятные авторы
1  Алина Морозова  0.69
2  Никита Королев  0.53
3  Илья Соколов    0.40
```

Если первым стоит Алина Морозова, инструмент работает как задумано. Если числа немного отличаются, проверьте веса в `compare_profiles()`.

## Что мы использовали

- [Установка Python](../../field-guide/install-python/) — Python 3.13+, виртуальная среда и установка зависимостей.
- [Строки `str`](../../field-guide/str/) — исходный текст и нормализация.
- [Regex](../../field-guide/regex/) — поиск русских слов без присоединённой пунктуации.
- [Списки `list`](../../field-guide/list/) — последовательность найденных слов.
- [Словари `dict`](../../field-guide/dict/) — профиль текста как набор признаков.
- [Множества `set`](../../field-guide/set/) — уникальные слова и пересечение признаков.
- [Counter](../../field-guide/counter/) — частоты слов и пунктуации.
- [Rich](../../field-guide/rich/) — читаемая таблица результата.
- [Функции](../../field-guide/functions/) — отдельные проверяемые шаги: нормализация, профиль, сравнение и отчёт.

## Усложняем проект

1. Добавьте n-граммы: сравнивайте не отдельные слова, а пары соседних слов.
2. Считайте любимые первые слова предложений.
3. Добавьте стоп-слова и проверьте, меняется ли победитель.
4. Сохраните отчёт в JSON.
5. Сделайте класс `AuthorProfile`, чтобы подготовиться к большему делу про систему расследований.

Когда закончите, откройте [разбор полного решения](../anonymous-letter-solution/).
