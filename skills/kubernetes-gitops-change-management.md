# Kubernetes GitOps Change Management Skill

## Purpose

Safely add, modify, review, deploy, or remove Kubernetes desired state in `Quazmoz/K8SHomelab` without breaking Flux reconciliation, leaking secrets, targeting the wrong cluster, or confusing a Git change with a verified runtime outcome.

This skill is the default implementation skill for `agents/kubernetes-homelab-engineer.md`.

## Trigger Conditions

Use when the task changes or reviews:

- `apps/base/` or `clusters/my-homelab/`
- Deployment, StatefulSet, DaemonSet, Job/CronJob, Service, Ingress, ConfigMap, Secret reference, PVC/PV, RBAC, NetworkPolicy, HelmRelease, HelmRepository, or Flux Kustomization resources
- enabled/disabled app state in Kustomize
- a GitOps rollback or removal

Pair with `skills/kubernetes-homelab-troubleshooting.md` when runtime failure is driving the change.

## Preconditions

Before writing:

1. establish repository and branch
2. read repo `AGENTS.md`
3. if local Graft is available, use `graft map` / `graft ask ... --source` as required by the repo
4. inspect the relevant repo-local `.github/skills/*/SKILL.md`
5. inspect the exact target manifests and parent Kustomization/HelmRelease path
6. determine whether the target branch is Flux-watched and whether `prune` applies
7. establish whether the user authorized repo mutation, deployment, and live-cluster mutation

Remote GitHub-only runtimes must not fabricate Graft output; state the limitation and continue from exact current GitHub files.

## Evidence Rules

Current manifests and runtime state outrank old topology documentation. If `README.md`, `AGENT_CONTEXT.md`, `docs/NETWORK.md`, app docs, or this skill disagree, report the drift and follow higher-authority/current evidence.

Do not rely on the old `apps/base/ORACLE_NODE_POLICY.md` path unless it exists on the target branch. Oracle/WireGuard behavior is conditional on current evidence.

## State and Side-Effect Model

- Git watched branch = desired state
- Flux = reconciliation/controller state
- Kubernetes API = runtime state
- PV/external database = persistent state that Git revert may not restore

A push/merge to the Flux-watched branch is a deployment side effect. With `prune: true`, removing a resource from desired state may delete it from runtime. Never treat such a deletion as an ordinary text edit.

## Permission Classes

### Observe

Read repository/Graft data, render manifests, inspect Kubernetes/Flux status.

### Propose

Produce a patch/plan without committing or deploying.

### Mutate repository

Allowed only when implementation authority is granted. Prefer a branch/PR for medium/high-risk changes when possible.

### Deploy / mutate runtime

Requires deployment/runtime authority plus a verified homelab context. High-risk changes require explicit approval and rollback/recovery evidence.

## Multi-Cluster Safety

Never overwrite kubeconfig and never assume the current context is the homelab.

Before live mutation:

```bash
kubectl config get-contexts
kubectl config current-context
kubectl --context <homelab-context> cluster-info
kubectl --context <homelab-context> get nodes -o wide
```

Prefer explicit `--context <homelab-context>` on subsequent runtime commands. If identity is ambiguous, stop before mutation.

## Change Procedure

1. **Trace inclusion.** Confirm every modified/new resource is reachable from the Flux Kustomization path. Detect orphan manifests and accidental removals.
2. **Inspect conventions.** Load the relevant repo-local deployment/storage/Flux/MCP skill and nearby app examples.
3. **Classify risk.** Low, medium, or high.
4. **Model dependencies.** Include secrets/config, storage, scheduling, service/ingress, external endpoints, architecture, and operator/controller dependencies.
5. **Implement minimally.** Preserve naming, namespace, labels, selectors, image architecture support, security context, and rollout/storage semantics.
6. **Validate desired state.** Render Kustomize, check YAML/API references, inspect diff, and scan for secret leakage.
7. **Adversarial review.** Check prune-driven deletes, selector drift, broken Service endpoints, PVC moves, broad RBAC, privileged/host access, public ingress, bad image tags/architectures, and unbounded autonomous-agent permissions.
8. **Deploy only if authorized.** Push/merge watched branch and reconcile only when deployment authority exists.
9. **Verify controller state.** Confirm Flux observed the intended revision and Ready status.
10. **Verify runtime.** Check the affected workload, endpoints, data/storage, events, and user-facing postcondition.
11. **Rollback.** Define Git revert plus any data/storage/manual recovery required.

## Risk Model

| Risk | Examples | Minimum handling |
|---|---|---|
| Low | docs/comments/read-only diagnostics | targeted validation |
| Medium | new app, version/resource/probe/config/ordinary ingress change | render + diff + rollback + post-deploy verification |
| High | prune deletion, PVC/PV, CNI/DNS/MetalLB/ingress controller/Flux, SOPS keys, node/control-plane, broad RBAC, public auth exposure, backup/restore | explicit approval + recovery evidence + staged verification |

## Manifest Safety Checks

Check as applicable:

- stable API versions and explicit namespace
- Kustomize/Flux resource inclusion
- correct labels/selectors
- pinned/reviewable image tag and target architecture support
- CPU/memory requests and sensible limits
- startup/readiness/liveness probes
- minimal ServiceAccount/RBAC
- non-root/no-privilege-escalation/dropped capabilities/read-only filesystem/seccomp where supported
- no unnecessary hostPath/hostNetwork/privileged/NodePort
- deliberate node affinity/tolerations
- safe RWO rollout and local PV node affinity
- internal cluster DNS for service calls
- protected ingress for sensitive administration surfaces

## Secret Handling

Never create or expose plaintext credentials. Use current repo SOPS/Age patterns and existing encrypted Secret references/templates.

Do not decrypt secret files into model-visible context. Before finalizing, inspect changed lines for likely secret material. Redact sensitive runtime logs.

## AI / Automation Workloads

For OpenClaw, Hermes Agent, MCP, n8n, OpenWebUI tools, or other tool-using automation, also verify:

- least-privilege identity/RBAC
- explicit allowed tools/endpoints
- bounded retries, loops, concurrency, and spend where applicable
- approval gates for destructive or privileged side effects
- idempotency/duplicate behavior for external mutations
- observable failure state without secret logging

## Retry and Failure Semantics

- Bounded retries only for clearly transient read operations.
- Never blindly retry push/merge/reconcile/restore/secret rotation after timeout or unknown result; verify authoritative state first.
- Do not issue repeated Flux reconciles to mask a bad desired-state revision.
- If rollback changes persistent data or external state, Git revert alone is insufficient; state the recovery procedure.

## Validation

Use the smallest applicable set:

```bash
kubectl kustomize apps/base
# optional if installed
kustomize build apps/base

git diff --check
git diff -- apps clusters

kubectl --context <homelab-context> get nodes -o wide
flux --context <homelab-context> get all -A
kubectl --context <homelab-context> get pods -A -o wide
kubectl --context <homelab-context> get events -A --sort-by=.lastTimestamp
```

After deployment, verify the specific app and dependency chain rather than relying only on global status.

## Output Contract

```text
STATUS
DISCOVERED
CHANGE
RISK
IMPLEMENTED
VERIFIED
UNVERIFIED
ROLLBACK
USER ACTION
```

## Completion Criteria

Complete only when the desired-state change is coherent and statically validated. If deployed, also require Flux revision/status and runtime postcondition evidence. If runtime access is unavailable, explicitly mark deployment health `UNVERIFIED`.