# Mobile Release Automation Security Model

## Agent boundary

Version 1.3 uses a risk-gated MCP surface rather than a read-only one.

Both `mra-mcp` and `mra-agent-mcp` expose the same local server. The AI may perform reads, dry-runs, and contained mutations directly. High-risk mutations require a real local operator approval before the vendor API call occurs.

## Risk classes

- `observe`: diagnostics, reads, and Play dry-runs.
- `contained`: internal-track Play releases, creation of individual RevenueCat objects that do not rewire live access, and individual AdMob app/ad-unit creation where supported.
- `high`: non-internal Play releases or promotions, making a RevenueCat offering current, attaching products to entitlements or packages, backing-store product creation, and future destructive, financial, or broad multi-app mutations.

High-risk MCP tools do not accept an agent-controlled `confirm=true` bypass. On macOS they invoke a native approval dialog describing the exact target. If the operator declines, the dialog times out, or native approval is unavailable, the action fails closed.

The operator CLI remains available for explicit local work and retains its own confirmation behavior.

## Credentials

Bitwarden Secrets Manager remains the static credential source. The Bitwarden machine-account token remains in macOS Keychain, and local MRA configuration stores only immutable secret references.

Google Play publisher credentials and the separate Google credential used by RevenueCat remain distinct. The publisher credential is used for Play release automation; the RevenueCat credential is the only Google credential intended to cross into RevenueCat.

## Verification

After updating MRA, run:

```bash
mra-agent doctor
```

The report should show `platform_mutations` as `risk-gated` and `human_approval` as ready on macOS.

For an MCP client, call `approval_policy` before mutation-heavy work. Reads and contained actions may proceed through MCP. High-risk operations must surface the local human approval dialog and must not execute without approval.

## Trust boundary

The native approval gate protects the MCP path. It does not make unrestricted shell access safe. An agent with unrestricted execution under the same macOS user could invoke local binaries directly. Where this approval boundary matters, expose the MCP server and restrict direct access to the operator CLI, Bitwarden CLI, and Keychain commands.
