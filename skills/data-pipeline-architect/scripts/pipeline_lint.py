#!/usr/bin/env python3
"""pipeline_lint.py - Lint a data pipeline design config for required safeguards.

Checks a pipeline specification (YAML or JSON) for the non-negotiable
properties of a production pipeline: idempotency, watermark/state handling,
schema-evolution policy, retries, and data-quality gates.

Usage:
    python pipeline_lint.py pipeline.yaml
    python pipeline_lint.py pipeline.json --strict
    cat pipeline.yaml | python pipeline_lint.py -

Exit codes:
    0  no errors (warnings allowed unless --strict)
    1  one or more errors (or warnings in --strict mode)
    2  could not parse input

Expected (flexible) config shape:
    name: orders_pipeline
    load_pattern: elt            # etl | elt
    sources:
      - name: orders
        strategy: incremental    # full | incremental | cdc
        watermark: updated_at    # required unless strategy == full
    idempotency:
      pattern: merge             # merge | delete_insert | staging_swap
      business_key: order_id
    schema_evolution:
      bronze: additive
      gold: contract
    orchestration:
      tool: airflow
      retries: 3
      backoff: exponential
      sla: 1h
    quality_checks:
      - stage: post_ingest
        checks: [schema, row_count, freshness]
        severity: block

YAML support is optional; if PyYAML is not installed, pass JSON.
"""
import argparse
import json
import sys


def load_config(text):
    """Parse config as JSON, falling back to YAML if available."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # type: ignore
    except ImportError:
        raise SystemExit(
            "ERROR: input is not JSON and PyYAML is not installed. "
            "Install pyyaml or provide JSON."
        )
    return yaml.safe_load(text)


class Linter:
    def __init__(self, cfg):
        self.cfg = cfg or {}
        self.errors = []
        self.warnings = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def run(self):
        c = self.cfg
        if not isinstance(c, dict):
            self.err("Config root must be a mapping/object.")
            return

        if not c.get("name"):
            self.warn("No 'name' set for the pipeline.")

        lp = str(c.get("load_pattern", "")).lower()
        if lp not in ("etl", "elt"):
            self.warn("load_pattern should be 'etl' or 'elt'.")

        self._check_sources(c.get("sources"))
        self._check_idempotency(c.get("idempotency"))
        self._check_schema_evolution(c.get("schema_evolution"))
        self._check_orchestration(c.get("orchestration"))
        self._check_quality(c.get("quality_checks"))

    def _check_sources(self, sources):
        if not sources:
            self.err("No 'sources' defined.")
            return
        if not isinstance(sources, list):
            self.err("'sources' must be a list.")
            return
        for i, s in enumerate(sources):
            label = s.get("name", f"#{i}") if isinstance(s, dict) else f"#{i}"
            if not isinstance(s, dict):
                self.err(f"source {label}: must be a mapping.")
                continue
            strat = str(s.get("strategy", "")).lower()
            if strat not in ("full", "incremental", "cdc"):
                self.err(
                    f"source {label}: strategy must be full|incremental|cdc "
                    f"(got {s.get('strategy')!r})."
                )
            if strat == "incremental" and not s.get("watermark"):
                self.err(
                    f"source {label}: incremental strategy requires a "
                    "'watermark' column."
                )
            if strat == "incremental" and not s.get("lookback"):
                self.warn(
                    f"source {label}: no 'lookback' set; late/same-timestamp "
                    "rows may be lost."
                )
            if strat == "full" and (s.get("volume_rows") or 0) > 1_000_000:
                self.warn(
                    f"source {label}: full reload of >1M rows; consider "
                    "incremental."
                )

    def _check_idempotency(self, idem):
        if not idem or not isinstance(idem, dict):
            self.err(
                "No 'idempotency' block. Every load must be safe to re-run "
                "(merge | delete_insert | staging_swap)."
            )
            return
        pattern = str(idem.get("pattern", "")).lower()
        valid = ("merge", "upsert", "delete_insert", "staging_swap")
        if pattern not in valid:
            self.err(
                f"idempotency.pattern must be one of {valid} "
                f"(got {idem.get('pattern')!r})."
            )
        if pattern in ("merge", "upsert", "delete_insert") and not idem.get(
            "business_key"
        ):
            self.err(
                f"idempotency.pattern '{pattern}' requires a 'business_key'."
            )

    def _check_schema_evolution(self, se):
        if not se or not isinstance(se, dict):
            self.warn(
                "No 'schema_evolution' policy. Define per-layer handling "
                "(bronze: additive; gold: contract)."
            )
            return
        bronze = str(se.get("bronze", "")).lower()
        if bronze and bronze not in ("additive", "strict", "none"):
            self.warn(f"schema_evolution.bronze unexpected value {bronze!r}.")
        gold = str(se.get("gold", "")).lower()
        if gold == "additive":
            self.warn(
                "schema_evolution.gold is 'additive'; auto-evolving consumer "
                "tables can break BI. Prefer 'contract'."
            )

    def _check_orchestration(self, orch):
        if not orch or not isinstance(orch, dict):
            self.err("No 'orchestration' block (tool, retries, sla).")
            return
        if not orch.get("tool"):
            self.warn("orchestration.tool not set.")
        retries = orch.get("retries")
        if retries is None:
            self.err("orchestration.retries not set.")
        elif isinstance(retries, int) and retries == 0:
            self.warn("orchestration.retries is 0; transient errors will fail.")
        if not orch.get("backoff"):
            self.warn("orchestration.backoff not set; prefer exponential.")
        if not orch.get("sla") and not orch.get("timeout"):
            self.warn("No SLA or timeout set; stale/hung runs go undetected.")

    def _check_quality(self, qc):
        if not qc:
            self.err(
                "No 'quality_checks'. Add gates at ingest, silver, and gold "
                "boundaries."
            )
            return
        if not isinstance(qc, list):
            self.err("'quality_checks' must be a list.")
            return
        stages = {str(g.get("stage", "")).lower() for g in qc
                  if isinstance(g, dict)}
        has_block = any(
            str(g.get("severity", "")).lower() == "block"
            for g in qc if isinstance(g, dict)
        )
        if not has_block:
            self.warn(
                "No quality check has severity 'block'; alert-only checks let "
                "bad data through."
            )
        if not any("ingest" in s for s in stages):
            self.warn("No post-ingest quality gate (schema/row_count/freshness).")
        freshness = any(
            "freshness" in str(g.get("checks", "")).lower()
            for g in qc if isinstance(g, dict)
        )
        if not freshness:
            self.warn("No freshness check found; stale data may pass silently.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("config", help="Path to YAML/JSON config, or '-' for stdin.")
    p.add_argument("--strict", action="store_true",
                   help="Treat warnings as errors.")
    args = p.parse_args(argv)

    text = sys.stdin.read() if args.config == "-" else open(args.config).read()
    try:
        cfg = load_config(text)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"Could not parse config: {e}", file=sys.stderr)
        return 2

    linter = Linter(cfg)
    linter.run()

    for w in linter.warnings:
        print(f"WARN:  {w}")
    for e in linter.errors:
        print(f"ERROR: {e}")

    n_err, n_warn = len(linter.errors), len(linter.warnings)
    print(f"\n{n_err} error(s), {n_warn} warning(s).")

    if n_err or (args.strict and n_warn):
        return 1
    print("OK: pipeline design passes lint.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
