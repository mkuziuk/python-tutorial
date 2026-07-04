# Дело 01. Кто написал анонимное письмо?

Первый проект учебника: инструмент стилометрии для сравнения анонимного письма с тремя образцами.

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
python anonymous_letter.py
```

В начале файл только загружает материалы. Дальше глава показывает, как постепенно добавить анализ слов, пунктуации, сравнение профилей и таблицу результатов.

## Что изучаем

- виртуальную среду и установку зависимости;
- строки;
- списки;
- словари;
- множества;
- регулярные выражения;
- `collections.Counter`;
- `rich.console.Console` и `rich.table.Table`;
- функции и небольшую архитектуру скрипта.
