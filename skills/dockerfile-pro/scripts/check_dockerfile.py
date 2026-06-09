#!/usr/bin/env python3
"""Static auditor for Dockerfile best practices (zero dependencies, stdlib only).

Flags common security, size, and reproducibility issues so you can fix them
before running hadolint/trivy. It is intentionally conservative and fast.

Usage:
    python3 check_dockerfile.py [PATH ...]
    python3 check_dockerfile.py Dockerfile
    python3 check_dockerfile.py            # defaults to ./Dockerfile

Exit codes:
    0  no errors (warnings may still be printed)
    1  one or more ERROR-level findings
    2  bad invocation / file not found

Findings are heuristic: review each in context. Not a substitute for hadolint
or a vulnerability scanner, but catches the highest-impact mistakes.
"""
import argparse
import os
import re
import sys

DIGEST_RE = re.compile(r"@sha256:[0-9a-f]{64}", re.IGNORECASE)
SECRET_ARG_RE = re.compile(
    r"\b(ARG|ENV)\s+.*?\b(\w*(SECRET|PASSWORD|PASSWD|TOKEN|APIKEY|API_KEY|"
    r"ACCESS_KEY|PRIVATE_KEY|CREDENTIAL)\w*)",
    re.IGNORECASE,
)


class Finding:
    def __init__(self, level, line_no, code, message):
        self.level = level  # "ERROR" or "WARN"
        self.line_no = line_no
        self.code = code
        self.message = message

    def __str__(self):
        loc = f"L{self.line_no}" if self.line_no else "-"
        return f"  [{self.level}] {self.code} ({loc}): {self.message}"


def logical_lines(raw_lines):
    """Yield (line_no, joined_instruction) handling backslash continuations."""
    buf = ""
    start = 0
    for i, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not buf and (not stripped or stripped.startswith("#")):
            continue
        if not buf:
            start = i
        if line.rstrip().endswith("\\"):
            buf += line.rstrip()[:-1] + " "
        else:
            buf += line
            yield start, buf.strip()
            buf = ""
    if buf:
        yield start, buf.strip()


def instruction_of(text):
    parts = text.split(None, 1)
    return (parts[0].upper(), parts[1] if len(parts) > 1 else "")


def is_exec_form(args):
    return args.lstrip().startswith("[")


