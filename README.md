# Demo Brix Template (xDO-Template)

This repository is a **template** for Brix (QBrix) projects using **Salesforce DX + CumulusCI/QX**, designed to work cleanly in **VSCode**, **Cursor**, and with multiple LLM assistants.

## Getting Started

- **Primary project config**: `cumulusci.yml`
- **Salesforce API version (source of truth)**: `cumulusci.yml > project > package > api_version` (and must match `sfdx-project.json > sourceApiVersion`)
- **VSCode tasks**: `.vscode/tasks.json` (recommended workflow entry point)

If you have not worked on Brix before, complete the [Brix Builder Certification](https://qlabs.my.trailhead.com/content/developers/trails/brix-builder-certification).

## Scratch Org Definitions (`orgs/`)

- **`orgs/dev.json`**: Default scratch org definition used for most development.\n+  - Includes additional features (including Einstein Generative Services feature flags) needed by some demos.\n+- **`orgs/dev_preview.json`**: Optional definition for preview/pinned-instance scenarios.\n+  - Includes an `instance` key and may omit some features present in `dev.json`.\n+\n+If you change one, either **keep them intentionally different and document why**, or align them to reduce template confusion.

## Cache / Temp Directories

These folders are **intentionally excluded from Git** and safe to delete when troubleshooting:

- **`.qbrix/`**: QX/Brix cache + temp workspace (Playwright tests may use this as their `testDir`).\n+- **`browser/traces/temp/`**: transient traces/cache (safe to clear).

## JS Tooling (Jest + Playwright)

This repo includes Jest/Playwright configs (`jest.config.js`, `playwright.config.ts`). Use:

- Install deps: `npm install`\n+- LWC tests: `npm run test:lwc`\n+- E2E tests: `npm run test:e2e`

## Required Inputs (`qbrix_local/inputs/`)

- **Default required inputs** are defined in `qbrix_local/inputs/required.json`.\n+- If using Marketing Cloud, `qbrix_local/inputs/mc_template_required.json` is provided as a starting point (copy/rename into `required.json` as needed).

## Support

The current owner of the Demo Brix is noted in `cumulusci.yml` next to `qbrix_owner_name`.
