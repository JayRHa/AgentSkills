# Clarity & Honesty Checklist

Run this before finalizing any chart. Every "No" is a defect to fix.

## A. The chart answers the question
- [ ] The chart type matches the intent (comparison / trend / distribution / relationship / part-to-whole / ranking / geo / flow).
- [ ] A first-time viewer gets the main point within ~5 seconds.
- [ ] The title states the **takeaway**, not just the variable. Good: "Churn fell to 2% after the redesign." Weak: "Churn rate."
- [ ] One primary message per chart. If there are two, split into small multiples.

## B. Axes & scales (honesty)
- [ ] **Bar charts start the value axis at zero.** Bar length must be proportional to value.
- [ ] Line charts use a sensible baseline; if non-zero, the focus is *change* and it is clearly labeled.
- [ ] No truncation, broken axes, or zoom that exaggerates small differences without disclosure.
- [ ] Axis scale type (linear vs log) is appropriate and labeled when log.
- [ ] No dual y-axes used to *imply* correlation between two series. (If two axes are unavoidable, state that scales are independent.)
- [ ] Consistent scales across small multiples so panels are comparable.

## C. Labels & units
- [ ] Both axes labeled with variable name and units (%, $, count, ms, etc.).
- [ ] Aggregation is stated (sum, mean, median, count) — a "mean" labeled as "value" is ambiguous.
- [ ] Number formatting is readable (thousands separators, sensible decimals, no 7-decimal noise).
- [ ] Sample size (n) shown where relevant (distributions, survey results, rates from small samples).
- [ ] Time axis direction is left-to-right and date format is unambiguous.

## D. Encoding choices
- [ ] Most important quantity uses the most accurate channel (position/length over area/color).
- [ ] Categorical bars are **sorted by value** unless order is inherent (time, age bands, Likert).
- [ ] Lines/series are **direct-labeled** or limited to ~5-7 to avoid legend hunting and spaghetti.
- [ ] Area/bubble size is not used where precise comparison is required.

## E. Color
- [ ] Color is used purposefully: categorical (distinct hues), sequential (single-hue ramp), diverging (two hues around a meaningful midpoint).
- [ ] No rainbow/jet ramp for sequential data (perceptually non-uniform).
- [ ] Color-vision-deficiency safe: not red/green-only; redundant encoding (labels, shapes, position) backs up color.
- [ ] Sufficient contrast between marks and background; text is legible.
- [ ] Color count is restrained (typically ≤ 7 categorical hues).

## F. Declutter (data-ink)
- [ ] No 3D effects, drop shadows, or skeuomorphic decoration that distort or distract.
- [ ] Gridlines are light/minimal; no heavy borders or background fills.
- [ ] No redundant elements (e.g., both a legend and direct labels for the same thing).
- [ ] Annotations (reference line, average, target, key events) add context where useful.

## G. Data integrity
- [ ] Missing data is handled honestly (gaps shown, not silently interpolated or dropped).
- [ ] Outliers are visible or explicitly noted, not clipped to flatter the story.
- [ ] Choropleths/maps use normalized rates, not raw counts, when population/area varies.
- [ ] Percentages have a clear denominator; parts of a whole actually sum to the whole.
- [ ] No cherry-picked time window that hides the broader trend.

## Quick deception smell-tests
1. Would the conclusion change if the y-axis started at zero? If yes and it's a bar chart, fix it.
2. Could a reader infer causation from a correlation shown here? If yes, add a caveat or remove the implication.
3. Are two unrelated series sharing a frame to suggest a link? Separate them.
4. Is the eye-catching difference real, or a scaling artifact? Recheck the scale.
