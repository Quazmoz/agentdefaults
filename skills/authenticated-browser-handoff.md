# Authenticated Browser Handoff

## Purpose

Allow a browser-capable agent to use authenticated websites while the human securely completes login, account selection, CAPTCHA, passkey, consent, and multifactor authentication steps.

This skill is mandatory for every browser workflow that reaches an authenticated or security-sensitive state.

## When To Use

Use this skill when:

- A legitimate site requests authentication.
- The browser shows account selection, SSO, CAPTCHA, passkey, security key, or multifactor authentication.
- Reauthentication or privilege elevation appears.
- A private export or consequential account action needs confirmation.
- The agent must resume a saved workflow after human takeover.

## Inputs Needed

- Expected legitimate domain.
- Intended destination page.
- Saved research checkpoint.
- Expected non-sensitive account or app context.
- Whether the requested task is read-only or includes a write action.
- Exact consequential action, if one was requested.

## Preconditions

1. Save the current workflow state.
2. Navigate to the legitimate login page.
3. Verify the visible domain.
4. Stop browser interaction before any credential or security challenge is entered.
5. Disable sensitive screenshots or artifact capture during authentication.

## Workflow

### 1. Verify and Pause

Confirm the domain and display:

```text
The legitimate login page is open. Please take control of the browser and complete login, passkey, CAPTCHA, or multifactor steps directly. Do not send credentials or security codes through chat. Tell me when the account page has loaded, and I will resume from the saved checkpoint.
```

### 2. Human Completes Authentication

The agent must not:

- Type or request passwords.
- Ask for one-time passwords or recovery codes.
- Read or export cookies, tokens, local storage, session storage, or request headers.
- Screenshot login fields or authentication screens.
- Attempt to solve CAPTCHA.
- Circumvent security warnings.

### 3. Detect Authenticated State

Resume only after:

- The user confirms completion, or
- The expected authenticated destination visibly loads.

Confirm context using non-sensitive visible indicators such as app name, workspace name, account display name, or dashboard heading.

Do not expose private identifiers in public artifacts.

### 4. Resume From Checkpoint

- Inspect the current page.
- Explain the detected non-sensitive state.
- Continue from the saved stage.
- Do not restart completed public research.
- Pause again if reauthentication, consent, CAPTCHA, or privilege elevation appears.

## Consequential-Action Protection

Research and account mutation are different safety classes.

Without explicit user authorization, do not:

- Publish or unpublish an app.
- Change pricing.
- Modify production releases.
- Add or remove users.
- Change banking or tax information.
- Accept legal agreements.
- Submit declarations.
- Delete data.
- Send communications.
- Change account security.
- Create credentials.
- Download sensitive user-level exports.
- Modify production configuration.

For an authorized write action:

1. Explain the exact final action.
2. Show the target account, app, release, or resource.
3. Pause immediately before the final consequential click.
4. Require explicit confirmation.
5. Perform only the confirmed action.
6. Capture a non-sensitive completion artifact.

## Human Handoff Points

Always hand off for:

- Passwords.
- Passkeys and security keys.
- CAPTCHA.
- Multifactor authentication.
- Account selection when ambiguous.
- Consent dialogs.
- Privilege elevation.
- Private report downloads.
- The final click of a consequential action.

## Authentication Behavior

- Reuse the active session only for the current user-directed workflow.
- Do not export session material.
- Do not copy secrets into files.
- Do not evade session expiration.
- Prefer a dedicated browser profile for research.
- Mark authenticated-source artifacts as private.

## Output Contract

```json
{
  "handoff_status": "not_needed|waiting_for_user|authenticated|blocked|expired",
  "expected_domain": "string",
  "detected_domain": "string|null",
  "destination_detected": true,
  "context_confirmed": "non-sensitive string|null",
  "resume_stage": "string",
  "consequential_action_pending": false
}
```

## Checkpoint Format

```json
{
  "skill": "authenticated-browser-handoff",
  "stage": "pre_auth|waiting|post_auth|confirmation|complete",
  "expected_domain": "string",
  "resume_skill": "string",
  "resume_unit_key": "string",
  "safe_context": {},
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Wrong domain: stop and navigate only to the verified legitimate domain.
- Unexpected account: pause and ask the user to select the correct context.
- Expired session: save state and repeat the handoff.
- CAPTCHA: stop all automation and request takeover.
- Consent or privilege prompt: stop and request takeover.
- Sensitive data visible in an artifact: discard or redact the artifact before continuing.
- Consequential action not explicitly confirmed: do not execute it.

## Privacy and Safety Requirements

- Never request credentials or security codes through chat.
- Never store authentication material.
- Never record authentication screens.
- Never infer authorization for account-changing actions from authorization to research.
- Keep private account data out of public reports unless specifically requested.

## Example Invocation

```text
Use authenticated-browser-handoff when Play Console requests login. Save the current app and report stage, let me complete authentication, then resume without repeating public research.
```

## Example Successful Result

```text
Authentication complete. The expected Play Console app dashboard is visible, and the workflow resumed at search-term export.
```

## Example Partial Result

```text
The legitimate login page is ready and the checkpoint is saved. Waiting for human authentication.
```

## Example Failure Result

```text
Stopped because the browser redirected to an unexpected domain. No credentials or session data were collected.
```

## Quality Bar

- Human enters every credential and security factor.
- Authentication screens are never captured.
- Resume is checkpoint-based.
- Consequential actions require immediate pre-action confirmation.
