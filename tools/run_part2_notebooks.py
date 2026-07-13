"""Execute all Part II solution notebooks in one clean, pinned environment."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PART_TWO = ROOT / "projects" / "part-2"
REQUIREMENTS = PART_TWO / "requirements-ci.txt"
INSIDE_ENV = "PYTHON_TUTORIAL_PART2_TEST_ENV"


def venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def run_in_clean_environment() -> None:
    if not REQUIREMENTS.is_file():
        raise SystemExit(f"Missing {REQUIREMENTS.relative_to(ROOT)}")
    with tempfile.TemporaryDirectory(prefix="python-tutorial-part2-env-") as temp:
        env_dir = Path(temp) / ".venv"
        venv.EnvBuilder(with_pip=True).create(env_dir)
        python = venv_python(env_dir)
        subprocess.run(
            [str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
            cwd=ROOT,
            check=True,
        )
        environment = os.environ.copy()
        environment[INSIDE_ENV] = "1"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        subprocess.run(
            [str(python), "-B", str(Path(__file__).resolve())],
            cwd=ROOT,
            env=environment,
            check=True,
        )


def source_text(cell: object) -> str:
    source = cell.get("source", "")  # type: ignore[attr-defined]
    return "".join(source) if isinstance(source, list) else str(source)


def verify_sha256_file(path: Path) -> None:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, relative = line.split(maxsplit=1)
        relative = relative.lstrip("*")
        target = path.parent / relative
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            raise AssertionError(f"checksum mismatch: {target.relative_to(ROOT)}")


def verify_manifest_paths() -> None:
    manifest_path = ROOT / "src" / "data" / "course.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    arc = next(item for item in manifest["arcs"] if item["id"] == "part-2")
    if len(arc["cases"]) != 6:
        raise AssertionError("course manifest must contain six Part II cases")
    for item in arc["cases"]:
        for notebook in item["notebooks"].values():
            if not (ROOT / notebook).is_file():
                raise AssertionError(f"manifest notebook does not exist: {notebook}")


def execute_notebooks() -> None:
    import nbformat
    from nbclient import NotebookClient

    os.environ["MPLBACKEND"] = "Agg"
    os.environ["PYTHONHASHSEED"] = "0"
    verify_manifest_paths()
    for checksum_file in sorted(PART_TWO.glob("case-*/data/CHECKSUMS.sha256")):
        verify_sha256_file(checksum_file)

    cases = sorted(path for path in PART_TWO.glob("case-*") if path.is_dir())
    if len(cases) != 6:
        raise AssertionError(f"expected six Part II cases, found {len(cases)}")

    with tempfile.TemporaryDirectory(prefix="python-tutorial-part2-run-") as temp:
        temp_root = Path(temp)
        for case in cases:
            copied_case = temp_root / case.name
            shutil.copytree(case, copied_case)
            notebook_path = (
                copied_case / "solution" / f"{case.name}-solution.ipynb"
            )
            notebook = nbformat.read(notebook_path, as_version=4)
            nbformat.validate(notebook)
            os.environ["NOTEBOOK_VARIANT"] = "solution"

            sources = "\n".join(source_text(cell) for cell in notebook.cells)
            if "RANDOM_STATE = 42" not in sources:
                raise AssertionError(f"{case.name}: RANDOM_STATE = 42 is required")
            for cell in notebook.cells:
                tags = set(cell.get("metadata", {}).get("tags", []))
                if "bootstrap" in tags:
                    continue
                source = source_text(cell)
                forbidden = ("fetch_openml(", "fetch_california_housing(")
                if any(token in source for token in forbidden):
                    raise AssertionError(
                        f"{case.name}: mutable dataset fetch outside bootstrap cell"
                    )

            print(
                f"\n== {case.name}: executing solution notebook ==",
                flush=True,
            )
            client = NotebookClient(
                notebook,
                timeout=600,
                kernel_name="python3",
                resources={"metadata": {"path": str(copied_case)}},
                allow_errors=False,
                store_widget_state=False,
            )
            client.execute()
            print(
                f"== {case.name}: solution Run All passed "
                f"({len(notebook.cells)} cells) ==",
                flush=True,
            )

        for case in cases:
            archive_path = ROOT / "public" / "downloads" / f"part-2-{case.name}.zip"
            checksum_path = archive_path.with_suffix(f"{archive_path.suffix}.sha256")
            if not archive_path.is_file() or not checksum_path.is_file():
                raise AssertionError(f"{case.name}: learner archive or checksum missing")
            expected_digest = checksum_path.read_text(encoding="ascii").split()[0]
            actual_digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
            if actual_digest != expected_digest:
                raise AssertionError(f"{case.name}: learner archive checksum mismatch")

            extracted_case = temp_root / f"downloaded-part-2-{case.name}"
            extracted_case.mkdir()
            with zipfile.ZipFile(archive_path) as archive:
                if any(
                    Path(name).is_absolute() or ".." in Path(name).parts
                    for name in archive.namelist()
                ):
                    raise AssertionError(f"{case.name}: unsafe learner archive path")
                archive.extractall(extracted_case)

            notebook_path = extracted_case / f"{case.name}.ipynb"
            canonical_learner = case / f"{case.name}.ipynb"
            if notebook_path.read_bytes() != canonical_learner.read_bytes():
                raise AssertionError(f"{case.name}: learner archive is stale")
            notebook = nbformat.read(notebook_path, as_version=4)
            nbformat.validate(notebook)
            if notebook.metadata.get("course", {}).get("variant") != "learner":
                raise AssertionError(f"{case.name}: learner metadata variant missing")
            sources = "\n".join(source_text(cell) for cell in notebook.cells)
            if "# BEGIN SOLUTION" in sources or "# END SOLUTION" in sources:
                raise AssertionError(f"{case.name}: solution markers leaked into learner")
            os.environ["NOTEBOOK_VARIANT"] = "learner"

            print(
                f"\n== {case.name}: executing learner from extracted ZIP ==",
                flush=True,
            )
            client = NotebookClient(
                notebook,
                timeout=600,
                kernel_name="python3",
                resources={"metadata": {"path": str(extracted_case)}},
                allow_errors=False,
                store_widget_state=False,
            )
            client.execute()
            print(
                f"== {case.name}: extracted learner Run All passed "
                f"({len(notebook.cells)} cells) ==",
                flush=True,
            )


def main() -> None:
    if os.environ.get(INSIDE_ENV) != "1":
        run_in_clean_environment()
        return
    execute_notebooks()


if __name__ == "__main__":
    main()
