"""Regenerate the frozen Digits CSV used by case II-05."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from sklearn import __version__ as sklearn_version
from sklearn.datasets import load_digits


OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT = OUTPUT_DIR / "digits.csv"
MANIFEST = OUTPUT_DIR / "dataset_manifest.json"


def main() -> None:
    bunch = load_digits()
    pixel_columns = [f"pixel_{row}_{column}" for row in range(8) for column in range(8)]
    frame = pd.DataFrame(bunch.data.astype("uint8"), columns=pixel_columns)
    frame["digit"] = bunch.target.astype("uint8")

    assert frame.shape == (1_797, 65)
    assert not frame.isna().any().any()
    frame.to_csv(OUTPUT, index=False, lineterminator="\n")

    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    manifest = {
        "dataset_id": "sklearn-digits-8x8-v1",
        "filename": OUTPUT.name,
        "rows": len(frame),
        "columns": len(frame.columns),
        "features": len(pixel_columns),
        "feature_names": pixel_columns,
        "target": "digit",
        "classes": list(range(10)),
        "image_shape": [8, 8],
        "pixel_range": [0, 16],
        "sha256": digest,
        "scikit_learn_version": sklearn_version,
        "source_loader": "sklearn.datasets.load_digits",
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "CHECKSUMS.sha256").write_text(
        f"{digest}  {OUTPUT.name}\n", encoding="ascii"
    )
    print(f"Wrote {OUTPUT.name}: {digest}")


if __name__ == "__main__":
    main()
