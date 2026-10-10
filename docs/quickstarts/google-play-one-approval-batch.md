# One-Approval Google Play Growth Batch

## Purpose

Enable Codex to assess and execute a **finite, approved collection** of no-build Google Play localization and regional-pricing actions with **one operator approval of the entire immutable plan**, not repeated native dialogs or per-app confirmations.

## Trust and authority

Planning, `mra play growth-batch-check`, and all read-only vendor observations need no approval. Codex presents the exact plan and its SHA-256, **then stops**. The operator approves it once in the current conversation using `APPROVE PLAY GROWTH BATCH <sha256>`; no other language or earlier approval counts. Codex may then call `mra --yes play growth-batch-apply` with exactly that SHA and original bytes. Do not call high-risk MCP tools for these already-authorized steps, because they trigger separate native dialogs. Other actions remain subject to their existing gates.

The CLI cannot cryptographically verify the conversation's human-authorship. `--yes` is therefore a *trusted operator* surface: Codex is responsible for ensuring the approval actually appeared in the current conversation and matches the complete manifest. The SHA, schema validation, live vendor read-back and drift checks protect **scope integrity**, but cannot substitute for authentic human approval.

Do not use this workflow to grant standing permission, schedule future batches, approve unspecified future actions, or silently regenerate an expired/drifted plan.

## Supported operation kinds

- `listing-create` — creates only an absent locale; refuses if another listing has appeared in that language; reads text back.
- `listing-update` — exact expected-current text (plus optional `video` metadata) checked inside the Play edit; current promotional video cannot silently be removed.
- `pricing-apply` — references a separately persisted, source-hashed MRA regional plan for a supported modern `OneTimeProduct`. No arbitrary direct price edits.

Out of scope: release builds/uploads, track changes, app availability, subscription price changes, legacy products, paid-app download prices, review replies, image replacement, or RevenueCat/AdMob mutations. Those require a separately scoped design and authorization; Codex must not improvise them inside this manifest.

## Approved manifest format (UTF-8 JSON)

The file contains `schema_version: 1`, `created_at`, `expires_at` UTC timestamp strings, and a non-empty `actions` array (maximum 50 actions; validity window at most seven days). Package names must match **live local MRA profiles**. Each action has a fixed schema; unknown fields are refused.

```json
{
  "schema_version": 1,
  "created_at": "2026-10-10T21:00:00Z",
  "expires_at": "2026-10-11T21:00:00Z",
  "actions": [
    {
      "kind": "listing-create",
      "profile": "example-app",
      "package_name": "com.example.application",
      "language": "es-ES",
      "desired": {
        "language": "es-ES",
        "title": "Nombre de ejemplo",
        "shortDescription": "Descripción corta verificada",
        "fullDescription": "Descripción completa que coincide con la aplicación publicada."
      }
    },
    {
      "kind": "listing-update",
      "profile": "another-app",
      "package_name": "com.example.second",
      "language": "de-DE",
      "expected_current": {
        "language": "de-DE",
        "title": "Alter Titel",
        "shortDescription": "Alter Kurztext",
        "fullDescription": "Alte Beschreibung",
        "video": null
      },
      "desired": {
        "language": "de-DE",
        "title": "Neuer Titel",
        "shortDescription": "Verbesserter Kurztext",
        "fullDescription": "Verbesserte Beschreibung der echten Funktionen."
      }
    },
    {
      "kind": "pricing-apply",
      "profile": "example-app",
      "package_name": "com.example.application",
      "plan_id": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    }
  ]
}
```

**Example only**: this sample has illustrative timestamps and placeholder identifiers. Regenerate it from current live Play data and real MRA plans before use. The `plan_id` must refer to a persisted plan on the same local machine. Preserve all approved bytes verbatim; do not auto-edit the manifest after obtaining approval.

## Operator flow

1. Codex inspects the Play production tracks, current listings and plans, privacy/policy constraints and real app capabilities. Do not market unreleased features or falsely claim that translated store text implies translated app UI.
2. Codex creates the manifest locally (not in a public repository) and runs:

   ```bash
   shasum -a 256 /path/to/play-growth-approved.json
   mra play growth-batch-check \
     --manifest /path/to/play-growth-approved.json \
     --sha256 <exact-64-hex-digest>
   ```

3. Codex displays **all apps, actions, exact current/proposed localized text and regional prices**, caveats, potential effects, and the final hash. Check that every action is `ready` or `already_applied`. Stop and ask for exactly one approval:

   ```text
   APPROVE PLAY GROWTH BATCH <exact-64-hex-digest>
   ```

4. After that exact operator approval in the same conversation, invoke once:

   ```bash
   mra --yes play growth-batch-apply \
     --manifest /path/to/play-growth-approved.json \
     --sha256 <approved-64-hex-digest>
   ```

5. MRA rechecks the full batch before any write, then checks each item again before mutation. Existing exact desired state is an idempotent no-op. Each committed item is verified against Play; pricing also validates protected US/GB prices, active purchase option, region version and other fields through the existing pricing engine.
6. On any failure, halt remaining actions and return partial results. **Google Play changes across apps are not atomic.** Do not automatically roll back previously verified updates or blindly retry an uncertain operation. Re-read remote state, distinguish already-applied from drift and report any new proposed plan for a *new* one-time approval.
7. A successful Play API read-back does **not** prove public publication. Inspect managed publishing, Console review queue and public listing propagation separately.

## Approval scope and expiry

An approval binds the **exact file bytes and all actions** identified by the displayed SHA-256. It does not authorize removing a line and applying a changed hash, changing price plans, adding a locale, or republishing a candidate feature set. An approved batch expires according to the manifest (within seven days). A new manifest, changed action, stale pricing plan or elapsed expiry requires new review and approval.

The execution command only handles listing text and supported regional pricing. Asset changes, review replies or other Play operations can be proposed during portfolio assessment, but are not silently included.

## Testing

```bash
python3 scripts/validate-agentdefaults.py
python3 -m unittest discover -s tools/mobile-release-automation/tests -t tools/mobile-release-automation
```

Review the `growth_batch.py` unit tests for malformed manifest, hash mismatch, scope conflicts, drift, partial failure, idempotent recovery, and the `--yes` gate.
