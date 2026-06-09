# Worked Example: "Make me a chart of sales"

This walks a vague request through the full workflow to a clean, honest spec.

## 1. The raw request
> "I have sales per region for this year and last year. Can you make a chart? Maybe a pie?"

The user proposed a pie, but we verify intent and data shape before committing.

## 2. Identify intent
The user wants to know **which regions sell the most** and **how each changed vs last year**. That is primarily **comparison** (across regions), with a secondary **before/after** angle. It is *not* part-to-whole — they care about ranking magnitudes, not each region's share of the total. So a pie is the wrong tool.

## 3. Profile the data

| Column | Type | Cardinality | Sums to total? |
|---|---|---|---|
| region | categorical | 9 | (n/a) |
| sales_this_year | quantitative | — | yes, but not the question |
| sales_last_year | quantitative | — | — |

9 categories with two values each.

## 4. Match intent + shape to a chart
From `references/chart-decision-matrix.md`:
- Comparison, 1 Cat (9, would be fine vertically but labels are region names) + 2 Quant before/after → **slope chart / dumbbell** is the cleanest for before vs after; **grouped horizontal bar** is the familiar runner-up.
- 9 regions with long names → horizontal orientation.

**Choice:** Dumbbell (connected-dot) chart, one row per region, two dots (last year, this year) joined by a line. It shows ranking, magnitude, and change at once. Grouped horizontal bar is the safe alternative for a general audience.

Programmatic check:

```
python3 scripts/suggest_chart.py --intent comparison \
    --col region:categorical:9 --col sales:quantitative
```

Output:

```
Intent: comparison
Columns: region (categorical, n=9), sales (quantitative)

  Recommended : Bar chart
  Runner-up   : Lollipop / dot plot
  Encodings   :
    - axis = category
    - length = quantitative value
    - sort bars by value
  Notes       :
    - Start the value axis at zero — bar length encodes magnitude.
```

The script recommends a bar (single-value comparison). Because we have a **before/after** pair, we upgrade to a dumbbell, which the matrix lists for "1 Cat + 2 Quant (before/after)".

## 5. Clean, honest spec

```
Chart type : Dumbbell (horizontal)
Rows       : region, sorted by sales_this_year descending
x-axis     : Sales (USD, $) — starts at 0
Marks      : open dot = last year, filled dot = this year, connector line
Color      : last year = gray, this year = brand blue (CVD-safe pair; not red/green)
Labels     : direct value labels on each "this year" dot; region names on y-axis
Annotation : vertical reference line at company average; arrow callouts on the
             two regions with the biggest swings
Title      : "West and South drove this year's growth; Midwest slipped 8%"
Units      : axis labeled "Sales (USD)"; aggregation noted as "total sales"
```

## 6. Critique against the checklist
From `references/clarity-and-honesty-checklist.md`:
- [x] Type matches intent (comparison + change).
- [x] x-axis starts at zero (these are magnitudes).
- [x] Sorted by value, direct-labeled, units shown.
- [x] Color pair is colorblind-safe and not red/green.
- [x] Title states the takeaway.
- [x] No pie (parts don't answer the ranking question).

## 7. Why not the pie?
A pie of 9 regions forces angle comparisons across nearly-equal slices and cannot show year-over-year change at all. The dumbbell answers both questions in one glance and reads honestly.
