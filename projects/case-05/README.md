# Расследование 05. Доска расследования

Пятый проект строит объектную доску из настоящих отчётов I-01–I-04. Каждая улика сохраняет `origin_finding_id`, а отдельные объекты `EvidenceLink` связывают её с проверяемой гипотезой.

## Подготовка

Нужен Python 3.13 или новее.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS или Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Запуск

```bash
python investigation_system.py
```

Стартовый файл намеренно пуст. По главе вы загрузите четыре файла из `data/artifacts/`, проверите их SHA-256 по индексу I-04, создадите объекты и примените связи из `data/relationships.json`. Результат сохраняется в `artifacts/05-case-board.json` и станет входом I-06.

## Самопроверка

После сборки запустите тесты из папки расследования:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- классы и методы;
- `dataclass` для компактных объектов;
- композицию: расследование содержит участников, улики, гипотезы и связи;
- проверку уникальности ID и происхождения каждой улики;
- чтение и запись JSON;
- `pathlib.Path`;
- `rich.console.Console` и `rich.table.Table` для отчёта в терминале.
