---
title: "Расследование 04. Последнее доказательство"
description: "Собираем выводы трёх расследований, ранжируем подозреваемых и открываем досье главного кандидата."
concepts:
  - JSON
  - dict
  - list
  - sorting
  - происхождение данных
  - валидация
difficulty: "средний"
projectId: "case-04"
time: "120–150 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> объединить выводы I-01–I-03 с последней проверкой журналов и определить, чьё досье нужно изучить подробно.</p>
  <p><strong>Инструменты</strong> JSON, словари, списки, поиск по ID, сортировка и проверка входных данных.</p>
  <p><strong>Вход</strong> три отчёта предыдущих расследований, <code>final_evidence.json</code> и локальные досье.</p>
  <p><strong>Результат</strong> <code>artifacts/04-investigation-summary.json</code> и завершение первой арки.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-04.zip">case-04.zip</a> · <a href="../final-evidence-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/json/">JSON</a> · <a href="../../field-guide/dict/">dict</a> · <a href="../../field-guide/list/">list</a> · <a href="../../field-guide/sorting/">sorting</a></p>
</div>

## Перед открытием

До открытия витрины осталось меньше часа. Три программы уже дали отдельные результаты:

- I-01 указало на Алину как вероятного автора предупреждения, но не установило автора подмены;
- I-02 нашло закрытый текст описи в черновике экскурсии;
- I-03 обнаружило два опасных письма, но не доказало успешный вход;
- утренняя проверка добавила расхождение хронологий, квитанцию о передаче и аудит двух файловых операций.

В этом проекте вы сделаете семь конкретных действий:

1. откроете три готовых JSON-отчёта I-01–I-03;
2. достанете из них четыре нужных вывода;
3. добавите семь результатов утренней проверки;
4. получите один список из 11 улик;
5. сложите веса улик отдельно для Алины, Ильи и Никиты;
6. отсортируете людей по баллу и возьмёте лидера;
7. по `person_id` лидера найдёте его учётную запись, пропуск и аппаратный ключ в локальном досье.

Короткие `finding_id` уже перечислены в листинге ниже. Запоминать или придумывать их не нужно: программа использует эти метки только для точного поиска нужной записи внутри JSON. Ваша задача — провести данные по цепочке и проверить итоговый отчёт, а не написать большой терминальный рассказ.

## Материалы

Скачайте [case-04.zip](../../downloads/case-04.zip) или откройте `projects/case-04/`.

### Подготовка окружения

После распаковки откройте папку `case-04` в файловом менеджере. В Windows щёлкните правой кнопкой по свободному месту в Проводнике и выберите **Открыть в терминале**. В macOS щёлкните по папке в Finder и выберите **Службы → Новый терминал по адресу папки**. В Linux щёлкните правой кнопкой внутри папки и выберите **Открыть в терминале**. Название системного действия может отличаться; терминал должен открыться в папке с `requirements.txt` и `final_evidence.py`.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

После активации в начале строки терминала обычно появляется `(.venv)`. Внешних библиотек нет: команды используют стандартную библиотеку Python из окружения этого расследования.

```text
data/
  artifacts/
    01-authorship.json
    02-text-matches.json
    03-mail-review.json
  final_evidence.json
  suspect_dossiers.json
```

`final_evidence.json` не переписывает старые выводы. Он содержит только новые материалы: две файловые операции, доступ к комнате, расхождение хронологий, квитанцию архивариуса и проверки альтернативных объяснений.

Откройте пустой `final_evidence.py` и начните с импортов и путей:

```python
import json
from pathlib import Path


def default_project_dir():
    script_dir = Path(__file__).resolve().parent
    return script_dir if (script_dir / "data").exists() else script_dir.parent


PROJECT_DIR = default_project_dir()
DATA_DIR = PROJECT_DIR / "data"
ARTIFACTS_DIR = DATA_DIR / "artifacts"
FINAL_EVIDENCE_PATH = DATA_DIR / "final_evidence.json"
DOSSIERS_PATH = DATA_DIR / "suspect_dossiers.json"
OUTPUT_PATH = PROJECT_DIR / "artifacts" / "04-investigation-summary.json"
```

Разберём строки:

