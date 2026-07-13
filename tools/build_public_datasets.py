"""Publish stable Part II dataset downloads and checksum sidecars."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public" / "datasets"
DATASETS = {
    "iris.csv": ROOT / "projects/part-2/case-01/data/iris.csv",
    "titanic.csv": ROOT / "projects/part-2/case-02/data/titanic.csv",
    "california_housing.csv": ROOT / "projects/part-2/case-04/data/california_housing.csv",
    "digits.csv": ROOT / "projects/part-2/case-05/data/digits.csv",
    "compass_digits_synthetic_captures.csv.gz": (
        ROOT / "projects/part-2/case-06/data/digits_compass.csv.gz"
    ),
}


def expected_files() -> dict[Path, bytes]:
    outputs: dict[Path, bytes] = {}
    for public_name, source in DATASETS.items():
        payload = source.read_bytes()
        destination = PUBLIC_DIR / public_name
        digest = hashlib.sha256(payload).hexdigest()
        outputs[destination] = payload
        outputs[destination.with_name(f"{public_name}.sha256")] = (
            f"{digest}  {public_name}\n".encode("ascii")
        )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = expected_files()

    if args.check:
        failures = [
            path.relative_to(ROOT).as_posix()
            for path, expected in outputs.items()
            if not path.is_file() or path.read_bytes() != expected
        ]
        if failures:
            for failure in failures:
                print(f"outdated public dataset: {failure}", file=sys.stderr)
            raise SystemExit(1)
        print(f"checked {len(DATASETS)} public datasets and checksum sidecars")
        return

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    for path, payload in outputs.items():
        path.write_bytes(payload)
    print(f"published {len(DATASETS)} public datasets to {PUBLIC_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
