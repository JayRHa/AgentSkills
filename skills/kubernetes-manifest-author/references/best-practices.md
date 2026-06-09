# Kubernetes Manifest Best Practices Reference

Deep reference for the decisions the skill encodes. Numbers are sane production defaults — tune to your SLOs and load tests.

## 1. Images

| Rule | Why |
|------|-----|
| Pin a tag (`v1.4.2`) or digest (`@sha256:...`) | Reproducible, rollback-safe deploys |
| Avoid `:latest` | Different nodes can pull different builds |
| `imagePullPolicy: IfNotPresent` with pinned tags | Avoid registry round-trips; deterministic |
| Use minimal base images (distroless/alpine) | Smaller attack surface, faster pulls |

## 2. Resources, requests, limits, and QoS

- **request** = guaranteed reservation, used by the scheduler. Set it to typical steady-state usage.
- **limit** = hard cap. CPU limit causes throttling; memory limit over leads to OOMKill.

### QoS classes

| QoS | Condition | Eviction order |
|-----|-----------|----------------|
| Guaranteed | requests == limits for cpu AND memory on every container | Last |
| Burstable | at least one request set, not Guaranteed | Middle |
| BestEffort | no requests/limits | First (evicted first) |

### CPU limits: the throttling nuance

CPU is compressible. A CPU **limit** throttles the container via CFS quota, which can add tail latency even when the node is idle. Common production guidance:

- ALWAYS set CPU **requests** (needed for scheduling and Guaranteed/Burstable).
- Consider OMITTING CPU **limits** for latency-sensitive services to avoid throttling, relying on requests for fair sharing.
- ALWAYS set memory **request == limit** (memory is incompressible; this gives predictable OOM behavior and Guaranteed-ish memory).

Starting point for a small web service:
```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    memory: "128Mi"   # == request; CPU limit intentionally omitted
```

## 3. Probes — timing math

Fields (all probe types share these):
- `initialDelaySeconds` — wait before first check.
- `periodSeconds` — interval between checks.
- `timeoutSeconds` — per-check timeout (default 1s — often too low).
- `failureThreshold` — consecutive failures before action.
- `successThreshold` — consecutive successes to be considered up (must be 1 for liveness/startup).

**Time to declare dead** = `initialDelaySeconds + periodSeconds * failureThreshold` (roughly).

### Recommended defaults

```yaml
startupProbe:        # gives the app up to 5m to boot
  httpGet: { path: /healthz, port: http }
  failureThreshold: 30
  periodSeconds: 10

readinessProbe:      # gates traffic; can check dependencies
  httpGet: { path: /readyz, port: http }
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3

livenessProbe:       # cheap, dependency-free; restarts a wedged process
  httpGet: { path: /healthz, port: http }
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3
```

Rules:
- Liveness must NOT depend on databases, caches, or downstreams. A shared dependency outage would restart every pod simultaneously.
- Readiness SHOULD check the dependencies the pod needs to serve a request.
- With a `startupProbe`, you can drop `initialDelaySeconds` on liveness/readiness to 0.

## 4. Security context (restricted Pod Security Standard)

```yaml
securityContext:        # container level
  runAsNonRoot: true
  runAsUser: 10001
  runAsGroup: 10001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

Pod-level extras when needed:
```yaml
securityContext:
  fsGroup: 10001          # for volume ownership
  fsGroupChangePolicy: OnRootMismatch
```

With `readOnlyRootFilesystem: true`, mount writable scratch space:
```yaml
volumeMounts:
  - { name: tmp, mountPath: /tmp }
volumes:
  - name: tmp
    emptyDir: {}
```

## 5. Rollouts and availability

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0     # zero-downtime: never drop below desired
    maxSurge: 1           # add one extra during rollout
```

Pair with a PodDisruptionBudget:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: my-app }
spec:
  minAvailable: 1        # or maxUnavailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: my-app
```

Also set `terminationGracePeriodSeconds` and a `preStop` sleep so in-flight requests drain before SIGTERM-driven shutdown:
```yaml
lifecycle:
  preStop:
    exec: { command: ["sleep", "5"] }
```

## 6. Recommended common labels

```yaml
labels:
  app.kubernetes.io/name: my-app
  app.kubernetes.io/instance: my-app-prod
  app.kubernetes.io/version: "1.4.2"
  app.kubernetes.io/component: api
  app.kubernetes.io/part-of: payments
  app.kubernetes.io/managed-by: kustomize
```

Use `app.kubernetes.io/name` + `app.kubernetes.io/instance` as the Service/HPA/PDB selector — they are stable across version bumps.

## 7. Anti-affinity for spreading replicas

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          topologyKey: kubernetes.io/hostname
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: my-app
```

Modern alternative — `topologySpreadConstraints` across zones:
```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        app.kubernetes.io/name: my-app
```

## 8. Validation commands

```bash
# Schema + admission (needs cluster access)
kubectl apply -f manifest.yaml --dry-run=server

# Client-side schema only
kubectl apply -f manifest.yaml --dry-run=client

# Confirm a Service has endpoints after deploy
kubectl get endpoints my-app

# Explain a field
kubectl explain deployment.spec.template.spec.containers.livenessProbe
```
