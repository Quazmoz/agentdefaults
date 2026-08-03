# Subreddit App Idea Validation

## Purpose

Research the historical record of an app idea within a subreddit or similar public community, identify prior requests and existing solutions, and determine whether a new validation post would add useful evidence.

## When To Use

Use this skill when the user asks questions such as:

```text
Has this subreddit discussed this app idea before?
Are people already asking for this?
Did someone build it already?
Would posting about the idea be repetitive?
What should I ask the community before building?
```

This skill is optimized for app and software-product validation. It may also be used for feature concepts, browser extensions, utilities, developer tools, and workflow products.

## Inputs Needed

- `concept`: proposed app, feature, or workflow.
- `problem`: the user problem the concept is intended to solve.
- `communities`: one or more public subreddits or forums.
- `platform`: Android, Wear OS, iOS, web, desktop, extension, or other.
- `date_range`: explicit range or `all`, with recent evidence emphasized.
- `locale`: geography or language when material.
- `known_terms`: product names, abbreviations, ingredients, devices, or adjacent terms.
- `known_competitors`: optional direct products or substitutes.
- `max_threads`: default 50 relevant threads.
- `output_mode`: research only, recommendation, or recommendation plus draft post.
- `safety_domain`: none, health, medication, supplements, finance, legal, or another high-stakes category.

## Preconditions

- Apply [`browser-research-foundations.md`](browser-research-foundations.md).
- Apply [`forum-demand-mining.md`](forum-demand-mining.md) for public-source collection and privacy rules.
- Confirm the communities and threads are publicly accessible.
- Check current community rules before recommending a new post.
- Define the evidence cutoff date and record the collection date.
- Do not assume Reddit's native search is complete.

## Query Expansion

Build a query matrix before browsing.

### 1. Exact concept queries

```text
"supplement interaction app"
"supplement interaction checker"
"app to track supplement interactions"
```

### 2. Problem-first queries

```text
how do you check interactions between supplements
how do you manage a large supplement stack
worried about combining supplements
track supplement timing and conflicts
```

### 3. App-search intent queries

```text
is there an app
looking for an app
recommend an app
does anyone use an app
wish there was an app
```

### 4. Existing-solution queries

```text
tracker
checker
database
spreadsheet
website
calendar
reminder
AI
ChatGPT
alternative
```

### 5. Dissatisfaction queries

```text
doesn't work
missing
inaccurate
unreliable
too expensive
privacy
affiliate
ads
outdated
false warning
```

### 6. Builder and launch queries

```text
I built
I made
beta testers
prototype
feedback on my app
launching
open source
```

Expand with common abbreviations, ingredient names, device names, brand names, misspellings, and adjacent terminology. Search the problem independently of the proposed implementation.

## Source Strategy

Use complementary discovery paths where available:

1. Native subreddit search with relevance and date sorting.
2. External search with `site:reddit.com/r/<community>` or equivalent domain filters.
3. Searches targeting titles, comments, and known phrases.
4. Known competitor names and product URLs.
5. Related communities only when the target community has insufficient evidence.
6. Archived or deleted-thread metadata only when lawfully and publicly available; do not bypass access controls.

Do not rely on one search engine, one query, or only the most-upvoted posts.

## Thread Classification

For every materially relevant thread, assign one primary type:

- `explicit_app_request`
- `recommendation_request`
- `problem_report`
- `workaround_discussion`
- `feature_request`
- `competitor_launch`
- `developer_validation`
- `trust_or_safety_concern`
- `general_topic_only`

Then assign a solution state:

- `solved`
- `partly_solved`
- `unresolved`
- `abandoned`
- `unknown`

And an evidence relationship:

- `exact_match`
- `close_substitute`
- `adjacent_problem`
- `background_only`

## Evidence Fields

Record at minimum:

```text
source_url
community
thread_title
published_at
last_activity_at
thread_type
match_type
problem_statement
requested_solution
current_workaround
products_recommended
product_sentiment
unresolved_gap
objections
trust_concerns
privacy_concerns
pricing_signal
willingness_signal
engagement_score_raw
comment_count_raw
solution_state
evidence_excerpt
confidence
collected_at
```

Usernames should be omitted from the primary report unless attribution is essential. Prefer paraphrase and short excerpts.

## Comment Analysis

Read enough comments to identify:

- Whether commenters share the original problem.
- Whether they recommend a tool that genuinely solves it.
- Whether recommendations are repeated independently.
- Why existing solutions were rejected or abandoned.
- Whether users prefer spreadsheets, websites, LLMs, professional advice, or doing nothing.
- Whether people express willingness to test, pay, switch, or contribute data.
- Whether skepticism concerns accuracy, privacy, evidence quality, maintenance, affiliate incentives, or regulatory risk.
- Whether the original poster returned with an outcome.

Do not treat supportive comments from the builder's own launch thread as independent demand without qualification.

## Duplicate and Campaign Handling

Collapse the following into one evidence group:

- Cross-posts of the same thread.
- The same developer promoting the same product repeatedly.
- Quoted or copied posts.
- News articles discussed in multiple communities when the user problem is not independently expressed.
- Multiple comments repeating one recommendation without independent experience.

Preserve individual source URLs while reporting the grouped signal count separately.

## Temporal Analysis

Create a chronological history rather than only a relevance-ranked list.

Distinguish:

```text
historic demand: older than 24 months
recent demand: within 24 months
current demand: within 6 months
active conversation: recent comments or ongoing updates
```

Use exact dates. A high-engagement old thread may establish historical demand but not current opportunity.

## Engagement Interpretation

Engagement is supporting evidence, not a demand metric.

Consider:

