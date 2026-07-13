# California Housing: provenance

- Dataset ID: `sklearn-california-housing-1990-frozen-v1`
- Frozen with: `scikit-learn==1.9.0`, `fetch_california_housing(as_frame=True)`
- Rows: 20,640 California census block groups
- Predictors: eight numeric columns
- Target: `MedHouseVal`, median house value in units of USD 100,000
- Original data: 1990 United States Census; StatLib mirror
- Reference: R. Kelley Pace and Ronald Barry, “Sparse Spatial Autoregressions”, *Statistics and Probability Letters* 33 (1997), 291–297
- Loader documentation: <https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_california_housing.html>
- StatLib description: <https://www.dcc.fc.up.pt/~ltorgo/Regression/cal_housing.html>

`california_housing.csv` is a frozen offline conversion. The notebook must not
download mutable data. `dataset_manifest.json` records its shape, conversion
version and SHA-256 digest. The dataset has no missing values. The target is
top-coded at `5.00001` (a little above USD 500,000), which is an important
limitation of residual and high-price-slice analysis.

To audit the conversion, run `freeze_california_housing.py` in the pinned
environment and compare the generated digest. Network access is needed only for
that maintainer operation, never for the learner notebook.
