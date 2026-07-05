# Дело 05. Доска расследования

Пятый проект: небольшая ООП-доска для расследования ночного сигнала архива. Мы храним участников, улики и заметки как объекты, загружаем исходные данные из JSON и сохраняем обновленный снимок дела.

## Подготовка

Нужен Python 3.14 или новее.

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS или Linux

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Запуск

```bash
python investigation_system.py
```

Стартовый файл уже умеет загрузить `data/case_seed.json` и показать краткую сводку. В главе вы постепенно добавите поиск по уликам, методы объектов, заметки и сохранение JSON-снимка `case_report.json`.

## Что изучаем

- классы и методы;
- `dataclass` для компактных объектов;
- композицию: дело содержит участников, улики и заметки;
- чтение и запись JSON;
- `pathlib.Path`;
- `rich.console.Console` и `rich.table.Table` для терминального отчета.
