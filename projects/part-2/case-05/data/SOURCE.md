# Digits: provenance

- Dataset ID: `sklearn-digits-8x8-v1`
- Snapshot: `digits.csv`, exported from `sklearn.datasets.load_digits()` in `scikit-learn==1.9.0`
- Shape: 1,797 samples, 64 integer-valued pixel features, 10 classes
- Image shape: 8 × 8; pixel values range from 0 to 16
- Upstream dataset: Optical Recognition of Handwritten Digits, UCI Machine Learning Repository
- scikit-learn documentation: <https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html>
- UCI record: <https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits>

The notebook is offline and performs no mutable download. `freeze_digits.py`
documents the conversion from the embedded scikit-learn copy to a table with 64
pixel columns and the `digit` target. `dataset_manifest.json` and
`CHECKSUMS.sha256` record the SHA-256 of the exact CSV bytes. The notebook checks
that value, reads the CSV into a pandas `DataFrame`, and only then creates NumPy
arrays for modeling.
