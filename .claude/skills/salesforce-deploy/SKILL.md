---
name: salesforce-deploy
description: Validates and deploys Salesforce brix changes with CumulusCI/QX lifecycle discipline after installed Salesforce deploy skills handle artifact-level concerns. Use for deploy planning, validate_qbrix, pre/deploy/post-deploy sequencing, publish/data/permission follow-through, and post-deploy proof. Also triggers on "deploy this brix", "run deploy_qbrix", "validate_qbrix", "qx deploy", "post-deploy verification", "deploy to QA org first". Do NOT use for: ad hoc one-off `sf project deploy start` not packaged through CumulusCI/QX (use deploying-metadata or sfdx-deploy-doctor); diagnosing a failed deploy after retries (use diagnostic-refresh); CumulusCI YAML authoring without a deploy in scope (use brix-cumulusci-qx-lifecycle); manual UI acceptance check authoring (use salesforce-ui-verification).
---

# Salesforce Deploy

## Workflow

1. Classify the deployment job: validate only, deploy, retrieve, publish, data load, or post-deploy verification.
2. Use installed Salesforce deployment skills for artifact-specific deploy guidance when needed; keep this skill focused on reusable Brix lifecycle execution.
3. Confirm target context before org-backed work:
   - explicit `--org <alias>` / `--target-org <alias>`, or
   - project-local target org from `.sf/config.json` or `.sfdx/sfdx-config.json`
4. Run lightweight local checks first when relevant:
   - `make check-rules-sync`
   - `make check-tools`
   - `npm run test:lwc`
   - `npm run test:e2e`
5. Use the brix lifecycle for reusable deployment:
   - `qx deploy --org <alias>`
   - `cci flow run deploy_qbrix --org <alias>`
   - `cci flow run validate_qbrix --org <alias>`
6. Keep pre/deploy/post sequencing explicit:
   - `prepare_org`: settings, feature prep, dependency setup
   - `source_dependencies`: dependent brix installs, guarded by `orgconfig_hydrate` and `when`
   - `deploy`: `force-app/main/default`
   - `post_qbrix_deploy`: permissions, data, publish, recently viewed, favorites, org shaping
7. Validate before deploying when the change is user-facing, cross-surface, or hard to reverse.
8. When a Lightning app shell is demo-critical, deploy and verify the app bundle together:
   - `CustomApplication`
   - tabs
   - landing or home `FlexiPage`
   - presenter permission set app/tab visibility
   - post-deploy assignment step
9. After deployment, run non-browser checks where useful and ask the user to inspect visible Salesforce UI paths. Use `salesforce-ui-verification` for the manual acceptance checklist and `brix-validation-authoring` when proof should become reusable validation.
10. End with target, scope, validation result, deploy result, verification result, and the next safe step.

## Guardrails

- Do not rely on a global default org for deploy work.
- Treat `validate_qbrix` as recommended when an org is available. It may be skipped for demo solution builds, but report the skip explicitly.
- Do not skip `orgconfig_hydrate` before `when` clauses in the same flow.
- Do not "fix" `task: None`; it is a valid template placeholder.
- Do not bypass CumulusCI/QX when the change must be reusable by brix consumers.
- Do not call a demo-critical app shell accepted until the user has manually inspected the named app and first surface, or the lack of user acceptance is reported as a caveat.
