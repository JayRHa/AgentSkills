# Resource Catalog — apiVersion, kind, and when to use

Quick lookup of the resources this skill commonly emits, with current stable `apiVersion`s.

## Workloads

| Kind | apiVersion | Use |
|------|-----------|-----|
| Deployment | `apps/v1` | Stateless apps; the default |
| StatefulSet | `apps/v1` | Stable identity/storage/ordering |
| DaemonSet | `apps/v1` | One pod per node |
| Job | `batch/v1` | Run-to-completion |
| CronJob | `batch/v1` | Scheduled jobs |

## Networking

| Kind | apiVersion | Use |
|------|-----------|-----|
| Service | `v1` | Stable virtual IP / DNS for pods |
| Ingress | `networking.k8s.io/v1` | HTTP(S) L7 routing into the cluster |
| NetworkPolicy | `networking.k8s.io/v1` | Pod-level firewall rules |

### Service types

| Type | Reach | Notes |
|------|-------|-------|
| `ClusterIP` | In-cluster only | Default; pair with Ingress for external |
| `NodePort` | Node IP : 30000-32767 | Dev/on-prem; rarely for prod |
| `LoadBalancer` | Cloud LB | Provisions a cloud load balancer |
| `ExternalName` | CNAME | Maps to an external DNS name |
| Headless (`clusterIP: None`) | Per-pod DNS | For StatefulSets / client-side LB |

## Config and secrets

| Kind | apiVersion | Use |
|------|-----------|-----|
| ConfigMap | `v1` | Non-secret config (env, files) |
| Secret | `v1` | Sensitive data (base64, not encrypted at rest by default) |

Injection patterns:
```yaml
# All keys as env vars
envFrom:
  - configMapRef: { name: my-app-config }
  - secretRef: { name: my-app-secrets }

# Single key
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef: { name: my-app-secrets, key: database-url }

# Mounted as files
volumes:
  - name: config
    configMap: { name: my-app-config }
volumeMounts:
  - { name: config, mountPath: /etc/app, readOnly: true }
```

Note: a Kubernetes `Secret` is only base64-encoded. For real secrecy use a KMS-backed solution (External Secrets Operator, Sealed Secrets, cloud secret managers) and enable etcd encryption-at-rest.

## Scaling and availability

### HorizontalPodAutoscaler (`autoscaling/v2`)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: my-app }
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
```
Do NOT set `replicas` on a Deployment managed by an HPA — they fight. Omit `replicas` or let the HPA own it.

### PodDisruptionBudget (`policy/v1`)
Protects against voluntary disruptions (node drains, upgrades). See `references/best-practices.md`.

## ServiceAccount (`v1`)
Give each workload a dedicated ServiceAccount and disable token automount unless the app calls the API:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata: { name: my-app }
automountServiceAccountToken: false
```
Reference it in the pod: `spec.serviceAccountName: my-app`.
