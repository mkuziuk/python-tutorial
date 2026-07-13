# Дело 05. Доска расследования

Пятый проект — небольшая объектная система для расследования ночного сигнала архива. Участники, улики и заметки представлены объектами; исходные данные загружаются из JSON, а обновлённый снимок дела сохраняется в отдельный файл.

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

В стартовом файле есть только учебные ориентиры. По главе вы добавите загрузку `data/case_seed.json`, поиск по уликам, методы объектов, заметки и сохранение JSON-снимка `case_report.json`.

## Самопроверка

После сборки запустите тесты из папки дела:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- классы и методы;
- `dataclass` для компактных объектов;
- композицию: дело содержит участников, улики и заметки;
- чтение и запись JSON;
- `pathlib.Path`;
- `rich.console.Console` и `rich.table.Table` для отчёта в терминале.
