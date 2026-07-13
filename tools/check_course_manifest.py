"""Validate the shared course manifest against repository content."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "src" / "data" / "course.json"


def route_source(route: str) -> Path:
    stripped = route.strip("/")
    if stripped in {"cases", "bureau"}:
        return ROOT / "src" / "content" / "docs" / stripped / "index.md"
    return ROOT / "src" / "content" / "docs" / f"{stripped}.md"


def require_keys(
    value: dict[str, Any],
    keys: tuple[str, ...],
    *,
    label: str,
    failures: list[str],
) -> None:
    for key in keys:
        if key not in value:
            failures.append(f"{label}: missing {key!r}")


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    if data.get("schemaVersion") != 1:
        failures.append("schemaVersion must be 1")

    arcs = data.get("arcs", [])
    if [arc.get("id") for arc in arcs] != ["part-1", "part-2"]:
        failures.append("arcs must be ordered as part-1, part-2")

    seen_numbers: set[str] = set()
    seen_routes: set[str] = set()
    for arc in arcs:
        arc_id = str(arc.get("id"))
        require_keys(
            arc,
            ("title", "route", "theme", "prerequisite", "cases"),
            label=arc_id,
            failures=failures,
        )
        cases = arc.get("cases", [])
        if len(cases) != 6:
            failures.append(f"{arc_id}: expected 6 cases, found {len(cases)}")
        overview = route_source(str(arc.get("route", "")))
        if not overview.is_file():
            failures.append(f"{arc_id}: missing overview {overview.relative_to(ROOT)}")

        for item in cases:
            label = f"{arc_id}/{item.get('number', '?')}"
            require_keys(
                item,
                (
                    "number",
                    "slug",
                    "title",
                    "time",
                    "format",
                    "concepts",
                    "route",
                    "solutionRoute",
                    "projectPath",
                    "archive",
                    "notebooks",
                    "datasetIds",
                ),
                label=label,
                failures=failures,
            )
            number = str(item.get("number", ""))
            if number in seen_numbers:
                failures.append(f"{label}: duplicate case number")
            seen_numbers.add(number)
            for route_key in ("route", "solutionRoute"):
                route = str(item.get(route_key, ""))
                if route in seen_routes:
                    failures.append(f"{label}: duplicate route {route}")
                seen_routes.add(route)
                source = route_source(route)
                if not source.is_file():
                    failures.append(f"{label}: missing page {source.relative_to(ROOT)}")

            project = ROOT / str(item.get("projectPath", ""))
            archive = ROOT / str(item.get("archive", ""))
            if not project.is_dir():
                failures.append(f"{label}: missing project {project.relative_to(ROOT)}")
            if not archive.is_file():
                failures.append(f"{label}: missing archive {archive.relative_to(ROOT)}")
            if not item.get("concepts") or not item.get("datasetIds"):
                failures.append(f"{label}: concepts and datasetIds must be non-empty")

            notebooks = item.get("notebooks", {})
            if arc_id == "part-2":
                for variant in ("learner", "solution"):
                    notebook = notebooks.get(variant)
                    if not notebook or not (ROOT / notebook).is_file():
                        failures.append(f"{label}: missing {variant} notebook")
                        continue
                    notebook_data = json.loads((ROOT / notebook).read_text(encoding="utf-8"))
                    notebook_course = notebook_data.get("metadata", {}).get("course", {})
                    if notebook_course.get("case_id") != number:
                        failures.append(f"{label}: {variant} notebook case_id differs")
                    if notebook_course.get("dataset_ids") != item.get("datasetIds"):
                        failures.append(
                            f"{label}: {variant} notebook dataset_ids differ from manifest"
                        )

                for record_name in (
                    "data/dataset_manifest.json",
                    "data/generation_report.json",
                ):
                    record_path = project / record_name
                    if not record_path.is_file():
                        continue
                    record = json.loads(record_path.read_text(encoding="utf-8"))
                    record_id = record.get("dataset_id")
                    if record_id and record_id not in item.get("datasetIds", []):
                        failures.append(
                            f"{label}: {record_name} dataset_id differs from manifest"
                        )

                if archive.is_file():
                    sidecar = archive.with_suffix(f"{archive.suffix}.sha256")
                    if not sidecar.is_file():
                        failures.append(f"{label}: missing archive checksum sidecar")
                    else:
                        expected = sidecar.read_text(encoding="ascii").split()[0]
                        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
                        if expected != actual:
                            failures.append(f"{label}: archive checksum sidecar differs")
            elif any(notebooks.get(key) is not None for key in ("learner", "solution")):
                failures.append(f"{label}: Part I notebook values must be null")

    if failures:
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        raise SystemExit(1)
    print("checked course manifest: 2 arcs, 12 cases")


if __name__ == "__main__":
    main()
