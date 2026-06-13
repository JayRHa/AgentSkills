---
name: workout-planner
description: Builds safe, progressive, personalized workout programs around a person's goal, experience level, available equipment, schedule, and constraints — with weekly splits, exercise selection, sets/reps, progression rules, and deload guidance. Use this skill when a user asks to "make me a workout plan", "build a training program", "gym routine for X days a week", "help me build muscle / lose fat / get stronger", "home workout with no equipment", or wants a push/pull/legs, upper/lower, or full-body split.
license: MIT
---

# Workout Planner

## Overview
This skill designs a structured, progressive training program tailored to the user's goal (strength, muscle, fat loss, endurance, general health), experience, equipment, days per week, and any limitations. It applies real training principles — progressive overload, appropriate volume, recovery, and periodization — rather than a random list of exercises.

**Keywords**: workout plan, training program, gym routine, strength training, hypertrophy, fat loss, push pull legs, upper lower, full body, home workout, bodyweight, progressive overload, sets and reps, deload.

## When to use vs. not
Use this to design or adjust a training program. **Not medical advice.** Always include a disclaimer: the user should clear new exercise with a doctor if they have injuries, cardiovascular conditions, are pregnant, or are returning from a long layoff. Defer to a physical therapist for rehab. Don't prescribe extreme calorie restriction or push through sharp pain.

## Inputs to gather first
1. **Primary goal** (strength / muscle / fat loss / endurance / general fitness) — one main goal beats three.
2. **Experience level** (beginner / intermediate / advanced) and any training history.
3. **Days per week** available and time per session.
4. **Equipment** (full gym / dumbbells only / bands / bodyweight / cardio machines).
5. **Constraints**: injuries, limitations, age, and recovery capacity.
6. **Preferences** (likes/dislikes, sports) to drive adherence.

## Workflow
1. **Confirm goal + reality.** Restate the goal and set honest expectations on timeline (e.g., meaningful strength in 8–12 weeks; body recomposition is slow). One primary goal drives the design.
2. **Pick the split** by days available and level. Beginners: full-body 3×/week. 4 days: upper/lower. 5–6 days: push/pull/legs. See `references/splits.md`.
3. **Select exercises.** Prioritize compound movements (squat, hinge, push, pull, carry) for the bulk of volume, accessories for weak points and balance. Match to available equipment with substitutions. See `references/exercise-library.md`.
4. **Set volume, sets, reps, and rest** by goal: strength (heavy, low reps, long rest), hypertrophy (moderate load/reps, moderate rest), endurance/fat-loss (higher reps, shorter rest, optional circuits). See `references/sets-reps-rest.md`.
5. **Define progression.** Give an explicit overload rule (add reps then load, double-progression, or % increases) so the plan advances week to week — this is what makes it work.
6. **Build the weekly schedule** with training days, rest days, and optional cardio/mobility. Balance push/pull and avoid training the same sore muscle two days running.
7. **Add warm-up, deload, and recovery guidance.** A 5–10 min warm-up template, a deload every 4–8 weeks, sleep/protein basics, and how to autoregulate on bad days.
8. **Make it trackable.** Provide a simple log format (exercise, sets×reps, load, RPE) and a check-in cadence to adjust the plan.

## Decision framework
| Goal | Rep range | Load | Rest | Weekly sets/muscle |
| --- | --- | --- | --- | --- |
| Strength | 3–6 | Heavy (80–90% 1RM) | 2–4 min | 10–15 |
| Hypertrophy | 6–12 | Moderate (65–80%) | 1–2 min | 12–20 |
| Endurance | 12–20+ | Light | 30–60 s | 10–15 |
| Fat loss | 8–15 + cardio | Moderate | Short / circuits | maintain to keep muscle |

| Days available | Suggested split |
| --- | --- |
| 2–3 | Full body |
| 4 | Upper / Lower |
| 5 | Upper/Lower + PPL hybrid |
| 6 | Push / Pull / Legs ×2 |

## Worked example
See `examples/ppl-4day.md` for a complete program for an intermediate lifter, 4 days/week, dumbbells + barbell, hypertrophy goal.

## Best Practices
- **Progressive overload is the engine** — every plan must define how load/reps increase.
- **Compounds first**, accessories after.
- **Recovery is part of training** — schedule rest, sleep, and deloads deliberately.
- **Adherence beats optimality** — the best plan is the one they'll actually do; build around preferences.
- **Form before weight.** Cue technique; progress load only when form holds.
- **Track everything** to know if it's working.

## Common Pitfalls
- **Too much volume too soon** → burnout and injury.
- **No progression scheme** → plateau.
- **Program-hopping** every week instead of running a plan for 8–12 weeks.
- **Neglecting one movement pattern** (all push, no pull) → imbalance/injury.
- **Ignoring pain** — sharp/joint pain means stop and reassess, not push through.
- **No warm-up** or skipping rest days.
- **Forgetting nutrition/sleep** drive most goals more than program tweaks.
