# Worked Example: a Node.js HTTP API

## Request

> "Write Kubernetes manifests for our orders API. It's a Node.js service,
> image `registry.example.com/orders-api:2.3.1`, listens on port 8080, needs
> a `DATABASE_URL` secret and a `LOG_LEVEL` config value, should run 3-12
> replicas based on CPU, and be reachable at `orders.example.com`."

## Reasoning (choices the skill makes)

- **Kind: Deployment** — stateless HTTP service.
- **No `replicas` field on the Deployment** — an HPA owns scaling; setting both causes a fight. `minReplicas: 3`.
- **Probes** — `/readyz` checks the DB connection (gates traffic), `/healthz` is cheap and dependency-free (liveness). A `startupProbe` covers Node + warmup.
- **Security** — non-root UID 10001, read-only rootfs with a `/tmp` emptyDir, all caps dropped, `RuntimeDefault` seccomp.
- **Config/secrets** — `LOG_LEVEL` from a ConfigMap, `DATABASE_URL` from a Secret.
- **Resilience** — PDB `minAvailable: 2`, `maxUnavailable: 0` rollout, zone spread.

## Output

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: orders-api-config
data:
  LOG_LEVEL: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: orders-api-secrets
type: Opaque
stringData:
  DATABASE_URL: "postgres://REPLACE_ME"   # supply via sealed-secrets / ESO in prod
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: orders-api
automountServiceAccountToken: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orders-api
  labels:
    app.kubernetes.io/name: orders-api
    app.kubernetes.io/instance: orders-api-prod
    app.kubernetes.io/version: "2.3.1"
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: orders
spec:
  # replicas omitted — HPA owns it
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: orders-api
      app.kubernetes.io/instance: orders-api-prod
  template:
    metadata:
      labels:
        app.kubernetes.io/name: orders-api
        app.kubernetes.io/instance: orders-api-prod
        app.kubernetes.io/version: "2.3.1"
    spec:
      serviceAccountName: orders-api
      automountServiceAccountToken: false
      terminationGracePeriodSeconds: 30
      securityContext:
        fsGroup: 10001
        seccompProfile:
          type: RuntimeDefault
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector:
            matchLabels:
              app.kubernetes.io/name: orders-api
      containers:
        - name: orders-api
          image: registry.example.com/orders-api:2.3.1
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
          envFrom:
            - configMapRef: { name: orders-api-config }
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef: { name: orders-api-secrets, key: DATABASE_URL }
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              memory: "256Mi"
          startupProbe:
            httpGet: { path: /healthz, port: http }
            failureThreshold: 30
            periodSeconds: 10
          readinessProbe:
            httpGet: { path: /readyz, port: http }   # checks DB
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          livenessProbe:
            httpGet: { path: /healthz, port: http }   # cheap, no DB
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          lifecycle:
            preStop:
              exec: { command: ["sleep", "5"] }
          securityContext:
            runAsNonRoot: true
            runAsUser: 10001
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          volumeMounts:
            - { name: tmp, mountPath: /tmp }
      volumes:
        - name: tmp
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: orders-api
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: orders-api
    app.kubernetes.io/instance: orders-api-prod
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: orders-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: orders-api
  minReplicas: 3
  maxReplicas: 12
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 70 }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: orders-api
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: orders-api
      app.kubernetes.io/instance: orders-api-prod
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: orders-api
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts: ["orders.example.com"]
      secretName: orders-api-tls
  rules:
    - host: orders.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: orders-api
                port: { name: http }
```

## Validate

```bash
python3 scripts/validate_manifest.py orders-api.yaml
kubectl apply -f orders-api.yaml --dry-run=server
kubectl get endpoints orders-api   # after apply: must list pod IPs
```

## What the user should tune

- Resource numbers — derived from a load test, not guessed.
- HPA `averageUtilization` and `max` — based on real traffic curves.
- Probe paths — must exist in the app (`/healthz`, `/readyz`).
- Secret delivery — replace the inline Secret with Sealed Secrets / External Secrets Operator and enable etcd encryption at rest.
