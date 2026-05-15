---
name: brix-cumulusci-qx-lifecycle
description: Authors and reviews CumulusCI/QX lifecycle wiring for Brix projects. Use when editing `cumulusci.yml`, adding pre-deploy/deploy/post-deploy steps, dependencies, `when` clauses, QX tasks, permission assignment, data flows, publish steps, or validation flows.
---

# Brix CumulusCI/QX Lifecycle

## Workflow

1. Identify which lifecycle phase owns the work:
   - `prepare_org`: settings, feature prep, dependency setup, pre-deploy repairs
   - `source_dependencies`: dependent brix installs
   - `deploy`: package metadata from `force-app/main/default`
   - `post_qbrix_deploy`: permissions, data, publish, favorites, org shaping
   - `deploy_qbrix_data`: data-specific loads
   - `validate_qbrix`: reusable validation
2. Keep `orgconfig_hydrate` before any step using `when` in the same flow.
3. Use `cci task info <task>` when task options are uncertain.
4. Keep brix dependencies declared under `sources` and referenced by flow, with guards such as `not org_config.is_qbrix_installed(...)`.
5. Use task placeholders intentionally:
   - `task: None` is valid in templates
   - replace it only when real reusable work exists
6. For permissions, assign permission sets, licenses, and groups in `post_qbrix_deploy` before data deployment.
7. For Experience Cloud publish steps, place repeatable post-deploy work in `post_qbrix_deploy` and keep manual Builder/Admin gaps explicit.
8. For Agentforce, deploy assets and document a manual activation checkpoint after the user is happy with the result; do not automate activation by default.
9. Run `make check-rules-sync` after rule changes. Treat `cci flow run validate_qbrix --org <alias>` as recommended when an org is available, but skippable for demo solution builds.

## Guardrails

- Do not put one-off org setup in prose when it can be encoded as a CumulusCI/QX step.
- Do not add `when` clauses before `orgconfig_hydrate`.
- Do not edit API version in only one of `cumulusci.yml` or `sfdx-project.json`.
- Do not hardcode org-specific IDs or secrets in flow options.
