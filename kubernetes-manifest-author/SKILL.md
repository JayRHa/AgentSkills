---
name: kubernetes-manifest-author
description: Authors production-grade Kubernetes manifests — Deployments, Services, Ingress, probes, resource requests/limits, security contexts, and ConfigMaps/Secrets wiring — following hardening and reliability best practices. Use this skill when the user asks to "write a Kubernetes deployment", "create a k8s manifest", "add liveness/readiness probes", "set resource limits", "harden a pod securityContext", "expose a service", "write a HorizontalPodAutoscaler", or otherwise produce or review YAML for deploying workloads to Kubernetes.
license: MIT
---

# Kubernetes Manifest Author

## Overview

Produce correct, secure, and reliable Kubernetes YAML for deploying stateless and stateful workloads. This skill turns an application description into a complete manifest set: workload (Deployment/StatefulSet/CronJob), Service, optional Ingress, probes, resource governance, security context hardening, and configuration wiring.

Keywords: kubernetes, k8s, manifest, yaml, deployment, statefulset, service, ingress, liveness probe, readiness probe, startup probe, resources requests limits, securityContext, runAsNonRoot, podSecurityStandards, HPA, autoscaling, ConfigMap, Secret, PodDisruptionBudget, rollout, kubectl, helm, kustomize.

This skill is opinionated toward the **restricted Pod Security Standard** and production SRE defaults. Loosen only when the user has a concrete reason.

## Workflow

1. **Gather the workload shape.** Determine: container image + tag (never `:latest`), listening port(s), stateless vs stateful, replica count, environment/config inputs, secrets, and exposure (cluster-internal, Ingress, LoadBalancer). If the user omits something, apply the safe defaults in `references/best-practices.md` and state the assumption.

2. **Pick the workload kind** using the decision table below. Most web/API services are `Deployment`.

3. **Author the workload manifest.** Start from `templates/deployment.yaml`. Always fill in: explicit labels, image with pinned tag, resource requests AND limits, all three probe types where appropriate, a hardened `securityContext`, and a `RollingUpdate` strategy.

4. **Add the Service.** Use `templates/service.yaml`. Match `selector` to the Pod template labels exactly. Default to `ClusterIP`; use `LoadBalancer`/`NodePort` only when externally requested.

5. **Add exposure and resilience extras as needed:** Ingress, HorizontalPodAutoscaler, PodDisruptionBudget, ConfigMap/Secret. See `references/resource-catalog.md`.

6. **Wire configuration.** Inject config via `envFrom`/`env` (ConfigMap) and secrets via `secretKeyRef` or mounted volumes. Never hardcode secrets in the manifest.

7. **Validate.** Run `scripts/validate_manifest.py` to catch the most common production mistakes (missing limits, `:latest`, root user, no probes, mismatched selectors). If `kubectl` is available, also run `kubectl apply --dry-run=server` and `kubectl explain` for field checks.

8. **Explain the manifest** to the user: label the security/reliability choices you made and what they should tune (resource numbers, replica count, probe paths).

## Decision Framework — which workload kind?

| Situation | Kind |
|-----------|------|
| Stateless HTTP/gRPC API or web app | `Deployment` |
| Needs stable network identity / ordered start / per-pod storage (DBs, Kafka) | `StatefulSet` |
| One pod per node (log/metrics agents, CNI) | `DaemonSet` |
| Run-to-completion task | `Job` |
| Scheduled run-to-completion task | `CronJob` |

## Probe decision framework

Probes are the most common source of production incidents. Apply this:

- **readinessProbe** — ALWAYS for anything in a Service. Gates traffic; failing readiness removes the pod from endpoints without restarting it. Should check that dependencies (DB, cache) the pod needs to serve are reachable.
- **livenessProbe** — only when the app can deadlock in a way a restart fixes. Make it CHEAP and dependency-free (it should NOT check the database — a DB outage shouldn't restart every pod). A bad liveness probe causes restart storms.
- **startupProbe** — for slow-starting apps (JVM, migrations). Disables liveness/readiness until the app has booted, so you can keep liveness aggressive without killing slow boots.

Probe handler choice: prefer `httpGet` for HTTP servers, `grpc` for gRPC, `exec` only as a last resort (forks a process each check).

See worked numbers and timing math in `references/best-practices.md`.

## Security context checklist (restricted PSS)

Every production Pod should set, at the container level unless noted:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001            # any non-zero UID
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  seccompProfile:             # pod-level also acceptable
    type: RuntimeDefault
```

`readOnlyRootFilesystem: true` requires mounting `emptyDir` volumes for any writable paths (e.g. `/tmp`, cache dirs). The template shows this pattern.

## Worked example

See `examples/web-api.md` for a full request → manifest walkthrough: a Node.js API with config, secrets, an HPA, a PDB, and an Ingress — including the reasoning for every non-default field.

## Best Practices

- Pin image tags (or digests); set `imagePullPolicy: IfNotPresent` for pinned tags.
- Set resource **requests** (for scheduling/QoS) AND **limits** (to cap blast radius). Set CPU request = limit only when you need predictable latency; otherwise omit the CPU limit to avoid throttling (see reference).
- Use the recommended common labels (`app.kubernetes.io/*`) so Services, HPAs, and dashboards select consistently.
- Minimum 2 replicas + a PodDisruptionBudget for any service that must stay up during node drains.
- Keep liveness probes dependency-free; put dependency checks in readiness.
- Prefer `RollingUpdate` with `maxUnavailable: 0` for zero-downtime when you have spare capacity.
- One concern per manifest file; order resources so dependencies (ConfigMap, Secret) come before consumers, or use separate files applied together.
- Run `scripts/validate_manifest.py` before shipping.

## Common Pitfalls

- **`:latest` tags** — non-reproducible rollouts and no rollback guarantee.
- **No resource limits** — one pod can starve a node; pods get `BestEffort` QoS and are evicted first.
- **Liveness probe checking the database** — turns a dependency outage into a cluster-wide restart storm.
- **Selector/label mismatch** — Service routes to nothing; `kubectl get endpoints` is empty.
- **Running as root** — blocked by restricted PSS; an escape is far more dangerous.
- **`readOnlyRootFilesystem: true` without writable `emptyDir` mounts** — app crashes trying to write `/tmp`.
- **Aggressive `initialDelaySeconds` on liveness for slow apps** — use a `startupProbe` instead.
- **Single replica + `maxUnavailable: 1`** — guaranteed downtime on every rollout and node drain.
