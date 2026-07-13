# Digits: provenance

- Dataset ID: `sklearn-digits-8x8-v1`
- Loader: `sklearn.datasets.load_digits()` in `scikit-learn==1.9.0`
- Shape: 1,797 samples, 64 integer-valued pixel features, 10 classes
- Image shape: 8 × 8; pixel values range from 0 to 16
- Upstream dataset: Optical Recognition of Handwritten Digits, UCI Machine Learning Repository
- scikit-learn documentation: <https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html>
- UCI record: <https://archive.ics.uci.edu/dataset/80/optical+recognition+of+handwritten+digits>

The data is embedded in scikit-learn, so the notebook is offline and performs no
mutable download. `dataset_manifest.json` records a content hash calculated by
concatenating little-endian float64 feature bytes and little-endian int64 target
bytes in C order. The notebook recomputes and verifies that hash before modeling.
