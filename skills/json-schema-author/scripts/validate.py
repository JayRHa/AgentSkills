#!/usr/bin/env python3
"""Lint and (optionally) validate JSON Schema documents.

This is a stdlib-only structural linter for the most common JSON Schema
authoring mistakes. If the third-party `jsonschema` package is installed, it
ALSO validates the schema against its meta-schema and can validate a data
instance against the schema.

Usage:
    python3 validate.py SCHEMA.json                 # lint schema structure
    python3 validate.py SCHEMA.json --data DATA.json # also validate instance
    python3 validate.py SCHEMA.json --strict         # treat warnings as errors

Exit codes:
    0  no problems (warnings allowed unless --strict)
    1  problems found
    2  bad invocation / unreadable file
"""
import argparse
import json
import sys

KNOWN_KEYWORDS = {
    "$schema", "$id", "$ref", "$defs", "definitions", "$anchor", "$comment",
    "title", "description", "default", "examples", "deprecated", "readOnly",
    "writeOnly", "type", "enum", "const", "minimum", "maximum",
    "exclusiveMinimum", "exclusiveMaximum", "multipleOf", "minLength",
    "maxLength", "pattern", "format", "contentEncoding", "contentMediaType",
    "items", "prefixItems", "additionalItems", "minItems", "maxItems",
    "uniqueItems", "contains", "minContains", "maxContains", "properties",
    "required", "additionalProperties", "patternProperties", "propertyNames",
    "minProperties", "maxProperties", "dependentRequired", "dependentSchemas",
    "unevaluatedProperties", "unevaluatedItems", "allOf", "anyOf", "oneOf",
    "not", "if", "then", "else", "discriminator", "nullable", "xml",
    "externalDocs", "example",
}

VALID_TYPES = {
    "object", "array", "string", "number", "integer", "boolean", "null",
}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, path, msg):
        self.errors.append((path or "<root>", msg))

    def warn(self, path, msg):
        self.warnings.append((path or "<root>", msg))


def walk(node, path, rep, root):
    if not isinstance(node, dict):
        return

    # Unknown keyword detection (only flag schema-ish objects).
    looks_schemaish = any(
        k in node for k in ("type", "properties", "items", "enum", "const",
                             "allOf", "anyOf", "oneOf", "$ref")
    )
    if looks_schemaish:
        for key in node:
            if key not in KNOWN_KEYWORDS and not key.startswith("x-"):
                rep.warn(path, f"unrecognized keyword '{key}' (typo?)")

    # type checks
    t = node.get("type")
    types = [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
    for tv in types:
        if tv not in VALID_TYPES:
            rep.err(path, f"invalid type '{tv}'")

    # required must reference declared properties (best-effort, same object)
    req = node.get("required")
    props = node.get("properties")
    if isinstance(req, list) and isinstance(props, dict):
        ap = node.get("additionalProperties")
        has_combinator = any(k in node for k in ("allOf", "anyOf", "oneOf", "$ref"))
        for name in req:
            if name not in props and not has_combinator:
                rep.warn(path, f"required '{name}' is not declared in properties")
        # strictness hint
        if ap is None and "additionalProperties" not in node:
            rep.warn(path, "object has no 'additionalProperties' (consider false for strict configs)")

    # additionalProperties:false combined with allOf/$ref is a classic trap
    if node.get("additionalProperties") is False and (
        "allOf" in node or "$ref" in node
    ):
        rep.warn(path, "additionalProperties:false with allOf/$ref may reject inherited keys; "
                       "prefer unevaluatedProperties:false")

    # oneOf branches should each pin a discriminator const for clean errors
    if isinstance(node.get("oneOf"), list) and len(node["oneOf"]) > 1:
        pinned = 0
        for branch in node["oneOf"]:
            bp = branch.get("properties", {}) if isinstance(branch, dict) else {}
            if any(isinstance(v, dict) and "const" in v for v in bp.values()):
                pinned += 1
        if pinned < len(node["oneOf"]):
            rep.warn(path, "oneOf branches lack discriminating 'const' values; "
                           "matches may be ambiguous and errors noisy")

    # pattern must be a string; warn on single-backslash sequences that JSON ate
    pat = node.get("pattern")
    if pat is not None and not isinstance(pat, str):
        rep.err(path, "pattern must be a string")

    # $ref pointing nowhere obvious (local only, best-effort)
    ref = node.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/"):
        target = resolve_pointer(root, ref[1:])
        if target is None:
            rep.err(path, f"$ref '{ref}' does not resolve within this document")

    # recurse
    for key, val in node.items():
        if isinstance(val, dict):
            walk(val, f"{path}/{key}", rep, root)
        elif isinstance(val, list):
            for i, item in enumerate(val):
                walk(item, f"{path}/{key}/{i}", rep, root)


def resolve_pointer(doc, pointer):
    cur = doc
    for raw in pointer.split("/"):
        if raw == "":
            continue
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict) and token in cur:
            cur = cur[token]
        elif isinstance(cur, list) and token.isdigit() and int(token) < len(cur):
            cur = cur[int(token)]
        else:
            return None
    return cur


def load(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(2)


def try_real_validation(schema, data_path, rep):
    try:
        import jsonschema
        from jsonschema import validators
    except ImportError:
        print("note: install 'jsonschema' for full meta-schema + instance validation")
        return
    # meta-schema check
    try:
        cls = validators.validator_for(schema)
        cls.check_schema(schema)
        print(f"meta-schema: OK ({cls.__name__})")
    except Exception as exc:  # noqa: BLE001
        rep.err("<root>", f"schema is invalid against its meta-schema: {exc}")
        return
    if data_path:
        data = load(data_path)
        v = cls(schema)
        errors = sorted(v.iter_errors(data), key=lambda e: list(e.absolute_path))
        if not errors:
            print(f"instance {data_path}: VALID")
        else:
            print(f"instance {data_path}: INVALID ({len(errors)} error(s))")
            for e in errors:
                loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
                print(f"  - {loc}: {e.message}")
            sys.exit(1)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint/validate a JSON Schema.")
    ap.add_argument("schema", help="path to the JSON Schema file")
    ap.add_argument("--data", help="optional instance to validate against the schema")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as failures")
    args = ap.parse_args(argv)

    schema = load(args.schema)
    rep = Report()

    if isinstance(schema, dict) and "$schema" not in schema:
        rep.warn("<root>", "missing $schema declaration (dialect ambiguous)")

    walk(schema, "", rep, schema)
    try_real_validation(schema, args.data, rep)

    for where, msg in rep.warnings:
        print(f"WARN  {where}: {msg}")
    for where, msg in rep.errors:
        print(f"ERROR {where}: {msg}")

    if rep.errors or (args.strict and rep.warnings):
        print(f"\nFAIL: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
        sys.exit(1)
    print(f"\nOK: {len(rep.warnings)} warning(s)")
    sys.exit(0)


if __name__ == "__main__":
    main()