- Post age.
- Community size and activity at the time when knowable.
- Upvote-to-comment imbalance.
- Whether comments contain personal experience or jokes/off-topic discussion.
- Whether the thread was pinned, cross-posted, controversial, or news-driven.
- Whether the post was removed or locked.

Avoid comparing raw upvotes across communities without context.

## Existing-Solution Map

For every named solution, record:

```text
name
solution_type
platform
core_job
source_of_recommendation
positive_evidence
negative_evidence
pricing_or_business_model
privacy_or_account_requirement
maintenance_status
reported_gap
verification_status
```

Verify current availability separately before describing a product as active. Do not assume a recommendation from an old thread is still valid.

## Post-Value Decision

A new post should answer a decision that the historical evidence did not resolve.

### Recommend `post now` when

- The problem appears repeatedly and recently.
- Existing solutions are incomplete or distrusted.
- The proposed differentiation is specific.
- No recent thread tests the same assumption.
- Community rules permit research-style discussion.

### Recommend `post, but narrow the question` when

- The broad concept already has demonstrated interest.
- One key assumption remains unclear, such as platform, evidence presentation, privacy, pricing, or workflow.
- A broad “would you use this?” post would add little value.

### Recommend `comment on an existing thread` when

- A recent, active, directly relevant thread already exists.
- The community allows follow-up questions.
- The user can contribute transparently without hijacking the discussion.

### Recommend `research elsewhere first` when

- The community discusses the topic but is not representative of likely users.
- Relevant history is too sparse.
- Another community, store-review corpus, or professional audience is more appropriate.

### Recommend `do not post` when

- A recent exact validation thread already answered the question.
- The intended post is mainly promotion.
- Community rules prohibit the format.
- The concept depends on unverified or unsafe claims.
- A credible product cannot be built without authoritative data the user has not identified.

## Validation Question Design

Prefer questions that reveal behavior and switching criteria:

```text
How do you handle this today?
Which tools have you tried?
Where did those tools fail?
How often does the problem recur?
What consequence makes the problem worth solving?
Which information would you need to trust the result?
What would make you stop using the tool?
Would local-only storage or source citations change your decision?
Which feature is essential versus merely convenient?
```

Avoid relying on:

```text
Would you use my app?
Is this a good idea?
Would you pay for this?
Do you like this feature list?
```

Those questions are leading, hypothetical, and weak predictors of behavior.

## Sensitive-Domain Requirements

For health, supplements, medication, diagnostics, finance, legal, or other high-stakes concepts:

1. Label community findings as market evidence only.
2. Do not infer safety, efficacy, causality, contraindications, or professional consensus from anecdotes.
3. Separate requests for tracking, organization, reminders, source transparency, and professional handoff from requests for individualized advice.
4. Flag dependence on authoritative and maintainable datasets.
5. Identify false-positive and false-negative risks.
6. Identify jurisdictional, regulatory, liability, and privacy constraints for later expert review.
7. Do not draft a post that asks users to recommend unsafe dosing, diagnose conditions, or override professional advice.

## Output Contract

Create or return:

### `community_history.csv`

One row per deduplicated evidence item.

### `community_history.json`

Structured equivalent with source groups and solution references.

### `validation_report.md`

```text
Concept:
Community:
Evidence cutoff:
Coverage:
Prior-history verdict:
Exact-match history:
Adjacent-history summary:
Existing solutions:
Repeated pain points:
Unresolved gaps:
Objections and trust barriers:
Recent-vs-historic assessment:
Sensitive-domain constraints:
Recommendation:
Confidence and limitations:
```

### `post_recommendation.md`

```text
Decision:
Why:
What remains unknown:
Best post angle:
Questions to ask:
Questions to avoid:
Rule or moderation considerations:
```

### `source_index.md`

List every material source with date, relevance, and verification status.

### `manual_review_queue.md`

Include deleted threads, inaccessible comments, ambiguous products, unverifiable dates, and claims requiring authoritative domain research.

## Checkpoint Format

```json
{
  "skill": "subreddit-app-idea-validation",
  "community": "r/example",
  "concept": "example app",
  "query_group": "problem-first",
  "last_query": "site:reddit.com/r/example example problem",
  "threads_reviewed": 18,
  "evidence_items_written": 11,
  "status": "in_progress",
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Native search misses known threads: use external domain search and record the discrepancy.
- Search result has no accessible body: preserve metadata and queue manual review.
- Deleted or removed post: do not reconstruct private content; mark unavailable.
- Product recommendation cannot be verified: mark availability unknown.
- Search results are dominated by one promoter: collapse the campaign and lower confidence.
- Community rules are ambiguous: recommend moderator review rather than assuming permission.
- Rate limit or CAPTCHA: stop, checkpoint, and request human assistance.
- Evidence is sparse: report insufficient evidence rather than manufacturing a verdict.

## Example Invocation

```text
Research all available r/Biohackers history for apps that track supplement-supplement and supplement-medication interactions. Search exact terms, problem-first language, stack-management workflows, existing trackers, competitor launches, privacy concerns, evidence-quality objections, and posts asking whether such an app would be useful. Separate market demand from clinical validity. Tell me whether a new validation post would add information, and propose the narrowest useful questions.
```

## Quality Bar

- Search coverage includes exact, problem-first, solution, dissatisfaction, and builder language.
- Historical and recent signals are distinguished.
- Comments and substitutes are analyzed, not merely counted.
- Duplicate promotion campaigns are collapsed.
- Current product availability is verified before recommendation.
- The post recommendation identifies the unresolved decision it would test.
- Sensitive-domain conclusions remain within the evidence and safety boundary.
