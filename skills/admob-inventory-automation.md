# AdMob Inventory Automation Skill

## Purpose

Create, list, and verify AdMob apps and ad units through the AdMob API where the account permits it, and handle the common case where Google has not granted the account access to the creation endpoints.

## Trigger Conditions

Load when the task involves AdMob apps, ad units, mediation inventory, or diagnosing why AdMob automation is not working.

## Establish Access Before Planning

AdMob is the one platform in this stack whose write path may simply be unavailable. Establish that first.

```text
1. Confirm the AdMob API is enabled on the Cloud project.
2. Confirm a cached OAuth token exists for a Google Account with AdMob access.
3. Probe monetization access without creating anything.
4. Record the result and plan against it.
```

Do not present a plan whose critical path assumes creation works before the probe says so.

## Two Structural Constraints

### Service accounts do not work

Google documents that all AdMob API requests "must be authorized by an authenticated user" and that "No other authorization protocols are supported." AdMob authenticates a Google Account, not a project identity.

Consequences:

- There is no IAM role, workload identity, or key file that makes a service account work against AdMob.
- Authentication requires an OAuth client of type **Desktop app** and a one-time browser consent by an account with AdMob access, producing a refresh token.
- That refresh token is a personal user credential. Losing it is an account compromise, not merely a broken pipeline.
- Unattended operation depends on that cached refresh token remaining valid.

### Creation is limited access

`accounts.apps.create` and `accounts.adUnits.create` both carry the documented note: "This method has limited access. If you see a 403 permission denied error, please reach out to your account manager for access."

Consequences:

- The gate is applied by Google per AdMob account. It is not a scope problem.
- Granting `admob.monetization` on the consent screen does not lift it.
- There is no documented self-service allowlist. Access comes through an AdMob account manager, which most accounts do not have.
- A 403 from these methods is a final answer for this account, not a transient error.

## Scopes

```text
https://www.googleapis.com/auth/admob.readonly      publicly documented
https://www.googleapis.com/auth/admob.report        publicly documented
https://www.googleapis.com/auth/admob.monetization  required for creation; the gated one
```

`admob.monetization` does not appear on AdMob's public OAuth setup page and appears only on the gated method pages. If the consent screen refuses it, request read scopes only and treat creation as unavailable.

## Probing Without Mutating

`accounts.mediationGroups.list` requires the same `admob.monetization` scope as the create methods and changes nothing, which makes it the safest available signal.

Interpretation:

```text
denied   monetization access is not granted; creation is unavailable
likely   the scope is accepted; creation is still separately gated
unknown  authentication or account resolution failed first
```

Report `likely` as an indicator, never as a guarantee. Confirm with one real creation before relying on it for a plan.

## When Creation Is Available

App creation:

- `platform` is `ANDROID` or `IOS`.
- Supplying `linkedAppInfo.appStoreId` (the Play package name for Android) links the AdMob app to the published store listing. Omitting it creates an unlinked manual entry, which is usually not what the operator wants.

Ad unit creation:

- `adFormat` is one of `BANNER`, `INTERSTITIAL`, `NATIVE`, `REWARDED`, `REWARDED_INTERSTITIAL`, `APP_OPEN`.
- `adTypes` is `RICH_MEDIA`, `VIDEO`, or both, where the format supports it.
- The parent `appId` must be an AdMob app id, not a Play package name.

## Ad Unit Ids Are Effectively Permanent

An ad unit id compiled into a shipped build cannot be changed without another release. Therefore:

- Create ad inventory **before** the build that embeds it.
- Report every created ad unit id prominently so it reaches source control before the next build.
- Never create replacement ad units to fix a naming preference once ids have shipped.

## When Creation Is Not Available

This is the expected case for most accounts. Do not attempt to work around it.

- Do not script the AdMob web console. It is fragile and outside the authorization this stack operates under.
- Produce the exact specification the operator needs: app display name, platform, linked store id, and for each ad unit its name, format, and ad types.
- After the operator completes the console steps, verify through the read-only API and record the resulting ids.
- If the operator has an AdMob account manager, the access request is a legitimate parallel path; it does not unblock today's task.

## Permission Classes

| Action | Class |
|---|---|
| List accounts, apps, ad units; generate reports; probe access | `observe` |
| Create an ad unit whose id has not shipped | `mutate_reversible` |
| Create an AdMob app | `mutate_reversible` |
| Create an ad unit intended for an imminent release | `mutate_irreversible` in practice, because the id will ship |

## Verification

Read inventory back and confirm each app's platform and linked store id, and each ad unit's id, format, ad types, and parent app.

## Failure Handling

| Symptom | Cause | Response |
|---|---|---|
| 403 on create | limited access, gated per account | report as a platform constraint; provide the manual specification; do not retry |
| no AdMob account visible | consented as the wrong Google Account | re-run consent as the publisher account owner |
| multiple accounts visible | the account owns several publisher ids | require an explicit publisher id |
| consent refuses `admob.monetization` | scope not permitted on the consent screen | proceed read-only; creation is unavailable |
| token refresh fails | revoked or expired refresh token | re-run the one-time consent |

## Safety

- Never script the AdMob console UI.
- The refresh token belongs to a person; never share, commit, or log it.
- Report an access denial honestly rather than presenting AdMob as automated when it is not.

## Output Contract

Report publisher id, the probe result with its evidence, every created or verified app and ad unit id with format, and explicitly which steps required manual console work.

## Completion Criteria

Access state is established with evidence, inventory matches intent, every ad unit id is reported before the build that embeds it, and unavailable capability is stated plainly with the manual path.
