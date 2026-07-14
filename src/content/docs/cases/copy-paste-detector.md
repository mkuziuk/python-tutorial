---
title: "Расследование 02. Детектор текстовых совпадений"
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
difficulty: "начальный+"
projectId: "case-02"
time: "90-120 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> найти пары архивных описаний с одинаковыми последовательностями слов и составить рейтинг по степени совпадения n-грамм.</p>
  <p><strong>Инструменты</strong> кортежи, n-граммы, множества, словари, сортировка, функции и понятный отчёт в терминале.</p>
  <p><strong>Вход</strong> архивные тексты, предупреждение и `01-authorship.json`.</p>
  <p><strong>Результат</strong> рейтинг совпадений и `artifacts/02-text-matches.json`.</p>
  <p><strong>Маршрут</strong> начальный+ · 90–120 минут · Python 3.13+</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-02.zip">case-02.zip</a> · <a href="../../materials/">материалы всех расследований</a> · <a href="../copy-paste-detector-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/control-flow/">условия и циклы</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/tuple/">tuple</a> · <a href="../../field-guide/set/">set</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/sorting/">sorting</a> · <a href="../../field-guide/functions/">functions</a> · <a href="../../field-guide/comprehensions/">включения</a> · <a href="../../field-guide/rich/">Rich</a></p>
</div>

## Проблема

После анонимной записки редактор просматривает соседние материалы архива. В черновике экскурсии почти дословно повторяются фрагменты закрытой описи, хотя эта опись ещё не должна была покинуть рабочую папку. Ещё одна пара отчётов тоже подозрительно похожа, но относится к учебному стенду: инструменту предстоит отделить возможную утечку от обычного повторного использования текста.

Вопрос расследования: какие пары действительно похожи на копирование или утечку, а какие просто описывают одну тему похожими словами?

Наша задача — не «поймать нарушителя», а создать рабочий инструмент первичной проверки. Программа прочитает несколько отчётов, сравнит каждую пару и поставит выше пары с большим количеством совпадающих последовательностей слов.

Скачайте архив [case-02.zip](../../downloads/case-02.zip) или откройте папку `projects/case-02/` в репозитории.

В учебном наборе:

- `copy_paste_detector.py` — пустой файл для программы, которую вы соберёте по главе;
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

Проверьте стартовый файл:

```bash
python copy_paste_detector.py
```

Пустой файл ничего не напечатает — это ожидаемо. Откройте `copy_paste_detector.py` и переносите листинги по порядку, чтобы провести данные от исходных текстов до отчёта.

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

Начните с импортов, поиска папки данных, размера n-граммы и консоли:

```python
import json
from pathlib import Path
from itertools import combinations

from rich.console import Console
from rich.table import Table


def default_data_dir():
    script_dir = Path(__file__).resolve().parent
    local_data = script_dir / "data"
    if local_data.exists():
        return local_data
    return script_dir.parent / "data"


DATA_DIR = default_data_dir()
PROJECT_DIR = DATA_DIR.parent
AUTHORSHIP_PATH = DATA_DIR / "artifacts" / "01-authorship.json"
ARTIFACT_PATH = PROJECT_DIR / "artifacts" / "02-text-matches.json"
NGRAM_SIZE = 4
TOP_EXAMPLES = 3
console = Console()
```

`combinations` позднее создаст каждую пару текстов один раз. `json` читает результат I-01 и сохраняет I-02, `Path` работает с файлами, а два класса Rich строят терминальную таблицу. `default_data_dir()` сначала ищет `data` рядом со скриптом студента; запасная ветка нужна тому же коду в подпапке `solution`. Поэтому самостоятельная и полная версии используют одни данные. Остальные константы задают вход I-01, выход I-02, окно из четырёх слов и три примера совпадений.

Четыре слова — чувствительность этого учебного расследования, а не универсальный стандарт плагиата. `TOP_EXAMPLES` ограничивает только число иллюстраций: сама оценка использует все совпадения.

Сначала разберите функцию чтения:

```python
def read_text(path):
    # Явная кодировка исключает зависимость результата от настроек операционной системы.
    return path.read_text(encoding="utf-8")
```

`path` содержит путь к одному отчёту. `read_text()` возвращает весь файл одной строкой, а явная кодировка исключает зависимость от настроек операционной системы.

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

Проверьте результат до перехода к окнам слов:

```python
words = normalize_words("Северный стол закрыт для посетителей.")
print(words)
```

```text
['северный', 'стол', 'закрыт', 'для', 'посетителей']
```

Список содержит пять слов без точки и заглавной буквы. Следующая функция будет двигать по этому списку окно длиной четыре.

