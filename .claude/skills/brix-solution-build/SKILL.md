---
name: brix-solution-build
description: Orchestrates Salesforce demo/PoC solution creation inside a Brix template using installed Salesforce skills for artifact implementation and local Brix skills for CumulusCI/QX lifecycle, data, validation, org capability, and completion packaging. Use when building or modifying custom apps, tabs, LWC, Apex, Flow, Agentforce, metadata, Experience Cloud assets, demo data, validation assets, or pre/deploy/post-deploy automation.
---

# Brix Solution Build

## Workflow

1. Read `CLAUDE.md` and `.claude/memory.md` before non-trivial work.
2. Assume `forcedotcom/sf-skills` is installed. Use the matching installed Salesforce skill for artifact implementation:
   - Apex, tests, triggers, SOQL, and integrations
   - LWC, Aura, Flow, metadata, permissions, and deployment
   - Agentforce agents, topics/actions, prompt templates, testing, and observability
3. Use local Brix skills for template-specific follow-through:
   - Brix lifecycle and CumulusCI/QX wiring: `brix-cumulusci-qx-lifecycle`
   - data packages, required inputs, and runtime substitution: `brix-data-packaging`
   - reusable validation assets: `brix-validation-authoring`
   - scratch/CDO/SDO capability planning: `brix-org-capability-planning`
   - Agentforce brix packaging after the installed Agentforce skills define artifacts: `brix-agentforce-packaging`
   - Experience Cloud source, publish, and reusable site packaging: `experience-cloud-lwr` or `experience-cloud-branding`
   - completion check before handoff: `brix-solution-completion`
   - failed deploys or durable bug fixes: `diagnostic-refresh`
4. Keep source layout brix-native:
   - package metadata in `force-app/main/default/`
   - pre/post unmanaged metadata in `unpackaged/pre/` or `unpackaged/post/`
   - local non-browser validation assets when useful
   - runtime inputs in `qbrix_local/inputs/`
   - CumulusCI/QX lifecycle in `cumulusci.yml`
5. Keep `cumulusci.yml` `project.package.api_version` and `sfdx-project.json` `sourceApiVersion` aligned.
6. When adding lifecycle work, place it in the right brix phase:
   - `prepare_org` for pre-deploy settings, feature prep, and dependency setup
   - `source_dependencies` for dependent brix installs guarded by `when`
   - `deploy` for `force-app/main/default`
   - `post_qbrix_deploy` for permissions, publish steps, data, and final org shaping
7. Add permission sets and post-deploy assignment steps for new user-facing features.
8. Validate incrementally with the smallest useful non-browser checks. Run `validate_qbrix` when an org is available and the work is not a demo-only solution build; otherwise report that it was skipped.
9. End by running the `brix-solution-completion` checklist or explicitly reporting which completion gates remain open.

## Guardrails

- Do not duplicate generic Salesforce artifact guidance that belongs to installed `sf-skills`; use them and then package the result as a reusable Brix.
- Do not bypass the brix lifecycle with ad hoc deploy instructions when the change must be reusable as a template.
- Do not add org-backed behavior without an explicit org alias or project-local target org.
- Do not leave app visibility, tab visibility, or permission-set assignment as implicit follow-up for demo-critical launch paths.
- Do not place broad planning, account research, pitch writing, or presentation narrative work in this repo unless it directly drives build, deploy, or test artifacts.
- Preserve existing template placeholders such as `task: None` unless replacing them with real brix work.
