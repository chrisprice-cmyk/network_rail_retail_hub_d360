---
name: salesforce-ui-verification
description: Prepares manual end-user UI acceptance for Brix changes and non-browser corroboration where useful. Use when a visible Lightning, Experience Cloud, or Agentforce path should be checked by the user rather than automated browser verification. Also triggers on "ask the user to confirm the UI", "manual acceptance", "App Launcher path", "is the demo path actually working", "presenter ready check". Do NOT use for: Playwright/Robot browser automation (out of scope unless explicitly requested); deploy execution (use salesforce-deploy); reusable validation asset authoring (use brix-validation-authoring); root-cause diagnosis when the UI fails (use diagnostic-refresh).
---

# Salesforce UI Verification

## When To Use

- A Lightning app, tab, FlexiPage, LWC, Flow screen, record page, Experience Cloud page, or Agentforce surface needs user acceptance.
- A deploy or validation flow needs a clear manual check for the end user.
- A demo/PoC presenter path must be reviewed by the person who will use it.

## Workflow

1. Confirm the target org alias or project-local target org before org-backed checks.
2. Define the exact check:
   - target surface
   - expected visible cues
   - user or permission set context
   - what the user should confirm
3. Pick any non-browser corroboration that helps:
   - `npm run test:lwc` for LWC unit behavior
   - `cci flow run validate_qbrix --org <alias>` for brix-level validation
   - `sf data query` or metadata checks when they explain expected UI state
4. Ask the end user to open the target surface and confirm they are happy with the result.
5. For app-shell scenes, ask the user to use App Launcher or equivalent user path into the named app, not only a deep link.
6. For Experience Cloud, confirm deployed metadata and publish/refresh status, then ask the user to inspect the public or authenticated page path.
7. When the user reports a failure, identify whether the likely owner is metadata placement, access, data, deploy/publish, rendering, or setup.

## Evidence Contract

For resolved UI checks, report:

- non-browser command run, if any
- manual path the user should inspect
- target org/user context
- expected cues
- user acceptance status when the user confirms it
- what remains unverified until user review

## Guardrails

- Do not treat deploy success as UI proof.
- Do not treat a direct deep link as proof that a user can find the app or tab.
- Do not leave missing data, permissions, or publish state as ambiguous UI failures.
- Do not add browser-based verification unless the user explicitly asks for it.
