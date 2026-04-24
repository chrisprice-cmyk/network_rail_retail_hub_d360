# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Authoritative Rules

Detailed project rules live in **`.claude/memory.md`** — load that file before doing non-trivial work. It covers Apex, LWC, CumulusCI flows, QBrix extension tasks, `when`-clause methods, permission-set conventions, and the demo-environment security posture. Do not duplicate its contents here; update it in place when rules change.

### Rule sync is enforced

The same ruleset is mirrored across four LLM tool surfaces. `make check-rules-sync` (part of `make precommit`) fails if any are missing or drift. When you change rules, update **all four**:

- `.cursorrules` and `.cursor/rules/*.mdc`
- `.claude/memory.md`
- `.gemini/rules/*.md`
- `.windsurf/rules/*.md`

Each file must contain an `LLM Rule Synchronization (Required)` section — the Makefile greps for that literal string.

## Repository shape

This is a **QBrix (Brix) template** — a Salesforce demo-org deployment package built on **CumulusCI + QX + Salesforce DX**. It is not production code; the target is CDO (Clean Demo Orgs) and scratch orgs, and the rules in `.claude/memory.md` explicitly relax FLS/sharing expectations accordingly.

### Config that must stay in sync

- `cumulusci.yml` — **source of truth** for API version (`project.package.api_version`), brix name, dependencies, and flows.
- `sfdx-project.json` — `sourceApiVersion` **must match** `cumulusci.yml`'s `api_version`. If you bump one, bump the other.
- `project.name` and `project.package.name` in `cumulusci.yml` must match the repo name (end of `git.repo_url`).

### Deployment architecture (`cumulusci.yml` flows)

The entry point is the `deploy_qbrix` flow, which runs three stages in order:

1. **`prepare_org`** — `orgconfig_hydrate` → `deploy_settings` → `update_dependencies`
2. **`source_dependencies`** — installs dependent brix (guarded by `when: not org_config.is_qbrix_installed(...)`)
3. **`deploy`** → **`post_qbrix_deploy`** — deploys `force-app/main/default`, then assigns permissions and runs `deploy_qbrix_data`

`orgconfig_hydrate` **must** appear before any step that uses a `when:` clause in the same flow — `when:` methods live on `org_config` and are populated by that task. See `.claude/memory.md` for the full list of supported `when:` methods.

### Directory layout (non-obvious pieces)

- `force-app/main/default/` — Salesforce metadata deployed by the `deploy` task.
- `qbrix/` — QBrix tooling and non-production helpers (referenced by `class_path:` in tasks).
- `qbrix_local/` — local-only; `inputs/required.json` declares runtime parameters the brix prompts for, `robot/` holds Robot Framework tests.
- `orgs/dev.json` — scratch org definition (features list matters: TSOs that install this brix need the same licenses enabled in BlackTab). `orgs/dev_preview.json` is an optional pinned-instance variant.
- `unpackaged/` — unmanaged metadata not part of the main package.
- `.qbrix/`, `browser/traces/temp/` — cache/temp, git-ignored, safe to delete.

## Common commands

### Node/JS (run from repo root)

```bash
npm install              # install dev deps
npm run test:lwc         # Jest LWC unit tests (sfdx-lwc-jest)
npm run test:e2e         # Playwright E2E (testDir is ./.qbrix)
npm run lint:lwc         # ESLint over force-app/main/default/lwc
npm run format           # Prettier write
npm run format:check     # Prettier check only
```

Single Jest test: `npx sfdx-lwc-jest -- -t "<test name pattern>"` or pass a path.
Single Playwright test: `npx playwright test path/to/spec.ts -g "<name>"`.

### Precommit / tooling checks

```bash
make precommit           # lockfiles + check-tools + check-rules-sync + npm-lint + npm-test
make check-tools         # verifies sf, cci, qx are installed
make check-rules-sync    # fails if LLM rule files are missing or drifted
make lockfiles           # regenerate package-lock.json
```

`make check-tools` requires `sf`, `cci`, and `qx` on PATH — use the devcontainer (`.devcontainer/`) if any are missing.

### Salesforce / QBrix workflow

VSCode tasks in `.vscode/tasks.json` are the recommended entry point (Cmd+Shift+B). From the CLI:

```bash
# Org creation (xDO pattern)
qx org pool --sdo --org dev          # pool a SDO (Simple Demo Org)
qx org pool --sdo --org qa           # pool a QA SDO
qx org create --org dev              # scratch org from orgs/dev.json

# Deploy
qx deploy --org <alias>              # runs deploy_qbrix
cci flow run deploy_qbrix --org <alias>
cci flow run validate_qbrix --org <alias>

# Introspection
sf config get target-org             # current default org
cci task info <task>                 # docs for any CumulusCI/QX task
cci task run list_qbrix --org <alias>
qx utils feature-search '<term>'     # find scratch-org features (including non-public)
qx utils doctor                      # fix common metadata/config issues
```

**Recommended QA→dev deployment loop**: deploy to a QA org first, run `validate_qbrix`, fix issues, then deploy to dev. Never test-deploy directly to dev.

## What not to do

- Do not use `@future` in Apex — use Queueable + `System.Finalizer` (per `.claude/memory.md`).
- Do not add SOQL/DML inside loops; bulkify everything.
- Do not hand-edit one LLM rule file without syncing the other three — CI will fail.
- Do not bump `cumulusci.yml` api_version without also bumping `sfdx-project.json` `sourceApiVersion`.
- `task: None` is a **valid** placeholder in CumulusCI flows — do not "fix" it.
