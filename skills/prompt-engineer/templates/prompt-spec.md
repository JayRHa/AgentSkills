# Prompt Spec: <name>

> One spec per prompt artifact. Update on every iteration; keep history in the log.

## Intent
- **Task**: <one sentence>
- **Consumer**: <human | parser/code | downstream LLM>
- **Success criteria**: <measurable target, e.g., >=95% exact match>
- **Hard constraints**: <length / format / forbidden content>
- **Known failure modes**: <what went wrong before>

## Pattern & params
- **Pattern**: <extraction | classification | generation | transformation | decomposition | agentic | judge>
- **Temperature**: <value>  **top_p**: <value>  **max_tokens**: <value>  **stop**: <seq>
- **Reasoning scaffold**: <none | scratchpad | steps | ReAct>

## Prompt (current version: vX)
```
<system / full prompt text here, with {{placeholders}}>
```

## Output contract
```
<exact schema + one filled example, or N/A>
```

## Few-shot examples
- <count> shots; cover: <which edge cases / classes>

## Evaluation
- **Golden set**: <path>, <N cases>
- **Scorer**: <exact | contains | json | rubric/judge>
- **Command**: `python scripts/eval_prompts.py --golden <path> --prompt <file> --scorer <s>`

### Results log (one row per change; change ONE variable per row)
| Version | Date | Change made | Mean score | Notable regressions | Keep? |
|---|---|---|---|---|---|
| v1 | YYYY-MM-DD | baseline | 0.00 | - | - |
| v2 | YYYY-MM-DD | <the single change> | 0.00 | <case> | yes/no |

## Decision
- **Shipped version**: <vX>
- **Rationale**: <why this won>
