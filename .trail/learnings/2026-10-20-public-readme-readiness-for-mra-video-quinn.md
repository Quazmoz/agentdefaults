---
title: Public README readiness for MRA video visitors
author: Quinn
date: 2026-10-20
branch: main
cost: { minutes: 4, tokens: 111538 }
touches:
  - README.md
  - docs/quickstarts/mobile-release-automation.md
  - skills/android-portfolio-release-orchestration.md
  - tools/mobile-release-automation/INSTALL.md
  - tools/mobile-release-automation/README.md
---

## Decided
- Root README carries a "Here from the Google Play MCP video?" callout pointing to tools/mobile-release-automation/README.md -> INSTALL.md -> docs/quickstarts/mobile-release-automation.md; new videos go first in the "Related videos" table.
- MRA README has an "At a glance" table: macOS is the supported platform (keychain.py and human_approval.py check sys.platform == "darwin"; off macOS, reads need BWS_ACCESS_TOKEN and high-risk MCP writes fail closed), Python >=3.10.
- INSTALL.md owns first-time Play service-account setup. The Bitwarden secret value is the entire service-account JSON (play_credentials.py parses it), bound with `mra-agent auth bind-play`.
- Google's current flow invites the service account email under Play Console "Users and permissions"; the old "API access" page is not part of setup.

## Tried and ruled out
- Scraping the channel ID from the @handle page grabs a wrong channel. Use the channelId that appears most often on a known video page, then read feeds/videos.xml?channel_id=... to find the newest video.

## Watch out
- validate-agentdefaults.py fails locally only because of the git-ignored local-audits/ folder. To check what a fresh clone sees, copy `git ls-files` into a scratch dir and run the validator there.
- Docs examples leaked a personal home path to the keystore; use /path/to/upload-key.jks. Grep `git grep 'quinnfavo/' -- '*.md' ':!local-audits'` before publishing.
- Repo has no LICENSE yet (README says "License to be added"); that's the owner's choice.