### Собираем n-граммы

Теперь нужна функция, которая двигает окно размера `size` по списку слов. Она возвращает список кортежей, потому что дальше эти кортежи можно положить во множество и быстро сравнивать.

```python
def make_ngrams(words, size=NGRAM_SIZE):
    # Проверяем параметр сразу, чтобы отрицательный диапазон не выглядел как корректный пустой результат.
    if size < 1:
        raise ValueError("N-gram size must be positive")

    # Последнее окно начинается в len(words) - size; +1 включает эту позицию.
    return [
        tuple(words[index : index + size])
        for index in range(len(words) - size + 1)
    ]
```

List comprehension перебирает допустимые начальные позиции окна. Срез `words[index:index + size]` получает соседние слова, а `tuple(...)` превращает их в неизменяемую n-грамму. Если слов меньше `size`, диапазон пуст и функция возвращает пустой список.

Для пяти слов из предыдущего шага получатся два перекрывающихся окна:

```python
print(make_ngrams(words))
```

```text
[('северный', 'стол', 'закрыт', 'для'),
 ('стол', 'закрыт', 'для', 'посетителей')]
```

Слова `стол`, `закрыт` и `для` входят в оба окна. Такое перекрытие позволяет найти длинную скопированную фразу, а не только отдельные общие слова.

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

Проверьте краткую форму профиля закрытой описи:

```python
profile = build_profile(DATA_DIR / "report_north_table.txt")
print(profile["title"])
print(profile["word_count"], profile["ngram_count"])
```

```text
Опись Северного стола
165 162
```

Профиль содержит 165 слов и 162 уникальные 4-граммы. Поле `ngrams` намеренно не печатаем целиком: оно нужно следующему этапу для пересечения множеств.

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
    left_ngrams = left["ngrams"]
    right_ngrams = right["ngrams"]
    # Сортировка делает примеры воспроизводимыми при любом порядке элементов множества.
    shared_ngrams = sorted(left_ngrams & right_ngrams)

    return {
        "pair": (str(left["title"]), str(right["title"])),
        "score": overlap_score(left_ngrams, right_ngrams),
        "shared_count": len(shared_ngrams),
        # examples содержит первые TOP_EXAMPLES n-грамм после сортировки.
        "examples": shared_ngrams[:TOP_EXAMPLES],
    }
```

Если редактор спросит: «Почему эта пара подозрительна?», поле `examples` покажет несколько совпавших n-грамм.

Сравните опись с черновиком экскурсии и выведите только сводку:

```python
left = build_profile(DATA_DIR / "report_north_table.txt")
right = build_profile(DATA_DIR / "report_tour_draft.txt")
comparison = compare_profiles(left, right)
print(comparison["score"], comparison["shared_count"])
print(" ".join(comparison["examples"][0]))
```

```text
0.273 49
а сначала отмечает расхождение
```

Число `49` показывает объём пересечения, `0.273` позволяет сравнить эту пару с другими, а первая n-грамма объясняет результат конкретным фрагментом.

### Ранжируем все пары

Чтобы сравнить каждый отчёт со всеми остальными, используем `combinations`, уже подключённую в начальном блоке импортов.

Загрузка профилей:

```python
def load_profiles(data_dir=DATA_DIR, ngram_size=NGRAM_SIZE):
    # Сначала берём отчёты, затем явно добавляем предупреждение к тому же корпусу.
    paths = sorted(data_dir.glob("report_*.txt"))
    anonymous_path = data_dir / "anonymous.txt"
    if anonymous_path.exists():
        paths.append(anonymous_path)
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
        if int(result["shared_count"]) > 0:
            results.append(result)

    return sorted(
        results,
        # Кортеж задаёт два ключа: сначала балл, затем число совпадений.
        key=lambda item: (float(item["score"]), int(item["shared_count"])),
        reverse=True,
    )
```

Сортировка получает ключ из двух значений: сначала оценка, потом количество общих n-грамм. Так пары с одинаковой оценкой будут упорядочены стабильнее.

Полный рейтинг содержит только две пары с общими 4-граммами:

```python
for result in rank_overlaps():
    print(result["pair"], result["score"], result["shared_count"])
```

```text
('Опись Северного стола', 'Черновик экскурсии') 0.273 49
('Отчёт учебного стенда', 'Отчёт охраны') 0.175 25
```

Теперь данные уже находятся в нужном порядке. Rich на следующем шаге только оформит этот список.

### Печатаем отчёт

[Rich](../../field-guide/rich/) нужен только для вывода. `Table` уже подключён в начальном блоке импортов, а анализ остаётся на стандартной библиотеке.

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
            f"{float(result['score']):.3f}",
            str(result["shared_count"]),
            example,
        )

    console.print(table)

    if results:
        best = results[0]
        left, right = best["pair"]
        console.print(
            f"\n[bold]Главная версия:[/bold] {left} и {right} "
            f"имеют самый сильный общий след: [cyan]{float(best['score']):.3f}[/cyan]."
        )
```

