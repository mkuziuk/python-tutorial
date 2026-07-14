import importlib.util
import json
from pathlib import Path
import sys
import tempfile

from build_part1_artifacts import expected_artifacts


ROOT = Path(__file__).resolve().parents[1]


def load_final_module():
    path = ROOT / "projects" / "case-06" / "solution" / "final_verdict.py"
    spec = importlib.util.spec_from_file_location("part1_final_verdict", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main():
    artifacts = expected_artifacts()
    expected_ids = ["I-01", "I-02", "I-03", "I-04", "I-05"]
    actual_ids = [artifacts[name]["investigation_id"] for name in artifacts]
    if actual_ids != expected_ids:
        raise SystemExit(f"Unexpected artifact chain: {actual_ids}")

    final = load_final_module()
    with tempfile.TemporaryDirectory(prefix="part1-pipeline-") as tmp_dir:
        board_path = Path(tmp_dir) / "05-case-board.json"
        board_path.write_text(
            json.dumps(artifacts["05-case-board.json"], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        bundle = final.load_bundle(
            board_path,
            ROOT / "projects" / "case-06" / "data" / "morning_updates.json",
        )
        verdict = final.build_verdict(bundle)

    if verdict["investigation_id"] != "I-06":
        raise SystemExit("Final artifact does not identify I-06")
    if verdict["ranked_hypotheses"][0]["hypothesis_id"] != "H-NIKITA":
        raise SystemExit("Canonical Part I conclusion changed")
    if verdict["operational_decision"]["opening"] != "postpone":
        raise SystemExit("Canonical opening decision changed")
    print("Part I pipeline passed: I-01 → I-02 → I-03 → I-04 → I-05 → I-06")


if __name__ == "__main__":
    main()
