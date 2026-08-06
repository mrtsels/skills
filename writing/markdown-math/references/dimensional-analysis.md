# Dimensional Analysis Workflow (Buckingham Pi)

Recipe used in Assignment 3 — reusable for any quant assignment involving dimensional analysis.

---

## Steps

1. **List variables and their dimensions.** Write each dimension as a product of fundamental units raised to powers (e.g. $[Q] = S$, $[P] = U/S$).

2. **Build the dimensional matrix.** Rows = fundamental dimensions, columns = variables. Cell $(i,j)$ = exponent of dimension $i$ in variable $j$.

3. **Compute rank** $r$ of the matrix (number of linearly independent rows).

4. **Number of dimensionless groups** = $n - r$ where $n$ = number of variables.

5. **Solve for each group** $\pi$ by setting $[\pi] = 1$ and solving the exponent linear system.

6. **If the dependent variable $G$ has its own dimension**, form the inhomogeneous system $By = a$ where $a$ is $G$'s dimension vector. The solution is $y = y_p + \ker(B)$.

7. **General form:**
   $$
   G = (\text{particular monomial from } y_p) \times f(\text{kernel monomial from } \ker(B))
   $$

8. **To get specific power-law forms:**
   - Write $x = \lambda_1 h$ where $h$ spans $\ker(B)$
   - Write $y = y_p + \lambda_2 h$
   - Assume $f(z) = c \times z^\alpha$
   - Total exponent vector $= y_p + (\lambda_2 + \lambda_1\alpha) \cdot h$
   - Match componentwise to target exponents → solve for $T = \lambda_2 + \lambda_1\alpha$

9. **Check consistency.** If one variable demands $T_a$ and another demands $T_b \neq T_a$, the target cannot be expressed as a pure power law → use a general function $f$.

---

## Common Q3 Pattern (5 variables, 4 dimensions)

| Variable | Typical dim | Column in $B$ |
|----------|-------------|---------------|
| $Q$ (order size) | $S$ | $(1,0,0,0)$ |
| $P$ (price) | $U/(AS)$ | $(-1,1,0,-1)$ |
| $V$ (volume) | $S/T$ | $(1,0,-1,0)$ |
| $\sigma^2$ (sq. vol) | $A^2/T$ | $(0,0,-1,2)$ |
| $C$ (ex. cost) | $U$ | $(0,1,0,0)$ |
| $G$ (impact) | $A$ | target $a = (0,0,0,1)$ |

Kernel: $\ker(B) = \text{span}\{(3,2,-1,1,-2)\}$ — this gives the dimensionless argument $Q^3 P^2 \sigma^2/(V C^2)$.

Particular: $y_p = (-1,-1,0,0,1)$ — gives prefactor $C/(QP)$.
