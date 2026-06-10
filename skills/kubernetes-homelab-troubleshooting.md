# Kubernetes Homelab Troubleshooting Skill

## Purpose

Use this skill when an agent needs to diagnose and resolve Kubernetes homelab issues in a practical, low-blast-radius way.

This skill supports `agents/kubernetes-homelab-engineer.md`, especially for Flux, DNS, Calico, MetalLB, WireGuard, ingress, local PV, and node scheduling problems.

## When To Use

Use this skill for:

- Flux reconciliation failures
- Pods stuck in Pending, CrashLoopBackOff, ImagePullBackOff, or Init states
- DNS failures
- Ingress routing failures
- MetalLB LoadBalancer issues
- Calico CNI/VXLAN problems
- Oracle/WireGuard node connectivity issues
- Local PV/PVC binding issues
- Metrics-server, CoreDNS, Prometheus, Grafana, or app health issues

## Inputs Needed

Ask for targeted command output only when repo inspection is not enough.

Useful inputs:

```bash
flux get all -A
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp | tail -50
kubectl describe pod -n <namespace> <pod>
kubectl logs -n <namespace> <pod-or-deploy> --tail=100
```

For homelab network issues:

```bash
kubectl get svc -A
kubectl get ingress -A
kubectl get pods -n kube-system -o wide
kubectl get pods -n metallb-system -o wide
kubectl get pods -n ingress-nginx -o wide
sudo wg show
```

## Instructions

### 1. Start With Scope

Classify the failure:

| Area | Symptoms |
|------|----------|
| Flux | Kustomization/HelmRelease not ready, source errors, apply errors |
| Scheduling | Pending pods, node affinity mismatch, taints, unavailable nodes |
| Image | ImagePullBackOff, wrong tag, private registry auth |
| Storage | PVC Pending, PV node affinity conflict, mount failures |
| Network | Service unreachable, ingress 404/502, MetalLB IP missing |
| DNS | `nslookup` fails, services unreachable by name, CoreDNS errors |
| CNI | Pods cannot communicate, Calico pods unhealthy, VXLAN/MTU issues |
| Node | NotReady, WireGuard down, kubelet issues, disk pressure |

### 2. Use Least-Destructive Diagnostics First

Prefer read-only diagnostics before restarts or deletes.

Good first checks:

```bash
flux get all -A
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp | tail -50
kubectl describe <resource> -n <namespace> <name>
```

Avoid jumping directly to:

- Deleting pods
- Deleting PVCs/PVs
- Reinstalling CNI
- Rebooting nodes
- Restarting kubelet
- Rebuilding Flux
- Changing MetalLB pools

### 3. Map Symptom to Likely Cause

Use these heuristics, but verify before acting:

- `Pending` + PVC: check PV/PVC binding, storage class, local PV node affinity.
- `Pending` + node affinity: check node labels and Oracle node exclusion rules.
- `ImagePullBackOff`: check image name, tag, registry auth, architecture support.
- Flux Kustomization error: run local `kubectl kustomize` or inspect missing resources.
- HelmRelease not ready: inspect HelmRelease events and chart values.
- Ingress 404: check host, path, ingress class, service name, service port.
- Ingress 502/504: check endpoints and pod readiness.
- LoadBalancer pending/missing IP: check MetalLB pool and speaker health.
- DNS failure: check CoreDNS placement, logs, and Oracle node scheduling.
- Calico failure: check node IP autodetection, VXLAN interface, MTU, and node readiness.
- Oracle node NotReady: check WireGuard and node reachability first.

### 4. Preserve Homelab Constraints

When diagnosing this repo, remember:

- Oracle nodes are scheduling-sensitive due to WireGuard reliability.
- Local PV workloads should stay on the correct local node.
- CoreDNS, metrics-server, and MetalLB speaker should avoid Oracle nodes unless explicitly supported.
- MetalLB IPs must not conflict.
- `.k8s.local` hosts usually require local DNS or `/etc/hosts` entries.
- GitOps drift should be fixed in git, not only in the live cluster.

### 5. Produce a Ranked Diagnosis

Do not list every theoretical cause. Give the most likely cause first.

Use this format:

```markdown
Likely cause: <cause>.

Evidence:
- <evidence from logs/files/output>

Fix:
- <repo change or command>

Validate:
```bash
<command>
```
```

### 6. Escalate Carefully

Only suggest higher-risk actions after safer checks fail.

Escalation order:

1. Inspect resources/logs/events.
2. Reconcile Flux.
3. Restart only the affected deployment/pod if safe.
4. Patch repo manifests and reconcile.
5. Restart node-level services only if evidence points there.
6. Change CNI, MetalLB, CoreDNS, or storage only with explicit rollback notes.

### 7. Convert Runtime Fixes Back to Git

If a temporary runtime command fixes the issue, identify the declarative change needed to make it permanent.

Example:

```markdown
The runtime restart may clear the current failure, but the durable fix is to update `<file>` so Flux reconciles the correct state.
```

## Validation Commands By Area

### Flux

```bash
flux get all -A
flux logs --all-namespaces --level=error --tail=100
kubectl describe kustomization -n flux-system apps
kubectl kustomize apps/base
```

### Scheduling

```bash
kubectl get nodes --show-labels
kubectl describe pod -n <namespace> <pod>
kubectl get events -A --field-selector reason=FailedScheduling
```

### Storage

```bash
kubectl get pv,pvc -A
kubectl describe pvc -n <namespace> <pvc>
kubectl describe pv <pv>
```

### DNS

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns -o wide
kubectl logs -n kube-system deploy/coredns --tail=100
kubectl run -it --rm dns-test --image=busybox --restart=Never -- nslookup kubernetes.default.svc.cluster.local
```

### Ingress

```bash
kubectl get ingress -A
kubectl describe ingress -n <namespace> <ingress>
kubectl get svc,endpoints -n <namespace>
```

### MetalLB

```bash
kubectl get ipaddresspools -A
kubectl get l2advertisements -A
kubectl get pods -n metallb-system -o wide
kubectl get svc -A | grep LoadBalancer
```

### Calico

```bash
kubectl get pods -n kube-system -l k8s-app=calico-node -o wide
kubectl logs -n kube-system -l k8s-app=calico-node --tail=50
kubectl get nodes -o wide
```

### WireGuard / Oracle Nodes

```bash
kubectl get nodes -o wide
sudo wg show
ping <wireguard-ip>
```

## Expected Output

```markdown
Likely cause: <specific cause>.

Evidence:
- <evidence>
- <evidence>

Fix:
- <specific action or file change>

Validate:
```bash
<commands>
```

Rollback:
- <only if risky>
```

## Quality Bar

A good troubleshooting response:

- Starts with the most likely cause
- Uses evidence from repo files or command output
- Avoids generic Kubernetes advice
- Avoids destructive fixes until necessary
- Preserves GitOps as the long-term fix
- Includes focused validation commands
- Notes rollback when blast radius is non-trivial

## Notes

Pair this skill with `skills/kubernetes-gitops-change-management.md` when a diagnosis requires a repo patch.