## Читаем вывод I-01 и сохраняем новый отчёт

`load_authorship_lead()` проверяет `investigation_id="I-01"` и переносит в новый отчёт фактического лидера рейтинга вместе с ограничением вывода. `load_profiles()` дополнительно включает `anonymous.txt`, поэтому предупреждение сравнивается с тем же корпусом. В канонических данных у предупреждения нет общих 4-грамм с отчётами, поэтому в итоговый рейтинг всё равно попадают две пары отчётов.

Разберите загрузку результата I-01:

```python
def load_authorship_lead(path=AUTHORSHIP_PATH):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("investigation_id") != "I-01":
        raise ValueError(f"Expected I-01 artifact: {path}")
    finding = data["findings"][0]
    return {
        "finding_id": finding["finding_id"],
        "candidate": finding["candidates"][0]["name"],
        "score": finding["candidates"][0]["score"],
        "limitation": finding["limitation"],
    }
```

Теперь преобразуйте кортежи в строки и списки, которые можно записать в JSON:

```python
def build_artifact(results, authorship_path=AUTHORSHIP_PATH):
    matches = []
    for position, result in enumerate(results, start=1):
        matches.append(
            {
                "rank": position,
                "pair": list(result["pair"]),
                "score": result["score"],
                "shared_count": result["shared_count"],
                "examples": [format_ngram(item) for item in result["examples"]],
            }
        )
    return {
        "schema_version": 1,
        "investigation_id": "I-02",
        "generated_at": "2026-03-15T06:50:00+03:00",
        "source_files": [
            "anonymous.txt",
            *[path.name for path in sorted(DATA_DIR.glob("report_*.txt"))],
            "artifacts/01-authorship.json",
        ],
        "inputs": {"authorship_lead": load_authorship_lead(authorship_path)},
        "findings": [
            {
                "finding_id": "F-I02-TEXT-MATCHES",
                "kind": "text-overlap-ranking",
                "title": "Совпадения n-грамм в материалах архива",
                "summary": (
                    f"Самая сильная пара: {' / '.join(matches[0]['pair'])}."
                    if matches
                    else "Совпадений n-грамм не найдено."
                ),
                "matches": matches,
            }
        ],
    }


def save_artifact(artifact, path=ARTIFACT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
```

В `load_authorship_lead()` первая строка превращает JSON-текст в словарь. Проверка не даёт случайно прочитать отчёт другого дела. Переменная `finding` выбирает единственный вывод I-01, а возвращаемый словарь оставляет только лидера, его балл и ограничение метода.

В `build_artifact()` цикл превращает внутренние значения Python в значения JSON: `pair` становится списком, а каждый кортеж n-граммы — строкой. Внешний словарь сохраняет входные файлы, использованный вывод I-01 и один новый вывод с полным рейтингом совпадений. Условное выражение в `summary` отдельно обрабатывает пустой рейтинг.

`save_artifact()` создаёт папку при первом запуске. `ensure_ascii=False` сохраняет русские буквы, `indent=2` добавляет отступы, а `"\n"` завершает файл переводом строки. Технические значения уже даны в листинге: студенту не требуется придумывать метки, они нужны следующей программе для точного чтения результата.

В конце `main()` печатает рейтинг и сохраняет его для I-03:

```python
def main():
    results = rank_overlaps()
    render_results(results)
    save_artifact(build_artifact(results))
    console.print(f"[green]Отчёт сохранён:[/green] {ARTIFACT_PATH.name}")


if __name__ == "__main__":
    main()
```

Проверка `__name__` запускает `main()` по команде ниже, но не запускает отчёт автоматически при импорте файла для проверки отдельных функций.

## Проверка

Запустите:

```bash
python copy_paste_detector.py
```

Ожидаемая форма результата:

```text
Подозрительные совпадения
1  Опись Северного стола / Черновик экскурсии       0.27  ...
2  Отчёт учебного стенда / Отчёт охраны              0.18  ...
Отчёт сохранён: 02-text-matches.json
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
4. Добавьте CSV-копию, не удаляя JSON для следующего расследования.
5. Добавьте режим сравнения одного нового файла со всей папкой известных отчётов.

Когда закончите, откройте [разбор полного решения](../copy-paste-detector-solution/).
