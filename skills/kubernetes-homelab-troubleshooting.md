# Kubernetes Homelab Troubleshooting Skill

## Purpose

Diagnose `Quazmoz/K8SHomelab` failures from authoritative desired state, Flux controller state, and live Kubernetes evidence while minimizing blast radius and converting temporary runtime workarounds into durable GitOps fixes.

## Trigger Conditions

Use for:

- Flux Kustomization/HelmRelease/source errors
- Pending, CrashLoopBackOff, ImagePullBackOff, OOMKilled, probe, or scheduling failures
- PVC/PV/mount problems
- Service/Ingress/MetalLB/DNS/Calico failures
- node readiness or capacity problems
- Prometheus/Grafana/Loki/Alloy failures
- MCP/OpenWebUI/n8n/OpenClaw/Hermes/Phoenix runtime issues

Pair with `skills/kubernetes-gitops-change-management.md` when remediation requires a repo patch.

## Preconditions

1. read `K8SHomelab/AGENTS.md`
2. use Graft-first discovery when local Graft is available
3. inspect the relevant current manifests and repo-local troubleshooting skill
4. identify the exact Git branch/revision under investigation
5. identify the exact Kubernetes context before running live commands

A remote GitHub-only agent can diagnose source-level issues but must mark live state as `UNVERIFIED` if it cannot query the cluster.

## Evidence Precedence

Use:

1. current manifests and exact Git revision
2. live Flux/Kubernetes state from the verified context
3. repo-local skill/current app docs
4. general README/AGENT_CONTEXT/docs
5. historical homelab assumptions

Current docs conflict on whether Oracle/WireGuard workers are active. Do not start an Oracle/WireGuard diagnosis unless current node/runtime/source evidence establishes those components.

## Cluster Context Safety

Before any mutation—and preferably before diagnostics when multiple clusters are configured—verify:

```bash
kubectl config get-contexts
kubectl config current-context
kubectl --context <homelab-context> cluster-info
kubectl --context <homelab-context> get nodes -o wide
```

Do not replace the operator's kubeconfig or silently switch an unrelated cluster context.

## Diagnostic Workflow

1. **Define symptom and postcondition.** What is failing, and what observable state would count as recovered?
2. **Inspect expected state.** Use Graft/current manifests to understand what Flux is meant to create.
3. **Check controller state.** Determine source revision, Kustomization/HelmRelease Ready status, and reconciliation errors.
4. **Check runtime state.** Nodes, pods, events, endpoints, PVC/PV, ingress, DNS, metrics, or logs as relevant.
5. **Correlate timelines.** Compare recent Git change/reconciliation generation with events/restarts.
6. **Rank hypotheses.** Give the evidence-backed most likely cause first; avoid shotgun lists.
7. **Use least-destructive test.** Prefer describe/log/get/render/connectivity checks before restart/delete.
8. **Remediate narrowly.** Patch desired state when configuration is causal. Runtime restarts are temporary diagnostics unless the desired state is already correct.
9. **Verify recovery.** Controller Ready + affected runtime/user postcondition + no new critical adjacent errors.
10. **Capture regression prevention.** Update manifests/docs/tests/monitoring when the defect can recur.

## Failure Classification

| Area | Typical evidence |
|---|---|
| Flux/source | source revision, reconciliation status, apply/health-check errors |
| Scheduling | FailedScheduling events, taints, affinity, resources, architecture |
| Image/runtime | pull errors, exit code, OOMKilled, command/args, architecture mismatch |
| Storage | PVC Pending, PV affinity, mount errors, RWO rollout conflict, disk capacity |
| Service | selectors, EndpointSlice/endpoints, readiness, targetPort |
| Ingress | host/path/class, backend endpoints, controller logs, 404/502/504 |
| MetalLB | pool/advertisement/speaker status, assigned IP, L2 reachability |
| DNS | CoreDNS readiness/logs, service lookup, upstream resolver behavior |
| CNI | Calico status/logs, node addressing, VXLAN/MTU/interface evidence |
| Node | Ready conditions, kubelet/container runtime/disk/memory/network |
| App dependency | Secret/config/database/cache/MCP/external API connection evidence |

