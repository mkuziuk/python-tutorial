import subprocess
import sys
import tempfile
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECTS_DIR = ROOT / "projects"


def venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def run(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


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
        run(
            [
                str(python),
                "-W",
                "error::DeprecationWarning",
                "-W",
                "error::PendingDeprecationWarning",
                "-m",
                "unittest",
                "discover",
                "-s",
                str(tests),
            ]
        )


def main() -> None:
    cases = discover_cases()
    if not cases:
        raise SystemExit("No case tests found under projects/case-*/tests")

    for project in cases:
        run_case_tests(project)


if __name__ == "__main__":
    main()
