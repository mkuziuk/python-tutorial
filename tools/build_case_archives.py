import argparse
import hashlib
from io import BytesIO
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
PART_TWO_DIR = PROJECTS_DIR / "part-2"
DOWNLOADS_DIR = ROOT / "public" / "downloads"
FIXED_TIMESTAMP = (2026, 3, 15, 0, 0, 0)
PART_TWO_TIMESTAMP = (2026, 4, 17, 0, 0, 0)


def learner_files(project: Path) -> list[Path]:
    files: list[Path] = []

    for name in ("README.md", "requirements.txt", "check_result.txt"):
        path = project / name
        if path.is_file():
            files.append(path)

    files.extend(sorted(project.glob("*.py")))

    for folder_name in ("data", "tests"):
        folder = project / folder_name
        if not folder.is_dir():
            continue
        files.extend(
            path
            for path in sorted(folder.rglob("*"))
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        )

    return sorted(set(files), key=lambda path: path.relative_to(project).as_posix())


def archive_bytes(
    project: Path,
    *,
    timestamp: tuple[int, int, int, int, int, int] = FIXED_TIMESTAMP,
) -> bytes:
    output = BytesIO()

    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in learner_files(project):
            relative_name = path.relative_to(project).as_posix()
            info = ZipInfo(relative_name, date_time=timestamp)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())

    return output.getvalue()


def discover_projects() -> list[Path]:
    return sorted(
        project
        for project in PROJECTS_DIR.glob("case-*")
        if project.is_dir() and (project / "README.md").is_file()
    )


def part_two_learner_files(project: Path) -> list[Path]:
    files: list[Path] = []
    for name in (
        "README.md",
        "requirements.txt",
        "requirements-colab.txt",
        "check_result.md",
        "check_result.txt",
    ):
        path = project / name
        if path.is_file():
            files.append(path)

    files.extend(sorted(project.glob("*.ipynb")))
    data_dir = project / "data"
    if data_dir.is_dir():
        files.extend(
            path
            for path in sorted(data_dir.rglob("*"))
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        )
    return sorted(set(files), key=lambda path: path.relative_to(project).as_posix())


def part_two_archive_bytes(project: Path) -> bytes:
    output = BytesIO()
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in part_two_learner_files(project):
            relative_name = path.relative_to(project).as_posix()
            info = ZipInfo(relative_name, date_time=PART_TWO_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    return output.getvalue()


def discover_part_two_projects() -> list[Path]:
    if not PART_TWO_DIR.is_dir():
        return []
    return sorted(
        project
        for project in PART_TWO_DIR.glob("case-*")
        if project.is_dir() and (project / "README.md").is_file()
    )


def write_archives(check: bool) -> int:
    failures: list[str] = []
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    for project in discover_projects():
        destination = DOWNLOADS_DIR / f"{project.name}.zip"
        expected = archive_bytes(project)

        if check:
            if not destination.is_file() or destination.read_bytes() != expected:
                failures.append(destination.relative_to(ROOT).as_posix())
            continue

        destination.write_bytes(expected)
        print(f"built {destination.relative_to(ROOT)}")

    for project in discover_part_two_projects():
        destination = DOWNLOADS_DIR / f"part-2-{project.name}.zip"
        expected = part_two_archive_bytes(project)
        checksum_destination = destination.with_suffix(f"{destination.suffix}.sha256")
        checksum = (
            f"{hashlib.sha256(expected).hexdigest()}  {destination.name}\n"
        ).encode("ascii")

        if check:
            if not destination.is_file() or destination.read_bytes() != expected:
                failures.append(destination.relative_to(ROOT).as_posix())
            if (
                not checksum_destination.is_file()
                or checksum_destination.read_bytes() != checksum
            ):
                failures.append(checksum_destination.relative_to(ROOT).as_posix())
            continue

        destination.write_bytes(expected)
        checksum_destination.write_bytes(checksum)
        print(f"built {destination.relative_to(ROOT)}")
        print(f"built {checksum_destination.relative_to(ROOT)}")

    if failures:
        print("Learner archives are stale or missing:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        print("Run: pnpm build:archives", file=sys.stderr)
        return 1

    if check:
        total = len(discover_projects()) + len(discover_part_two_projects())
        print(f"checked {total} learner archives")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic learner ZIP files.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when a committed archive differs from its project files",
    )
    arguments = parser.parse_args()
    raise SystemExit(write_archives(check=arguments.check))


if __name__ == "__main__":
    main()
