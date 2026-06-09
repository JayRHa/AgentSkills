# Macro & Calorie Targets

Use this when the user does not supply calorie/macro numbers. Always state the inputs and assumptions you used.

## Step 1 — Basal Metabolic Rate (Mifflin-St Jeor)

Metric (kg, cm, years):

- Men:   BMR = 10 x weight_kg + 6.25 x height_cm - 5 x age + 5
- Women: BMR = 10 x weight_kg + 6.25 x height_cm - 5 x age - 161

Imperial conversion: kg = lb / 2.2046; cm = in x 2.54.

If sex is unspecified or the user prefers, average the two formulas (i.e., use the constant of -78 instead of +5 / -161).

## Step 2 — Total Daily Energy Expenditure (TDEE)

TDEE = BMR x activity factor.

| Activity level | Description | Factor |
|---|---|---|
| Sedentary | Desk job, little exercise | 1.2 |
| Light | Light exercise 1-3 days/wk | 1.375 |
| Moderate | Exercise 3-5 days/wk | 1.55 |
| Active | Hard exercise 6-7 days/wk | 1.725 |
| Very active | Physical job + training | 1.9 |

## Step 3 — Goal Adjustment

| Goal | Adjustment to TDEE |
|---|---|
| Fat loss (moderate) | -15% to -20% |
| Fat loss (aggressive, short term) | -25% (floor: not below ~1200 kcal women / ~1500 kcal men) |
| Maintenance | 0% |
| Lean gain | +10% to +15% |

Never recommend below the floor calories without telling the user to consult a professional.

## Step 4 — Macro Split

Protein first (it is the hard floor), then set fat, then carbs fill the rest.

Calories per gram: protein 4, carbs 4, fat 9, alcohol 7.

### Protein floor
- General health / maintenance: 1.6 g/kg bodyweight.
- Fat loss (preserve muscle): 1.8-2.2 g/kg.
- Muscle gain: 1.6-2.0 g/kg.
- Older adults: lean toward the higher end.

### Preset splits (% of calories: protein / carb / fat)

| Preset | Protein | Carb | Fat | Notes |
|---|---|---|---|---|
| Balanced | 30 | 40 | 30 | Default for most people |
| High-protein cut | 40 | 30 | 30 | Fat loss while training |
| Endurance / high-carb | 25 | 55 | 20 | Heavy cardio volume |
| Keto | 25 | 5 | 70 | <30-50 g net carbs/day |
| Low-fat | 30 | 50 | 20 | Personal preference / GI |
| Mediterranean | 25 | 45 | 30 | Emphasize olive oil, fish, legumes |

## Worked example

34-year-old woman, 68 kg, 165 cm, moderate activity, fat-loss goal, balanced-ish high-protein.

1. BMR = 10x68 + 6.25x165 - 5x34 - 161 = 680 + 1031.25 - 170 - 161 = 1380 kcal.
2. TDEE = 1380 x 1.55 = 2139 kcal.
3. Fat loss -18%: 2139 x 0.82 = ~1754 kcal target.
4. Protein floor 1.8 g/kg = 122 g (488 kcal). Fat 30% = 58 g (526 kcal). Carbs = remaining 740 kcal / 4 = 185 g.
5. Final daily target: ~1750 kcal, 122 P / 185 C / 58 F.

## Notes
- These are estimates. Adjust after 2 weeks based on real weight trend.
- Fiber target: ~14 g per 1000 kcal (so ~25-35 g/day for most plans).
- Add hydration and any alcohol into the energy budget if relevant.
