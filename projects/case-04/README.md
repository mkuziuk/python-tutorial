# Дело 04. Архивариус секретной папки

Четвертый проект учебника: индексатор папки, который собирает JSON-манифест, ищет дубли по SHA-256 и показывает изменения между запусками.

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
python secret_folder_archive.py
```

Стартовый файл уже обходит `data/secret_folder/` и показывает черновую таблицу. В главе вы постепенно добавите SHA-256, timestamps, JSON-манифест, поиск дублей и сравнение с прошлым запуском.

## Что изучаем

- `pathlib.Path`;
- рекурсивный обход файлов;
- `hashlib.sha256`;
- JSON;
- timestamps в UTC;
- поиск дублей;
- обнаружение добавленных, удаленных и измененных файлов;
- `rich.console.Console` и `rich.table.Table`.