- `json` превращает текст файла в словари и списки Python, а в конце выполняет обратное преобразование;
- `Path` соединяет части пути оператором `/` и читает файлы с явной кодировкой;
- `default_project_dir()` сначала ищет `data` рядом со скриптом, а для канонического файла в `solution/` поднимается на один уровень;
- `PROJECT_DIR` поэтому всегда указывает на `case-04`, даже если команду запустили из другой папки;
- три следующих пути разделяют старые отчёты, новые улики и досье;
- `OUTPUT_PATH` задаёт ещё не существующий итоговый файл. Папку `artifacts` программа создаст перед записью.

Затем добавьте две таблицы, которые задают связь между файлами и выводами:

```python
UPSTREAM_FILES = {
    "I-01": "01-authorship.json",
    "I-02": "02-text-matches.json",
    "I-03": "03-mail-review.json",
}

SELECTED_FINDINGS = {
    "I-01": ["F-I01-AUTHORSHIP"],
    "I-02": ["F-I02-TEXT-MATCHES"],
    "I-03": ["F-I03-LOCKOUT", "F-I03-CAMERA"],
}

MISSING_LIMITATION = (
    "Ограничение не указано в исходном артефакте; "
    "вывод нельзя трактовать шире его summary."
)
```

`UPSTREAM_FILES` отвечает на вопрос «какой файл относится к какому делу». `SELECTED_FINDINGS` отвечает на вопрос «какие записи взять из этого файла». Поэтому студент не ищет загадочные номера вручную: цикл ниже прочитает таблицу сам.

## Шаг 1. Проверить входной отчёт

Файл с правильным именем ещё не гарантирует правильное содержимое. Загрузите JSON и сравните `investigation_id` с ожидаемым значением:

```python
def load_artifact(path, expected_id):
    data = json.loads(path.read_text(encoding="utf-8"))
    actual_id = data.get("investigation_id")
    if actual_id != expected_id:
        raise ValueError(f"Expected {expected_id} in {path}, found {actual_id!r}")
    return data
```

`path.read_text(encoding="utf-8")` возвращает строку. `json.loads(...)` превращает её в словарь `data`. Метод `.get()` безопасно возвращает `None`, если поле отсутствует, поэтому и отсутствующий, и неправильный ID попадут в одну понятную ошибку. Только после проверки функция возвращает словарь вызывающему коду.

Например, вызов

```python
artifact = load_artifact(ARTIFACTS_DIR / "01-authorship.json", "I-01")
print(artifact.keys())
```

даст ключи `schema_version`, `investigation_id`, `generated_at`, `source_files` и `findings`. Это ещё не одна улика, а весь отчёт I-01.

Отсутствующий файл должен вызвать `FileNotFoundError`. Не перехватывайте эту ошибку: без одного из отчётов финальный результат будет неполным.

Мы получили словарь полного отчёта I-01 и проверили его `investigation_id`. Для сборки цепочки нужен не весь словарь, а одна запись из списка `findings`, поэтому теперь найдём её по стабильному `finding_id`.

## Шаг 2. Найти вывод по ID

Положение записи в списке может измениться, поэтому используйте стабильный `finding_id`:

```python
def find_finding(artifact, finding_id):
    for finding in artifact.get("findings", []):
        if finding.get("finding_id") == finding_id:
            return finding
    raise KeyError(f"Finding not found: {finding_id}")
```

Цикл получает по одному словарю из списка `findings`. Условие сравнивает метку текущего словаря с нужной. `return` немедленно завершает функцию при совпадении. Если весь список просмотрен, выполнение доходит до `raise KeyError`: молча продолжать без нужного вывода нельзя.

Для общего списка приведите выводы к одной форме:

```python
def normalize_finding(finding, source_id):
    limitation = str(finding.get("limitation") or "").strip()
    if not limitation:
        limitation = MISSING_LIMITATION
    return {
        "finding_id": finding["finding_id"],
        "source_investigation_id": source_id,
        "title": finding["title"],
        "summary": finding["summary"],
        "limitation": limitation,
        "effects": [dict(effect) for effect in finding.get("effects", [])],
    }
```

Здесь новый словарь играет роль аккуратной карточки улики:

- `finding_id` позволяет позднее объяснить, какая запись изменила балл;
- `source_investigation_id` показывает, из какого дела пришла карточка;
- `title` и `summary` сохраняют исходную человеческую формулировку;
- `limitation` становится непустой строкой: исходный текст сохраняется, а отсутствующее или пустое поле получает буквальную метку `MISSING_LIMITATION`;
- список `effects` содержит техническое поле и значение для поиска в досье, а `dict(effect)` копирует каждый вложенный словарь, чтобы дальнейший расчёт не менял загруженный файл.