def audit(path):
    findings = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        raw = fh.readlines()

    instrs = list(logical_lines(raw))
    from_lines = [(ln, a) for ln, t in instrs for i, a in [instruction_of(t)] if i == "FROM"]
    user_lines = [(ln, a) for ln, t in instrs for i, a in [instruction_of(t)] if i == "USER"]

    # Multi-stage check
    if len(from_lines) < 2:
        findings.append(Finding("WARN", from_lines[0][0] if from_lines else 0, "DFP001",
                                "Single-stage build: consider multi-stage to keep the "
                                "final image free of build tooling."))

    # Per-FROM: pin by digest, no :latest
    for ln, args in from_lines:
        base = args.split(" AS ")[0].split(" as ")[0].strip()
        if base.startswith("$") or base == "scratch":
            continue
        if not DIGEST_RE.search(base):
            findings.append(Finding("WARN", ln, "DFP002",
                                    f"Base '{base}' is not pinned by @sha256 digest "
                                    "(tags are mutable -> non-reproducible)."))
        if base.endswith(":latest") or (":" not in base and "@" not in base):
            findings.append(Finding("ERROR", ln, "DFP003",
                                    f"Base '{base}' uses 'latest'/no tag -> non-reproducible."))

    # Non-root: there must be a USER that is not root after the final FROM
    final_from_line = from_lines[-1][0] if from_lines else 0
    final_users = [a.strip() for ln, a in user_lines if ln > final_from_line]
    final_base = from_lines[-1][1].split(" AS ")[0].lower() if from_lines else ""
    distroless_nonroot = "nonroot" in final_base
    if not final_users and not distroless_nonroot:
        findings.append(Finding("ERROR", final_from_line, "DFP010",
                                "No USER set in the final stage: container runs as root."))
    elif final_users and final_users[-1].split(":")[0] in ("root", "0"):
        findings.append(Finding("ERROR", 0, "DFP011",
                                "Final USER is root/0: drop to a non-root user."))

    for ln, text in instrs:
        instr, args = instruction_of(text)

        # Secrets in ARG/ENV
        if instr in ("ARG", "ENV") and SECRET_ARG_RE.search(text):
            findings.append(Finding("ERROR", ln, "DFP020",
                                    "Possible secret in ARG/ENV (persists in image history). "
                                    "Use RUN --mount=type=secret instead."))

        # Copying .env files
        if instr in ("COPY", "ADD") and re.search(r"(^|\s)\.env(\s|$)", args):
            findings.append(Finding("ERROR", ln, "DFP021",
                                    "Copying a .env file bakes secrets into a layer."))

        # ADD for local files
        if instr == "ADD" and not re.search(r"https?://", args) and "--chmod" not in args:
            findings.append(Finding("WARN", ln, "DFP030",
                                    "Use COPY for local files; reserve ADD for remote URLs/tar."))

        # Shell-form CMD/ENTRYPOINT/HEALTHCHECK
        if instr in ("CMD", "ENTRYPOINT") and args and not is_exec_form(args):
            findings.append(Finding("ERROR", ln, "DFP031",
                                    f"{instr} uses shell form; use exec form [\"...\"] so PID 1 "
                                    "receives signals (graceful shutdown)."))
        if instr == "HEALTHCHECK" and "CMD" in args.upper():
            cmd_part = args.upper().split("CMD", 1)[1].strip()
            if cmd_part and not cmd_part.startswith("["):
                findings.append(Finding("WARN", ln, "DFP032",
                                        "HEALTHCHECK CMD uses shell form; prefer exec form."))

        # apt-get upgrade
        if instr == "RUN" and re.search(r"apt-get\s+(-y\s+)?upgrade|apk\s+upgrade", args):
            findings.append(Finding("WARN", ln, "DFP040",
                                    "Avoid 'upgrade' in builds; rebuild on a newer pinned base."))

        # apt-get install without cleanup or no-install-recommends
        if instr == "RUN" and "apt-get install" in args:
            if "--no-install-recommends" not in args:
                findings.append(Finding("WARN", ln, "DFP041",
                                        "apt-get install without --no-install-recommends (bloat)."))
            if "rm -rf /var/lib/apt/lists" not in args and \
               "--mount=type=cache" not in text:
                findings.append(Finding("WARN", ln, "DFP042",
                                        "apt cache not cleaned in same layer "
                                        "(rm -rf /var/lib/apt/lists/* or use a cache mount)."))

        # chmod 777
        if instr == "RUN" and re.search(r"chmod\s+-?R?\s*0?777", args):
            findings.append(Finding("WARN", ln, "DFP050",
                                    "chmod 777 grants world-write; scope permissions tightly."))

    # .dockerignore presence (relative to the Dockerfile dir)
    dockerignore = os.path.join(os.path.dirname(os.path.abspath(path)), ".dockerignore")
    if not os.path.exists(dockerignore):
        findings.append(Finding("WARN", 0, "DFP060",
                                "No .dockerignore next to the Dockerfile: context bloat / "
                                "risk of leaking .git and secrets."))

    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit a Dockerfile for best practices.")
    parser.add_argument("paths", nargs="*", default=["Dockerfile"],
                        help="Dockerfile path(s) (default: ./Dockerfile)")
    args = parser.parse_args(argv)
    paths = args.paths or ["Dockerfile"]

    had_error = False
    missing = True
    for path in paths:
        if not os.path.isfile(path):
            print(f"{path}: not found", file=sys.stderr)
            continue
        missing = False
        findings = audit(path)
        errors = [f for f in findings if f.level == "ERROR"]
        warns = [f for f in findings if f.level == "WARN"]
        had_error = had_error or bool(errors)

        print(f"\n{path}: {len(errors)} error(s), {len(warns)} warning(s)")
        for f in sorted(findings, key=lambda x: (x.level != "ERROR", x.line_no)):
            print(f)
        if not findings:
            print("  OK - no issues detected.")

    if missing:
        return 2
    return 1 if had_error else 0


if __name__ == "__main__":
    sys.exit(main())
