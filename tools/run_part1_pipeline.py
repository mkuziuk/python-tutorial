import importlib.util
import json
from pathlib import Path
import sys

from build_part1_artifacts import expected_artifacts


ROOT = Path(__file__).resolve().parents[1]


def load_final_module():
    path = ROOT / "projects" / "case-04" / "solution" / "final_evidence.py"
    spec = importlib.util.spec_from_file_location("part1_final_evidence", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    artifacts = expected_artifacts()
    expected_ids = ["I-01", "I-02", "I-03"]
    actual_ids = [artifacts[name]["investigation_id"] for name in artifacts]
    if actual_ids != expected_ids:
        raise SystemExit(f"Unexpected artifact chain: {actual_ids}")

    final = load_final_module()
    summary = final.build_summary(
        ROOT / "projects" / "case-04" / "data" / "artifacts",
        ROOT / "projects" / "case-04" / "data" / "final_evidence.json",
        ROOT / "projects" / "case-04" / "data" / "suspect_dossiers.json",
    )

    if summary["investigation_id"] != "I-04":
        raise SystemExit("Final artifact does not identify I-04")
    if summary["main_suspect"]["person_id"] != "P-NIKITA":
        raise SystemExit("Canonical Part I conclusion changed")
    if "винов" in json.dumps(summary["main_suspect"], ensure_ascii=False).casefold():
        raise SystemExit("Machine summary must stop at the main suspect")
    print("Part I pipeline passed: I-01 → I-02 → I-03 → I-04")


if __name__ == "__main__":
    main()
