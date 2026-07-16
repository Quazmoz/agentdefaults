#!/usr/bin/env python3
"""Validate AgentDefaults repository structure, JSON, manifest references, and Markdown links."""

from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "INDEX.md",
    "README.md",
    "agentdefaults.manifest.json",
    ".gitignore",
    ".github/FUNDING.yml",
    ".github/copilot-instructions.md",
    ".github/agents/token-economy-orchestrator.agent.md",
    ".github/agents/terse-technical-coding.agent.md",
    ".github/agents/token-efficiency-benchmark.agent.md",
    ".github/agents/palmierpro-video-editor.agent.md",
    ".github/agents/google-play-growth-optimizer.agent.md",
    ".cursor/rules/agentdefaults.mdc",
    ".windsurfrules",
    "docs/user-guide.md",
    "docs/ux-roadmap.md",
    "docs/tool-integration-guide.md",
    "docs/palmierpro-mcp-tool-map.md",
    "docs/app-market-research-acceptance-tests.md",
    "docs/google-play-growth-acceptance-tests.md",
    "docs/quickstarts/cli.md",
    "docs/quickstarts/claude.md",
    "docs/quickstarts/gemini.md",
    "docs/quickstarts/editor.md",
    "docs/quickstarts/repo-assistant.md",
    "docs/quickstarts/palmierpro-mcp.md",
    "docs/quickstarts/app-market-research.md",
    "docs/quickstarts/google-play-growth.md",
    "docs/benchmarks/token-efficiency-smoke-test.md",
    "docs/benchmarks/token-efficiency-fresh-2026-06-25.md",
    "docs/patterns/default.md",
    "docs/patterns/skill.md",
    "docs/patterns/prompt.md",
    "docs/patterns/benchmark.md",
    "examples/coding.md",
    "examples/copilot-token-efficiency.md",
    "examples/benchmark.md",
    "examples/compression.md",
    "examples/handoff.md",
    "examples/local-model.md",
    "examples/repository-profile.md",
    "examples/palmierpro-mcp-workflow.md",
    "examples/app-market-research-brief.yaml",
    "examples/google-play-growth-brief.yaml",
    "schemas/app-market-research-brief.schema.json",
    "schemas/google-play-growth-brief.schema.json",
    "agents/token-efficient-response-agent.md",
    "agents/token-economy-orchestrator.md",
    "agents/terse-technical-coding-agent.md",
    "agents/kubernetes-homelab-engineer.md",
    "agents/comet-authenticated-research-agent.md",
    "agents/seo-ai-search-optimization-agent.md",
    "agents/palmierpro-mcp-video-editor-agent.md",
    "agents/app-market-research-agent.md",
    "agents/google-play-growth-optimizer-agent.md",
    "skills/copilot-token-efficiency.md",
    "skills/token-efficient-response-compression.md",
    "skills/context-budgeting-and-pruning.md",
    "skills/token-output-budgeting.md",
    "skills/prompt-and-memory-compression.md",
    "skills/token-efficiency-measurement.md",
    "skills/kubernetes-gitops-change-management.md",
    "skills/kubernetes-homelab-troubleshooting.md",
    "skills/comet-authenticated-research.md",
    "skills/comet-local-bridge-safety.md",
    "skills/palmierpro-mcp-setup-and-safety.md",
    "skills/palmierpro-timeline-editing.md",
    "skills/palmierpro-transcript-cuts-and-captions.md",
    "skills/palmierpro-ai-generation-workflow.md",
    "skills/browser-research-foundations.md",
    "skills/authenticated-browser-handoff.md",
    "skills/play-store-autocomplete-research.md",
    "skills/play-store-competitor-discovery.md",
    "skills/play-store-listing-teardown.md",
    "skills/forum-demand-mining.md",
    "skills/play-console-search-term-analysis.md",
    "skills/market-opportunity-clustering.md",
    "skills/app-market-research-orchestrator.md",
    "skills/google-play-aso-foundations.md",
    "skills/google-play-keyword-and-metadata-optimization.md",
    "skills/google-play-creative-conversion-optimization.md",
    "skills/google-play-quality-and-retention-signals.md",
    "skills/app-web-seo-and-entity-optimization.md",
    "skills/ai-agent-recommendation-readiness.md",
    "skills/app-growth-experimentation-and-measurement.md",
    "skills/google-play-growth-orchestrator.md",
    "prompts/token-efficiency/common-task-benchmark.md",
    "prompts/token-efficiency/agent-retrofit.md",
    "prompts/token-efficiency/compress-memory-file.md",
    "prompts/token-efficiency/compare-models.md",
    "prompts/palmierpro/full-edit-pass.md",
    "prompts/palmierpro/story-assembly-from-project-media.md",
    "prompts/palmierpro/youtube-short-from-long-form.md",
    "prompts/palmierpro/transcript-cleanup-pass.md",
    "prompts/palmierpro/short-form-social-cutdown.md",
]

