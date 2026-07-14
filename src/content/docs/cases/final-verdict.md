---
title: "Расследование 06. Вердикт перед открытием"
description: "Добавляем новые утренние материалы к доске I-05, ранжируем гипотезы и сохраняем решение."
concepts:
  - StrEnum
  - match
  - dataclasses
  - datetime
  - sorting
  - JSON
difficulty: "продвинутый"
projectId: "case-06"
time: "110-140 минут"
---

<div class="case-meta">
  <p><strong>Миссия</strong> объединить доску I-05 с новыми утренними проверками и принять решение об открытии.</p>
  <p><strong>Инструменты</strong> `StrEnum`, `match`, `datetime`, сортировка и агрегирование баллов.</p>
  <p><strong>Вход</strong> `05-case-board.json` и `morning_updates.json`.</p>
  <p><strong>Результат</strong> `artifacts/06-verdict.json`.</p>
</div>

<div class="materials-panel">
  <p><strong>Быстрые ссылки:</strong> <a href="../../downloads/case-06.zip">case-06.zip</a> · <a href="../final-verdict-solution/">разбор решения</a></p>
  <p><strong>Справочник:</strong> <a href="../../field-guide/enums-match/">StrEnum и match</a> · <a href="../../field-guide/datetime/">datetime</a> · <a href="../../field-guide/json/">JSON</a></p>
</div>

## Что приходит из предыдущего расследования

`data/artifacts/05-case-board.json` содержит людей, гипотезы, двенадцать улик и их связи. Эти данные не переписываются заново.

`data/morning_updates.json` содержит только новые материалы:

- аудит перезаписи рабочей хронологии;
- подписанный аудит `SEC-774`;
- проверку почтового компромисса;
- проверку синхронизации;
- проверку согласования поздней передачи;
- подтверждение Алины.

Так видно, какие факты существовали до утра, а какие появились перед финальной оценкой.

## Шаг 1. Объединить два источника

```python
def load_bundle(board_path=BOARD_PATH, updates_path=UPDATES_PATH):
    board = json.loads(board_path.read_text(encoding="utf-8"))
    if board.get("investigation_id") != "I-05":
        raise ValueError(f"Expected I-05 board: {board_path}")

    updates = json.loads(updates_path.read_text(encoding="utf-8"))
    combined = {
        **board,
        "analysis_time": updates["analysis_time"],
        "evidence": [*board["evidence"], *updates["evidence"]],
    }
    return CaseBundle.from_dict(combined)
```

Программа не меняет доску I-05. Она создаёт новый объект для финального расчёта.

## Шаг 2. Ограничить допустимые значения

```python
class Stance(StrEnum):
    SUPPORT = "support"
    CONFLICT = "conflict"
```

`StrEnum` отклоняет опечатку при загрузке. `frozen=True` не позволяет случайно изменить уже загруженную улику.

## Шаг 3. Построить хронологию

```python
ordered = sorted(
    evidence,
    key=lambda item: (item.occurred_at, item.evidence_id),
)
```

`occurred_at` преобразуется в `datetime` со смещением часового пояса. ID используется как второй ключ для стабильного порядка событий с одинаковым временем.

## Шаг 4. Рассчитать поддержку и противоречия

Каждая связь содержит надёжность улики и вес связи:

```text
баллы связи = reliability × weight
итог = сумма поддержки − сумма противоречий
```

```python
points = item.reliability * effect.weight
match effect.stance:
    case Stance.SUPPORT:
        support_points += points
        support.append(item.evidence_id)
    case Stance.CONFLICT:
        conflict_points += points
        conflicts.append(item.evidence_id)
```

Итоговый балл — сумма назначенных аналитиком значений `reliability × weight`. Эти значения не обучены на сопоставимых расследованиях, а входные данные не содержат прямого наблюдения мотива или человека за клавиатурой. Поэтому балл только ранжирует четыре гипотезы.

## Шаг 5. Присвоить статус

```python
match support_points, conflict_points:
    case 0, 0:
        return AssessmentStatus.NO_EVIDENCE
    case support, conflict if support >= 15 and support >= conflict * 2:
        return AssessmentStatus.STRONGLY_SUPPORTED
    case support, conflict if conflict > support:
        return AssessmentStatus.NOT_SUPPORTED
    case _:
        return AssessmentStatus.UNRESOLVED
```

Порядок веток важен: `match` возвращает первый подходящий статус.

## Шаг 6. Сформировать решение

`build_verdict()` сохраняет:

- полную хронологию;
- рейтинг четырёх гипотез;
- списки поддержки и противоречий;
- подтверждённое авторство предупреждения;
- незакрытую фишинговую ветку;
- решение отложить открытие и три следующих действия.

Канонический результат остаётся осторожным:

- действия в двух сеансах связаны с учётной записью `nikita.k` и аппаратным ключом;
- журналы фиксируют сеансы учётной записи `nikita.k` и аппаратный ключ, но не фиксируют, кто находился за клавиатурой и зачем изменил файлы, поэтому они не устанавливают личность пользователя или мотив;
- данных об успешном фишинговом входе нет;
- открытие откладывается из-за нарушенной целостности материалов и непроверенных доступов.

## Проверка

```bash
python final_verdict.py
python -m json.tool artifacts/06-verdict.json
python -m unittest discover -s tests -v
```

Ожидаемые контрольные значения:

- первая гипотеза — `H-NIKITA`, итоговый балл `73`;
- `H-MISTAKE` — `2`;
- `H-PHISHING` — `-16`;
- `H-SYNC` — `-20`;
- решение `opening` равно `postpone`.

## Что мы использовали

- результат I-05 вместо нового вручную собранного набора;
- отдельный файл только для новых утренних материалов;
- неизменяемые dataclass-объекты;
- `StrEnum` и `match`;
- сортировку `datetime`;
- объяснимое агрегирование поддержки и противоречий.

## Задания после финала

1. Добавьте проверку повторного `evidence_id` при объединении файлов.
2. Выведите вклад каждой улики в балл гипотезы.
3. Сформируйте отдельный короткий отчёт только с операционным решением.
