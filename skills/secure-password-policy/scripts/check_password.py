#!/usr/bin/env python3
"""Password policy checker aligned with NIST SP 800-63B.

Validates a candidate password against NIST-style memorized-secret rules and,
optionally, screens it against the Have I Been Pwned (HIBP) breach corpus using
the k-anonymity range API (only the first 5 hex chars of the SHA-1 are sent).

Standard library only.

Usage:
    # Read password from stdin (recommended — keeps it out of shell history):
    echo -n 'correct horse battery staple' | python3 check_password.py --stdin

    # Provide context terms to reject (site/user/email) and enforce a longer min:
    python3 check_password.py --stdin --min-length 12 \\
        --context acme --context alice --context alice@acme.com

    # Skip the online breach check (offline only):
    python3 check_password.py --stdin --no-hibp

Exit codes: 0 = acceptable, 1 = rejected, 2 = usage/error.
"""
import argparse
import getpass
import hashlib
import sys
import urllib.error
import urllib.request

HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/"

# A small embedded blocklist of extremely common passwords. In production, screen
# against a large dictionary (e.g. the top 100k+ list) loaded from a file.
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "12345678", "111111",
    "1234567890", "123123", "abc123", "password1", "iloveyou", "admin",
    "welcome", "monkey", "letmein", "dragon", "passw0rd", "p@ssw0rd",
    "qwerty123", "1q2w3e4r", "sunshine", "princess", "login", "starwars",
}


def has_repetition(pw: str, run: int = 4) -> bool:
    """True if the password contains a repeated single char run of length >= run."""
    count = 1
    for i in range(1, len(pw)):
        count = count + 1 if pw[i] == pw[i - 1] else 1
        if count >= run:
            return True
    return False


def has_sequence(pw: str, run: int = 4) -> bool:
    """True if the password contains an ascending/descending run (e.g. 1234, abcd)."""
    low = pw.lower()
    asc = desc = 1
    for i in range(1, len(low)):
        delta = ord(low[i]) - ord(low[i - 1])
        asc = asc + 1 if delta == 1 else 1
        desc = desc + 1 if delta == -1 else 1
        if asc >= run or desc >= run:
            return True
    return False


def hibp_breach_count(pw: str, timeout: float = 6.0) -> int:
    """Return how many times pw appears in HIBP via k-anonymity. -1 if unavailable."""
    sha1 = hashlib.sha1(pw.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    req = urllib.request.Request(
        HIBP_RANGE_URL + prefix,
        headers={"User-Agent": "secure-password-policy-skill", "Add-Padding": "true"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError):
        return -1
    for line in body.splitlines():
        candidate, _, count = line.partition(":")
        if candidate.strip() == suffix:
            try:
                return int(count.strip())
            except ValueError:
                return 1
    return 0


def check(pw: str, min_length: int, contexts, use_hibp: bool):
    """Return (ok: bool, issues: list[str], notes: list[str])."""
    issues, notes = [], []

    if len(pw) < min_length:
        issues.append(f"too short: {len(pw)} chars (minimum {min_length}).")
    if len(pw) > 1024:
        issues.append("absurdly long (>1024 chars); cap maximum at a sane value like 256.")

    low = pw.lower().strip()
    if low in COMMON_PASSWORDS:
        issues.append("appears on the common-password blocklist.")
    for term in contexts:
        term = term.strip().lower()
        if not term:
            continue
        # Compare against the full context term and its email local-part.
        local = term.split("@")[0]
        if term and term in low:
            issues.append(f"contains context-specific term: '{term}'.")
        elif local and local != term and local in low:
            issues.append(f"contains context-specific term: '{local}'.")

    if has_repetition(pw):
        issues.append("contains a long run of repeated characters (e.g. 'aaaa').")
    if has_sequence(pw):
        issues.append("contains a sequential run (e.g. '1234' or 'abcd').")

    if use_hibp:
        count = hibp_breach_count(pw)
        if count > 0:
            issues.append(f"found in {count:,} known breaches (HIBP). Choose another.")
        elif count == 0:
            notes.append("not found in HIBP breach corpus.")
        else:
            notes.append("HIBP check skipped (network unavailable).")

    # Informational only — NIST does NOT require composition; we never fail on it.
    if len(pw) >= 15:
        notes.append("length >= 15 — strong; passphrases of this length are encouraged.")

    return (len(issues) == 0, issues, notes)


def main(argv=None):
    p = argparse.ArgumentParser(description="NIST 800-63B password policy checker.")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--stdin", action="store_true",
                     help="read the password from stdin (no echo via pipe).")
    src.add_argument("--password", help="password literal (avoid: visible in process list).")
    p.add_argument("--min-length", type=int, default=8,
                   help="minimum length to enforce (default 8; 12+ recommended).")
    p.add_argument("--context", action="append", default=[],
                   help="context term to reject (repeatable): site, username, email.")
    p.add_argument("--no-hibp", action="store_true", help="skip the online breach check.")
    args = p.parse_args(argv)

    if args.password is not None:
        pw = args.password
    elif args.stdin:
        pw = sys.stdin.readline().rstrip("\n")
    else:
        pw = getpass.getpass("Password: ")

    if not pw:
        print("error: empty password", file=sys.stderr)
        return 2

    ok, issues, notes = check(pw, args.min_length, args.context, not args.no_hibp)

    for n in notes:
        print(f"note: {n}")
    if ok:
        print("ACCEPTED: password meets NIST 800-63B screening.")
        return 0
    print("REJECTED:")
    for i in issues:
        print(f"  - {i}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
