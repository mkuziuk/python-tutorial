"""Regenerate the frozen California Housing CSV used by case II-04.

The notebook never calls this script. It is retained so maintainers can audit
the exact conversion from scikit-learn's fetcher to the offline snapshot.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sklearn import __version__ as sklearn_version
from sklearn.datasets import fetch_california_housing


OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT = OUTPUT_DIR / "california_housing.csv"
MANIFEST = OUTPUT_DIR / "dataset_manifest.json"


def main() -> None:
    bunch = fetch_california_housing(as_frame=True)
    frame = bunch.frame

    assert frame.shape == (20_640, 9)
    assert list(frame.columns) == [
        "MedInc",
        "HouseAge",
        "AveRooms",
        "AveBedrms",
        "Population",
        "AveOccup",
        "Latitude",
        "Longitude",
        "MedHouseVal",
    ]
    assert not frame.isna().any().any()

    frame.to_csv(OUTPUT, index=False, lineterminator="\n")
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    manifest = {
        "dataset_id": "sklearn-california-housing-1990-frozen-v1",
        "filename": OUTPUT.name,
        "rows": len(frame),
        "columns": len(frame.columns),
        "sha256": digest,
        "scikit_learn_version": sklearn_version,
        "target": "MedHouseVal",
        "target_unit": "100000 USD",
        "target_cap": 5.00001,
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT.name}: {digest}")


if __name__ == "__main__":
    main()
