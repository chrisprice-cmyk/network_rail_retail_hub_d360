# AGENTS.md — network_rail_retail_hub_d360

## Project context

**Customer:** Network Rail — Commercial Property / Retail Hub  
**Unique ref:** retail_hub_d360  
**Template:** Live xDO clone from sfdc-qbranch-emu/xDO-Template  
**Demo date:** 15 July 2026, Waterloo (2 hours — show & tell + requirements/Q&A)

## What this brix is

A Tableau Next (embedded analytics) demo powered by Data Cloud (D360) for Network Rail's Retail Hub team. Shows a unified station compliance and commercial dashboard across NR's 19 managed stations, with a view to scaling to ~200 under GBR.

**Agentforce demo (policy search, retailer onboarding, web-to-case) is owned by Richard Steer — NOT in scope here.** This brix covers the Data Cloud → Tableau Next analytics layer only.

## Key stakeholders

- **Vince** — NR Commercial Property lead (exec sponsor)
- **Kieran** — Retail Hub Product Owner (day-to-day contact)
- **Ashleigh Jordan** — Salesforce AE (ashleigh.jordan@salesforce.com)
- **Neil Hutchinson** — SE lead on analytics (nhutchinson@salesforce.com)
- **Richard Steer** — SE on Agentforce (rsteer@salesforce.com)
- **Chris Price** — SE assigned to Tableau Next / D360 analytics piece

## Demo story

NR already has Retail Hub built on Salesforce and Data Cloud licensed. The demo shows:
1. Data Cloud unifying Retail Hub Salesforce data + footfall data into a single station profile
2. Tableau Next dashboard — Statutory Compliance pillar as lead (Pillar 1), Revenue/Commercial secondary
3. Station-level slicing by: Station Type (Cat A/B/C), Geographic Region, Risk Profile

## Pillars in scope

**Primary — Statutory Compliance**
- Overall Station Compliance Score (%)
- EICR Validity Rate
- Fire Risk Assessment Status (days to next / outstanding actions)
- Fire Alarm & Sprinkler Testing Compliance Rate
- COSHH Risk Assessment Completion Rate
- Cleaning Standard Pass Rate

**Secondary — Revenue & Commercial**
- Revenue per Square Foot
- Retail Unit Vacancy Rate (%)
- Footfall-to-Revenue Conversion Rate
- Lease Renewal Conversion Rate

## Data model (synthetic)

- `Station__c` — profile (name, type Cat A/B/C, region, managed_by)
- `ComplianceCheck__c` — inspection records (station lookup, type, status, due date, score)
- `RetailUnit__c` — commercial units (sqft, tenant, lease expiry, revenue)
- `FootfallRecord__c` — daily/weekly footfall counts per station

These feed Data Cloud DMOs for unified analytics.

## Known constraints

- PSS removed from NR shelfware — compliance tracking uses custom objects, not PSS module
- Org access TBC — may be NR sandbox (D360 already licensed) or SDO with D360 enabled
- Tableau Next vs CRM Analytics to confirm against what's licensed in target org
- Synthetic data required until NR sandbox access confirmed
- Microsoft Copilot competitor thread (HSSE) is separate — not relevant to this analytics brix

---

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
