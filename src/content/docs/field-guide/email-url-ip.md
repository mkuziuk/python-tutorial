---
title: "email, URL и IP: разбираем письмо"
description: "Стандартные модули для анализа писем, ссылок и сетевых адресов."
concept: "email-url-ip"
usedIn:
  - "case-03"
order: 9
---

## Что это

Python умеет разбирать письма, ссылки и IP-адреса стандартными модулями: `email`, `urllib.parse` и `ipaddress`.

## Когда использовать

Используйте эти модули, когда формат уже известен. Они надежнее, чем ручной разбор строк через срезы.

```python
from urllib.parse import urlparse

parsed = urlparse("https://portal.example.test/report")
print(parsed.netloc)
```

## Мини-пример

```python
import ipaddress
from urllib.parse import urlparse

host = urlparse("http://192.0.2.42/login").hostname
address = ipaddress.ip_address(host)
print(address.is_private, address.is_global)
```

## Типичные ловушки

- `.hostname` может быть `None`, если строка не похожа на URL.
- `ipaddress.ip_address()` бросает `ValueError`, если передать обычный домен.
- Модуль `email` разбирает структуру письма, но не решает сам, опасно оно или нет.

## Где встречается в делах

- [Дело 03. Фишинговое письмо или нет?](../../cases/phishing-email/) - достаем заголовки, ссылки и сетевые признаки из писем дела.
