# Embedded dataset checksum

`sklearn.datasets.load_digits()` is embedded in the installed scikit-learn
package, so this case does not redistribute a separate data file. In the pinned
`scikit-learn==1.9.0` environment, concatenate `X` as little-endian float64 C-order
bytes with `y` as little-endian int64 C-order bytes and calculate SHA-256:

```text
f6d9e39f37dc45d327f6db33428ee58970ccceabb2535a5c179de35886b70443
```

The solution notebook verifies this value before splitting the data.