Поле `limitation` принципиально важно. Рейтинг I-01 не превращается в доказанное авторство, а признаки I-03 не превращаются в доказанный взлом только потому, что записи попали в финальный отчёт. В текущем handoff I-02 отдельная оговорка отсутствует. Программа не придумывает её содержание и не скрывает пробел пустой строкой: метка прямо сообщает, что вывод о совпадении n-грамм нельзя расширять за пределы исходного `summary`.

Мы научились находить одну запись и получили карточку с одинаковыми шестью полями, включая явную границу интерпретации. Чтобы ранжирование учитывало все выбранные источники, теперь соберём четыре старые и семь новых карточек в один упорядоченный список без повторяющихся ID.

## Шаг 3. Собрать цепочку улик

Пройдите по I-01–I-03 в фиксированном порядке и возьмите ID из `SELECTED_FINDINGS`. Затем добавьте новые выводы I-04. Множество поможет обнаружить повторяющийся ID:

```python
def collect_evidence(artifacts, final_evidence):
    evidence = []
    seen_ids = set()

    for investigation_id in ("I-01", "I-02", "I-03"):
        artifact = artifacts[investigation_id]
        for finding_id in SELECTED_FINDINGS[investigation_id]:
            finding = find_finding(artifact, finding_id)
            item = normalize_finding(finding, investigation_id)
            if item["finding_id"] in seen_ids:
                raise ValueError(f"Duplicate finding ID: {item['finding_id']}")
            seen_ids.add(item["finding_id"])
            evidence.append(item)

    for finding in final_evidence.get("findings", []):
        item = normalize_finding(finding, "I-04")
        if item["finding_id"] in seen_ids:
            raise ValueError(f"Duplicate finding ID: {item['finding_id']}")
        seen_ids.add(item["finding_id"])
        evidence.append(item)

    return evidence
```

Первые две строки создают будущий результат `evidence` и пустое множество уже использованных меток `seen_ids`. Внешний цикл задаёт порядок дел. Внутренний цикл читает готовую таблицу `SELECTED_FINDINGS`, поэтому в I-01 и I-02 берётся по одной записи, а в I-03 — две.

Для каждой записи программа выполняет одинаковые четыре действия: находит исходный словарь, нормализует его, проверяет повтор, добавляет метку в `seen_ids` и карточку в `evidence`. Второй цикл повторяет ту же проверку для семи новых записей I-04. В конце длина списка должна быть `4 + 7 = 11`.

После реализации можно временно проверить форму данных:

```python
evidence = collect_evidence(artifacts, final_evidence)
print(len(evidence))                    # 11
print(evidence[0]["title"])            # Рейтинг сходства с предупреждением
print(evidence[0]["limitation"][:40])  # ограничение метода I-01 не потерялось
print(evidence[1]["limitation"])        # пробел в handoff I-02 отмечен явно
```

Ожидаемый результат — число `11`, заголовок «Рейтинг сходства с предупреждением», начало ограничения I-01 и строка `Ограничение не указано в исходном артефакте; вывод нельзя трактовать шире его summary.` для I-02. Эти четыре значения подтверждают одновременно размер списка, фиксированный порядок источников, сохранение существующей оговорки и видимость отсутствующей.

Мы получили список из 11 карточек и проверили происхождение первых двух записей и обе границы `limitation`. Для многократного сопоставления технических значений с людьми нужен доступ по `person_id`, поэтому теперь преобразуем список досье в словарный индекс.

## Шаг 4. Построить индекс досье

Список удобен для JSON, но повторный поиск проще выполнять через словарь:

```python
def dossier_index(dossiers):
    index = {}
    for dossier in dossiers:
        person_id = dossier.get("person_id", "").strip()
        if not person_id:
            raise ValueError("Dossier person_id must not be empty")
        if person_id in index:
            raise ValueError(f"Duplicate person ID: {person_id}")
        index[person_id] = dossier
    return index


def lookup_dossier(dossiers, person_id):
    try:
        return dossier_index(dossiers)[person_id]
    except KeyError as error:
        raise KeyError(f"Unknown person: {person_id}") from error
```

