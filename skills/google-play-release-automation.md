# Google Play Release Automation Skill

## Purpose

Upload, stage, promote, and verify Google Play releases and monetization products through the Play Developer API v3, without rebuilding artifacts and without unauthorized exposure to real users.

## Trigger Conditions

Load when the task involves app bundle upload, testing tracks, staged rollout, track promotion, or Play subscriptions, base plans, offers, or in-app products.

## Required Inputs

```text
package name        the exact Play package
bundle              path, version code, and how it was built
track               internal | alpha | beta | production | custom track name
release status      draft | inProgress | halted | completed
rollout fraction    required when status is inProgress
release notes       language-keyed text where the track shows them
authorization       the operator's approval naming this track
```

## Preconditions

- The Google Play Android Developer API is enabled on the Cloud project.
- The service account is invited in Play Console with the permissions this task needs, and no more.
- The app already exists in Play Console. The API cannot create a new app listing, complete content rating, or set target audience. A brand-new app requires those steps in the Console first. Data safety is the exception among these: `applications.dataSafety` does accept a declaration, but it is write-only, so treat the Console form as the only place the resulting state can be read.
- The bundle is signed consistently with what Play expects for this package.

## Authentication

Service account JSON with scope `https://www.googleapis.com/auth/androidpublisher`. Play Console permission propagation after a new invite is not immediate; a 401 or 403 shortly after granting access is usually propagation, not misconfiguration.

## The Edit Lifecycle

Every mutation happens inside an edit, and an edit is a transaction:

```text
1. POST   /applications/{package}/edits                       -> editId
2. POST   /upload/.../edits/{editId}/bundles?uploadType=media  -> versionCode, sha256
3. PUT    /applications/{package}/edits/{editId}/tracks/{track}
4. POST   /applications/{package}/edits/{editId}:commit
```

Rules:

- The upload endpoint is on the `/upload/` host path with `uploadType=media` and `Content-Type: application/octet-stream`. The non-upload path will not accept a bundle.
- Version codes are sent as strings in the track release body even though they are integers elsewhere.
- Always clean up an edit that is not committed. A failed or dry-run edit must be deleted rather than abandoned.
- Never force a commit over unknown pending Console changes. `changesNotSentForReview` changes review semantics and is not a way to bypass a conflict.
- A dry run validates and discards, but the upload itself already reached Google. Validation cannot happen against a bundle Play has not received.

## Track Semantics

| Track | Reaches | Permission class |
|---|---|---|
| internal | internal testers only, fast availability | `mutate_reversible` |
| alpha / beta (closed/open) | external testers | `mutate_irreversible` |
| production | real users | `mutate_irreversible` |

- `status: completed` makes the release fully available on that track.
- `status: inProgress` requires a `userFraction` strictly between 0 and 1 and begins a staged rollout.
- `status: draft` stages without releasing and still requires a Console action to proceed.
- `halted` stops an in-progress rollout.

## Promotion

Promotion moves version codes that Play already has. It never rebuilds and never re-uploads.

```text
read the source track's newest release -> take its version codes
assign those exact codes to the target track
commit
```

If the artifact would change, it is not a promotion. Preserve package name, version code, and bundle digest across the move, and say so in the report.

## Monetization Products

- Subscriptions: `POST /applications/{package}/subscriptions` requires both `productId` and `regionsVersion.version` as query parameters.
- One-time products: `PATCH /applications/{package}/onetimeproducts/{productId}` needs `updateMask` as a comma-separated list of fully qualified field names. `*` is rejected with `400 Invalid update_mask: [*]`. Mask exactly the fields being sent: a field outside the mask is ignored, and a masked field that was not sent is cleared.
- Base plans and offers are separate resources under a subscription. Only auto-renewing base plans can carry offers.
- A new offer is created in `DRAFT` and must be activated before new subscribers see it.
- Price and billing terms are user-visible and constrained after activation. Creating or activating any of these is `mutate_irreversible`.

## Data Safety Declarations

`POST /applications/{package}/dataSafety` writes the app's Safety Labels from
the contents of the Data safety CSV, in the `safetyLabels` field. Scope is the
ordinary `androidpublisher` scope, and the response body is empty on success.

Rules:

- There is no matching GET. Nothing can read safety labels back through the API,
  so a successful write is never `PLATFORM VERIFIED`; say the write was accepted
  and point at the Console form for the authoritative state.
- The CSV is the operator's exported declaration. Do not synthesise one. A
  fabricated compliance answer is worse than an absent one, and this call
  replaces the whole declaration rather than merging into it.
- A dry run is local only, because Google offers no validate mode here.
- `Contains ads` is a separate advertising declaration and is **not** part of
  this CSV or any other current public endpoint. It stays a Console action.

## Verification

After a release action, read the tracks back and confirm:

```text
the intended version code is present on the intended track
its status matches the intent
the rollout fraction matches the intent when staged
release notes are attached where the track displays them
```

After a product action, list the products and confirm the identifier, type, and state.

A Data safety write has no read-back, so report it as accepted-by-API and never
as verified.

Play Console permissions are granular, and monetization writes and pricing are
granted separately from read and release access. `onetimeproducts.patch` and
`pricing:convertRegionPrices` returning 403 while product reads succeed means
the service account is missing that grant, not that the call is malformed.

## Failure Handling

| Symptom | Cause | Response |
|---|---|---|
| 403 shortly after inviting the service account | permission propagation | confirm the grant, wait, retry once |
| 403 persistently | the grant lacks this capability | request the specific Console permission; do not broaden beyond the task |
| edit conflict on commit | concurrent Console or API changes | abandon, re-read state, rebuild the edit |
| upload succeeded, commit failed | partially applied | reconcile actual version codes before re-uploading |
| version code already used | the artifact was uploaded before | never reuse a version code; rebuild with a higher one |

## Safety

- Production and staged-rollout changes are separate authorizations from testing-track work.
- Never widen the service account's Play Console permissions to make a command succeed.
- The service account key can publish. Treat it as a publishing credential, owner-readable only, never in the repository.

## Output Contract

Report the package, track, version code, bundle digest, resulting status, and whether the state was read back from Play.

## Completion Criteria

The intended version code is confirmed on the intended track at the intended status, artifact identity is preserved, and any Console-only prerequisite is stated explicitly.
