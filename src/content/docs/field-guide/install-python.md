---
title: Установка Python
description: Короткая настройка Python, виртуальной среды и зависимостей перед делом.
concept: "install-python"
usedIn:
  - "case-01"
  - "case-02"
  - "case-03"
  - "case-04"
  - "case-05"
  - "case-06"
order: 0
---

## Что нужно

Для дел нужен Python 3.13 или новее. Сначала проверьте версию:

```powershell
py -3 --version
```

```bash
python3 --version
```

Обе команды должны показать версию не ниже 3.13. На Windows `py -3` выбирает установленный Python 3, не привязывая окружение к конкретному минорному выпуску.

## Где запускать команды

Каждое дело запускается из своей папки: `projects/case-01/`, `projects/case-02/` и так дальше. Если открыть терминал не там, Python может не найти `data/` и `requirements.txt`.

## Виртуальная среда

Виртуальная среда - отдельная папка с Python и библиотеками только для одного дела. Так разные проекты не мешают друг другу.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` ставит нужные библиотеки для текущего дела. В первой арке это в основном Rich: он делает терминальные таблицы читаемыми, а логика расследования остается на стандартной библиотеке Python.

## Где встречается в делах

- [Дело 01. Кто оставил предупреждение?](../../cases/anonymous-letter/) - первая настройка окружения.
- [Дела 02–06](../../cases/) - тот же порядок: открыть папку дела, активировать `.venv`, установить зависимости и запускать скрипт.
