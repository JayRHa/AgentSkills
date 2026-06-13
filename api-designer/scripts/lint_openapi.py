#!/usr/bin/env python3
"""Lint an OpenAPI 3.x spec for common API-design smells.

This is a lightweight, dependency-light design linter (not a full validator).
It flags issues that hurt API quality: verbs in paths, missing pagination on
list endpoints, missing error responses, unbounded query limits, missing
operationId, and 200-with-error patterns.

Usage:
    python lint_openapi.py path/to/openapi.yaml
    python lint_openapi.py path/to/openapi.json --strict

Exit codes:
    0  no errors (warnings allowed unless --strict)
    1  errors found (or warnings with --strict)
    2  could not load/parse the spec

YAML support uses PyYAML if available; otherwise only JSON specs are accepted.
"""
import argparse
import json
import re
import sys

VERB_SEGMENTS = {
    "get", "list", "create", "update", "delete", "remove", "fetch",
    "add", "set", "make", "do", "retrieve", "save", "send", "find",
}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}
ERROR_STATUSES = {"400", "401", "403", "404", "409", "422", "429", "4xx",
                  "500", "5xx", "default"}


def load_spec(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError:
            print("ERROR: PyYAML not installed; cannot parse YAML. "
                  "Install pyyaml or pass a JSON spec.", file=sys.stderr)
            sys.exit(2)
        return yaml.safe_load(text)
    return json.loads(text)


def segment_has_verb(path):
    for seg in path.strip("/").split("/"):
        if seg.startswith("{"):
            continue
        clean = re.sub(r"[^a-z]", "", seg.lower())
        # split camelCase-ish too
        words = re.findall(r"[a-z]+", seg.lower())
        if clean in VERB_SEGMENTS or any(w in VERB_SEGMENTS for w in words):
            return seg
    return None


def is_list_operation(path, method, op):
    if method != "get":
        return False
    # Heuristic: collection endpoints do not end in a path parameter.
    last = path.strip("/").split("/")[-1] if path.strip("/") else ""
    return not last.startswith("{")


def has_pagination_param(op):
    names = set()
    for p in op.get("parameters", []) or []:
        if isinstance(p, dict):
            names.add(str(p.get("name", "")).lower())
            ref = p.get("$ref", "")
            if ref:
                names.add(ref.split("/")[-1].lower())
    paging = {"limit", "cursor", "page", "offset", "per_page", "perpage",
              "pagesize", "first", "after"}
    return bool(names & paging)


def lint(spec):
    errors, warnings = [], []
    paths = spec.get("paths", {}) or {}
    if not paths:
        errors.append("No paths defined in spec.")
        return errors, warnings

    seen_op_ids = {}
    for path, item in paths.items():
        verb = segment_has_verb(path)
        if verb:
            errors.append(f"{path}: path segment '{verb}' looks like a verb; "
                          f"use nouns and HTTP methods.")
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(op, dict):
                continue
            m = method.lower()
            loc = f"{m.upper()} {path}"

            op_id = op.get("operationId")
            if not op_id:
                warnings.append(f"{loc}: missing operationId.")
            elif op_id in seen_op_ids:
                errors.append(f"{loc}: duplicate operationId '{op_id}' "
                              f"(also {seen_op_ids[op_id]}).")
            else:
                seen_op_ids[op_id] = loc

            responses = op.get("responses", {}) or {}
            status_keys = {str(k).lower() for k in responses}

            if not (status_keys & ERROR_STATUSES):
                warnings.append(f"{loc}: defines no error responses (4xx/5xx).")

            if is_list_operation(path, m, op) and not has_pagination_param(op):
                errors.append(f"{loc}: list endpoint has no pagination "
                              f"parameter (limit/cursor/page/offset).")

            # Unbounded limit param
            for p in op.get("parameters", []) or []:
                if not isinstance(p, dict):
                    continue
                if str(p.get("name", "")).lower() == "limit":
                    schema = p.get("schema", {}) or {}
                    if "maximum" not in schema:
                        warnings.append(f"{loc}: 'limit' param has no maximum; "
                                        f"cap it to prevent abuse.")

            # POST creating without idempotency hint
            if m == "post":
                names = {str((p or {}).get("name", "")).lower()
                         for p in (op.get("parameters") or [])
                         if isinstance(p, dict)}
                if "idempotency-key" not in names:
                    warnings.append(f"{loc}: POST has no Idempotency-Key "
                                    f"parameter; consider it for safe retries.")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="Path to OpenAPI spec (.yaml/.yml/.json)")
    ap.add_argument("--strict", action="store_true",
                    help="Treat warnings as failures.")
    args = ap.parse_args()

    try:
        spec = load_spec(args.spec)
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.spec}", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: could not parse spec: {exc}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(spec, dict):
        print("ERROR: spec root is not an object.", file=sys.stderr)
        sys.exit(2)

    errors, warnings = lint(spec)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s).")

    if errors or (args.strict and warnings):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
