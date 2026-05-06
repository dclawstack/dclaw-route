# Troubleshooting

Common issues and solutions for DClaw Route.

## Quick Diagnostics

```bash
# Check app pods
kubectl get pods -n dclaw-route

# Check logs
kubectl logs -n dclaw-route deployment/dclaw-route-backend

# Check database
kubectl get clusters -n dclaw-route
```

## Sections

- [Common Issues](./common-issues)
- [FAQ](./faq)
