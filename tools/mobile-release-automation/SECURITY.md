# Mobile Release Automation Security Model

## Agent boundary

Version 1.2 makes the installed MCP surface read-only by default.

Both of these entry points run the read-only server:

```text
mra-mcp
mra-agent-mcp
```

They may inspect configured Google Play and RevenueCat state, but they do not expose platform publish, promote, create-product, create-app, or other live mutation tools.

Live changes remain operator actions through the local `mra` CLI. Mutating CLI commands continue to require `--yes`. Do not grant an AI client unrestricted shell access to the operator CLI if the intent is to enforce the MCP boundary.

## Bitwarden bootstrap

The Bitwarden Secrets Manager machine-account access token remains in macOS Keychain. Static vendor credentials are stored in the `mobile-release-automation` Bitwarden Secrets Manager project. Local configuration stores only immutable secret UUIDs.

## Google Play publisher credential

Store the Google Play publisher service-account JSON as a Bitwarden secret, for example:

```text
mra/google-play/publisher-service-account-json
```

Copy the Bitwarden secret UUID and bind it locally:

```bash
mra-agent auth bind-play --secret-id YOUR_BITWARDEN_SECRET_UUID
```

`mra-agent doctor` should then report `google_play_publisher` with source `bitwarden-secrets-manager`.

Google Play API sessions load the JSON directly from Bitwarden into process memory. No temporary credential file is created.

## Dedicated RevenueCat Google Play credential

Do not hand RevenueCat the publisher credential. Create a separate Google service account for RevenueCat and store its JSON as another Bitwarden secret, for example:

```text
mra/google-play/revenuecat-service-account-json
```

Bind that UUID separately:

```bash
mra-agent auth bind-revenuecat-play --secret-id YOUR_BITWARDEN_SECRET_UUID
```

This keeps release/publishing authority separate from the credential that is allowed to cross the RevenueCat vendor boundary.

## Play Console permissions

Do not use `Admin (all permissions)` for automation unless there is a specific requirement for the service account to manage Play Console users and permissions.

For the publisher service account, grant only what the automated workflow needs. A typical portfolio release account needs:

```text
View app information and download bulk reports (read-only)
Release apps to testing tracks
Release to production, exclude devices and use Play app signing
Manage store presence        # only when Play product/store configuration is automated
```

Add `Manage testing tracks and edit tester lists` only if the automation actually manages tester configuration.

For the separate RevenueCat service account, follow RevenueCat's documented Play permissions instead of granting release authority:

```text
View app information and download bulk reports (read-only)
View financial data, orders, and cancellation survey responses
Manage orders and subscriptions
Manage store presence
```

## Verification

After binding the publisher secret:

```bash
mra-agent doctor
mra play tracks --profile motionguard
mra play products --profile motionguard
```

Those commands verify credential resolution and read access without publishing a release.

For AI clients, use the read-only MCP entry point and ask it to run `doctor`, list Play tracks/products, and list RevenueCat apps/products. Platform mutations should be proposed by the AI and executed by the operator through the CLI after reviewing the exact target and blast radius.
