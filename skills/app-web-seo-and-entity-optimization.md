# App Web SEO and Entity Optimization

## Purpose

Build a crawlable, indexable, consistent web presence for an app so search engines, users, journalists, and AI retrieval systems can identify the product and verify its capabilities.

## When To Use

Use for app landing pages, portfolio pages, support sites, changelogs, comparison pages, launch pages, GitHub READMEs, and cross-channel entity alignment.

## Inputs Needed

- Canonical app name and package name.
- Play listing URL.
- Website and app landing-page URLs.
- Developer or organization identity.
- Current title, metadata, headings, and copy.
- Screenshots, videos, documentation, changelog, support, and privacy pages.
- Search Console and analytics data if available.
- Target query and intent map.
- Pricing, compatibility, privacy, and limitation facts.

## Workflow

### 1. Define the Canonical App Entity

Create an entity record:

```yaml
name:
alternate_names:
package_name:
developer:
category:
platforms:
form_factors:
primary_job:
audience:
key_features:
price_model:
account_required:
data_practices:
compatibility:
play_url:
canonical_web_url:
support_url:
privacy_url:
changelog_url:
source_repository:
video_urls:
last_verified:
```

Use the same facts across Play, website, GitHub, YouTube, support, and social profiles.

### 2. Audit Crawlability and Indexability

Check:

- HTTP status.
- `robots.txt`.
- robots meta and `X-Robots-Tag`.
- canonical URL.
- XML sitemap.
- server-rendered or otherwise indexable primary content.
- JavaScript rendering issues.
- mobile usability.
- internal links.
- duplicate URLs.
- broken links and redirect chains.
- image alt text.
- page titles, descriptions, and headings.

Do not claim a page is indexed without checking an index or Search Console source.

### 3. Build the App Landing Page

Recommended structure:

1. Clear H1 with app name, category, platform, and primary value.
2. Direct summary.
3. Current screenshots or demo.
4. Specific features.
5. Who it is for and when to use it.
6. Compatibility and requirements.
7. Pricing and monetization.
8. Privacy, account, and data behavior.
9. Limitations and unsupported scenarios.
10. FAQ based on real questions.
11. Changelog or update evidence.
12. Support and privacy links.
13. Prominent, accurate Play link.

The page must add information beyond copying the Play description.

### 4. Build Supporting Intent Pages

Create only genuinely useful pages, such as:

- Use-case guides.
- Setup and troubleshooting.
- Feature documentation.
- Honest comparison pages.
- Alternative pages.
- Device compatibility.
- Sensor requirements.
- Privacy and local-first architecture.
- Release notes.
- Case studies or demonstrations.

Do not create thin pages for every keyword variation.

### 5. Add Structured Data Carefully

Evaluate `SoftwareApplication` or another applicable type.

Rules:

- Mark up only content visible on the page.
- Keep name, application category, operating system, offers, aggregate rating, and other properties accurate.
- Do not fabricate ratings, prices, reviews, or availability.
- Validate syntax and rich-result eligibility separately.
- Structured data can improve machine understanding and rich-result eligibility but is not an AI-recommendation switch.

### 6. Strengthen Entity Connections

Use clear links among:

- Official landing page.
- Google Play listing.
- Developer portfolio.
- Support and privacy pages.
- GitHub repository where public.
- YouTube demonstrations.
- Changelog and documentation.
- Relevant authentic community or editorial coverage.

Avoid artificial link schemes or manufactured mentions.

### 7. Optimize International Pages

- Use distinct localized URLs when appropriate.
- Add correct `hreflang`.
- Keep canonical and locale relationships consistent.
- Localize app facts and Play links.
- Avoid auto-generated low-quality locale pages.

## Output Contract

Return these sections:

```text
Canonical Entity Record
Technical SEO Findings
Landing Page Plan
Supporting Pages
Structured Data
Entity Consistency
```

Use the following tables:

| Priority | Technical Finding | Evidence | Fix | Validation |
|---|---|---|---|---|

| Landing-Page Section | User Question | Required Evidence | CTA |
|---|---|---|---|

| Supporting Page | Intent | Unique Value | Internal Links | Priority |
|---|---|---|---|---|

| Surface | Name | Category | Features | Price | Compatibility | Status |
|---|---|---|---|---|---|---|

For structured data, report the recommended type, visible properties, excluded properties, and validation status.

## Example Invocation

```text
Audit the web presence for a Wear OS light-meter app. Align the Play listing, app landing page, GitHub README, privacy policy, support page, screenshots, and YouTube demo around one verifiable entity record.
```

## Quality Bar

- The landing page adds original evidence.
- Entity facts are consistent.
- Technical SEO issues are validated.
- Schema matches visible content.
- No thin or deceptive page strategy is proposed.
