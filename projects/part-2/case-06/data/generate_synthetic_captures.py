"""Build the deterministic synthetic scanner-capture stress test for II-06.

This derivative is intentionally artificial. It creates related captures that
cross the vendor's row-wise split, plus an unseen scanner-C batch. It is designed
to teach validation leakage and distribution shift, not to emulate production
handwriting or benchmark model quality.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.datasets import load_digits
from sklearn.metrics import f1_score
from sklearn.model_selection import (
    StratifiedGroupKFold,
    cross_val_predict,
    train_test_split,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


RANDOM_STATE = 42
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT = OUTPUT_DIR / "digits_compass.csv.gz"
REPORT = OUTPUT_DIR / "generation_report.json"
PIXEL_COLUMNS = [f"pixel_{row}_{column}" for row in range(8) for column in range(8)]


def make_row(
    *,
    source_index: int,
    digit: int,
    variant_id: str,
    scanner_batch: str,
    vendor_split: str,
    transform: str,
    pixels: np.ndarray,
) -> dict[str, object]:
    source_id = f"digits-{source_index:04d}"
    row: dict[str, object] = {
        "sample_id": f"{source_id}-{variant_id}",
        "source_id": source_id,
        "variant_id": variant_id,
        "scanner_batch": scanner_batch,
        "vendor_split": vendor_split,
        "digit": int(digit),
        "instructional_synthetic": True,
        "synthetic_transform": transform,
    }
    row.update(dict(zip(PIXEL_COLUMNS, pixels.ravel(), strict=True)))
    return row


def build_frame() -> pd.DataFrame:
    digits = load_digits()
    indices = np.arange(len(digits.target))
    development_ids, batch_c_ids = train_test_split(
        indices,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=digits.target,
    )
    rng = np.random.default_rng(RANDOM_STATE)
    rows: list[dict[str, object]] = []

    # Each A/B source has four very similar captures. Two go to vendor train
    # and two to vendor test, so source identity leaks across the boundary.
    schedule = [
        ("a-train", "A", "train"),
        ("b-train", "B", "train"),
        ("a-test", "A", "test"),
        ("b-test", "B", "test"),
    ]
    for source_index in development_ids:
        source_fingerprint = rng.uniform(0.0, 16.0, size=(8, 8))
        base_capture = 0.5 * digits.images[source_index] + 0.5 * source_fingerprint
        for variant_id, scanner_batch, vendor_split in schedule:
            pixels = np.clip(
                base_capture + rng.normal(0.0, 0.3, size=(8, 8)),
                0.0,
                16.0,
            )
            rows.append(
                make_row(
                    source_index=int(source_index),
                    digit=int(digits.target[source_index]),
                    variant_id=variant_id,
                    scanner_batch=scanner_batch,
                    vendor_split=vendor_split,
                    transform="synthetic source fingerprint + low Gaussian capture noise",
                    pixels=pixels,
                )
            )

    # Batch C contains entirely new sources and a documented horizontal smear,
    # contrast blend and stronger noise. It is sealed until model selection.
    for source_index in batch_c_ids:
        source_fingerprint = rng.uniform(0.0, 16.0, size=(8, 8))
        base_capture = 0.5 * digits.images[source_index] + 0.5 * source_fingerprint
        shifted = np.roll(base_capture, 1, axis=1)
        pixels = np.clip(
            0.55 * base_capture
            + 0.45 * shifted
            + rng.normal(0.0, 2.5, size=(8, 8)),
            0.0,
            16.0,
        )
        rows.append(
            make_row(
                source_index=int(source_index),
                digit=int(digits.target[source_index]),
                variant_id="c-shift",
                scanner_batch="C",
                vendor_split="holdout",
                transform="synthetic scanner-C horizontal smear + strong Gaussian noise",
                pixels=pixels,
            )
        )

    frame = pd.DataFrame(rows)
    return frame.sort_values("sample_id").reset_index(drop=True)


def locked_model():
    return make_pipeline(
        StandardScaler(),
        SVC(C=2, gamma="scale", kernel="rbf"),
    )


def audit_metrics(frame: pd.DataFrame) -> dict[str, float]:
    development = frame.loc[frame["scanner_batch"].isin(["A", "B"])].copy()
    batch_c = frame.loc[frame["scanner_batch"].eq("C")].copy()
    x_development = development[PIXEL_COLUMNS].to_numpy()
    y_development = development["digit"].to_numpy()
    groups = development["source_id"].to_numpy()

    vendor_train = development["vendor_split"].eq("train").to_numpy()
    vendor_test = development["vendor_split"].eq("test").to_numpy()
    model = locked_model()
    model.fit(x_development[vendor_train], y_development[vendor_train])
    vendor_f1 = f1_score(
        y_development[vendor_test],
        model.predict(x_development[vendor_test]),
        average="macro",
    )

    grouped_cv = StratifiedGroupKFold(
        n_splits=3,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    grouped_predictions = cross_val_predict(
        locked_model(),
        x_development,
        y_development,
        groups=groups,
        cv=grouped_cv,
        n_jobs=1,
    )
    grouped_f1 = f1_score(y_development, grouped_predictions, average="macro")

    model.fit(x_development, y_development)
    batch_c_f1 = f1_score(
        batch_c["digit"],
        model.predict(batch_c[PIXEL_COLUMNS].to_numpy()),
        average="macro",
    )
    return {
        "vendor_macro_f1": float(vendor_f1),
        "grouped_macro_f1": float(grouped_f1),
        "batch_c_macro_f1": float(batch_c_f1),
        "vendor_to_grouped_gap": float(vendor_f1 - grouped_f1),
        "grouped_to_batch_c_gap": float(grouped_f1 - batch_c_f1),
    }


def write_deterministic_gzip(frame: pd.DataFrame) -> None:
    csv_bytes = frame.to_csv(
        index=False,
        float_format="%.6f",
        lineterminator="\n",
    ).encode("utf-8")
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", compresslevel=9, mtime=0) as stream:
        stream.write(csv_bytes)
    OUTPUT.write_bytes(buffer.getvalue())


def main() -> None:
    frame = build_frame()
    assert frame["sample_id"].is_unique
    assert frame["instructional_synthetic"].all()
    assert set(frame["scanner_batch"]) == {"A", "B", "C"}
    assert set(frame["vendor_split"]) == {"train", "test", "holdout"}

    # Round-trip through the frozen six-decimal representation before checking
    # the contractual gaps, so the report describes exactly what learners use.
    write_deterministic_gzip(frame)
    frozen = pd.read_csv(OUTPUT)
    metrics = audit_metrics(frozen)
    assert metrics["vendor_to_grouped_gap"] >= 0.05
    assert metrics["grouped_to_batch_c_gap"] >= 0.05

    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    report = {
        "dataset_id": "compass-digits-synthetic-captures-v1",
        "instructional_synthetic_stress_test": True,
        "source_dataset": "sklearn-digits-8x8-v1",
        "random_state": RANDOM_STATE,
        "rows": len(frozen),
        "sources": int(frozen["source_id"].nunique()),
        "pixel_columns": len(PIXEL_COLUMNS),
        "sha256": digest,
        **metrics,
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