`dossier_index()` начинает с пустого словаря. Для каждого досье она читает `person_id`, убирает случайные пробелы через `.strip()` и отдельно запрещает две ошибки входных данных: пустой ID и повторный ID. Строка `index[person_id] = dossier` превращает, например, список из трёх элементов в такой быстрый указатель:

```python
{
    "P-ALINA": {...},
    "P-ILYA": {...},
    "P-NIKITA": {...},
}
```

После этого `lookup_dossier()` делает одно обращение по ключу. Конструкция `raise ... from error` сохраняет исходную причину, но показывает студенту понятное сообщение `Unknown person: P-...`.

Новые технические записи не содержат готовый `person_id`. Они называют учётную запись, пропуск или аппаратный ключ. Следующая функция сопоставляет такое значение с локальным индексом досье:

```python
def resolve_effect_person(effect, people):
    match_field = effect.get("match_field", "")
    if match_field not in {"account", "badge_id", "hardware_key_id"}:
        raise ValueError(f"Unknown dossier field: {match_field!r}")

    match_value = str(effect.get("match_value", "")).casefold()
    matches = [
        person_id
        for person_id, dossier in people.items()
        if str(dossier.get(match_field, "")).casefold() == match_value
    ]
    if not matches:
        raise ValueError(f"No dossier matches {match_field}={match_value!r}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous dossier match: {match_field}={match_value!r}")
    return matches[0]
```

`match_field` разрешает только три поля, которые действительно существуют в учебных досье. `match_value` переводится в строку и сравнивается без учёта регистра. List comprehension собирает все совпавшие `person_id`: отсутствие совпадения означает неизвестное техническое значение, а два совпадения — неоднозначные досье. Только один результат считается пригодным для рейтинга.

Например, программа сама установит владельца сеанса:

```python
dossiers_bundle = load_artifact(DOSSIERS_PATH, "I-04-DOSSIERS")
people = dossier_index(dossiers_bundle["people"])
effect = {"match_field": "account", "match_value": "nikita.k"}
print(resolve_effect_person(effect, people))
```

```text
P-NIKITA
```

Именно на этом шаге техническая запись впервые связывается с человеком. Исходный `final_evidence.json` не сообщает программе готовый ответ.

Досье — вымышленный локальный набор курса. Программа не ищет сведения о реальных людях и не обращается в интернет.

## Шаг 5. Ранжировать подозреваемых

Новые выводы содержат короткие связи `effects`. `support` прибавляет вес, `conflict` вычитает. Эти числа выбраны для учебного дела и не являются вероятностью виновности.

```python
def rank_suspects(evidence, dossiers):
    people = dossier_index(dossiers)
    scores = {
        person_id: {
            "person_id": person_id,
            "name": dossier["name"],
            "score": 0,
            "supporting_finding_ids": [],
            "conflicting_finding_ids": [],
        }
        for person_id, dossier in people.items()
    }

    for finding in evidence:
        for effect in finding.get("effects", []):
            # Техническая улика содержит account, badge_id или hardware_key_id.
            # resolve_effect_person() находит владельца значения в локальных досье.
            person_id = resolve_effect_person(effect, people)
            weight = int(effect["weight"])
            if weight < 1:
                raise ValueError("Evidence weight must be positive")

            stance = effect["stance"]
            if stance == "support":
                scores[person_id]["score"] += weight
                scores[person_id]["supporting_finding_ids"].append(finding["finding_id"])
            elif stance == "conflict":
                scores[person_id]["score"] -= weight
                scores[person_id]["conflicting_finding_ids"].append(finding["finding_id"])
            else:
                raise ValueError(f"Unknown evidence stance: {stance}")

    return sorted(
        scores.values(),
        key=lambda item: (-item["score"], item["name"].casefold()),
    )
```

Сначала comprehension создаёт по одной строке рейтинга для каждого досье. Начальный балл равен нулю, а два списка пока пусты. Внешний цикл читает улики, внутренний — связи `effects` внутри улики. Проверки не дают незаметно сослаться на отсутствующего человека, использовать нулевой вес или написать неизвестный тип связи.

При `support` вес прибавляется, при `conflict` вычитается. Одновременно ID записи сохраняется в списке причин. Поэтому итоговый балл можно проверить, а не принимать на веру. Ключ сортировки содержит два значения: `-score` ставит больший балл выше, `name.casefold()` стабильно упорядочивает равные результаты по имени.

