---
name: diagnostic-refresh
description: Runs root-cause analysis and durable remediation for Salesforce brix bugs, failed CumulusCI/QX deploys, broken validation flows, Apex/LWC regressions, Experience Cloud publish issues, or org-specific deployment failures. Use when a simple fix failed or proof is required.
---

# Diagnostic Refresh

## Workflow

1. Establish a read-only baseline:
   - current git diff
   - relevant `cumulusci.yml` flow/task configuration
   - target org alias or project-local target org, if org-backed
   - failing command, log, or validation artifact
2. Isolate the smallest failing case:
   - metadata deploy
   - dependency install
   - permission assignment
   - data load
   - Salesforce CLI/data check, LWC test, or CumulusCI validation
   - Experience Cloud publish or runtime path
3. Form a root-cause hypothesis and prove or disprove it with safe checks.
4. Apply the smallest durable fix after the cause is confirmed.
5. Re-run the failing path and one adjacent regression check.
6. Report root cause, fix, evidence, and residual risk.

## Guardrails

- Do not patch symptoms without evidence.
- Do not revert unrelated user changes.
- Do not edit generated or org-specific output when the durable fix belongs in source metadata, CumulusCI flow configuration, validation assets, or required inputs.
- Prefer platform-native and brix-native fixes over one-off scripts.
