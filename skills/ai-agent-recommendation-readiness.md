# AI Agent Recommendation Readiness

## Purpose

Make an app easier for AI assistants, answer engines, retrieval systems, and browser agents to discover, understand, compare, verify, and recommend accurately.

## When To Use

Use when the goal includes ChatGPT search visibility, Gemini or Google AI search visibility, Copilot or Bing visibility, Perplexity visibility, browser-agent compatibility, or general AI recommendation readiness.

## Inputs Needed

- Canonical app entity record.
- App landing page and Play listing.
- Robots and crawler policy.
- Documentation, support, privacy, pricing, compatibility, changelog, screenshots, and videos.
- Authentic third-party references.
- Target recommendation prompts and audiences.
- Web analytics or referral data if available.
- Current official crawler and AI-search guidance.

## Principles

- AI recommendation readiness is an information-quality and retrieval problem, not a guaranteed-placement service.
- Durable SEO remains foundational.
- Clear, crawlable, evidence-backed facts are more useful than content written in a synthetic "AI style."
- Different AI products use different crawlers, indexes, partnerships, user-triggered fetches, and ranking systems.
- Crawler controls for search, user-triggered access, and model training may be separate.
- `llms.txt` is optional and must not be presented as a Google Search ranking requirement.
- Authentic independent discussion can add corroboration, but manufactured mentions are spam.
- The strongest recommendation asset is a product that clearly solves a specific job and has verifiable evidence.

## Workflow

### 1. Define Recommendation Prompts

Test prompt classes:

```text
best <app category> for <audience>
best <platform> app for <specific job>
which app can <capability>
<app> alternatives
<app> vs <competitor>
privacy-friendly <category> app
offline <category> app
one-time purchase <category> app
<device> app for <use case>
```

For each prompt, define:

- Intended user.
- Required capabilities.
- Purchase constraints.
- Platform and device.
- Evidence needed.
- Honest disqualifiers.

### 2. Create a Recommendation Fact Matrix

| Prompt | Required Fact | Canonical Source | Independent Evidence | Freshness | Gap |
|---|---|---|---|---|---|

Facts commonly needed:

- What the app does.
- Who it is for.
- Platform and device compatibility.
- Key differentiators.
- Price and monetization.
- Account requirements.
- Privacy and data handling.
- Offline behavior.
- Integrations.
- Limitations.
- Current maintenance status.
- Support quality.
- Ratings and reviews, when legitimately available.
- Evidence of the actual UI and workflow.

### 3. Audit Crawl and Fetch Controls

Check current official documentation for each target system.

For OpenAI, evaluate separately:

- `OAI-SearchBot` for ChatGPT search discovery.
- `GPTBot` for potential model-training use.
- `ChatGPT-User` for user-triggered fetches.

Do not conflate allowing search discovery with allowing training.

For Google:

- Apply normal crawlability, indexing, snippet eligibility, helpful content, and technical SEO.
- Do not claim special AI markup is required.
- Use Search Console reports that are actually available to the site.

For other systems:

- Verify current user agents, webmaster controls, and indexing requirements.
- Record the source and verification date.

### 4. Make Facts Easy to Retrieve

Ensure important information is:

- Present in accessible page text.
- Organized with descriptive headings.
- Specific and current.
- Supported by screenshots, video, docs, changelog, or code.
- Linked from the canonical app page.
- Consistent across official surfaces.
- Not hidden only behind login, canvas rendering, images, or client-side interaction.
- Available without deceptive cloaking.

Use concise answer blocks where they help users:

```text
What is <app>?
Who is it for?
Which devices does it support?
How much does it cost?
Does it require an account?
What data does it collect?
Does it work offline?
What are its limitations?
How is it different from alternatives?
```

### 5. Add Comparison Utility

Create honest, evidence-backed content that helps a system choose:

- Best-fit scenarios.
- Poor-fit scenarios.
- Supported and unsupported features.
- Competitor or substitute comparisons.
- Pricing model differences.
- Privacy and account differences.
- Device or sensor requirements.

Do not publish biased comparison tables that omit obvious disadvantages.

### 6. Strengthen Corroboration

Prioritize authentic sources:

- Current Play listing.
- Official website.
- Documentation and changelog.
- Public repository.
- Demonstration video.
- Genuine reviews.
- Relevant Reddit or forum discussions.
- Editorial coverage.
- Product directories with maintained data.

Do not purchase mentions, seed fake discussions, or fabricate reviews.

### 7. Test Retrieval and Recommendation

Run a reproducible prompt set across target systems when authorized.

Record:

| System | Date | Locale | Prompt | Mentioned | Position/Role | Facts Correct | Sources | Notes |
|---|---|---|---|---|---|---|---|---|

Treat results as snapshots. AI responses vary and are not stable rankings.

Classify failures:

```text
not discovered
wrong entity
missing capability
incorrect price
incorrect compatibility
weak evidence
competitor dominates
crawler blocked
page not indexed
stale source
prompt mismatch
```

### 8. Produce a Remediation Plan

Prioritize:

- P0: blocked crawl, wrong entity, materially false facts, broken canonical pages.
- P1: missing canonical facts, no comparison utility, inconsistent pricing or compatibility, inaccessible evidence.
- P2: stronger demos, FAQs, use-case pages, changelog, structured data, authentic coverage.
- P3: optional `llms.txt`, experimental machine-readable summaries, emerging agent protocols.

## Output Contract

```markdown
## AI Recommendation Readiness
- Target systems:
- Evidence cutoff:
- Overall status:
- Main blocker:

## Recommendation Prompt Matrix
| Prompt | Audience | Required Capabilities | Current Fit | Evidence Gap |
|---|---|---|---|---|

## Crawler Policy
| System/User Agent | Purpose | Current Rule | Desired Rule | Source Date | Action |
|---|---|---|---|---|---|

## Canonical Facts
| Fact | Official Source | Independent Support | Freshness | Status |
|---|---|---|---|---|

## Retrieval Test
| System | Prompt | Result | Accuracy | Sources | Remediation |
|---|---|---|---|---|---|

## Priority Actions
- P0:
- P1:
- P2:
- P3:
```

## Example Invocation

```text
Improve the chance that AI assistants accurately recommend a one-time paid Wear OS barometer app to users who want local pressure trends without an account. Audit crawl controls, entity facts, comparison usefulness, compatibility evidence, and current recommendation prompts.
```

## Quality Bar

- Search crawling and training crawling are distinguished.
- No recommendation guarantee is made.
- Facts are verifiable and current.
- Prompt tests are reproducible snapshots.
- Optional AI-specific files are not oversold.
