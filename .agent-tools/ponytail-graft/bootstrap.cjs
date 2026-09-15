#!/usr/bin/env node
// Hardened entrypoint for the generated Ponytail + Graft bootstrap.
// Opt-in only: this file runs only when explicitly invoked by a user/agent.
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const OWNER = 'multi-repo-ponytail-graft/v1';
const SIDECAR = path.resolve(__dirname);
const REPO = path.resolve(SIDECAR, '..', '..');
const CORE = path.join(SIDECAR, 'bootstrap-core.cjs');
const MODULES = path.join(SIDECAR, 'node_modules');
const args = process.argv.slice(2);
const modeArgs = args.filter((arg) => arg.startsWith('--mode='));
const MODE = (modeArgs[0] || '--mode=repo').slice(7);

function fail(message) {
  process.stderr.write(`[${OWNER}] REFUSED: ${message}\n`);
  process.exit(1);
}

if (modeArgs.length > 1) fail('pass at most one --mode argument');
if (!['repo', 'workspace'].includes(MODE)) fail(`unsupported mode ${JSON.stringify(MODE)}; expected repo or workspace`);
if (!fs.existsSync(CORE)) fail(`missing generated bootstrap core: ${CORE}`);

function relativeTarget(target) {
  const absolute = path.resolve(REPO, target);
  const relative = path.relative(REPO, absolute);
  if (relative === '..' || relative.startsWith(`..${path.sep}`) || path.isAbsolute(relative)) {
    fail(`target escapes repository root: ${target}`);
  }
  return { absolute, relative: relative || '.' };
}

/**
 * Refuse writes through symlinked repository surfaces. Following a symlink can
 * turn a repo-scoped installer into a write outside the authorized checkout.
 * Missing trailing components are fine; every existing parent must be real.
 */
function rejectSymlinkComponents(target) {
  const { absolute, relative } = relativeTarget(target);
  const parts = relative === '.' ? [] : relative.split(path.sep);
  let current = REPO;
  for (const part of parts) {
    current = path.join(current, part);
    let stat;
    try {
      stat = fs.lstatSync(current);
    } catch (error) {
      if (error && error.code === 'ENOENT') return;
      throw error;
    }
    if (stat.isSymbolicLink()) {
      fail(`${path.relative(REPO, current)} is a symlink; refusing repo-scoped mutation through it`);
    }
  }
  // Keep the lexical containment check above even when the final target exists.
  void absolute;
}

const sharedTargets = [
  '.agent-tools/ponytail-graft/package.json',
  '.agent-tools/ponytail-graft/package-lock.json',
  '.agent-tools/ponytail-graft/bootstrap-core.cjs',
  '.agent-tools/ponytail-graft/node_modules',
  '.agent-tools/ponytail-graft/state',
  'graft',
];
const repoTargets = [
  'AGENTS.md',
  'CLAUDE.md',
  '.github/copilot-instructions.md',
  '.claude/settings.json',
  '.claude/helpers',
  '.claude/skills',
  '.agents/skills',
  '.cursor/hooks.json',
  '.cursor/hooks',
  '.cursor/mcp.json',
  '.cursor/rules',
  '.kiro/settings/mcp.json',
  '.kiro/steering',
  '.mcp.json',
  '.gitignore',
  'docs/AGENT_TOOLING.md',
];
for (const target of MODE === 'workspace' ? sharedTargets : [...sharedTargets, ...repoTargets]) {
  rejectSymlinkComponents(target);
}

function readJson(file, label) {
  let parsed;
  try {
    parsed = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (error) {
    fail(`${label} is missing or invalid JSON: ${error.message}`);
  }
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) fail(`${label} must be a JSON object`);
  return parsed;
}

const packageFile = path.join(SIDECAR, 'package.json');
const lockFile = path.join(SIDECAR, 'package-lock.json');
const manifest = readJson(packageFile, 'sidecar package.json');
const lock = readJson(lockFile, 'sidecar package-lock.json');
const pins = manifest.dependencies || {};
const expectedPackages = ['@dietrichgebert/ponytail', '@nanonets/graft'];
for (const name of expectedPackages) {
  const wanted = pins[name];
  if (typeof wanted !== 'string' || !/^\d+\.\d+\.\d+$/.test(wanted)) {
    fail(`sidecar package.json must pin ${name} to an exact semantic version`);
  }
  const locked = lock.packages && lock.packages[`node_modules/${name}`] && lock.packages[`node_modules/${name}`].version;
  if (locked !== wanted) {
    fail(`tracked lock drift for ${name}: package.json=${wanted}, package-lock.json=${locked || 'missing'}; update pins deliberately instead of repairing implicitly`);
  }
}

function installedVersion(name) {
  const file = path.join(MODULES, ...name.split('/'), 'package.json');
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8')).version || null;
  } catch {
    return null;
  }
}

const stale = expectedPackages.some((name) => installedVersion(name) !== pins[name]);
if (stale) {
  process.stdout.write(`[${OWNER}] sidecar dependencies are absent/stale; repairing from the tracked lock with npm ci\n`);
  try {
    execFileSync('npm', ['ci', '--no-audit', '--no-fund'], {
      cwd: SIDECAR,
      stdio: 'inherit',
      timeout: 600000,
      env: {
        ...process.env,
        DO_NOT_TRACK: '1',
        npm_config_fund: 'false',
        npm_config_audit: 'false',
      },
    });
  } catch (error) {
    fail(`npm ci failed while repairing sidecar dependencies${error && error.status !== undefined ? ` (exit ${error.status})` : ''}`);
  }
}
for (const name of expectedPackages) {
  const installed = installedVersion(name);
  if (installed !== pins[name]) fail(`installed ${name}@${installed || 'missing'} does not match pinned ${pins[name]} after npm ci`);
}

try {
  execFileSync(process.execPath, [CORE, ...args], {
    cwd: REPO,
    stdio: 'inherit',
    timeout: 600000,
    env: process.env,
  });
} catch (error) {
  process.exit(error && Number.isInteger(error.status) ? error.status : 1);
}
