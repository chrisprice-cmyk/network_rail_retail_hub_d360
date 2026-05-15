---
name: brix-validation-authoring
description: Turns Brix acceptance criteria into non-browser reusable validation assets such as `validate_qbrix` flow steps, local test commands, Salesforce CLI data checks, and metadata/data assertions. Use when a solution needs repeatable proof beyond one-off deploy success.
---

# Brix Validation Authoring

## Workflow

1. Define the acceptance criterion in one sentence: surface, user context, expected cue, and failure meaning.
2. Pick the validation level:
   - Apex tests for server behavior
   - LWC Jest for component logic
   - Salesforce CLI `sf data` checks for record presence or data shape
   - metadata/deploy checks for source correctness
   - `validate_qbrix` flow when the check should run as part of Brix validation
3. Use installed Salesforce testing skills for artifact-specific test strategy.
4. Keep Brix validation reusable:
   - no org-specific IDs or URLs
   - use aliases, SOQL lookups, visible labels, External IDs, or required inputs
5. For UI paths, do not create browser-based verification by default. Ask the end user to open the target app, page, site, or agent and confirm they are happy with the result.
6. Add the validation to `cumulusci.yml` only when it should run for every Brix validation.
7. Treat `validate_qbrix` as recommended when an org is available; it may be skipped for demo-only solution builds.
8. Report the command, artifact path, expected result, and what remains manual.

## Guardrails

- Do not add Playwright, browser-based Robot, or other browser automation unless the user explicitly requests it.
- Do not make tests depend on transient IDs.
- Do not put secrets or frontdoor URLs in test files, logs, or artifacts.
