#!/usr/bin/env python3
"""Summarize a unified diff to help size and risk-rank a code review.

Reads a unified diff (git diff / git show / gh pr diff output) from a file or
stdin and reports per-file churn plus heuristic risk hints (added lines that
match dangerous patterns: secrets, injection-prone calls, weak crypto, etc.).

This does NOT replace human review judgment; it points the reviewer at the
hunks most likely to contain Critical/High findings.

Usage:
    git diff main...HEAD | python3 diff_stats.py
    gh pr diff 123 | python3 diff_stats.py
    python3 diff_stats.py path/to/change.diff
    python3 diff_stats.py change.diff --json

Exit code is always 0; this is an advisory tool.
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field

# (label, compiled regex) applied to ADDED lines only.
RISK_PATTERNS = [
    ("secret", re.compile(r"(?i)(api[_-]?key|secret|passwd|password|token)\s*[:=]\s*['\"][^'\"]+")),
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("sql-concat", re.compile(r"(?i)(select|insert|update|delete)\b.*((\+\s*\w)|%\s|\.format\(|f['\"])")),
    ("shell-exec", re.compile(r"(?i)(os\.system|subprocess\.[a-z]+\(.*shell\s*=\s*True|child_process\.exec\(|\beval\(|\bexec\()")),
    ("deserialize", re.compile(r"(?i)(pickle\.load|yaml\.load\s*\((?!.*Loader)|unserialize\(|readObject\()")),
    ("weak-crypto", re.compile(r"(?i)\b(md5|sha1|DES|ECB)\b")),
    ("weak-random", re.compile(r"(?i)(math\.random|random\.random\(|random\.randint)")),
    ("xss-sink", re.compile(r"(?i)(innerHTML|dangerouslySetInnerHTML|\|\s*safe\b|v-html)")),
    ("todo-fixme", re.compile(r"(?i)\b(TODO|FIXME|HACK|XXX)\b")),
    ("broad-except", re.compile(r"(?i)(except\s*:|except\s+Exception\s*:|catch\s*\(\s*Exception)")),
    ("debug-leftover", re.compile(r"(?i)(console\.log\(|print\(|debugger;|binding\.pry)")),
]

HIGH_RISK = {"secret", "private-key", "sql-concat", "shell-exec", "deserialize", "weak-crypto"}


@dataclass
class FileStat:
    path: str
    added: int = 0
    removed: int = 0
    hits: list = field(default_factory=list)  # (label, lineno, text)

    @property
    def churn(self) -> int:
        return self.added + self.removed

    @property
    def risk_score(self) -> int:
        score = sum(5 if label in HIGH_RISK else 1 for label, _, _ in self.hits)
        score += self.churn // 50  # very large files are riskier to review
        return score


def parse_diff(text: str) -> list:
    files = []
    cur = None
    new_lineno = 0
    for raw in text.splitlines():
        if raw.startswith("diff --git"):
            m = re.search(r" b/(.+)$", raw)
            cur = FileStat(path=m.group(1) if m else "?")
            files.append(cur)
            continue
        if raw.startswith("+++ "):
            path = raw[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            if cur is not None and path not in ("/dev/null", ""):
                cur.path = path
            continue
        if raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            new_lineno = int(m.group(1)) if m else 0
            continue
        if cur is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            cur.added += 1
            content = raw[1:]
            for label, pat in RISK_PATTERNS:
                if pat.search(content):
                    cur.hits.append((label, new_lineno, content.strip()[:120]))
            new_lineno += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            cur.removed += 1
        else:
            new_lineno += 1
    return files


def render_text(files: list) -> str:
    if not files:
        return "No diff content detected on input."
    out = []
    total_a = sum(f.added for f in files)
    total_r = sum(f.removed for f in files)
    out.append(f"Diff summary: {len(files)} file(s), +{total_a}/-{total_r} lines\n")
    out.append(f"{'RISK':>4}  {'+ADD':>5} {'-DEL':>5}  FILE")
    out.append("-" * 64)
    for f in sorted(files, key=lambda x: x.risk_score, reverse=True):
        out.append(f"{f.risk_score:>4}  {f.added:>5} {f.removed:>5}  {f.path}")
    flagged = [f for f in files if f.hits]
    if flagged:
        out.append("\nRisk hints (review these added lines first):")
        for f in flagged:
            out.append(f"\n  {f.path}")
            for label, lineno, text in f.hits:
                marker = "!!" if label in HIGH_RISK else "  "
                out.append(f"   {marker} [{label}] :{lineno}  {text}")
    else:
        out.append("\nNo pattern-based risk hints. Still review logic, error paths, and tests manually.")
    out.append("\nReminder: pattern hits are advisory, not findings. Confirm by reading the code.")
    return "\n".join(out)


def render_json(files: list) -> str:
    return json.dumps(
        {
            "files": [
                {
                    "path": f.path,
                    "added": f.added,
                    "removed": f.removed,
                    "risk_score": f.risk_score,
                    "hits": [
                        {"label": l, "line": ln, "text": t} for l, ln, t in f.hits
                    ],
                }
                for f in sorted(files, key=lambda x: x.risk_score, reverse=True)
            ],
            "totals": {
                "files": len(files),
                "added": sum(f.added for f in files),
                "removed": sum(f.removed for f in files),
            },
        },
        indent=2,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize a unified diff for code review sizing.")
    ap.add_argument("diff", nargs="?", help="Path to a diff file. Reads stdin if omitted.")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = ap.parse_args()

    if args.diff:
        with open(args.diff, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    else:
        if sys.stdin.isatty():
            ap.error("no diff file given and stdin is empty; pipe a diff or pass a path")
        text = sys.stdin.read()

    files = parse_diff(text)
    print(render_json(files) if args.json else render_text(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
