---
name: brix-org-capability-planning
description: Plans Brix org capabilities before build or deploy, including scratch org features, CDO/SDO choice, package dependencies, permission set licenses, settings, target-org assumptions, and BlackTab/TSO readiness. Use when a solution needs org features, licenses, packages, or setup dependencies. Also triggers on "what features do I need in the org", "update orgs/dev.json", "PSL licenses", "managed package dependency", "brix dependency", "BlackTab readiness", "TSO needs". Do NOT use for: provisioning a new org (use get-demo-org or org-builder); writing CumulusCI flow steps that consume the capabilities (use brix-cumulusci-qx-lifecycle).
---

# Brix Org Capability Planning

## Workflow

1. Identify required capabilities from the solution:
   - Salesforce clouds/features
   - Agentforce, Prompt Builder, Data Cloud, Experience Cloud, Industries, or Analytics
   - permission set licenses and user flags
   - managed packages or dependent brix
2. Decide the development/QA org type:
   - CDO or scratch org for xDO-style work
   - SDO when the brix pattern requires it
   - explicit user-provided org when neither default applies
3. Update or document org assumptions:
   - `orgs/dev.json` features and settings
   - `orgs/dev_preview.json` only when intentionally different
   - package dependencies in `cumulusci.yml`
   - dependent brix under `sources`
   - required manual target-org enablement that cannot be automated
4. Use `qx utils feature-search '<term>'` when feature names are uncertain.
5. Put automatable setup in `prepare_org` or `source_dependencies`.
6. Verify with a QA deploy before treating capability assumptions as stable.

## Output Format

End with:

- required org capabilities (clouds, features, packages, dependent brix)
- recommended dev/QA org type (CDO / SDO / scratch / explicit BYO)
- changes made to `orgs/dev.json` (and `orgs/dev_preview.json` if applicable)
- `cumulusci.yml` dependencies and `sources` updates
- permission set licenses and user flags required
- BlackTab / TSO readiness gaps the user must arrange manually
- next safe step (typically a QA deploy) before treating capability assumptions as stable

## Guardrails

- Do not add metadata that only deploys in a feature-enabled org without documenting or encoding that feature dependency.
- Do not assume dev scratch-org features are available in target Salesforce orgs.
- Do not hide license or PSL assumptions in chat only.
