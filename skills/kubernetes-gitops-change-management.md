# Kubernetes GitOps Change Management Skill

## Purpose

Use this skill when an agent needs to add, modify, or review Kubernetes resources in a Flux/Kustomize/HelmRelease repository without breaking GitOps or cluster safety.

This skill supports `agents/kubernetes-homelab-engineer.md` and any general DevOps/Kubernetes agent.

## When To Use

Use this skill for:

- Adding a new app to `apps/base/<app>/`
- Updating Deployments, Services, Ingresses, PVCs, PVs, ConfigMaps, Secrets, RBAC, NetworkPolicies, or HelmReleases
- Reviewing whether a Kubernetes change is safe to reconcile through Flux
- Converting one-off Kubernetes changes into declarative GitOps manifests
- Preparing validation and rollback steps for homelab cluster changes

## Inputs Needed

The agent should gather:

- Target repository and branch
- Target app or namespace
- Relevant `kustomization.yaml` files
- Existing app directory conventions
- Any storage, ingress, secret, or scheduling requirements
- Runtime error output, if debugging an existing failed change

## Instructions

### 1. Inspect Current Structure

Before writing changes, inspect:

```text
README.md
AGENT_CONTEXT.md
apps/base/kustomization.yaml
clusters/<cluster>/
apps/base/<target-app>/
apps/base/local-storage/storage.yaml
```

If any file does not exist, search for the nearest equivalent.

### 2. Classify Change Risk

Use this risk model:

| Risk | Examples | Required Handling |
|------|----------|-------------------|
| Low | Labels, docs, comments, non-critical ConfigMap updates | Normal validation |
| Medium | New app, resource changes, ingress changes, probes, limits | Manifest render + Flux validation |
| High | Storage, CNI, DNS, ingress controller, MetalLB, auth, secrets, node scheduling | Explicit rollback and user-visible warning |

### 3. Preserve GitOps

All steady-state changes must be represented in git.

Do not use manual `kubectl apply` as the normal path. If temporary runtime debugging is needed, clearly mark it as non-GitOps and ensure the final desired state is committed to the repository.

### 4. Update Kustomize Correctly

When adding a resource or app:

- Add a local app `kustomization.yaml`.
- Add all resource files to the local app kustomization.
- Add the app directory to the parent `apps/base/kustomization.yaml`.
- Keep resources named consistently.
- Avoid orphan manifests that Flux will not apply.

### 5. Keep Manifests Safe

Check every resource for:

- Stable API version
- Explicit namespace where appropriate
- Consistent labels and selectors
- Resource requests and limits
- Probes where the app supports them
- Least-privilege RBAC
- Safe security context where image support allows
- No plaintext credentials
- No `latest` tag unless explicitly justified
- No unnecessary hostPath, privileged mode, hostNetwork, or broad ClusterRole permissions

### 6. Handle Secrets Correctly

Never write plaintext secrets.

Acceptable patterns:

- Reference an existing SOPS-encrypted Secret.
- Add a clearly marked placeholder requiring SOPS encryption before commit.
- Provide a local secret creation command for the user to run.
- Use the repository's existing secret pattern if one exists.

Run or recommend a secret scan before finalizing:

```bash
rg -n "password|passwd|secret|token|api[_-]?key|private[_-]?key|client_secret|connectionstring|webhook" apps docs clusters
```

### 7. Handle Storage Carefully

For stateful workloads:

- Check existing PV/PVC naming conventions.
- Check node affinity for local PVs.
- Do not move local PV workloads between nodes casually.
- Do not delete PVCs/PVs without explicit warning and rollback notes.
- Confirm reclaim policy is intentional.

### 8. Handle Networking Carefully

For services and ingress:

- Prefer existing IngressClass and annotation conventions.
- Avoid static MetalLB IP conflicts.
- Use `.k8s.local` hostnames for local-only homelab services unless instructed otherwise.
- Protect sensitive admin UIs with the repo's existing auth/network pattern.
- Avoid NodePort unless the repo already uses it or there is a clear reason.

### 9. Validate

Recommend the smallest relevant validation set:

```bash
kubectl kustomize apps/base
flux get all -A
flux reconcile kustomization apps --with-source
kubectl get pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp | tail -50
```

For app-specific validation:

```bash
kubectl get all -n <namespace>
kubectl describe ingress -n <namespace> <ingress>
kubectl logs -n <namespace> deploy/<deployment> --tail=100
```

## Expected Output

For a change plan:

````markdown
## Plan

- `<file>` — <change>
- `<file>` — <change>

## Risk

<low|medium|high> — <why>

## Validate

```bash
<commands>
```

## Rollback

<rollback path>
````

For completed work:

````markdown
Done — <summary>.

Changed:
- `<file>` — <change>

Validate:
```bash
<commands>
```

Rollback:
- Revert commit `<sha>` or restore `<file>`.
````

## Quality Bar

A good use of this skill:

- Preserves declarative GitOps
- Updates all required Kustomize references
- Avoids plaintext secrets
- Handles storage and scheduling deliberately
- Includes validation and rollback
- Avoids unnecessary cluster-wide changes

## Notes

This skill pairs directly with `skills/kubernetes-homelab-troubleshooting.md` when the change is driven by a runtime failure.