На учебных данных расчёт выглядит так:

| Человек | Подтверждающие веса | Итог |
| --- | --- | ---: |
| Никита Королев | `2 + 3 + 3 + 2` | `10` |
| Алина Морозова | нет связей `effects` | `0` |
| Илья Соколов | нет связей `effects` | `0` |

Фишинговая версия и сбой синхронизации проверены отдельными записями без `effects`: они закрывают альтернативные объяснения, но не добавляют искусственный штраф конкретному человеку. Числа — прозрачные учебные веса, а не вероятность виновности.

После сортировки первым должен стать `P-NIKITA` с 10 баллами. Два балла даёт пропуск `B-31`, по три — сеанс `nikita.k` и ключ `NK-17` в двух файловых операциях, ещё два — сеанс в квитанции передачи. Различие хронологий подтверждает сокрытие строки, но само по себе никого не называет и поэтому не получает `effects`. Результат рейтинга — направление углублённой проверки, а не финальный приговор программы.

## Шаг 6. Собрать и сохранить отчёт

Сначала маленькая функция фиксирует происхождение старого отчёта:

```python
def source_record(investigation_id, filename, artifact):
    return {
        "investigation_id": investigation_id,
        "path": f"artifacts/{filename}",
        "finding_ids": [
            item["finding_id"] for item in artifact.get("findings", [])
        ],
    }
```

`investigation_id` и `path` говорят, какой файл был прочитан. List comprehension проходит все его `findings` и сохраняет их метки. Эта запись не влияет на рейтинг; она позволяет позднее проверить происхождение результата.

Сначала отдельная функция загружает пять входов и возвращает четыре готовых значения:

```python
def load_investigation_inputs(
    artifacts_dir=ARTIFACTS_DIR,
    final_evidence_path=FINAL_EVIDENCE_PATH,
    dossiers_path=DOSSIERS_PATH,
):
    artifacts = {}
    source_artifacts = []

    for investigation_id, filename in UPSTREAM_FILES.items():
        artifact = load_artifact(artifacts_dir / filename, investigation_id)
        artifacts[investigation_id] = artifact
        source_artifacts.append(
            source_record(investigation_id, filename, artifact)
        )

    final_evidence = load_artifact(final_evidence_path, "I-04-EVIDENCE")
    dossiers_bundle = load_artifact(dossiers_path, "I-04-DOSSIERS")
    dossiers = dossiers_bundle.get("people", [])
    return artifacts, source_artifacts, final_evidence, dossiers
```

`artifacts` хранит полные отчёты по ключам `I-01`, `I-02`, `I-03`, а `source_artifacts` — короткие сведения о тех же файлах для итогового JSON. Цикл берёт пару «ожидаемый ID — имя файла» из `UPSTREAM_FILES`, проверяет файл и заполняет оба контейнера. Два следующих вызова отдельно проверяют новые улики и досье. Возвращаемый кортеж содержит словарь старых отчётов, список их источников, словарь новых улик и список из трёх досье.

Теперь `build_summary()` выполняет только анализ и сборку результата:

```python
def build_summary(
    artifacts_dir=ARTIFACTS_DIR,
    final_evidence_path=FINAL_EVIDENCE_PATH,
    dossiers_path=DOSSIERS_PATH,
):
    artifacts, source_artifacts, final_evidence, dossiers = (
        load_investigation_inputs(
            artifacts_dir,
            final_evidence_path,
            dossiers_path,
        )
    )

    evidence = collect_evidence(artifacts, final_evidence)
    ranking = rank_suspects(evidence, dossiers)
    if not ranking or ranking[0]["score"] <= 0:
        raise ValueError("Evidence does not identify a main suspect")

    main_suspect = ranking[0]
    dossier = lookup_dossier(dossiers, main_suspect["person_id"])

    return {
        "schema_version": 1,
        "investigation_id": "I-04",
        "generated_at": "2026-03-15T09:15:00+03:00",
        "source_artifacts": source_artifacts,
        "evidence": evidence,
        "suspect_ranking": ranking,
        "main_suspect": {
            "person_id": main_suspect["person_id"],
            "name": main_suspect["name"],
            "score": main_suspect["score"],
            "conclusion": "Главный подозреваемый для углублённой проверки",
        },
        "dossier": dict(dossier),
        "unresolved_threads": [
            dict(item) for item in final_evidence.get("unresolved_threads", [])
        ],
        "recommended_actions": [
            str(item) for item in final_evidence.get("recommended_actions", [])
        ],
    }
```

