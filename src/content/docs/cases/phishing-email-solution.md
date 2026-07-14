---
title: "Разбор полного решения"
description: "Полный код третьего дела: анализ .eml-писем, правила риска и объяснимый отчёт."
concepts:
  - повторение регулярных выражений
  - email
  - urllib.parse
  - ipaddress
  - exceptions
  - rules
  - Rich
difficulty: "средний"
projectId: "case-03"
time: "15-20 минут"
---

Обращайтесь к этой странице после самостоятельной сборки `phishing_email.py`. Если открыть её раньше, работа над правилами риска сведётся к переписыванию готового ответа.

## Полный код

```python
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path
import ipaddress
import re
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table


def default_data_dir():
    # Один и тот же пример запускается из корня проекта и из каталога solution/.
    script_dir = Path(__file__).resolve().parent
    local_data = script_dir / "data"
    if local_data.exists():
        return local_data
    return script_dir.parent / "data"


DATA_DIR = default_data_dir()
TEXT_CONTENT_TYPES = {"text/plain", "text/html"}
TRAILING_URL_CHARS = ".,;:!?)]}"

# URL_RE и HTML_LINK_RE находят ссылки http/https в учебных письмах.
URL_RE = re.compile(r"https?://[^\s<>'\"\\]+", re.IGNORECASE)
HTML_LINK_RE = re.compile(
    r"<a\s+[^>]*href=[\"'](?P<url>https?://[^\"']+)[\"'][^>]*>"
    r"(?P<label>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
DOMAIN_RE = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b",
    re.IGNORECASE,
)
URGENT_RE = re.compile(
    r"срочно|немедленно|сегодня|до конца дня|последнее уведомление|urgent|immediately",
    re.IGNORECASE,
)
RISKY_ATTACHMENT_RE = re.compile(r"\.(exe|js|scr|cmd|bat|vbs|ps1)$", re.IGNORECASE)

console = Console()


class EmailAnalysisError(Exception):
    """Raised when an .eml file cannot be parsed for this case."""


# frozen защищает уже созданный объект от случайного изменения на следующих этапах.
@dataclass(frozen=True)
class LinkInfo:
    raw: str
    label: str
    scheme: str
    host: str
    display_host: str
    is_ip_host: bool


@dataclass(frozen=True)
class RiskSignal:
    title: str
    points: int
    level: str


@dataclass(frozen=True)
class EmailReport:
    filename: str
    subject: str
    sender: str
    sender_domain: str
    links: list[LinkInfo]
    signals: list[RiskSignal]
    score: int
    verdict: str


def clean_url(raw_url):
    # Убираем только знаки, которыми URL обычно заканчивается в прозе; путь и параметры не меняем.
    return raw_url.rstrip(TRAILING_URL_CHARS)


def clean_label(raw_label):
    # Удаляем разметку только из видимой подписи; адрес href разбирается отдельно.
    without_tags = TAG_RE.sub(" ", raw_label)
    return SPACE_RE.sub(" ", without_tags).strip()


def is_ip_address(host):
    if not host:
        return False
    try:
        # ip_address() возвращает объект для корректного IP
        # и бросает ValueError для остальных строк.
        # Квадратные скобки допустимы вокруг IPv6 в URL, но не являются частью самого адреса.
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def normalize_host(host):
    # Завершающая точка и регистр не должны превращать один DNS-хост в два разных.
    return host.strip().strip(".").lower()


def base_domain(host):
    host = normalize_host(host)
    if not host or is_ip_address(host):
        return host

    labels = host.split(".")
    if len(labels) < 2:
        return host
    # В учебных данных базовый домен — две последние части хоста.
    return ".".join(labels[-2:])


def domain_from_address(value):
    # parseaddr возвращает адрес без отображаемого имени отправителя.
    _, address = parseaddr(value or "")
    if "@" not in address:
        return ""
    return normalize_host(address.rsplit("@", 1)[1])


def display_host_from_label(label):
    # DOMAIN_RE извлекает первый домен из текста ссылки.
    match = DOMAIN_RE.search(label)
    if match is None:
        return ""
    return normalize_host(match.group(0))


def make_link_info(raw_url, label=""):
    # urlparse разделяет raw_url на схему, хост, путь и параметры.
    parsed = urlparse(raw_url)
    # hostname уже отделён от схемы, порта, пути и параметров URL.
    host = normalize_host(parsed.hostname or "")
    return LinkInfo(
        raw=raw_url,
        label=label,
        scheme=parsed.scheme.lower(),
        host=host,
        display_host=display_host_from_label(label),
        is_ip_host=is_ip_address(host),
    )


def extract_links(text):
    links = []
    # Множество хранит уже учтённые адреса между двумя проходами по HTML и обычному тексту.
    seen_urls = set()

    # Сначала читаем HTML-ссылки: только так можно сравнить видимую подпись с реальным href.
    for match in HTML_LINK_RE.finditer(text):
        url = clean_url(match.group("url"))
        label = clean_label(match.group("label"))
        if url not in seen_urls:
            links.append(make_link_info(url, label))
            seen_urls.add(url)

    # href уже найден выше; seen_urls не даёт учесть тот же URL второй раз.
    for match in URL_RE.finditer(text):
        url = clean_url(match.group(0))
        if url not in seen_urls:
            links.append(make_link_info(url))
            seen_urls.add(url)

    return links


def load_message(path):
    try:
        with path.open("rb") as file:
            # Читаем исходные байты, чтобы policy.default корректно декодировала MIME.
            message = BytesParser(policy=policy.default).parse(file)
    except OSError as exc:
        # as exc сохраняет исходную ошибку, а from exc связывает её с EmailAnalysisError.
        raise EmailAnalysisError(f"Cannot read {path}") from exc

    # Без отправителя и темы правила ниже потеряют контекст, поэтому неполное письмо отклоняем сразу.
    if not message.get("From"):
        raise EmailAnalysisError(f"{path.name}: missing From header")
    if not message.get("Subject"):
        raise EmailAnalysisError(f"{path.name}: missing Subject header")

    return message


def text_from_message(message):
    try:
        if not message.is_multipart():
            content = message.get_content()
            return content if isinstance(content, str) else ""

        chunks = []
        # MIME-дерево — структура частей письма: контейнеры могут содержать текст,
        # вложения и другие контейнеры.
        for part in message.walk():
            # walk() возвращает и multipart-контейнеры, поэтому пропускаем их и вложения.
            if part.is_multipart() or part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() in TEXT_CONTENT_TYPES:
                content = part.get_content()
                if isinstance(content, str):
                    chunks.append(content)
        return "\n".join(chunks)
    except (LookupError, UnicodeDecodeError) as exc:
        # Кортеж в except перехватывает любую из двух ошибок декодирования.
        raise EmailAnalysisError("Cannot decode message body") from exc


# attachment_names() собирает имена MIME-частей с типом attachment.
def attachment_names(message):
    names = []
    for part in message.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                names.append(filename)
    return names


def add_signal(
    signals,
    title,
    points,
    level="warning",
):
    # Каждый тип риска добавляем один раз, даже если ему соответствуют несколько ссылок.
    # Повторяющиеся ссылки не должны повторно добавлять сигнал и увеличивать score.
    # all() возвращает True, только если title отличается
    # от заголовка каждого существующего сигнала.
    if all(signal.title != title for signal in signals):
        signals.append(RiskSignal(title=title, points=points, level=level))


def risk_verdict(score):
    # score от 7 означает высокий риск, от 3 — ручную проверку.
    if score >= 7:
        return "высокий риск"
    if score >= 3:
        return "проверить вручную"
    return "низкий риск"


def analyze_message(message, filename="<memory>"):
    # Сначала извлекаем поля письма и ссылки, затем проверяем правила риска.
    subject = str(message.get("Subject", "(без темы)"))
    sender = str(message.get("From", ""))
    sender_domain = domain_from_address(sender)
    reply_to_domain = domain_from_address(message.get("Reply-To"))
    body = text_from_message(message)
    links = extract_links(body)
    signals = []

    if reply_to_domain and base_domain(reply_to_domain) != base_domain(sender_domain):
        add_signal(signals, "Reply-To ведёт в другой домен", 2)

    # Срочность ищем и в теме, и в теле: отправитель может вынести давление в любое из полей.
    if URGENT_RE.search(f"{subject}\n{body}"):
        add_signal(signals, "Есть слова срочности", 1)

    for link in links:
        # Одна ссылка может нарушать несколько независимых правил, поэтому проверки не связаны через elif.
        if link.is_ip_host:
            add_signal(signals, "Ссылка ведёт на IP-адрес вместо домена", 3, "danger")

        if link.scheme == "http":
            add_signal(signals, "Ссылка использует http без шифрования", 2)

        # Текст ссылки может обещать один домен, а href вести на другой.
        if link.display_host and base_domain(link.display_host) != base_domain(link.host):
            add_signal(signals, "Видимый домен ссылки не совпадает с реальным", 3, "danger")

        if (
            sender_domain
            and link.host
            and not link.is_ip_host
            and base_domain(link.host) != base_domain(sender_domain)
        ):
            add_signal(signals, "Ссылка ведёт в домен, отличный от домена отправителя", 1)

    if len(links) >= 4:
        add_signal(signals, "В письме слишком много ссылок", 1)

    risky_attachments = [
        name for name in attachment_names(message) if RISKY_ATTACHMENT_RE.search(name)
    ]
    if risky_attachments:
        add_signal(signals, "Есть вложение с рискованным расширением", 3, "danger")

    # score равен сумме points всех сигналов, поэтому вклад каждого правила виден в отчёте.
    score = sum(signal.points for signal in signals)
    return EmailReport(
        filename=filename,
        subject=subject,
        sender=sender,
        sender_domain=sender_domain,
        links=links,
        signals=signals,
        score=score,
        verdict=risk_verdict(score),
    )


def analyze_file(path):
    # Читаем письмо из файла и передаём разобранное сообщение в analyze_message().
    return analyze_message(load_message(path), filename=path.name)


def analyze_directory(data_dir=DATA_DIR):
    # Фиксированный порядок файлов делает отчёт одинаковым на разных файловых системах.
    paths = sorted(data_dir.glob("*.eml"))
    if not paths:
        raise EmailAnalysisError(f"No .eml files found in {data_dir}")
    return [analyze_file(path) for path in paths]


def render_results(reports):
    table = Table(title="Проверка писем")
    table.add_column("Файл", style="cyan")
    table.add_column("Вердикт")
    table.add_column("Балл", justify="right")
    table.add_column("Сигналы")

    # sorted() создаёт новый список отчётов в порядке убывания score.
    for report in sorted(reports, key=lambda item: item.score, reverse=True):
        signals = "\n".join(
            f"{signal.title} (+{signal.points})" for signal in report.signals
        )
        table.add_row(
            report.filename,
            report.verdict,
            str(report.score),
            signals or "явных сигналов нет",
        )

    console.print(table)

    # При равных баллах max сохраняет первый отчёт из стабильного файлового порядка.
    highest = max(reports, key=lambda item: item.score)
    console.print(
        f"\n[bold]Самая рискованная версия:[/bold] {highest.filename} "
        f"({highest.verdict}, {highest.score} баллов)."
    )


def main():
    try:
        reports = analyze_directory()
    except EmailAnalysisError as exc:
        # При ошибке печатаем причину и завершаем программу; render_results() здесь не вызывается.
        console.print(f"[bold red]Ошибка:[/bold red] {exc}")
        raise SystemExit(1) from exc

    render_results(reports)


if __name__ == "__main__":
    main()
```

