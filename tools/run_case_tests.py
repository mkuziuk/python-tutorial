import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"
MINIMUM_PYTHON = (3, 13)
TEST_TARGET_VARIABLE = "PYTHON_TUTORIAL_TEST_TARGET"


def venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def run(command: list[str], *, environment: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=ROOT, env=environment, check=True)


def discover_cases() -> list[Path]:
    return sorted(
        project
        for project in PROJECTS_DIR.glob("case-*")
        if (project / "tests").is_dir()
    )


def run_case_tests(project: Path) -> None:
    requirements = project / "requirements.txt"
    tests = project.relative_to(ROOT) / "tests"

    with tempfile.TemporaryDirectory(prefix=f"{project.name}-tests-") as temp_dir:
        env_dir = Path(temp_dir) / ".venv"
        venv.EnvBuilder(with_pip=True).create(env_dir)
        python = venv_python(env_dir)

        print(f"\n== {project.name}: installing requirements ==")
        if requirements.exists():
            run([str(python), "-m", "pip", "install", "-r", str(requirements)])

        print(f"== {project.name}: running maintainer tests ==")
        environment = os.environ.copy()
        environment[TEST_TARGET_VARIABLE] = "solution"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        run(
            [
                str(python),
                "-B",
                "-W",
                "error::DeprecationWarning",
                "-W",
                "error::PendingDeprecationWarning",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(tests),
            ],
            environment=environment,
        )


def main() -> None:
    if sys.version_info < MINIMUM_PYTHON:
        required = ".".join(map(str, MINIMUM_PYTHON))
        current = ".".join(map(str, sys.version_info[:3]))
        raise SystemExit(
            f"Python {required}+ is required to run the case tests; found {current}."
        )

    cases = discover_cases()
    if not cases:
        raise SystemExit("No case tests found under projects/case-*/tests")

    for project in cases:
        run_case_tests(project)


if __name__ == "__main__":
    main()
