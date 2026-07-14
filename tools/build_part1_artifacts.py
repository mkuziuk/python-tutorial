import argparse
import importlib.util
import json
from pathlib import Path
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"


def ensure_rich_imports():
    try:
        import rich  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    class Placeholder:
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, _name):
            return lambda *args, **kwargs: None

    rich_module = types.ModuleType("rich")
    console_module = types.ModuleType("rich.console")
    table_module = types.ModuleType("rich.table")
    console_module.Console = Placeholder
    table_module.Table = Placeholder
    sys.modules.update(
        {
            "rich": rich_module,
            "rich.console": console_module,
            "rich.table": table_module,
        }
    )


def load_solution(case_number, module_name):
    path = PROJECTS / f"case-{case_number}" / "solution" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"case_{case_number}_{module_name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def expected_artifacts():
    ensure_rich_imports()
    case01 = load_solution("01", "anonymous_letter")
    case02 = load_solution("02", "copy_paste_detector")
    case03 = load_solution("03", "phishing_email")

    data01 = case01.build_artifact(case01.rank_candidates(), case01.DATA_DIR)

    with temporary_artifact(PROJECTS / "case-02" / "data" / "artifacts" / "01-authorship.json", data01):
        data02 = case02.build_artifact(
            case02.rank_overlaps(),
            PROJECTS / "case-02" / "data" / "artifacts" / "01-authorship.json",
        )

    with temporary_inputs(
        PROJECTS / "case-03" / "data" / "artifacts",
        {"01-authorship.json": data01, "02-text-matches.json": data02},
    ):
        reports03 = case03.analyze_directory(
            case03.DATA_DIR,
            PROJECTS / "case-03" / "data" / "artifacts" / "02-text-matches.json",
        )
        data03 = case03.build_artifact(reports03)

    return {
        "01-authorship.json": data01,
        "02-text-matches.json": data02,
        "03-mail-review.json": data03,
    }


class temporary_artifact:
    def __init__(self, path, data):
        self.path = path
        self.data = data
        self.previous = None

    def __enter__(self):
        if self.path.exists():
            self.previous = self.path.read_bytes()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(encoded(self.data))

    def __exit__(self, *_):
        if self.previous is None:
            self.path.unlink(missing_ok=True)
        else:
            self.path.write_bytes(self.previous)


class temporary_inputs:
    def __init__(self, directory, items):
        self.directory = directory
        self.items = items
        self.previous = {}

    def __enter__(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        for name, data in self.items.items():
            path = self.directory / name
            self.previous[name] = path.read_bytes() if path.exists() else None
            path.write_bytes(encoded(data))

    def __exit__(self, *_):
        for name, previous in self.previous.items():
            path = self.directory / name
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(previous)


def destinations(artifacts):
    return {
        PROJECTS / "case-02" / "data" / "artifacts" / "01-authorship.json": artifacts["01-authorship.json"],
        PROJECTS / "case-03" / "data" / "artifacts" / "01-authorship.json": artifacts["01-authorship.json"],
        PROJECTS / "case-03" / "data" / "artifacts" / "02-text-matches.json": artifacts["02-text-matches.json"],
        PROJECTS / "case-04" / "data" / "artifacts" / "01-authorship.json": artifacts["01-authorship.json"],
        PROJECTS / "case-04" / "data" / "artifacts" / "02-text-matches.json": artifacts["02-text-matches.json"],
        PROJECTS / "case-04" / "data" / "artifacts" / "03-mail-review.json": artifacts["03-mail-review.json"],
    }


def main():
    parser = argparse.ArgumentParser(description="Build canonical Part I handoff artifacts.")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifacts = expected_artifacts()
    stale = []
    for path, data in destinations(artifacts).items():
        content = encoded(data)
        if args.check:
            if not path.exists() or path.read_bytes() != content:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            print(f"built {path.relative_to(ROOT)}")
    if stale:
        print("Part I artifacts are stale:", file=sys.stderr)
        for path in stale:
            print(f"- {path}", file=sys.stderr)
        raise SystemExit(1)
    if args.check:
        print(f"checked {len(destinations(artifacts))} Part I artifact copies")


if __name__ == "__main__":
    main()
