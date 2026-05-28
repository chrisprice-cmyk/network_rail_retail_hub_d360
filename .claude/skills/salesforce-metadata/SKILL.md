---
name: salesforce-metadata
description: Applies Brix-specific follow-through around Salesforce metadata work after installed Salesforce skills create or inspect artifacts. Use for source placement, app-shell bundling, permission/data/validation impacts, and CumulusCI/QX lifecycle implications for custom objects, fields, rules, record types, apps, tabs, FlexiPages, and related metadata. Also triggers on "where does this metadata live in the brix", "bundle the app shell", "force-app/main/default placement", "unpackaged/pre vs post", "what else needs to change for this metadata to ship". Do NOT use for: net-new artifact authoring (use the matching installed sf-skill such as metadata-generator, generating-custom-object, generating-custom-field, flexipage-generator, or generating-validation-rule); access/permission grant authoring (use field-level-security); flow YAML wiring (use brix-cumulusci-qx-lifecycle).
---

# Salesforce Metadata

## Workflow

1. Classify the request: inspect existing metadata, generate new metadata, refine existing metadata, or map downstream impacts.
2. For generic artifact creation or deep review, use the matching installed `sf-skills` first, then return here for Brix packaging and lifecycle follow-through.
3. Start from local source whenever possible:
   - `force-app/main/default/`
   - `unpackaged/pre/`
   - `unpackaged/post/`
   - `cumulusci.yml`
   - `qbrix_local/inputs/`
4. Use org-backed retrieve or inspection only when the user provided an org alias or the repo has a project-local target org.
5. Keep API versions aligned between `cumulusci.yml` and `sfdx-project.json`.
6. If the change introduces or changes objects, fields, record types, validation rules, tabs, apps, layouts, or FlexiPages, read `reference.md` for the compact follow-through checklist.
7. For demo-critical Lightning app shells, treat the shell as one deployable bundle:
   - `CustomApplication`
   - required tabs
   - landing/home `FlexiPage`
   - presenter permission-set `applicationVisibilities`
   - tab visibility and object access
   - post-deploy permission assignment
8. Prefer additive metadata changes that fit existing project conventions.
9. Hand access follow-through to `field-level-security`, flow wiring to `brix-cumulusci-qx-lifecycle`, data impacts to `brix-data-packaging`, and validation to `brix-validation-authoring`.
10. End with metadata touched, access impact, CumulusCI flow impact, dependent surfaces, and next verification step.

## Guardrails

- Do not invent metadata structure when the local project already shows a convention.
- Do not bypass installed `sf-skills` when the work is primarily artifact-specific implementation.
- Do not use profile-centric access changes as the default; prefer permission sets.
- Do not treat XML existence as completion when the metadata is not deployed, assigned, or visible in the launch path.
- Do not split app metadata, landing-page placement, and presenter app visibility into unrelated later tasks for demo-critical scenes.
