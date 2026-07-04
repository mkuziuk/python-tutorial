from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path
import re
from urllib.parse import urlparse

from rich.console import Console
from rich.table import Table

DATA_DIR = Path(__file__).with_name("data")
URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.IGNORECASE)

console = Console()


def load_message(path: Path) -> EmailMessage:
    with path.open("rb") as file:
        return BytesParser(policy=policy.default).parse(file)


def text_from_message(message: EmailMessage) -> str:
    if not message.is_multipart():
        content = message.get_content()
        return content if isinstance(content, str) else ""

    chunks: list[str] = []
    for part in message.walk():
        if part.is_multipart() or part.get_content_disposition() == "attachment":
            continue
        if part.get_content_type() in {"text/plain", "text/html"}:
            content = part.get_content()
            if isinstance(content, str):
                chunks.append(content)
    return "\n".join(chunks)


def extract_links(text: str) -> list[str]:
    links: set[str] = set()
    for match in URL_RE.finditer(text):
        links.add(match.group(0).rstrip(".,;:!?)]}"))
    return sorted(links)


def host_from_url(url: str) -> str:
    parsed = urlparse(url)
    return (parsed.hostname or "").lower()


def collect_messages(data_dir: Path = DATA_DIR) -> list[tuple[Path, EmailMessage]]:
    return [(path, load_message(path)) for path in sorted(data_dir.glob("*.eml"))]


def render_overview(messages: list[tuple[Path, EmailMessage]]) -> None:
    table = Table(title="Черновой обзор писем")
    table.add_column("Файл")
    table.add_column("Тема")
    table.add_column("Найденные хосты")

    for path, message in messages:
        links = extract_links(text_from_message(message))
        hosts = ", ".join(host_from_url(link) for link in links) or "ссылок нет"
        table.add_row(path.name, str(message.get("Subject", "(без темы)")), hosts)

    console.print(table)
    console.print(
        "\n[dim]Дальше в главе мы добавим правила риска и объяснение каждого сигнала.[/dim]"
    )


def main() -> None:
    render_overview(collect_messages())


if __name__ == "__main__":
    main()
