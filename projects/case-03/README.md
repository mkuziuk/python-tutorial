# Дело 03. Фишинговое письмо или нет?

Консольный инструмент, который читает `.eml`-письма и объясняет, какие признаки риска он нашел.

В папке `data/` шесть писем: два похожи на ловушки перед открытием архива, четыре выглядят как обычная рабочая переписка.

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
python phishing_email.py
```

В начале файл только разбирает письма, показывает темы и найденные ссылки. Дальше глава показывает, как добавить правила риска: срочность, несовпадение `Reply-To`, ссылки на IP-адреса, `http` без шифрования, расхождение видимого домена с реальной ссылкой и рискованные имена вложений.

## Что изучаем

- модуль `email` для чтения `.eml`;
- регулярные выражения для аккуратного поиска ссылок и слов срочности;
- `urllib.parse.urlparse`;
- `ipaddress.ip_address`;
- собственные исключения;
- правила как небольшие проверяемые функции;
- `rich.console.Console` и `rich.table.Table` для терминального отчета.
