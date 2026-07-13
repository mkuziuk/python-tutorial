"""Regenerate the frozen Iris CSV used by case II-01."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sklearn import __version__ as sklearn_version
from sklearn.datasets import load_iris


OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT = OUTPUT_DIR / "iris.csv"
MANIFEST = OUTPUT_DIR / "dataset_manifest.json"


def main() -> None:
    bunch = load_iris(as_frame=True)
    frame = bunch.frame.rename(columns={"target": "species_code"}).copy()
    feature_names = list(bunch.feature_names)
    class_names = [str(name) for name in bunch.target_names]
    frame["species_code"] = frame["species_code"].astype("int64")
    frame["species"] = frame["species_code"].map(dict(enumerate(class_names)))

    assert frame.shape == (150, 6)
    assert not frame.isna().any().any()
    frame.to_csv(OUTPUT, index=False, lineterminator="\n", float_format="%.1f")

    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    manifest = {
        "dataset_id": "sklearn-iris",
        "filename": OUTPUT.name,
        "rows": len(frame),
        "columns": len(frame.columns),
        "feature_names": feature_names,
        "target": "species_code",
        "classes": class_names,
        "sha256": digest,
        "scikit_learn_version": sklearn_version,
        "source_loader": "sklearn.datasets.load_iris",
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
