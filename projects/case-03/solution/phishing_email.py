from dataclasses import dataclass
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr
from pathlib import Path
import ipaddress
import re
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table


def default_data_dir() -> Path:
    script_dir = Path(__file__).resolve().parent
    local_data = script_dir / "data"
    if local_data.exists():
        return local_data
    return script_dir.parent / "data"


DATA_DIR = default_data_dir()
TEXT_CONTENT_TYPES = {"text/plain", "text/html"}
TRAILING_URL_CHARS = ".,;:!?)]}"

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


def clean_url(raw_url: str) -> str:
    return raw_url.rstrip(TRAILING_URL_CHARS)


def clean_label(raw_label: str) -> str:
    without_tags = TAG_RE.sub(" ", raw_label)
    return SPACE_RE.sub(" ", without_tags).strip()


def is_ip_address(host: str) -> bool:
    if not host:
        return False
    try:
        ipaddress.ip_address(host.strip("[]"))
    except ValueError:
        return False
    return True


def normalize_host(host: str) -> str:
    return host.strip().strip(".").lower()


def base_domain(host: str) -> str:
    host = normalize_host(host)
    if not host or is_ip_address(host):
        return host

    labels = host.split(".")
    if len(labels) < 2:
        return host
    return ".".join(labels[-2:])


def domain_from_address(value: str | None) -> str:
    _, address = parseaddr(value or "")
    if "@" not in address:
        return ""
    return normalize_host(address.rsplit("@", 1)[1])


def display_host_from_label(label: str) -> str:
    match = DOMAIN_RE.search(label)
    if match is None:
        return ""
    return normalize_host(match.group(0))


def make_link_info(raw_url: str, label: str = "") -> LinkInfo:
    parsed = urlparse(raw_url)
    host = normalize_host(parsed.hostname or "")
    return LinkInfo(
        raw=raw_url,
        label=label,
        scheme=parsed.scheme.lower(),
        host=host,
        display_host=display_host_from_label(label),
        is_ip_host=is_ip_address(host),
    )


def extract_links(text: str) -> list[LinkInfo]:
    links: list[LinkInfo] = []
    seen_urls: set[str] = set()

    for match in HTML_LINK_RE.finditer(text):
        url = clean_url(match.group("url"))
        label = clean_label(match.group("label"))
        if url not in seen_urls:
            links.append(make_link_info(url, label))
            seen_urls.add(url)

    for match in URL_RE.finditer(text):
        url = clean_url(match.group(0))
        if url not in seen_urls:
            links.append(make_link_info(url))
            seen_urls.add(url)

    return links


def load_message(path: Path) -> EmailMessage:
    try:
        with path.open("rb") as file:
            message = BytesParser(policy=policy.default).parse(file)
    except OSError as exc:
        raise EmailAnalysisError(f"Cannot read {path}") from exc

    if not message.get("From"):
        raise EmailAnalysisError(f"{path.name}: missing From header")
    if not message.get("Subject"):
        raise EmailAnalysisError(f"{path.name}: missing Subject header")

    return message


def text_from_message(message: EmailMessage) -> str:
    try:
        if not message.is_multipart():
            content = message.get_content()
            return content if isinstance(content, str) else ""

        chunks: list[str] = []
        for part in message.walk():
            if part.is_multipart() or part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() in TEXT_CONTENT_TYPES:
                content = part.get_content()
                if isinstance(content, str):
                    chunks.append(content)
        return "\n".join(chunks)
    except (LookupError, UnicodeDecodeError) as exc:
        raise EmailAnalysisError("Cannot decode message body") from exc


def attachment_names(message: EmailMessage) -> list[str]:
    names: list[str] = []
    for part in message.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
                names.append(filename)
    return names


def add_signal(
    signals: list[RiskSignal],
    title: str,
    points: int,
    level: str = "warning",
) -> None:
    if all(signal.title != title for signal in signals):
        signals.append(RiskSignal(title=title, points=points, level=level))


def risk_verdict(score: int) -> str:
    if score >= 7:
        return "высокий риск"
    if score >= 3:
        return "проверить вручную"
    return "низкий риск"


def analyze_message(message: EmailMessage, filename: str = "<memory>") -> EmailReport:
    subject = str(message.get("Subject", "(без темы)"))
    sender = str(message.get("From", ""))
    sender_domain = domain_from_address(sender)
    reply_to_domain = domain_from_address(message.get("Reply-To"))
    body = text_from_message(message)
    links = extract_links(body)
    signals: list[RiskSignal] = []

    if reply_to_domain and base_domain(reply_to_domain) != base_domain(sender_domain):
        add_signal(signals, "Reply-To ведет в другой домен", 2)

    if URGENT_RE.search(f"{subject}\n{body}"):
        add_signal(signals, "Есть слова срочности", 1)

    for link in links:
        if link.is_ip_host:
            add_signal(signals, "Ссылка ведет на IP-адрес вместо домена", 3, "danger")

        if link.scheme == "http":
            add_signal(signals, "Ссылка использует http без шифрования", 2)

        if link.display_host and base_domain(link.display_host) != base_domain(link.host):
            add_signal(signals, "Видимый домен ссылки не совпадает с реальным", 3, "danger")

        if (
            sender_domain
            and link.host
            and not link.is_ip_host
            and base_domain(link.host) != base_domain(sender_domain)
        ):
            add_signal(signals, "Ссылка ведет в домен, отличный от домена отправителя", 1)

    if len(links) >= 4:
        add_signal(signals, "В письме слишком много ссылок", 1)

    risky_attachments = [
        name for name in attachment_names(message) if RISKY_ATTACHMENT_RE.search(name)
    ]
    if risky_attachments:
        add_signal(signals, "Есть вложение с рискованным расширением", 3, "danger")

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


def analyze_file(path: Path) -> EmailReport:
    return analyze_message(load_message(path), filename=path.name)


def analyze_directory(data_dir: Path = DATA_DIR) -> list[EmailReport]:
    paths = sorted(data_dir.glob("*.eml"))
    if not paths:
        raise EmailAnalysisError(f"No .eml files found in {data_dir}")
    return [analyze_file(path) for path in paths]


def render_results(reports: list[EmailReport]) -> None:
    table = Table(title="Проверка учебных писем")
    table.add_column("Файл", style="cyan")
    table.add_column("Вердикт")
    table.add_column("Балл", justify="right")
    table.add_column("Сигналы")

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

    highest = max(reports, key=lambda item: item.score)
    console.print(
        f"\n[bold]Самая рискованная версия:[/bold] {highest.filename} "
        f"({highest.verdict}, {highest.score} баллов)."
    )


def main() -> None:
    try:
        reports = analyze_directory()
    except EmailAnalysisError as exc:
        console.print(f"[bold red]Ошибка:[/bold red] {exc}")
        raise SystemExit(1) from exc

    render_results(reports)


if __name__ == "__main__":
    main()
