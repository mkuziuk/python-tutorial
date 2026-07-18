---
title: "email, URL и IP: разбираем письмо"
description: "Стандартные модули для анализа писем, ссылок и сетевых адресов."
concept: "email-url-ip"
usedIn:
  - "case-03"
order: 9
---

## Что это

Python умеет разбирать письма, ссылки и IP-адреса стандартными модулями:
`email`, `urllib.parse` и `ipaddress`. Каждый модуль отвечает за свою границу
формата: MIME-структуру письма, компоненты URL или числовой сетевой адрес.

## Когда использовать

Используйте эти модули, когда формат уже известен. Они надёжнее ручного разбора
строк через срезы. Начнём с URL: на входе находится строка, а на выходе —
объект `ParseResult` с именованными компонентами.

```python
from urllib.parse import urlparse

parsed = urlparse("https://portal.example.test/report")
print(parsed.scheme)
print(parsed.hostname)
print(parsed.path)
```

Результат:

```text
https
portal.example.test
/report
```

Вывод подтверждает, что схема, имя узла и путь доступны отдельно. Разбор
описывает структуру строки, но не проверяет существование сайта и не определяет,
безопасна ли ссылка. Мы получили имя узла; чтобы проверить, является ли оно
IP-адресом, передадим именно `parsed.hostname` модулю `ipaddress`.

```python
import ipaddress
from urllib.parse import urlparse

host = urlparse("http://192.0.2.42/login").hostname
if host is None:
    raise ValueError("В URL нет имени узла")

address = ipaddress.ip_address(host)
print(address)
print(address.version)
print(address.is_global)
```

```text
192.0.2.42
4
False
```

Проверка `None` фиксирует границу между синтаксическим разбором URL и разбором
адреса. `ip_address()` вернул объект IPv4; `version == 4` подтверждает семейство
адреса. Флаг `is_global` описывает классификацию адреса библиотекой, а не
доступность узла. Адрес `192.0.2.42` зарезервирован для документации, поэтому
он не является глобальным.

Для письма сначала преобразуйте исходные байты `.eml` в `EmailMessage`.
`BytesParser` учитывает объявленные MIME-заголовки и кодировки частей:

```python
from email import policy
from email.parser import BytesParser

raw_message = (
    b"From: sender@example.test\r\n"
    b"To: analyst@example.test\r\n"
    b"Subject: Check\r\n"
    b"Content-Type: text/plain; charset=utf-8\r\n"
    b"\r\n"
    b"Open https://portal.example.test/report\r\n"
)
message = BytesParser(policy=policy.default).parsebytes(raw_message)
plain = message.get_body(preferencelist=("plain",))
attachments = [part.get_filename() for part in message.iter_attachments()]
print(message["Subject"])
print(plain.get_content().strip() if plain is not None else None)
print(attachments)
```

```text
Check
Open https://portal.example.test/report
[]
```

`message` хранит заголовки и MIME-части, `plain` — выбранную текстовую часть
или `None`, а `attachments` — список имён вложений. Вывод подтверждает, что
парсер декодировал UTF-8-тело и что в этом письме нет вложений. Мы получили
текст письма как строку; следующий этап расследования может извлечь из неё URL,
а затем разобрать каждый URL так же, как в первом этапе.

## Типичные ловушки

- `.hostname` может быть `None`, если строка не похожа на URL.
- `ipaddress.ip_address()` бросает `ValueError`, если передать обычный домен.
- Для строки `example.test/path` без схемы `urlparse()` может принять первую
  часть за путь. Если вход обязан быть абсолютным URL, отдельно требуйте
  непустые `scheme` и `hostname`.
- Не декодируйте весь `.eml` заранее через произвольную кодировку: письмо может
  содержать части с разными кодировками и бинарные вложения. Передавайте байты
  `BytesParser`, а текст получайте из выбранной MIME-части через `get_content()`.
- Имя вложения может быть `None`; само имя не доказывает тип или безопасность
  содержимого.
- После разбора письма правила риска всё равно нужно определить в программе.

## Где встречается в расследованиях

- [Расследование 03. Фишинговое письмо или нет?](../../cases/phishing-email/) - достаем заголовки, ссылки и сетевые признаки из писем расследования.
