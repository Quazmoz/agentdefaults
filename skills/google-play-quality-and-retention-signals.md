# Google Play Quality and Retention Signals

## Purpose

Connect ASO work to the product quality, user experience, reputation, and retention signals that determine whether acquired users remain satisfied.

## When To Use

Use when listing conversion is weak, ratings or reviews are deteriorating, organic growth stalls after acquisition gains, a form-factor quality issue exists, or the app is being prepared for featuring and recommendations.

## Inputs Needed

- Android vitals and affected versions.
- Ratings and review trends by market and device.
- Review samples and developer responses.
- Retention, uninstall, refund, and engagement data if approved.
- Onboarding and paywall flow.
- Support issues and release history.
- Device catalog and form-factor quality findings.
- App value proposition and listing claims.

## Workflow

### 1. Align Promise With Product

Create a claim-to-experience matrix:

| Listing Claim | First Product Proof | Time to Value | Friction | Failure Mode |
|---|---|---:|---|---|

Prioritize any mismatch where users cannot quickly experience the advertised value.

### 2. Audit Activation

Review:

- First launch.
- Permissions.
- Account or sign-in requirements.
- Purchase or paywall timing.
- Empty states.
- Setup complexity.
- Companion-device handoff.
- Demo or test mode.
- First successful outcome.
- Error recovery.
- Accessibility and large-font behavior.
- Round-screen and small-screen behavior for Wear OS.

Recommend the shortest truthful path to first value.

### 3. Audit Technical Quality

Use current Android and Google Play quality guidance. Review:

- Crash and ANR patterns.
- Startup and interaction responsiveness.
- Battery, background work, wake locks, sensors, and network behavior.
- Offline and degraded-network behavior.
- Device-specific failures.
- Latest Android version compatibility.
- Form-factor guidelines.
- Permissions and privacy.
- Billing reliability.
- Update and migration safety.

Do not imply that fixing a metric guarantees ranking improvement. State it as a product-quality and visibility hypothesis.

### 4. Analyze Ratings and Reviews

Sample across:

- Recent positive reviews.
- Recent critical reviews.
- High-impact markets.
- Relevant devices.
- Current and prior versions.
- Paid and free expectations where visible.

Cluster:

```text
missing capability
confusing onboarding
bug or crash
device incompatibility
billing or entitlement
performance or battery
privacy or permissions
listing mismatch
pricing or value
support
delight or differentiation
```

Separate isolated reports from repeated themes.

### 5. Improve Review Operations

Permitted actions:

- Ask for a rating at a contextually appropriate successful moment.
- Make the prompt dismissible and non-coercive.
- Respond professionally to reviews.
- Route support issues to a real support channel.
- Fix repeated problems and mention fixes accurately in release notes.

Prohibited actions:

- Incentivized ratings.
- Review gating.
- Asking only happy users.
- Preventing negative feedback.
- Fabricated reviews.
- Pressuring users after payment.
- Repeated disruptive prompts.

### 6. Prioritize Product Work

Use:

```text
impact = affected users × severity × promise relevance × confidence
priority = impact / effort
```

P0 examples:

- Store claim is false or materially misleading.
- Purchase or entitlement failure.
- Crash blocks the core job.
- Major privacy or security issue.
- Unsupported device shown as supported.

P1 examples:

- Onboarding prevents first value.
- Repeated review complaint tied to the primary job.
- Poor form-factor adaptation.
- High-friction permission flow.
- Missing support or recovery path.

## Output Contract

```markdown
## Promise-to-Product Alignment
| Claim | Product Proof | Friction | Risk | Fix |
|---|---|---|---|---|

## Quality Findings
| Priority | Signal | Segment | Evidence | Product Fix | Growth Hypothesis |
|---|---|---|---|---|---|

## Review Themes
| Theme | Frequency | Recency | Severity | Version/Device | Response |
|---|---:|---|---:|---|---|

## Activation Plan
- Current time to value:
- Primary blocker:
- Proposed first-success path:
- Measurement:

## Review Operations
- Prompt moment:
- Support path:
- Response backlog:
- Policy checks:
```

## Example Invocation

```text
Analyze why a paid Wear OS utility has reasonable listing traffic but weak buyer conversion and mixed ratings. Compare listing promises with first-launch, billing, device compatibility, and recurring review themes.
```

## Quality Bar

- Marketing and product changes are connected.
- Review themes are sampled and qualified.
- Quality hypotheses are not presented as secret ranking factors.
- The plan prioritizes user value and reliability.
