# Mobile Release Automation Toolkit

## Purpose

Give an agent a safe, auditable way to perform the repetitive Google Play,
RevenueCat, and AdMob work that is otherwise done by hand: uploading builds to
internal testing, promoting releases, wiring a new app into RevenueCat, and
creating AdMob inventory.

Every operation is a thin wrapper over a documented public API. No vendor web UI
is scripted. Credentials never leave your machine except to the owning vendor's
own API host.

## The Three Platforms Are Not Equally Automatable

Read this before planning any work. The differences are not preferences.

| Platform | Auth | Automatable today |
|---|---|---|
| Google Play | GCP service account | Yes. Upload, tracks, promotion, and monetization products are all API-driven. |
| RevenueCat | API v2 secret key | Yes. Apps, products, entitlements, offerings, and packages are all API-driven. A first-party MCP server exists. |
| AdMob | OAuth **user** credentials only | Reporting and listing: yes. Creating apps and ad units: **only if Google has allowlisted your AdMob account**. |

Two AdMob facts that cannot be engineered around:

1. **Service accounts do not work.** Google documents that "All requests to the
   AdMob API must be authorized by an authenticated user" and that "No other
   authorization protocols are supported." There is no IAM role that changes
   this. AdMob needs a browser consent from the Google Account that owns the
   publisher account, which this toolkit caches as a local refresh token.
2. **Creation is limited access.** `accounts.apps.create` and
   `accounts.adUnits.create` both carry the note: "This method has limited
   access. If you see a 403 permission denied error, please reach out to your
   account manager for access." The gate is applied per AdMob account by Google.
   Granting yourself the `admob.monetization` scope does not lift it.

Run `mra admob probe` before promising anyone that AdMob setup is automated.

## Install

```bash
cd tools/mobile-release-automation
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The `mcp` requirement is needed only for the local MCP server. Both mcp 1.x
(`FastMCP`) and mcp 2.x (`MCPServer`) are supported.

## Credential Setup

All credentials live in `~/.config/mobile-release-automation` (override with
`MRA_HOME`). The toolkit refuses to read any credential file that is group- or
world-readable, so `chmod 600` everything.

```bash
mkdir -p ~/.config/mobile-release-automation
chmod 700 ~/.config/mobile-release-automation
```

### Google Play

1. In Google Cloud, create a project and enable the **Google Play Android
   Developer API**.
2. Create a service account and download its JSON key.
3. In Play Console, go to **Users and permissions**, invite the service account
   email, and grant only what the task needs: *Release to testing tracks* for
   internal testing, plus *Manage store presence* or monetization permissions
   only if you intend to script products.
4. Save the key and lock it down:

```bash
cp ~/Downloads/play-sa.json ~/.config/mobile-release-automation/play-service-account.json
chmod 600 ~/.config/mobile-release-automation/play-service-account.json
```

Play Console propagates new permissions slowly. A fresh invite can take a while
before the API accepts it.

### AdMob

1. In the same Google Cloud project, enable the **AdMob API**.
2. Configure the OAuth consent screen. Add the AdMob scopes you intend to use.
   `admob.readonly` and `admob.report` are publicly documented;
   `admob.monetization` is required for creation and is the gated one.
3. Create an OAuth client of type **Desktop app** and download its JSON.

```bash
cp ~/Downloads/admob-client.json ~/.config/mobile-release-automation/admob-oauth-client.json
chmod 600 ~/.config/mobile-release-automation/admob-oauth-client.json
mra admob login       # one-time browser consent, caches a refresh token
mra admob probe       # says whether monetization access is actually granted
```

Sign in as the Google Account that owns the AdMob publisher account. If
`mra admob login` fails because `admob.monetization` is not permitted on your
consent screen, re-run `mra admob login --read-only` to get reporting working
and treat creation as unavailable.

### RevenueCat

In RevenueCat, create an API key with version **V2** and only the permissions
the task needs (`project_configuration:apps:read_write` to create apps,
`project_configuration:products:read_write` for products).

```bash
printf '%s' 'sk_your_key' > ~/.config/mobile-release-automation/revenuecat-v2-secret.key
chmod 600 ~/.config/mobile-release-automation/revenuecat-v2-secret.key
```

Or export `REVENUECAT_V2_SECRET_KEY`, which takes precedence over the file.

### Verify

```bash
.venv/bin/python -m mra.cli doctor
```

## Profiles

A profile maps one app's identity across all three platforms so commands do not
need long flags.

```bash
mra profile set --slug myapp \
  --package-name com.example.myapp \
  --revenuecat-project-id proj_abc123 \
  --admob-app-id ca-app-pub-000~111
```

## Common Commands

```bash
# Google Play
mra play tracks --profile myapp
mra play publish --profile myapp --aab app/build/outputs/bundle/release/app-release.aab --dry-run
mra play publish --profile myapp --aab ... --track internal --notes "en-US=Bug fixes" --yes
mra play promote --profile myapp --source internal --target alpha --yes

# AdMob
mra admob probe
mra admob apps
mra admob create-app --name "My App" --platform ANDROID --app-store-id com.example.myapp --yes
mra admob create-adunit --app-id ca-app-pub-000~111 --name "Rewarded" --format REWARDED --type VIDEO --yes

# RevenueCat
mra rc projects
mra rc create-play-app --profile myapp --name "My App" --yes
mra rc products --profile myapp
```

Every command prints JSON on stdout so an agent can parse the result. Failures
go to stderr with a non-zero exit code.

## Safety Model

- **Mutating commands refuse to run without `--yes`.** There is no way to
  configure that away.
- **`mra play publish` supports `--dry-run`**, which validates the Play edit and
  then discards it. The upload still reaches Google, because Play cannot
  validate a bundle it has not received, but nothing reaches testers.
- **Play edits are always cleaned up.** A failed or dry-run edit is deleted so
  nothing is left dangling in the Console.
- **Credential files must be owner-only** or the toolkit refuses to read them.
- **`mra rc create-play-app` sends your Play service account key to
  RevenueCat.** That is the documented way RevenueCat validates Play purchases,
  but it is a real credential leaving your machine, so the command says so.

## MCP Server

`mra.mcp_server` exposes the same operations over stdio MCP, with `confirm=true`
required for every mutating tool and `dry_run` defaulting to `true`.

Register it with Claude Code:

```bash
claude mcp add mobile-release-automation -- \
  /absolute/path/to/tools/mobile-release-automation/.venv/bin/python -m mra.mcp_server
```

For RevenueCat, prefer the first-party hosted server instead:

```bash
claude mcp add --transport http revenuecat https://mcp.revenuecat.ai/mcp
```

The RevenueCat tools in this local server exist only to cover gaps in that
server and to support unattended scripting.

Do not install a third-party Play Console or AdMob MCP server. There is no
first-party one, and any such server would hold your Play Console service
account and AdMob refresh token.

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -t .
```

The suite is fully offline: it uses in-memory HTTP doubles and never contacts a
real platform. It covers the Play edit lifecycle and its cleanup paths, release
validation, promotion, AdMob 403 handling and the access probe, RevenueCat
request shaping and pagination, credential permission enforcement, and the
confirmation gates in both the CLI and the MCP server.