`load_investigation_inputs()` выполняется первым и отделяет файловый ввод от анализа. `collect_evidence()` создаёт 11 карточек, а `rank_suspects()` связывает технические значения с досье и возвращает три строки рейтинга. Проверка перед `[0]` запрещает выбрать лидера из пустого или полностью неподтверждённого рейтинга. `lookup_dossier()` получает `person_id` лидера и возвращает полную связанную запись. Итоговый `return` собирает семь содержательных разделов: источники, улики, рейтинг, лидера, досье, незакрытые линии и рекомендуемые действия.

`dict(dossier)` и `dict(item)` создают отдельные словари для результата. `str(item)` гарантирует, что рекомендации останутся обычными строками. Фиксированное учебное время делает ожидаемый JSON воспроизводимым.

Сохранение остаётся отдельной функцией:

```python
def save_summary(summary, path=OUTPUT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    path.write_text(payload, encoding="utf-8")
```

`mkdir(..., parents=True, exist_ok=True)` создаёт всю недостающую цепочку папок и не падает при повторном запуске. `ensure_ascii=False` оставляет русский текст читаемым, `indent=2` добавляет отступы, а финальный `"\n"` аккуратно завершает текстовый файл. Отдельная переменная `payload` позволяет увидеть границу между преобразованием данных и записью на диск.

Последняя функция намеренно печатает только служебную проверку:

```python
def main():
    summary = build_summary()
    save_summary(summary)
    print(f"Собрано улик: {len(summary['evidence'])}")
    print(f"Основной подозреваемый: {summary['main_suspect']['name']}")
    print(f"Отчёт сохранён: {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
```

`summary` вычисляется один раз и тот же словарь передаётся в `save_summary()`. Три `print()` подтверждают количество, лидера и имя файла, но не дублируют весь JSON в терминале. Проверка `__name__` запускает `main()` только при прямой команде; при импорте модуль лишь определяет функции.

Запустите программу и проверьте сохранённый JSON:

```bash
python final_evidence.py
python -m json.tool artifacts/04-investigation-summary.json
```

Рабочий запуск печатает только:

```text
Собрано улик: 11
Основной подозреваемый: Никита Королев
Отчёт сохранён: 04-investigation-summary.json
```

Откройте сохранённый JSON и проверьте три связи: у `main_suspect` стоит `P-NIKITA`, в `dossier` находятся `nikita.k` и `NK-17`, а в первой записи I-01 по-прежнему присутствует ограничение «не устанавливает автора». После этого переходите к развязке.

## Развязка

В итоговом JSON первым стоит Никита Королев. Вера использует `person_id` `P-NIKITA` и поднимает подробные материалы по двум сеансам `nikita.k`.

Два проверяющих независимо просматривают записи внутренней камеры. На первой записи Никита находится у рабочей станции, когда в 17:56 сохраняется черновик экскурсии с фрагментами закрытой описи. На второй он снова находится за той же станцией в 23:19, когда рабочая хронология сохраняется без строки о передаче в 23:07. В обоих сеансах использован его персональный аппаратный ключ `NK-17`.

Квитанция архивариуса подтверждает, что копия действительно была передана в 23:07 без согласования. Удалённая строка скрывала эту передачу. Совпадение личности на двух записях, аппаратного ключа, учётной записи и двух файловых операций закрывает последний пробел между сеансом и человеком.

**Никита Королев скопировал закрытые сведения в общий черновик, передал копию без согласования и изменил хронологию, чтобы скрыть передачу.** Открытие витрины откладывают, исходные материалы фиксируют, а доступ Никиты отзывают до формального разбирательства.

Алина подтверждает, что написала предупреждение, когда заметила закрытый текст в общем черновике. Она предупредила о подмене, но не выполняла её. Фишинговые письма остаются отдельной реальной атакой: их автор неизвестен, а следов успешного входа нет.

## Что мы использовали

- проверку `investigation_id` и поиск по `finding_id`;
- списки и словарные индексы;
- сохранение происхождения и ограничений выводов;
- объяснимую сортировку подозреваемых;
- JSON как итоговый отчёт четырёх связанных программ.
