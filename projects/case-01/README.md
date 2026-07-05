# Дело 01. Кто оставил предупреждение?

Первый проект: инструмент стилометрии для поиска источника тревожной записки о полуночной правке.

## Подготовка

Нужна современная версия Python 3.

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
python anonymous_letter.py
```

Стартовый файл пустой. В главе вы вручную добавите загрузку материалов, анализ слов, пунктуации, сравнение профилей и таблицу результатов.

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
