from difflib import ndiff
import hashlib
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table


def default_project_dir():
    script_dir = Path(__file__).resolve().parent
    return script_dir if (script_dir / "data").exists() else script_dir.parent


PROJECT_DIR = default_project_dir()
PROJECT_DATA_DIR = PROJECT_DIR / "data"
DATA_DIR = PROJECT_DATA_DIR / "secret_folder"
INPUT_ARTIFACTS_DIR = PROJECT_DATA_DIR / "artifacts"
ARTIFACT_PATH = PROJECT_DIR / "artifacts" / "04-evidence-index.json"
console = Console()


def iter_files(root):
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Expected a folder: {root}")
    return sorted(path for path in root.rglob("*") if path.is_file())


def relative_name(root, path):
    return path.relative_to(root).as_posix()


def file_sha256(path, chunk_size=65_536):
    digest = hashlib.sha256()
    with path.open("rb") as file:
        # Чтение блоками не загружает большой файл целиком в память.
        while chunk := file.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def build_record(root, path):
    return {
        "path": relative_name(root, path),
        "size": path.stat().st_size,
        "sha256": file_sha256(path),
    }


def scan_folder(root):
    root = root.resolve()
    return [build_record(root, path) for path in iter_files(root)]


def detect_duplicates(records):
    by_hash = {}
    for record in records:
        by_hash.setdefault(record["sha256"], []).append(record["path"])
    return [
        {"sha256": digest, "paths": sorted(paths)}
        for digest, paths in sorted(by_hash.items())
        if len(paths) > 1
    ]


def compare_timeline_versions(current_path, backup_path):
    current_lines = current_path.read_text(encoding="utf-8").splitlines()
    backup_lines = backup_path.read_text(encoding="utf-8").splitlines()
    differences = {"current": [], "backup": []}
    for line in ndiff(current_lines, backup_lines):
        if line.startswith("- "):
            differences["current"].append(line[2:])
        elif line.startswith("+ "):
            differences["backup"].append(line[2:])
    return differences


def read_timed_events(path):
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if len(line) >= 7 and line[2] == ":" and " - " in line:
            time, text = line.split(" - ", 1)
            events.append(
                {"occurred_at": f"2026-03-14T{time}:00+03:00", "text": text}
            )
    return events


def load_upstream_artifact(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("investigation_id") not in {"I-01", "I-02", "I-03"}:
        raise ValueError(f"Unexpected upstream artifact: {path}")
    return data


def build_evidence_index(secret_folder=DATA_DIR, artifacts_dir=INPUT_ARTIFACTS_DIR):
    upstream_paths = sorted(artifacts_dir.glob("0[1-3]-*.json"))
    if len(upstream_paths) != 3:
        raise FileNotFoundError(f"Expected three artifacts from I-01–I-03 in {artifacts_dir}")

    verified_artifacts = []
    source_files = []
    for path in upstream_paths:
        artifact = load_upstream_artifact(path)
        record = {
            "path": f"artifacts/{path.name}",
            "size": path.stat().st_size,
            "sha256": file_sha256(path),
        }
        source_files.append(record)
        verified_artifacts.append(
            {
                "investigation_id": artifact["investigation_id"],
                "path": record["path"],
                "sha256": record["sha256"],
                "finding_ids": [
                    item["finding_id"] for item in artifact.get("findings", [])
                ],
            }
        )

    folder_records = scan_folder(secret_folder)
    source_files.extend(
        {
            **record,
            "path": f"secret_folder/{record['path']}",
        }
        for record in folder_records
    )
    timeline = compare_timeline_versions(
        secret_folder / "drafts" / "timeline.txt",
        secret_folder / "drafts" / "timeline_backup.txt",
    )
    return {
        "schema_version": 1,
        "investigation_id": "I-04",
        "generated_at": "2026-03-15T07:00:00+03:00",
        "source_files": sorted(source_files, key=lambda item: item["path"]),
        "verified_artifacts": verified_artifacts,
        "findings": [
            {
                "finding_id": "F-I04-DUPLICATES",
                "kind": "duplicate-files",
                "title": "Байтовые копии фотоиндекса",
                "summary": "Два файла фотоиндекса имеют одинаковый SHA-256.",
                "groups": detect_duplicates(folder_records),
            },
            {
                "finding_id": "F-I04-TIMELINE",
                "kind": "timeline-difference",
                "title": "Расхождение рабочей и резервной хронологий",
                "summary": "Рабочая версия заканчивается в 22:53, а резервная содержит строку 23:07.",
                "differences": timeline,
            },
            {
                "finding_id": "F-I04-ACCESS-LOG",
                "kind": "preserved-log",
                "title": "Журнал доступа сохранён вместе с отчётами",
                "summary": "Журнал фиксирует выдачу ключа Никите, сигнал датчика и его объяснение о работе с копией.",
                "source_file": "secret_folder/notes/access_log_excerpt.txt",
                "events": read_timed_events(secret_folder / "notes" / "access_log_excerpt.txt"),
            },
        ],
    }


def save_artifact(index, path=ARTIFACT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_timeline_difference(differences):
    table = Table(title="Расхождение хронологий")
    table.add_column("Версия")
    table.add_column("Строка только в этой версии")
    for line in differences["current"]:
        table.add_row("Рабочая", line)
    for line in differences["backup"]:
        table.add_row("Резервная", line)
    console.print(table)


def render_evidence_index(index):
    table = Table(title="Зафиксированные материалы")
    table.add_column("Показатель")
    table.add_column("Значение", justify="right")
    table.add_row("Проверенных отчётов", str(len(index["verified_artifacts"])))
    table.add_row("Файлов с SHA-256", str(len(index["source_files"])))
    table.add_row("Выводов", str(len(index["findings"])))
    console.print(table)


def main():
    index = build_evidence_index()
    render_evidence_index(index)
    render_timeline_difference(index["findings"][1]["differences"])
    save_artifact(index)
    console.print(f"[bold green]Индекс сохранён:[/bold green] {ARTIFACT_PATH.name}")


if __name__ == "__main__":
    main()
