# Cointegration Pair Selection Workflow

## Step-by-step

1. **Get stock list** → AKShare or cached CSV
2. **Fetch daily data** → yfinance batch download, clear proxies
3. **Store in MongoDB** → InsertOne with `{_id: code_date}`
4. **Load price matrix** → Aggregation pipeline → pivot table
5. **Compute returns** → `np.log(prices / prices.shift(1))`
6. **Pearson correlation** → `returns.corr()`
7. **Distance matrix** → `1 - corr`, clamped to `[0, 2]`
8. **Hierarchical clustering** → Ward linkage, `fcluster(K)`
9. **Per-cluster pair search** → Filter by correlation > 0.3
10. **Engle-Granger test** → OLS residuals → ADF test
11. **Rank by zero-crossings** → Higher = more trading opportunities
12. **Trading signals** → Z-score of spread, ±2 entry, ±1 exit
13. **Risk management** → 2% per pair, max 20 concurrent, stop at |Z|>3 for 5 days
14. **Rolling backtest** → 2Y train + 1Y test, no overlap

## Key formulas

| Step | Formula |
|------|---------|
| Log returns | $R_{i,t} = \ln(P_{i,t} / P_{i,t-1})$ |
| Pearson r | $r_{ij} = \frac{\sum (R_{i,t} - \bar{R}_i)(R_{j,t} - \bar{R}_j)}{\sqrt{\sum (R_{i,t} - \bar{R}_i)^2 \sum (R_{j,t} - \bar{R}_j)^2}}$ |
| Distance | $d_{ij} = \sqrt{2(1 - r_{ij})}$ |
| OLS cointegration | $y_1 = \alpha + \beta y_2 + \epsilon$, ADF on $\epsilon$ |
| Z-score | $Z_t = (z_t - \mu(z)) / \sigma(z)$ |
| Zero-crossings | $\sum_{t=2}^T \mathbb{1}\{Z_t \cdot Z_{t-1} < 0\}$ |
