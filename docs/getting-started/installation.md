# Installation

## Via DPanel

1. Open DPanel at `https://panel.yourdomain.com`
2. Find **DClaw Route** in the app grid
3. Click **Install**
4. The DClaw Operator will provision:
   - Namespace: `dclaw-route`
   - Frontend deployment (Next.js)
   - Backend deployment (FastAPI)
   - PostgreSQL database (CloudNativePG)
   - Ingress with TLS

## Via kubectl

```bash
# Apply the DClawApp CRD
kubectl apply -f - <<EOF
apiVersion: platform.dclaw.io/v1
kind: DClawApp
metadata:
  name: route
spec:
  appId: route
  appName: DClaw Route
  version: 0.1.0
  category: logistics
  enabled: true
  frontend:
    image: ghcr.io/dclawstack/dclaw-route:latest
    replicas: 2
  backend:
    image: ghcr.io/dclawstack/dclaw-route-backend:latest
    replicas: 2
  database:
    enabled: true
    storage: 10Gi
  ingress:
    enabled: true
    host: route.yourdomain.com
    tls: true
EOF
```

## Verify

```bash
kubectl get pods -n dclaw-route
kubectl get ingress -n dclaw-route
```
