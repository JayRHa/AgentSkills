#!/usr/bin/env python3
"""Validate an OpenAPI 3.x document for common structural mistakes.

This is a lightweight, dependency-light linter. It checks the issues that most
often break OpenAPI tooling and that are easy to introduce by hand. It is NOT a
full JSON-Schema/OpenAPI validator, but it catches the high-frequency errors
listed in references/openapi-3.1-reference.md.

Checks performed:
  - openapi version present and 3.x
  - info.title and info.version present
  - at least one server with a url
  - every operation has a unique operationId (warn if missing)
  - every response has a description
  - in: path parameters are required: true
  - every local $ref ('#/...') resolves to an existing node
  - 3.0-style 'nullable: true' flagged when doc is 3.1 (use type arrays)
  - requestBody has a content map

Usage:
  python3 validate_openapi.py spec.yaml [spec2.json ...]

Exit code 0 if no errors (warnings allowed), 1 if any error or load failure.
YAML support requires PyYAML; JSON works with the stdlib alone.
"""
import argparse
import json
import sys


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if path.endswith((".yaml", ".yml")):
        try:
            import yaml  # type: ignore
        except ImportError:
            raise SystemExit(
                "PyYAML is required for YAML files. Install it (pip install pyyaml) "
                "or convert the spec to JSON."
            )
        return yaml.safe_load(text)
    return json.loads(text)


def resolve_ref(root, ref):
    """Resolve a local JSON pointer like '#/components/schemas/User'."""
    if not ref.startswith("#/"):
        return True  # external refs not checked
    node = root
    for raw in ref[2:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            try:
                node = node[int(key)]
            except (ValueError, IndexError):
                return False
        elif isinstance(node, dict) and key in node:
            node = node[key]
        else:
            return False
    return True


def walk_refs(node, path=""):
    """Yield (json_path, ref_string) for every $ref in the document."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "$ref" and isinstance(v, str):
                yield path, v
            else:
                yield from walk_refs(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_refs(v, f"{path}/{i}")


def walk_keys(node, key_name, path=""):
    """Yield (json_path, value) for every occurrence of key_name."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == key_name:
                yield path, v
            yield from walk_keys(v, key_name, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_keys(v, key_name, f"{path}/{i}")


HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def validate(doc):
    errors, warnings = [], []

    def err(msg):
        errors.append(msg)

    def warn(msg):
        warnings.append(msg)

    if not isinstance(doc, dict):
        return ["Root document is not a mapping."], []

    version = str(doc.get("openapi", ""))
    if not version:
        err("Missing 'openapi' version field.")
    elif not version.startswith("3."):
        err(f"Unsupported openapi version '{version}'; expected 3.x.")
    is_31 = version.startswith("3.1")

    info = doc.get("info", {})
    if not info.get("title"):
        err("Missing info.title.")
    if not info.get("version"):
        err("Missing info.version.")

    servers = doc.get("servers", [])
    if not servers or not any(isinstance(s, dict) and s.get("url") for s in servers):
        warn("No servers[].url defined; clients won't know the base URL.")

    # Operations: operationId uniqueness, response descriptions, path params.
    seen_ops = {}
    paths = doc.get("paths", {}) or {}
    for path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(op, dict):
                continue
            loc = f"{method.upper()} {path}"
            op_id = op.get("operationId")
            if not op_id:
                warn(f"{loc}: missing operationId (SDK generators need it).")
            elif op_id in seen_ops:
                err(f"Duplicate operationId '{op_id}' ({loc} and {seen_ops[op_id]}).")
            else:
                seen_ops[op_id] = loc

            responses = op.get("responses", {})
            if not responses:
                err(f"{loc}: no responses defined.")
            for code, resp in (responses or {}).items():
                if isinstance(resp, dict) and "$ref" not in resp and not resp.get("description"):
                    err(f"{loc}: response '{code}' missing description.")

            rb = op.get("requestBody")
            if isinstance(rb, dict) and "$ref" not in rb and not rb.get("content"):
                err(f"{loc}: requestBody has no content map.")

    # in: path parameters must be required.
    for jpath, value in walk_keys(doc, "in"):
        if value == "path":
            container = jpath  # the parameter object path is parent of '/in'
            # find the parameter object by re-walking is overkill; check sibling.
    # Simpler: scan all parameter-like objects.
    for jpath, params in walk_keys(doc, "parameters"):
        if not isinstance(params, list):
            continue
        for p in params:
            if isinstance(p, dict) and p.get("in") == "path" and p.get("required") is not True:
                name = p.get("name", "?")
                err(f"{jpath}: path parameter '{name}' must be required: true.")

    # nullable on 3.1
    if is_31:
        for jpath, _ in walk_keys(doc, "nullable"):
            err(f"{jpath}/nullable: 3.0 'nullable' is invalid in 3.1; use type: [..., 'null'].")

    # $ref resolution
    for jpath, ref in walk_refs(doc):
        if not resolve_ref(doc, ref):
            err(f"{jpath}: unresolved $ref '{ref}'.")

    return errors, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an OpenAPI 3.x document.")
    parser.add_argument("specs", nargs="+", help="Path(s) to .yaml/.yml/.json spec files.")
    args = parser.parse_args(argv)

    overall_ok = True
    for path in args.specs:
        print(f"== {path} ==")
        try:
            doc = load(path)
        except SystemExit:
            raise
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR: failed to load: {exc}")
            overall_ok = False
            continue

        errors, warnings = validate(doc)
        for w in warnings:
            print(f"  WARN:  {w}")
        for e in errors:
            print(f"  ERROR: {e}")
        if errors:
            overall_ok = False
            print(f"  -> {len(errors)} error(s), {len(warnings)} warning(s).")
        else:
            print(f"  OK ({len(warnings)} warning(s)).")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
