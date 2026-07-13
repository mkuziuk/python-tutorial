# Дело 04. Ночной сигнал архива

Четвёртый проект — индексатор папки после ночного сигнала архива. Он собирает JSON-манифест, ищет дубли по SHA-256, показывает изменения между запусками и сравнивает две версии хронологии.

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
python secret_folder_archive.py
```

Стартовый файл намеренно пуст. По главе вы добавите обход `data/secret_folder/`, вычисление SHA-256, временные метки, JSON-манифест, поиск дублей, сравнение с прошлым запуском и построчное сравнение двух хронологий через `difflib`.

Хэш SHA-256 работает как цифровой отпечаток файла: одинаковые байты дают одинаковую строку, а небольшая правка меняет её.

## Самопроверка

После сборки запустите тесты из папки дела:

```bash
python -m unittest discover -s tests
```

## Что изучаем

- `pathlib.Path`;
- рекурсивный обход файлов;
- `hashlib.sha256`;
- JSON;
- временные метки в UTC;
- поиск дублей;
- обнаружение добавленных, удалённых и изменённых файлов;
- `difflib.ndiff` для расхождения `22:53` / `23:07` в хронологиях;
- `rich.console.Console` и `rich.table.Table`.