## Read-Only Diagnostic Library

Use only relevant commands with an explicit context:

```bash
flux --context <homelab-context> get all -A
kubectl --context <homelab-context> get nodes -o wide
kubectl --context <homelab-context> get pods -A -o wide
kubectl --context <homelab-context> get events -A --sort-by=.lastTimestamp

kubectl --context <homelab-context> describe pod -n <namespace> <pod>
kubectl --context <homelab-context> logs -n <namespace> <pod> --tail=100
kubectl --context <homelab-context> get svc,endpoints,endpointslices -n <namespace>
kubectl --context <homelab-context> get ingress -A
kubectl --context <homelab-context> get pv
kubectl --context <homelab-context> get pvc -A
```

### DNS

```bash
kubectl --context <homelab-context> get pods -n kube-system -l k8s-app=kube-dns -o wide
kubectl --context <homelab-context> logs -n kube-system deploy/coredns --tail=100
```

Create a temporary DNS test pod only if runtime mutation authority permits it; remove it afterward and do not confuse it with desired GitOps state.

### MetalLB

```bash
kubectl --context <homelab-context> get ipaddresspools -A
kubectl --context <homelab-context> get l2advertisements -A
kubectl --context <homelab-context> get pods -n metallb-system -o wide
kubectl --context <homelab-context> get svc -A
```

### Calico

```bash
kubectl --context <homelab-context> get pods -n kube-system -l k8s-app=calico-node -o wide
kubectl --context <homelab-context> logs -n kube-system -l k8s-app=calico-node --tail=100
```

## Escalation Order

1. current Git/Graft evidence
2. read-only controller/runtime status
3. targeted logs/events/describe
4. local render/diff/manifest correction
5. reconcile the corrected desired state
6. restart only the affected workload when evidence supports it
7. node service restart only when node-level evidence supports it
8. CNI/DNS/MetalLB/storage/control-plane change only with explicit approval and rollback/recovery plan

Never delete PVC/PV, reset kubeadm, reinstall CNI, rotate SOPS keys, or wipe storage as an early troubleshooting step.

## Timeout and Retry Rules

- Retry transient read failures only with a small bound.
- After an uncertain mutation result, inspect authoritative state before repeating it.
- A Flux reconcile timeout may still have succeeded; check observed revision/conditions before retrying.
- A timed-out external side effect from an automation workload may have succeeded; inspect idempotency/state before retry.
- Stop if repeated evidence contradicts the current hypothesis rather than escalating blindly.

## AI / MCP / Automation Failure Rules

For OpenClaw, Hermes Agent, MCP, n8n, OpenWebUI tools, or similar systems, distinguish:

- Kubernetes transport/runtime failure
- service configuration or credential reference failure
- MCP/tool contract failure
- model/agent reasoning failure
- external API side-effect failure

Do not fix an agent/tool semantic defect by repeatedly restarting Kubernetes. For external mutations, investigate duplicate/idempotency semantics and approval boundaries before retrying.

## Remediation Requirements

A proposed fix must include:

- evidence tying it to the failure
- exact target file/resource or runtime operation
- blast radius
- rollback/recovery path when non-trivial
- validation commands and expected postconditions

If a temporary runtime action fixes the symptom, identify whether a Git change, alert, runbook, probe, resource setting, or dependency fix is needed to prevent recurrence.

## Output Contract

```text
STATUS
SYMPTOM
EVIDENCE
LIKELY CAUSE
IMPLEMENTED
VERIFIED
UNVERIFIED
RISKS
ROLLBACK
USER ACTION
```

## Completion Criteria

Do not call an incident resolved until the affected postcondition is observed and the controller/runtime state is consistent with desired state. If cluster access is unavailable, provide the evidence-backed diagnosis and targeted checks but mark resolution `UNVERIFIED`.