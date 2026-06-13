#!/usr/bin/env python3
"""Evaluate and compare LLM prompt variants against a golden set.

This harness is provider-agnostic: you supply a `runner` (a Python callable
that takes a rendered prompt string and returns the model's output string).
A built-in `EchoRunner` lets you test the harness offline, and a sample
`make_anthropic_runner` shows how to wire a real API.

Golden set format (JSON file): a list of cases, each:
  {"input": "...", "expected": "...", "tags": ["edge"]}

Prompt template format: a text file containing the placeholder {{input}}.

Scoring: defaults to normalized exact match. Pass --scorer json to compare
parsed JSON objects field-by-field, or --scorer contains for substring match.

Usage:
  # Offline smoke test (echoes the input back):
  python eval_prompts.py --golden golden.json --prompt p1.txt --offline

  # Compare two prompts:
  python eval_prompts.py --golden golden.json --prompt a.txt --prompt b.txt \
      --scorer json

Exit code is 0 if at least one variant scored > 0, else 1.
"""
import argparse
import json
import re
import sys
from typing import Callable, List, Dict, Any


# --------------------------- Runners ---------------------------------------

def echo_runner(prompt: str) -> str:
    """Offline runner: returns the text after the last 'input:' marker, else the
    whole prompt. Useful for testing the harness wiring without an API."""
    m = re.search(r"(?is)input:\s*(.*)$", prompt)
    return (m.group(1) if m else prompt).strip()


def make_anthropic_runner(model: str = "claude-opus-4-8",
                          temperature: float = 0.0,
                          max_tokens: int = 1024) -> Callable[[str], str]:
    """Return a runner that calls the Anthropic Messages API.
    Requires `pip install anthropic` and ANTHROPIC_API_KEY in the env.
    """
    from anthropic import Anthropic  # imported lazily
    client = Anthropic()

    def run(prompt: str) -> str:
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text").strip()

    return run


# --------------------------- Scorers ---------------------------------------

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def score_exact(output: str, expected: str) -> float:
    return 1.0 if _norm(output) == _norm(expected) else 0.0


def score_contains(output: str, expected: str) -> float:
    return 1.0 if _norm(expected) in _norm(output) else 0.0


def _strip_fences(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
    s = re.sub(r"\n?```$", "", s)
    return s.strip()


def score_json(output: str, expected: str) -> float:
    """Field-by-field match over parsed JSON objects. Returns fraction of
    expected keys that match (1.0 = all match). Parse failure scores 0."""
    try:
        out = json.loads(_strip_fences(output))
        exp = json.loads(expected) if isinstance(expected, str) else expected
    except (json.JSONDecodeError, TypeError):
        return 0.0
    if not isinstance(out, dict) or not isinstance(exp, dict) or not exp:
        return 1.0 if out == exp else 0.0
    hits = sum(1 for k, v in exp.items() if out.get(k) == v)
    return hits / len(exp)


SCORERS = {"exact": score_exact, "contains": score_contains, "json": score_json}


# --------------------------- Eval ------------------------------------------

def render(template: str, case: Dict[str, Any]) -> str:
    out = template
    for k, v in case.items():
        out = out.replace("{{%s}}" % k, str(v))
    return out


def evaluate(template: str, cases: List[Dict[str, Any]],
             runner: Callable[[str], str],
             scorer: Callable[[str, str], float]) -> Dict[str, Any]:
    rows = []
    for i, case in enumerate(cases):
        prompt = render(template, case)
        try:
            output = runner(prompt)
        except Exception as e:  # noqa: BLE001 - report, don't crash the run
            output, err = "", str(e)
        else:
            err = None
        s = scorer(output, case.get("expected", "")) if err is None else 0.0
        rows.append({"i": i, "score": s, "tags": case.get("tags", []),
                     "output": output, "error": err})
    mean = sum(r["score"] for r in rows) / len(rows) if rows else 0.0
    return {"mean": mean, "rows": rows}


def tag_breakdown(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    by_tag: Dict[str, List[float]] = {}
    for r in rows:
        for t in (r["tags"] or ["<untagged>"]):
            by_tag.setdefault(t, []).append(r["score"])
    return {t: sum(v) / len(v) for t, v in by_tag.items()}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--golden", required=True, help="JSON golden-set file")
    p.add_argument("--prompt", action="append", required=True,
                   help="Prompt template file (repeat to compare variants)")
    p.add_argument("--scorer", choices=list(SCORERS), default="exact")
    p.add_argument("--offline", action="store_true",
                   help="Use the offline echo runner (no API calls)")
    p.add_argument("--model", default="claude-opus-4-8")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--show", type=int, default=0,
                   help="Print N failing cases per variant")
    args = p.parse_args(argv)

    with open(args.golden, encoding="utf-8") as f:
        cases = json.load(f)
    if not isinstance(cases, list) or not cases:
        print("Golden set must be a non-empty JSON list", file=sys.stderr)
        return 2

    runner = echo_runner if args.offline else make_anthropic_runner(
        args.model, args.temperature)
    scorer = SCORERS[args.scorer]

    any_positive = False
    results = []
    for path in args.prompt:
        with open(path, encoding="utf-8") as f:
            template = f.read()
        res = evaluate(template, cases, runner, scorer)
        results.append((path, res))
        any_positive = any_positive or res["mean"] > 0

    print("\n=== Prompt evaluation (%s scorer, %d cases) ===" %
          (args.scorer, len(cases)))
    for path, res in sorted(results, key=lambda r: -r[1]["mean"]):
        print("\n%-30s  mean=%.3f" % (path, res["mean"]))
        for tag, sc in sorted(tag_breakdown(res["rows"]).items()):
            print("    %-18s %.3f" % (tag, sc))
        if args.show:
            fails = [r for r in res["rows"] if r["score"] < 1.0][:args.show]
            for r in fails:
                exp = cases[r["i"]].get("expected", "")
                print("    FAIL #%d score=%.2f exp=%r got=%r%s" %
                      (r["i"], r["score"], exp, r["output"],
                       " err=%s" % r["error"] if r["error"] else ""))

    if len(results) > 1:
        best = max(results, key=lambda r: r[1]["mean"])
        print("\nWinner: %s (mean=%.3f)" % (best[0], best[1]["mean"]))

    return 0 if any_positive else 1


if __name__ == "__main__":
    raise SystemExit(main())
