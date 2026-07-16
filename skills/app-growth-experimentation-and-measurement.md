# App Growth Experimentation and Measurement

## Purpose

Turn ASO, creative, product-quality, web SEO, and AI-discovery recommendations into controlled experiments with explicit metrics, guardrails, decision rules, and rollback plans.

## When To Use

Use before changing a live listing, creative set, onboarding flow, pricing presentation, landing page, localization, or AI-discovery configuration.

## Inputs Needed

- Primary business objective.
- Baseline metrics and segments.
- Proposed change.
- Play Console experiment capabilities available to the app.
- Analytics and Search Console setup.
- Release calendar.
- Minimum acceptable quality and revenue guardrails.
- Expected traffic or sample constraints.
- Rollback capability.

## Experiment Contract

Every experiment must define:

```text
hypothesis
target segment
control
variant
primary variable
primary metric
secondary metrics
guardrails
sample or duration rule
decision rule
rollback trigger
owner
start date
observation window
confounds
```

Do not run a test merely because an asset can be changed.

## Workflow

### 1. Select the Right Test Type

Use:

- Google Play store-listing experiment when supported and appropriate.
- Custom store listing for a distinct query, country, campaign, or audience.
- Locale rollout for translation and local creative.
- Phased app release for product changes.
- Web A/B test where search-engine guidelines and implementation permit.
- Before/after observation only when a controlled test is unavailable, with explicit causal limitations.
- Recommendation prompt snapshot tests for AI visibility, never as a stable ranking metric.

### 2. Isolate the Hypothesis

Good:

```text
Changing the first phone screenshot from a settings screen to the completed core workflow will improve store-listing conversion among UK organic search visitors.
```

Weak:

```text
New screenshots, title, description, icon, price, and onboarding will improve growth.
```

Change one primary variable where practical. If multiple changes must ship together, label the result as a package test.

### 3. Choose Metrics

Possible primary metrics:

- Store listing conversion rate.
- Buyer conversion.
- First-time installers.
- Activated users.
- Day 7 retention.
- Landing-page organic click-through rate.
- Landing-page to Play click rate.
- Support issue rate.
- Accurate AI recommendation rate across a fixed prompt set.

Guardrails:

- Refunds.
- Uninstalls.
- Rating decline.
- Crash or ANR regression.
- Revenue per visitor.
- Support volume.
- Policy violations.
- Incorrect AI facts.

### 4. Define Segments

Do not aggregate away the target effect. Segment by:

- Country and locale.
- Acquisition source.
- Form factor.
- New versus returning user.
- App version.
- Device class.
- Paid versus organic source.

### 5. Define the Decision Rule

Example:

```text
Adopt the variant only when the primary metric improves beyond the predefined practical threshold, no guardrail regresses beyond tolerance, the sample or duration rule is met, and no material instrumentation issue exists.
```

Do not select a winner solely from an early positive swing.

### 6. Track Confounds

Record:

- App release.
- Price change.
- Promotion or social post.
- Seasonal demand.
- Competitor launch.
- Policy enforcement.
- Country expansion.
- Store algorithm or UI change.
- Rating shock.
- Tracking outage.
- Website deployment.
- News or viral traffic.

### 7. Measure AI Recommendation Readiness

Use a fixed prompt suite and record:

- System and model/product.
- Date and locale.
- Prompt.
- Mention status.
- Factual accuracy.
- Source links.
- Competitors mentioned.
- Recommendation rationale.

Do not treat one answer as representative.

### 8. Maintain an Experiment Ledger

| ID | Hypothesis | Segment | Status | Start | End | Result | Decision | Notes |
|---|---|---|---|---|---|---|---|---|

Preserve failed and neutral tests to avoid repeating them.

## Output Contract

```markdown
## Experiment Specification
- ID:
- Hypothesis:
- Segment:
- Control:
- Variant:
- Primary variable:
- Primary metric:
- Secondary metrics:
- Guardrails:
- Sample/duration rule:
- Decision rule:
- Rollback trigger:
- Confounds:
- Owner:

## Instrumentation Checklist
- [ ] Baseline captured
- [ ] Segment filters verified
- [ ] Conversion event verified
- [ ] Revenue/purchase event verified
- [ ] Quality guardrails verified
- [ ] Annotation added to release calendar
- [ ] Rollback path confirmed

## Result
- Outcome:
- Confidence:
- Practical significance:
- Guardrail status:
- Confounds:
- Decision:
- Follow-up:
```

## Example Invocation

```text
Design a Play listing experiment for a paid Wear OS app that tests the first screenshot promise while holding title, price, icon, and remaining screenshots stable.
```

## Quality Bar

- The hypothesis is falsifiable.
- The primary variable and metric are explicit.
- Segments and confounds are recorded.
- Early results are not overinterpreted.
- A rollback rule exists.
