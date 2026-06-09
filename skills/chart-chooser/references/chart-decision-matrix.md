# Chart Decision Matrix

Use this after identifying (1) the question intent and (2) the data shape. Find your intent row, then narrow by data shape. "Primary" is the default; "Runners-up" are valid alternatives; "Avoid" lists common wrong choices.

## Legend for data shape
- **Cat** = categorical, **Ord** = ordinal, **Quant** = quantitative (numeric), **Temp** = temporal (date/time), **Geo** = geographic.
- **Cardinality** = number of distinct values in a categorical/temporal field.

---

## 1. Comparison (which categories are larger/smaller)

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| 1 Cat (≤ ~12) + 1 Quant | Vertical bar | Lollipop, dot plot | Pie (unless part-to-whole) |
| 1 Cat (many / long labels) + 1 Quant | Horizontal bar (sorted) | Lollipop | Vertical bar (labels collide) |
| 2 Cat + 1 Quant | Grouped bar | Small multiples of bars, heatmap | Stacked bar (hard to compare non-base segments) |
| 1 Cat + 2 Quant (before/after) | Slope chart / dumbbell | Grouped bar | Two separate charts |

**Note:** Always sort bars by value unless the category has a natural order. Start the value axis at zero.

---

## 2. Trend / change over time

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| 1 Temp + 1 Quant | Line | Area (if magnitude/volume matters), bar (few discrete periods) | Pie, scatter |
| 1 Temp + 1 Quant, few periods (≤ ~8) | Column (bar) | Line | — |
| 1 Temp + several Quant series (≤ ~5) | Multi-line (direct-labeled) | Small multiples | Spaghetti (too many lines) |
| 1 Temp + many series | Small multiples | Highlighted line (focus one, gray others) | Single overcrowded line chart |
| 1 Temp + parts of a whole | Stacked area | 100% stacked area (if share matters), streamgraph | Stacked area with many wiggly parts |

**Note:** Line baselines may be non-zero when *change* is the message — label clearly. Keep time on the x-axis, left-to-right.

---

## 3. Distribution (shape/spread/outliers of one quantitative variable)

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| 1 Quant | Histogram | Density plot, dot/strip plot (small n) | Bar chart of raw values |
| 1 Quant across groups (1 Cat) | Box plot or violin | Strip/jitter plot, ridgeline | Bar of means alone (hides spread) |
| 1 Quant, cumulative view | ECDF / cumulative curve | Histogram | — |

**Note:** Choose histogram bin width deliberately; too wide hides structure, too narrow adds noise. Show n. Bar-of-means hides variance — prefer box/violin or overlay points.

---

## 4. Relationship / correlation (two+ numeric variables)

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| 2 Quant | Scatter plot | Hexbin/2D-density (large n, overplotting) | Line (unless ordered by x) |
| 2 Quant + 1 Cat | Scatter colored by category | Faceted scatter (small multiples) | Too many colors |
| 3 Quant | Bubble (3rd = size) carefully | Scatter + color for 3rd | Bubble for precise reads |
| Many Quant (pairwise) | Correlation heatmap | Scatterplot matrix (SPLOM) | Single overloaded chart |

**Note:** Add a trend/regression line only if a real relationship exists and the fit is labeled. Beware overplotting — use transparency, jitter, or binning. Correlation is not causation; do not imply it.

---

## 5. Part-to-whole (composition of a single total)

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| 1 Cat (≤4 slices, clearly different) + 1 Quant summing to 100% | Pie / donut (acceptable) | Single stacked bar | Pie with >5 slices |
| 1 Cat (5+ parts) | Sorted horizontal bar | Treemap (hierarchy/space-fill) | Pie |
| Hierarchical parts | Treemap | Sunburst, icicle | Nested pies |
| Composition over time | 100% stacked area/bar | Stacked area | — |

**Note:** Part-to-whole requires parts that meaningfully sum to a total. If they don't sum, it's a comparison, not composition — use a bar. Prefer a bar over a pie whenever precise comparison matters.

---

## 6. Ranking

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| 1 Cat + 1 Quant, order matters | Sorted horizontal bar | Lollipop, ordered dot plot | Unsorted bar, pie |
| Rank change over time | Bump chart / slope chart | Multi-line | Cluttered table |

---

## 7. Geospatial

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| Geo region + 1 Quant (rate/normalized) | Choropleth | Symbol/bubble map | Choropleth of raw counts (population bias) |
| Geo points + value | Symbol/proportional bubble map | Dot density | Choropleth for point events |

**Note:** Choropleths should map normalized rates (per capita, per area), not raw counts, to avoid "more people = darker" artifacts.

---

## 8. Flow / stages

| Data shape | Primary | Runners-up | Avoid |
|---|---|---|---|
| Stage-to-stage drop-off | Funnel | Bar chart of stages | Pie |
| Flows between nodes | Sankey | Chord diagram | Overloaded network |

---

## Tie-breakers
1. Pick the chart that answers the **single most important question** fastest.
2. Prefer position/length encodings over angle/area for quantitative accuracy.
3. Prefer the **simplest** chart that works; complexity must earn its place.
4. If two charts tie, choose the one your audience reads most fluently (bars and lines beat exotic forms for general audiences).
