---
name: demo-prep
description: Coordinates brix demo preparation assets such as seed/reset data flows, presenter utility actions, demo user setup, prompt/demo automation, and validation follow-through. Use when the user asks for demo prep, demo data automation, reset buttons, stream/seed records, or presenter-ready org shaping inside this Salesforce DX + CumulusCI template.
---

# Demo Prep

## Workflow

1. Identify the demo/PoC scenario, presenter path, objects involved, and whether the need is reset, seed, stream, or guided action.
2. Use installed Salesforce skills for artifact implementation such as Apex, LWC, Flow, Prompt Builder, Agentforce, or metadata; keep this skill focused on repeatable Brix demo readiness.
3. Choose the least fragile implementation surface:
   - data: `brix-data-packaging`
   - org/user setup: `user_manager`, permission assignment, or required inputs
   - presenter controls: utility bar app metadata, LWC, Flow action, or small Apex controller
   - repeatable non-browser validation: `brix-validation-authoring`
4. Wire reusable automation into `cumulusci.yml` instead of leaving one-off manual steps:
   - preconditions in `prepare_org`
   - dependencies in `source_dependencies`
   - user/access/data/publish work in `post_qbrix_deploy`
   - data-specific steps in `deploy_qbrix_data`
5. If the presenter path depends on a Lightning app, include app, tab, landing page, permission-set visibility, and first-screen proof in the same build plan.
6. Add or update non-browser validation assets when the behavior should survive template reuse. For visible UI behavior, ask the end user to inspect the deployed surface and confirm they are happy.
7. Hand off schema/access work to installed Salesforce skills plus `salesforce-metadata` and `field-level-security`; hand deployment proof to `salesforce-deploy` or `salesforce-ui-verification`.

## Guardrails

- Do not treat seeded data as demo readiness when the launch surface is missing or unverified.
- Do not hardcode org IDs, user IDs, URLs, or environment-specific record IDs.
- Prefer required inputs, CumulusCI cache values, SOQL lookups, or External IDs for values that vary by org.
- Keep demo convenience acceptable, but do not hide brittle manual setup from the brix lifecycle.
