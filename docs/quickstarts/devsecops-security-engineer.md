# DevSecOps Security Engineer Quickstart

## Purpose

Provide the shortest reliable path for using the DevSecOps Security Engineer to review and harden Terraform/OpenTofu, Ansible/Automation Platform, Jenkins, CI/CD, GitOps, Kubernetes, cloud/IAM, containers, and software supply-chain controls.

## Use This Stack

```text
agents/devsecops-security-engineer.md
skills/devsecops-security-engineering.md
prompts/implementation/devsecops-security-task.md
schemas/devsecops-security-task.schema.json
examples/devsecops-security-task.yaml
docs/devsecops-security-engineer-acceptance-tests.md
.github/agents/devsecops-security-engineer.agent.md
```

## Best-Fit Tasks

- audit Jenkins controller/agent/credential/plugin security
- harden pull-request and deployment trust boundaries
- audit Terraform state, backend, provider/module provenance, identity, and plan/apply controls
- audit Ansible/AAP secrets, `become`, inventories, execution environments, collections, RBAC, credentials, and output leakage
- investigate CI/CD credential exposure, dependency poisoning, cache/artifact integrity, or excessive automation privilege
- qualify a security-sensitive DevOps change before release
- implement a narrowly scoped security remediation with explicit verification

## Start With the Privileged Path

Before scanning everything, establish:

```text
source/change entry point
attacker-controlled inputs
privileged identities
secret acquisition and use
execution environment
state owner
artifact and deployment path
network/trust boundaries
audit evidence
rollback/recovery
```

The most important question is usually not “which scanner is installed?” but “what untrusted input can reach what privileged capability?”

## Platform Priorities

### Terraform / OpenTofu

Treat state and plans as sensitive assets. Verify backend access/encryption/locking/recovery, provider/module provenance, `.terraform.lock.hcl`, runner identity, environment isolation, destructive plans, and mutable references. `sensitive` redacts output but must not be assumed to remove a value from state; verify supported state-omission mechanisms for the actual Terraform/provider version before using them.

### Ansible / Automation Platform

Do not store plaintext secrets. Vault protects data at rest; decrypted runtime output still needs safe handling such as `no_log` when secret-bearing output can be exposed. Review `become`, shell/command usage, TLS/SSH verification, inventory authority, collection/role provenance, execution-environment trust, AAP RBAC/credentials/templates/webhooks, and logging/artifact leakage.

### Jenkins

Review Security Realm and Authorization Strategy, controller isolation, trusted versus untrusted agents, credential scope, PR/fork trust, shared-library/Groovy trust, JCasC/seed ownership, plugin advisories, CSRF, reverse proxy/TLS, parameter/environment injection, workspaces/caches/artifacts, and deployment identity.

## Example Invocation

Use [`../../prompts/implementation/devsecops-security-task.md`](../../prompts/implementation/devsecops-security-task.md), or adapt [`../../examples/devsecops-security-task.yaml`](../../examples/devsecops-security-task.yaml).

A concise request can be:

```text
Use the DevSecOps Security Engineer.

Target: <repo/system/environment>
Mode: review
Platforms: terraform, ansible, automation_platform, jenkins
Goal: Find the highest-risk ways untrusted code or users could reach production credentials or infrastructure authority.
Authority: observe/propose only.
First: trace identities, secrets, untrusted inputs, controller/agent boundaries, state ownership, dependency provenance, and deployment path.
Done when: findings are evidence-backed, P0-P3 prioritized, remediation is concrete, and unverified runtime checks are explicit.
```

## Security Review Order

A strong first pass is usually:

1. identify privileged identities and credentials
2. identify attacker-controlled code/data
3. map where the two can meet
4. inspect state/secret persistence and logs/artifacts
5. inspect dependency/plugin/provider/module/collection trust
6. inspect controller/runner/agent isolation
7. inspect enforced approvals and environment boundaries
8. inspect audit/detection and recovery
9. run available scanners to find additional defects
10. verify the actual security postcondition after remediation

## Scope Boundary

This agent owns security-focused DevOps decisions and fixes. Broad platform refactors with no security-specific outcome belong to `agents/principal-devops-engineer.md`. Documentation-only work belongs to `agents/devops-documentation-engineer.md`. AI application security belongs to `agents/principal-ai-engineer.md` unless the platform and AI behavior must change together.

## Validation

For AgentDefaults stack changes run:

```bash
python3 scripts/validate-agentdefaults.py
```

For a real target, run only the applicable repository/platform security checks that are actually available and authorized. A green scanner is not proof of a secure privileged control path.

## Completion

A task is complete only when requested findings or mutations exist, material claims are traceable to evidence, authority is respected, intended security postconditions are verified where possible, secret values were not exposed, and every unrun check remains `UNVERIFIED`.