## Как читать решение

Данные проходят несколько этапов: `load_message()` разбирает `.eml`, `text_from_message()` собирает текст письма, `extract_links()` создаёт список `LinkInfo`, `analyze_message()` добавляет сигналы `RiskSignal`, а `EmailReport` передаётся в таблицу.

Главное решение — сохранить правила явными. Инструмент не выносит необъяснимый вердикт: каждый балл связан с проверяемым фактом, который можно показать в отчёте. `score` — сумма баллов правил, а не вероятность фишинга. Совпадение расширения добавляет сигнал для ручной проверки, но само по себе не доказывает вредоносность файла.

Частые ошибки: вручную резать URL строками, считать домен из видимого текста ссылки вместо `href`, добавлять один и тот же сигнал много раз или ловить все исключения слишком широко.

Справочник: [email, URL и IP](../../field-guide/email-url-ip/), [regex](../../field-guide/regex/), [exceptions](../../field-guide/exceptions/), [str](../../field-guide/str/), [list](../../field-guide/list/), [functions](../../field-guide/functions/), [dataclasses](../../field-guide/dataclasses/), [Rich](../../field-guide/rich/).

## Что важно заметить

`email` разбирает структуру письма, но не решает за нас, опасно оно или нет. Все решения вынесены в явные правила внутри `analyze_message()`. Регулярные выражения рассчитаны на формат учебных писем; для произвольного HTML нужен полноценный парсер.

`urlparse()` нужен вместо ручного деления строки по `/`: он аккуратно достает `scheme` и `hostname`, даже если в ссылке есть путь и параметры.

`ipaddress.ip_address()` используется как проверка с исключением. Домен вызывает исключение, но для анализа это не ошибка, а обычный ответ: «это не IP-адрес».

Rich остаётся только слоем вывода: `Console` печатает, `Table` строит таблицу, а анализ писем работает на стандартной библиотеке.
