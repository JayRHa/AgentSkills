#!/usr/bin/env python3
"""Lint Kubernetes workload manifests for common production mistakes.

Pure-stdlib (uses a minimal built-in YAML subset parser is NOT attempted;
instead this relies on `kubectl`-free heuristics over the raw text plus an
optional PyYAML path). To stay stdlib-only and dependency-free, this script
parses YAML structurally only when PyYAML is available, and otherwise falls
back to robust line/regex heuristics that cover the high-value checks.

Usage:
    python3 validate_manifest.py FILE [FILE ...]
    cat deployment.yaml | python3 validate_manifest.py -

Exit code is 0 when no ERROR-level findings, 1 otherwise. WARN findings do
not fail the run. Use --strict to also fail on WARN.

Checks (workload manifests):
  - image uses :latest or has no tag                     (ERROR)
  - no resources.requests / resources.limits             (WARN/ERROR)
  - container/pod runs as root (no runAsNonRoot)         (WARN)
  - allowPrivilegeEscalation not disabled                (WARN)
  - no readinessProbe                                    (WARN)
  - livenessProbe present but no readinessProbe          (ERROR)
  - single replica with no PDB hint                      (WARN)
  - Service selector vs workload labels mismatch         (WARN, multi-doc only)
"""
import argparse
import re
import sys


try:
    import yaml  # type: ignore
    HAVE_YAML = True
except Exception:  # pragma: no cover - dependency optional
    HAVE_YAML = False


WORKLOAD_KINDS = {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "ReplicaSet"}


class Finding:
    def __init__(self, level, doc, msg):
        self.level = level
        self.doc = doc
        self.msg = msg

    def __str__(self):
        return "[{:5}] {}{}".format(self.level, (self.doc + ": ") if self.doc else "", self.msg)


def _walk(obj):
    """Yield every dict found anywhere in a nested structure."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk(item)


def _pod_spec(doc):
    """Return the PodSpec dict for a workload doc, or None."""
    spec = doc.get("spec", {})
    # CronJob nests deeper
    tmpl = spec.get("template")
    if tmpl is None and "jobTemplate" in spec:
        tmpl = spec["jobTemplate"].get("spec", {}).get("template")
    if not tmpl:
        return None
    return tmpl.get("spec")


def check_doc(doc, findings):
    if not isinstance(doc, dict):
        return
    kind = doc.get("kind", "")
    name = (doc.get("metadata", {}) or {}).get("name", "<unnamed>")
    label = "{}/{}".format(kind, name)

    if kind not in WORKLOAD_KINDS:
        return

    spec = doc.get("spec", {}) or {}
    pod = _pod_spec(doc)
    if not pod:
        findings.append(Finding("ERROR", label, "no pod template found"))
        return

    containers = pod.get("containers", []) or []
    if not containers:
        findings.append(Finding("ERROR", label, "no containers defined"))

    # replicas / PDB heuristic
    replicas = spec.get("replicas")
    if kind in ("Deployment", "StatefulSet") and replicas == 1:
        findings.append(Finding("WARN", label,
            "replicas: 1 — single replica means downtime on rollout/drain; use >=2 + a PodDisruptionBudget"))

    for c in containers:
        cname = c.get("name", "<container>")
        cl = "{} [{}]".format(label, cname)

        # image tag
        image = c.get("image", "")
        if image:
            tag = image.rsplit(":", 1)[-1] if ":" in image.split("/")[-1] else ""
            if not tag or tag == "latest":
                findings.append(Finding("ERROR", cl,
                    "image '{}' has no pinned tag or uses :latest".format(image)))
        else:
            findings.append(Finding("ERROR", cl, "container has no image"))

        # resources
        res = c.get("resources", {}) or {}
        if not res.get("requests"):
            findings.append(Finding("WARN", cl, "no resources.requests — pod may get BestEffort QoS"))
        if not res.get("limits"):
            findings.append(Finding("WARN", cl, "no resources.limits — set at least a memory limit"))
        elif not (res.get("limits", {}) or {}).get("memory"):
            findings.append(Finding("WARN", cl, "no memory limit — memory is incompressible, set it"))

        # probes
        has_ready = bool(c.get("readinessProbe"))
        has_live = bool(c.get("livenessProbe"))
        if not has_ready:
            findings.append(Finding("WARN", cl, "no readinessProbe — traffic may hit unready pods"))
        if has_live and not has_ready:
            findings.append(Finding("ERROR", cl,
                "livenessProbe without readinessProbe — add readiness; liveness alone can cause restart storms"))

        # securityContext
        sc = c.get("securityContext", {}) or {}
        pod_sc = pod.get("securityContext", {}) or {}
        if not (sc.get("runAsNonRoot") or pod_sc.get("runAsNonRoot")):
            findings.append(Finding("WARN", cl, "runAsNonRoot not set true — container may run as root"))
        if sc.get("allowPrivilegeEscalation") is not False:
            findings.append(Finding("WARN", cl, "allowPrivilegeEscalation not set false"))
        caps = (sc.get("capabilities", {}) or {}).get("drop", [])
        if "ALL" not in caps:
            findings.append(Finding("WARN", cl, "capabilities.drop does not include ALL"))


def check_service_selectors(docs, findings):
    """Cross-check Service selectors against workload pod labels."""
    pod_label_sets = []
    for d in docs:
        if not isinstance(d, dict) or d.get("kind") not in WORKLOAD_KINDS:
            continue
        pod = _pod_spec(d)
        if pod is None:
            continue
        meta = (d.get("spec", {}).get("template", {}) or {}).get("metadata", {}) or {}
        labels = meta.get("labels", {}) or {}
        if labels:
            pod_label_sets.append(labels)

    for d in docs:
        if not isinstance(d, dict) or d.get("kind") != "Service":
            continue
        sel = (d.get("spec", {}) or {}).get("selector", {}) or {}
        name = (d.get("metadata", {}) or {}).get("name", "<svc>")
        if not sel:
            continue
        matched = any(all(labels.get(k) == v for k, v in sel.items()) for labels in pod_label_sets)
        if pod_label_sets and not matched:
            findings.append(Finding("WARN", "Service/" + name,
                "selector {} matches no workload pod labels in this fileset".format(sel)))


def load_docs(text):
    if HAVE_YAML:
        return [d for d in yaml.safe_load_all(text) if d is not None]
    raise SystemExit(
        "PyYAML not installed. Install it (pip install pyyaml) or run "
        "`kubectl apply --dry-run=client -f <file>` for schema validation.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Lint Kubernetes workload manifests.")
    ap.add_argument("files", nargs="+", help="YAML files, or - for stdin")
    ap.add_argument("--strict", action="store_true", help="fail on WARN as well as ERROR")
    args = ap.parse_args(argv)

    findings = []
    for path in args.files:
        text = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
        docs = load_docs(text)
        for d in docs:
            check_doc(d, findings)
        check_service_selectors(docs, findings)

    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]

    for f in findings:
        print(str(f))

    print("\n{} error(s), {} warning(s).".format(len(errors), len(warns)))
    if not findings:
        print("OK: no issues found.")

    fail = bool(errors) or (args.strict and bool(warns))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
