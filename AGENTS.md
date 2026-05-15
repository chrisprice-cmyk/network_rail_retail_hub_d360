# AGENTS.md

This file provides guidance to Codex when working with code in this repository.

## Authoritative Rules

Detailed Codex rules live in `codex/rules/`. Load the relevant rule files before non-trivial work:

- `codex/rules/general_development.md`
- `codex/rules/brix_development.md`
- `codex/rules/brix_technology.md`
- `codex/rules/apex_development.md`
- `codex/rules/lwc_development.md`
- `codex/rules/brix_robot_framework.md`

These files mirror the Cursor, Gemini, and Windsurf split rule files. `make check-rules-sync` fails if they drift.

Assume the Salesforce skills from `https://github.com/forcedotcom/sf-skills` are automatically installed. Use those installed Salesforce skills for artifact-specific work such as Apex, LWC, Flow, metadata, permissions, Agentforce, integration, and testing. Use the local Brix rules and skills for CumulusCI/QX lifecycle wiring, data packaging, validation assets, org capability planning, Agentforce Brix packaging, and solution-completion checks.

## LLM Rule Synchronization (Required)

When updating any LLM/tooling rules, keep these surfaces synchronized:

- Cursor: `.cursor/rules/*` and `.cursorrules`
- Claude: `.claude/*` (notably `.claude/memory.md`)
- Codex: `AGENTS.md` and `codex/rules/*`
- Gemini: `.gemini/rules/*`
- Windsurf: `.windsurf/rules/*`

## Repository Shape

This is a QBrix/Brix template: a Salesforce demo-org deployment package built on CumulusCI, QX, and Salesforce DX. The target is demo and PoC environments, not production packaging.

## Required Discipline

- Keep `cumulusci.yml` `project.package.api_version` and `sfdx-project.json` `sourceApiVersion` aligned.
- Use `deploy_qbrix` for reusable brix deployment. Treat `validate_qbrix` as recommended when an org is available, but skippable for demo solution builds.
- Do not add browser-based verification by default. Ask the end user to inspect visible UI paths and confirm they are happy with the result.
- Keep reusable source in the brix lifecycle rather than relying on one-off manual org changes.
- Never store real secrets in the repo. Redact keys, tokens, passwords, auth URLs, frontdoor URLs, private keys, org credentials, and customer-sensitive data.
