"""Build deterministic learner notebooks from canonical Part II solutions."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PART_TWO = ROOT / "projects" / "part-2"
BEGIN_MARKER = "# BEGIN SOLUTION"
END_MARKER = "# END SOLUTION"
SOLUTION_BLOCK = re.compile(
    r"(?ms)^(?P<indent>[ \t]*)# BEGIN SOLUTION[^\n]*\n"
    r".*?^(?P=indent)# END SOLUTION[^\n]*(?:\n|$)"
)


def notebook_paths() -> list[tuple[Path, Path]]:
    pairs: list[tuple[Path, Path]] = []
    for case_dir in sorted(PART_TWO.glob("case-*")):
        if not case_dir.is_dir():
            continue
        case_name = case_dir.name
        solution = case_dir / "solution" / f"{case_name}-solution.ipynb"
        learner = case_dir / f"{case_name}.ipynb"
        if solution.is_file():
            pairs.append((solution, learner))
    return pairs


def source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else str(source)


def metadata_tags(cell: dict[str, Any]) -> set[str]:
    tags = cell.get("metadata", {}).get("tags", [])
    return {str(tag) for tag in tags}


def pop_learner_source(cell: dict[str, Any]) -> str | None:
    metadata = cell.setdefault("metadata", {})
    direct = metadata.pop("learner_source", None)
    course_metadata = metadata.get("course")
    nested = None
    if isinstance(course_metadata, dict):
        nested = course_metadata.pop("learner_source", None)
        if not course_metadata:
            metadata.pop("course", None)
    value = direct if direct is not None else nested
    if value is None:
        return None
    return "".join(value) if isinstance(value, list) else str(value)


def strip_solution_blocks(source: str) -> str:
    replacement_count = 0

    def replacement(match: re.Match[str]) -> str:
        nonlocal replacement_count
        replacement_count += 1
        indent = match.group("indent")
        return (
            f"{indent}# TODO: напишите решение этого шага.\n"
            f"{indent}pass\n"
        )

    stripped = SOLUTION_BLOCK.sub(replacement, source)
    if replacement_count == 0 and (BEGIN_MARKER in source or END_MARKER in source):
        raise ValueError("unbalanced solution markers")
    return stripped


def learner_from_solution(solution: dict[str, Any]) -> dict[str, Any]:
    learner = deepcopy(solution)
    course = learner.setdefault("metadata", {}).setdefault("course", {})
    course["variant"] = "learner"

    cells: list[dict[str, Any]] = []
    for original in learner.get("cells", []):
        cell = deepcopy(original)
        tags = metadata_tags(cell)
        if "solution-only" in tags:
            continue

        override = pop_learner_source(cell)
        if cell.get("cell_type") == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
            if override is not None:
                cell["source"] = override
            elif "exercise" in tags:
                cell["source"] = strip_solution_blocks(source_text(cell))
        elif override is not None:
            cell["source"] = override

        cells.append(cell)

    learner["cells"] = cells
    return learner


def normalized_bytes(notebook: dict[str, Any]) -> bytes:
    payload = json.dumps(
        notebook,
        ensure_ascii=False,
        indent=1,
        sort_keys=False,
    )
    return f"{payload}\n".encode("utf-8")


def validate_notebook(
    notebook: dict[str, Any],
    *,
    path: Path,
    expected_variant: str,
) -> list[str]:
    failures: list[str] = []
    label = path.relative_to(ROOT).as_posix()
    if notebook.get("nbformat") != 4:
        failures.append(f"{label}: nbformat must be 4")

    course = notebook.get("metadata", {}).get("course", {})
    required = {
        "arc": "part-2",
        "variant": expected_variant,
        "schema_version": 1,
    }
    for key, expected in required.items():
        if course.get(key) != expected:
            failures.append(f"{label}: metadata.course.{key} must be {expected!r}")
    if not re.fullmatch(r"II-0[1-6]", str(course.get("case_id", ""))):
        failures.append(f"{label}: invalid metadata.course.case_id")
    if not isinstance(course.get("dataset_ids"), list) or not course["dataset_ids"]:
        failures.append(f"{label}: metadata.course.dataset_ids must be non-empty")

    ids: list[str] = []
    all_tags: set[str] = set()
    for index, cell in enumerate(notebook.get("cells", [])):
        cell_id = cell.get("id")
        if not isinstance(cell_id, str) or not cell_id:
            failures.append(f"{label}: cell {index} has no stable id")
        else:
            ids.append(cell_id)
        tags = metadata_tags(cell)
        all_tags.update(tags)
        source = source_text(cell)
        if cell.get("cell_type") == "code":
            if cell.get("execution_count") is not None or cell.get("outputs", []):
                failures.append(f"{label}: code cell {cell_id or index} must have cleared output")
        if expected_variant == "learner":
            if "solution-only" in tags:
                failures.append(f"{label}: learner contains solution-only cell {cell_id or index}")
            if BEGIN_MARKER in source or END_MARKER in source:
                failures.append(f"{label}: learner contains solution marker in {cell_id or index}")
            metadata = cell.get("metadata", {})
            if "learner_source" in metadata or "learner_source" in metadata.get("course", {}):
                failures.append(f"{label}: learner_source leaked into learner cell {cell_id or index}")
        elif "exercise" in tags:
            metadata = cell.get("metadata", {})
            has_override = "learner_source" in metadata or "learner_source" in metadata.get("course", {})
            has_markers = BEGIN_MARKER in source and END_MARKER in source
            if not has_override and not has_markers:
                failures.append(
                    f"{label}: exercise cell {cell_id or index} needs markers or learner_source"
                )

    if len(ids) != len(set(ids)):
        failures.append(f"{label}: duplicate cell ids")
    for required_tag in ("bootstrap", "exercise", "validation"):
        if required_tag not in all_tags:
            failures.append(f"{label}: missing required cell tag {required_tag!r}")
    return failures


def read_notebook(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build(*, check: bool) -> list[str]:
    pairs = notebook_paths()
    failures: list[str] = []
    if len(pairs) != 6:
        failures.append(f"expected 6 solution notebooks, found {len(pairs)}")

    for solution_path, learner_path in pairs:
        solution = read_notebook(solution_path)
        failures.extend(
            validate_notebook(
                solution,
                path=solution_path,
                expected_variant="solution",
            )
        )
        try:
            expected_learner = learner_from_solution(solution)
        except ValueError as error:
            failures.append(f"{solution_path.relative_to(ROOT)}: {error}")
            continue

        expected = normalized_bytes(expected_learner)
        if check:
            if not learner_path.is_file() or learner_path.read_bytes() != expected:
                failures.append(
                    f"{learner_path.relative_to(ROOT)} is missing or stale; "
                    "run pnpm build:notebooks"
                )
        else:
            learner_path.write_bytes(expected)
            print(f"built {learner_path.relative_to(ROOT)}")

        if learner_path.is_file():
            learner = read_notebook(learner_path)
            failures.extend(
                validate_notebook(
                    learner,
                    path=learner_path,
                    expected_variant="learner",
                )
            )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build learner notebooks from canonical Part II solutions."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when learners are missing or stale",
    )
    arguments = parser.parse_args()
    failures = build(check=arguments.check)
    if failures:
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)
    if arguments.check:
        print("checked 6 Part II learner notebooks")


if __name__ == "__main__":
    main()
