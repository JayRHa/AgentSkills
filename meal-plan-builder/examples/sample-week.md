# Worked Example: 7-Day Plan

## Intake (as given)
One adult woman, 34, 68 kg, 165 cm, moderate activity, goal = moderate fat loss. Pescatarian (eats fish + eggs + dairy, no other meat). No nut allergy. Budget ~50 USD/week. ~25 min weeknight cook time, willing to batch-prep Sunday. Has oven + stove + blender. Plan breakfast, lunch, dinner, 1 snack, 7 days.

## Targets & Assumptions
Using Mifflin-St Jeor (see references/macro-targets.md):
- BMR = 1380, TDEE (x1.55) = 2139, fat loss -18% -> **~1750 kcal/day**.
- Macros: **122 g protein / 185 g carbs / 58 g fat** (protein floor 1.8 g/kg).
- Assumptions: 1 serving per meal; pantry has salt, pepper, olive oil, common spices, soy sauce.

## Strategy
- Anchor proteins: eggs, canned tuna/salmon, Greek yogurt, tofu.
- Anchor carbs: oats, brown rice, potatoes.
- Shared base: onion + garlic + lemon + olive oil; plus a soy-ginger base for the stir-fry night.
- Repeat breakfast (oats or yogurt bowl). Lunches are mostly dinner leftovers. 5 distinct dinners.

## Weekly Grid (per-serving kcal shown; full macros tracked in plan.json)

| Day | Breakfast | Lunch | Dinner | Snack | Day total |
|-----|-----------|-------|--------|-------|-----------|
| Mon | Oats + berries + yogurt (430) | Tuna-white-bean salad (480) | Salmon, roasted potatoes, broccoli (640) | Apple + yogurt (200) | ~1750 |
| Tue | Yogurt + oats + seeds (420) | Leftover salmon grain bowl (500) | Tofu veg stir-fry + rice (610) | Cottage cheese + fruit (210) | ~1740 |
| Wed | Oats + berries (430) | Leftover stir-fry (520) | Veg + chickpea frittata + salad (580) | Yogurt (210) | ~1740 |
| Thu | Yogurt bowl (420) | Leftover frittata + bread (510) | Lemon-garlic shrimp pasta (640) | Apple + cheese (190) | ~1760 |
| Fri | Oats + seeds (430) | Tuna-white-bean salad (480) | Flex: leftovers / eat out (~640) | Yogurt (200) | ~1750 |
| Sat | Egg + veg scramble + toast (450) | Big grain + roasted veg bowl (520) | Salmon tacos, cabbage slaw (600) | Fruit + nuts (190) | ~1760 |
| Sun | Egg scramble + toast (450) | Leftover taco bowl (520) | Tofu stir-fry round 2 (600) | Yogurt + fruit (190) | ~1760 |

Weekly average/day: ~1750 kcal, ~124 P / ~182 C / ~57 F (within tolerance).

## plan.json (feed to scripts/plan_calc.py)
```json
{
  "targets": {"calories": 1750, "protein": 122, "carbs": 185, "fat": 58},
  "days": {
    "Monday": [
      {"name": "Oats+berries+yogurt", "protein": 24, "carbs": 58, "fat": 11},
      {"name": "Tuna white-bean salad", "protein": 35, "carbs": 42, "fat": 16},
      {"name": "Salmon+potato+broccoli", "protein": 42, "carbs": 55, "fat": 22},
      {"name": "Apple+yogurt", "protein": 15, "carbs": 28, "fat": 3}
    ],
    "Tuesday": [
      {"name": "Yogurt oats seeds", "protein": 24, "carbs": 54, "fat": 12},
      {"name": "Salmon grain bowl", "protein": 34, "carbs": 52, "fat": 16},
      {"name": "Tofu stir-fry+rice", "protein": 28, "carbs": 78, "fat": 16},
      {"name": "Cottage cheese+fruit", "protein": 18, "carbs": 22, "fat": 4}
    ]
  }
}
```
Running `python3 scripts/plan_calc.py plan.json` totals each day and flags any below the 122 g protein floor or outside +/-5% of 1750 kcal.

## Batch-Prep Schedule (Sunday, ~60 min)
1. Oven: roast 2 trays vegetables (broccoli, peppers, onion) + potatoes.
2. Stove: cook a pot of brown rice; hard-boil nothing (use fresh eggs as needed).
3. Mix: lemon-garlic-olive-oil dressing; soy-ginger sauce; cabbage slaw.
4. Portion: tuna-white-bean salad x2; rice into containers; wash berries.
Storage: rice/veg/salad -> fridge (3-4 days); freeze Thu+Fri shrimp portions if not cooking until late week. Label all containers with date.

## Grocery List (by aisle)
**Produce**: broccoli (2 heads), bell peppers (3), onions (3), garlic (1 bulb), lemons (3), potatoes (1 kg), cabbage (1 small), mixed berries (1 punnet), apples (4), banana (1 bunch)
**Meat & Seafood**: salmon fillets (4 = ~600 g), shrimp (250 g)
**Dairy & Eggs**: Greek yogurt (1 kg tub), cottage cheese (1 tub), eggs (1 dozen), block cheese (small), milk (small)
**Frozen**: frozen mixed veg (1 bag, backup)
**Canned & Jarred**: tuna (3 cans), white beans (2 cans), chickpeas (1 can)
**Dry Goods & Grains**: brown rice (1 bag), rolled oats (1 bag), pasta (1 box), bread (1 loaf), corn tortillas (1 pack), mixed seeds (small bag)
**Deli & Prepared**: firm tofu (2 blocks)
**Pantry Staples (check first)**: olive oil, soy sauce, salt, pepper, garlic powder, paprika

Estimated cost: ~48 USD (within budget). Flex slot Friday covers eating out or clearing leftovers.

## Swaps & Notes
- No fish that day? Swap salmon for an extra tofu or egg dish (keep protein >= floor).
- Dairy-free version: replace Greek yogurt/cottage cheese with soy yogurt + extra tofu; recheck protein.
- Reheat all cooked items to steaming hot; eat dressed salads same day.
