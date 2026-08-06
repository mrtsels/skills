# Power Method SVD — Implementation Reference

From session 2026-07-27, Task 4 of quant-academy.

## Matrix Data Structure (Row-Major)

```cpp
struct Matrix {
    int rows, cols;
    std::vector<double> data;

    Matrix() : rows(0), cols(0) {}
    Matrix(int r, int c) : rows(r), cols(c), data(r * c, 0.0) {}
    Matrix(int r, int c, const std::vector<double>& d) : rows(r), cols(c), data(d) {
        if ((int)d.size() != r * c)
            throw std::invalid_argument("data size mismatch");
    }

    double& operator()(int i, int j) { return data[i * cols + j]; }
    const double& operator()(int i, int j) const { return data[i * cols + j]; }
    Matrix T() const { /* transpose into new Matrix */ }
};
```

## Linear Algebra Helpers

- `vec_dot(v1, v2)` — dot product
- `vec_norm(v)` — L2 norm
- `vec_normalize(v)` — unit vector (with zero-vector protection)
- `mat_mul(A, B)` — matrix multiplication (triple loop)
- `mat_vec_mul(A, v)` — matrix-vector multiply
- `mat_frobenius_norm(A)` — Frobenius norm

## Power Iteration Signatures

```cpp
auto [lambda, v] = power_iteration(AtA, max_iter=5000, tol=1e-10);
```

- Operates on A^T A (symmetric PSD) for SVD context
- Sign-flip convergence: `min(||b_next-b||, ||b_next+b||) < tol`
- Eigenvalue stagnation exit: if lambda stabilizes for 10+ iterations
- Zero-vector protection before normalization

## SVD Pipeline

```
for idx in 0..k:
    AtA = A_cur^T * A_cur
    (lambda, v) = power_iteration(AtA)
    sigma = sqrt(lambda)
    u = A_cur * v / sigma
    store u in U[:, idx], v in Vt[idx, :]
    A_cur -= sigma * u * v^T   (skip if sigma ≈ 0)
```

## Key Bug Fixes Encountered

1. **Re-seeding RNG**: `srand(42)` inside `power_iteration` causes same random vector every call → deflation collapses. Fix: seed once externally.
2. **Sign-flip convergence**: Without `min(diff, sum)` logic, power iteration appears to never converge on degenerate eigenvalues.
3. **Vt orthogonality axis**: Vt has orthonormal ROWS (V^T), so check `Vt @ Vt.T - I`, not `Vt.T @ Vt - I`.
4. **Partial SVD reconstruction error**: Rank-k approx of full-rank matrix is inherently lossy. Don't check reconstruction error for partial SVD.
5. **Rank-deficient orthogonality**: Zero vectors from deflation of zero-sigma components aren't orthogonal. Only check non-zero columns.

## pybind11 Module Build

```bash
cd cpp/ && mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_PREFIX_PATH=$(python3 -c "import pybind11; print(pybind11.get_cmake_dir())")
cmake --build .
```

Output: `python/power_svd.cpython-*.so`

## Validation Results (All Pass)

- 9 test cases × 6 metrics = 54/54 checks
- Full SVD reconstruction error: ~1e-16 (machine epsilon)
- U orthogonal error: < 1e-7 (all cases)
- Vt orthogonal error: < 1e-15 (all cases)
- All singular values non-negative and decreasing
- Matches NumPy within 1e-4
- No memory leak (0.3 MB delta over 10 calls)
