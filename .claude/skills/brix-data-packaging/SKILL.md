---
name: brix-data-packaging
description: Packages reusable demo/PoC data for Brix projects using only NextGen Data Tool or CSV files compatible with Salesforce CLI `sf data` commands, plus required inputs, External IDs, and CumulusCI/QX data flows. Use when seeding records, reset data, uploading files, substituting org-specific values, or wiring `deploy_qbrix_data`. Also triggers on "seed records into the brix", "load demo data", "wire deploy_qbrix_data", "External IDs for the data", "qbrix_upload_files", "make data org-portable". Do NOT use for: SFDMU-based loads or custom dynamic generation; org-specific record inspection (use querying-soql or salesforce-ui-verification); presenter reset buttons (use demo-prep, which delegates back here for the data layer).
---

# Brix Data Packaging

## Workflow

1. Classify the data need:
   - static reference data
   - demo scenario records
   - reset or stream data
   - files/content
   - org/user-specific substitutions
2. Choose the packaging surface:
   - NextGen Data Tool for reusable brix data packs
   - CSV files compatible with Salesforce CLI `sf data` commands, such as `sf data import tree`, `sf data export tree`, `sf data upsert bulk`, and `sf data query`
   - `qbrix_upload_files` for files only when file upload is the actual requirement
3. Keep variable values out of source:
   - `qbrix_local/inputs/*.json` for required parameters, with safe defaults only
   - External IDs for record matching
   - CumulusCI cache values or SOQL lookups for runtime IDs
4. Wire data into `deploy_qbrix_data` and call that flow from `post_qbrix_deploy` when the main solution depends on it.
5. Validate the data shape:
   - row counts
   - lookup resolution
   - record values needed by the manual UI acceptance path
   - KPI plausibility when the data supports a demo story
6. Hand reusable validation to `brix-validation-authoring`.

## Output Format

End with:

- data classification (static reference, scenario, reset/stream, files, substitution)
- packaging surface chosen (NextGen Data Tool / `sf data` CSV / `qbrix_upload_files`) with paths
- External IDs / lookup-resolution strategy
- required inputs added (`qbrix_local/inputs/*.json`)
- `deploy_qbrix_data` wiring (call site + flow)
- shape verification results (row counts, lookups resolved, KPI plausibility)
- validation handoff (`brix-validation-authoring`) and what remains manual

## Guardrails

- Do not commit real customer data unless the user explicitly confirms it is approved demo data.
- Do not hardcode record IDs, user IDs, org URLs, or auth/frontdoor URLs.
- Do not use SFDMU or custom dynamic data-generation code by default.
- Do not treat a data load as done until non-browser validation or user acceptance confirms the expected records.
