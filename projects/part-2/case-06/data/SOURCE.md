# Compass Digits synthetic captures: provenance

- Dataset ID: `compass-digits-synthetic-captures-v1`
- Source: `sklearn.datasets.load_digits()` from `scikit-learn==1.9.0`
- Generator: `generate_synthetic_captures.py`
- Random seed: 42
- Frozen derivative: `digits_compass.csv.gz`

## Important label

**Every image row in this derivative is an instructional synthetic stress
test.** It is not a natural scanner capture, not a production benchmark and not
evidence about a real vendor. The boolean column `instructional_synthetic` is
always true, and `synthetic_transform` describes the applied alteration.

For scanner batches A and B, each original source receives a stable random
source fingerprint and low Gaussian capture noise. Four related variants are
then deliberately divided across the vendor train and test rows. This makes a
row-wise split able to recognize sources it has effectively already seen.

Scanner C contains different source digits. Its images additionally receive a
documented one-pixel horizontal smear, contrast blend and stronger Gaussian
noise. Batch C is labeled `vendor_split=holdout` and must remain sealed until
model selection is complete.

`generation_report.json` records the frozen file digest and reference metrics.
The generator asserts that vendor-to-grouped and grouped-to-C macro-F1 gaps are
both at least 0.05 under the case's locked model.

Upstream documentation:
<https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html>
