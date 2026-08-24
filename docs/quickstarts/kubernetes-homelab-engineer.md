# Kubernetes Homelab Engineer Quickstart

## Purpose

Provide the shortest safe entry path for using AgentDefaults against `Quazmoz/K8SHomelab` from Claude/Codex/Copilot or another repository-aware coding agent.

## Load Order

Use only the context needed for the task:

```text
agents/kubernetes-homelab-engineer.md
skills/kubernetes-gitops-change-management.md      # for implementation/review
skills/kubernetes-homelab-troubleshooting.md      # when diagnosing runtime failure
Quazmoz/K8SHomelab/AGENTS.md
Quazmoz/K8SHomelab/.github/skills/<relevant>/SKILL.md
current target manifests/runtime evidence
```

## Start Every K8SHomelab Task

1. Confirm repository/branch and whether the user wants analysis, repo implementation, deployment, or live remediation.
2. Read `AGENTS.md`.
3. If working from a local checkout with Graft, run `graft map` when needed and `graft ask "<task>" --source` before broad source reading.
4. Read only the task-relevant repo-local skill and exact manifests.
5. Treat current source/runtime evidence as authoritative; flag documentation drift rather than inheriting stale Oracle/WireGuard assumptions.
6. If live cluster access is needed, verify the homelab kube context and use explicit `--context`.
7. Before a watched-branch push/merge, remember that Flux may deploy automatically and `prune: true` can turn a source deletion into runtime deletion.

## Common Modes

### Review

Inspect desired state, reconciliation path, secrets, storage, scheduling, networking, security, observability, rollback, and runtime verification requirements. Do not mutate.

### Implement

Make the smallest coherent repo change, render/validate it, review the diff adversarially, and deploy only if deployment authority exists.

### Incident

Use desired state + Flux + runtime evidence, rank the most likely cause, choose least-destructive diagnostics, fix the durable GitOps cause, and verify the user-visible postcondition.

## Multi-Cluster Runtime Check

Before mutation:

```bash
kubectl config get-contexts
kubectl config current-context
kubectl --context <homelab-context> cluster-info
kubectl --context <homelab-context> get nodes -o wide
```

Do not overwrite another cluster's kubeconfig.

## Completion Rule

Repository validation can prove only repository correctness. A deployed-task success claim requires the intended Git revision, successful Flux observation/reconciliation, and affected runtime/user postcondition evidence. If runtime access is unavailable, state `UNVERIFIED` instead.