PURPOSE_GLOBS = [
    "agents/*.md",
    "skills/*.md",
    "prompts/token-efficiency/*.md",
    "prompts/palmierpro/*.md",
    "docs/*.md",
    "docs/quickstarts/*.md",
    "docs/benchmarks/*.md",
    "docs/patterns/*.md",
    "examples/*.md",
    ".github/agents/*.agent.md",
]

PURPOSE_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
]

JSON_FILES = [
    "agentdefaults.manifest.json",
    "schemas/app-market-research-brief.schema.json",
    "schemas/google-play-growth-brief.schema.json",
]

LINK_EXTENSIONS = (
    ".md",
    ".mdc",
    ".agent.md",
    ".windsurfrules",
    ".json",
    ".py",
    ".yml",
    ".yaml",
)


def print_fail(title, failures):
    print(f"FAIL: {title}")
    for failure in failures:
        print(f"  - {failure}")
    return 1


def check_required_files():
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    if missing:
        return print_fail("required files", missing)
    print(f"PASS: required files ({len(REQUIRED_FILES)} checked)")
    return 0


def check_purpose_sections():
    paths = []
    for pattern in PURPOSE_GLOBS:
        paths.extend(ROOT.glob(pattern))
    paths.extend(ROOT / name for name in PURPOSE_FILES)

    failures = []
    seen = set()
    for path in paths:
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8")
        if "## Purpose" not in text:
            failures.append(str(path.relative_to(ROOT)))

    if failures:
        return print_fail("Markdown files missing ## Purpose", failures)
    print(f"PASS: Markdown structure ({len(seen)} checked)")
    return 0


def check_json_files():
    failures = []
    for name in JSON_FILES:
        path = ROOT / name
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"{name}: {exc}")

    if failures:
        return print_fail("JSON files", failures)
    print(f"PASS: JSON files ({len(JSON_FILES)} checked)")
    return 0


def iter_manifest_paths(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {
                "primary_entrypoint",
                "validation",
                "quickstart",
                "agent",
                "schema",
                "example",
                "acceptance_tests",
                "wrapper",
            } and isinstance(child, str):
                yield child
            elif key in {"skills", "prompts"} and isinstance(child, list):
                for item in child:
                    if isinstance(item, str):
                        yield item
            yield from iter_manifest_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_manifest_paths(child)


def check_manifest_references():
    path = ROOT / "agentdefaults.manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return print_fail("manifest references", [str(exc)])

    missing = sorted({
        ref for ref in iter_manifest_paths(manifest)
        if not (ROOT / ref).is_file()
    })
    if missing:
        return print_fail("manifest references", missing)
    print("PASS: manifest references")
    return 0


def should_check_link(target):
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return False
    path_part = target.split("#", 1)[0]
    return bool(path_part) and path_part.endswith(LINK_EXTENSIONS)


def check_links():
    failures = []
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = target.strip()
            if not should_check_link(target):
                continue
            path_part = target.split("#", 1)[0]
            if not (md.parent / path_part).resolve().exists():
                failures.append(f"{md.relative_to(ROOT)} -> {target}")

    if failures:
        return print_fail("broken Markdown links", failures)
    print("PASS: Markdown links")
    return 0


def main():
    print("AgentDefaults validation")
    print("========================")
    failures = (
        check_required_files()
        + check_purpose_sections()
        + check_json_files()
        + check_manifest_references()
        + check_links()
    )
    if failures:
        print("\nResult: FAIL")
        return 1
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
