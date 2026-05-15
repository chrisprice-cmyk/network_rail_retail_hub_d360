# Salesforce Metadata Reference

Use this checklist when schema or admin metadata changes need follow-through across brix deployment, permissions, and validation.

Use installed Salesforce skills for artifact-specific implementation first. This reference covers the Brix follow-through that makes the artifact reusable in this template.

## Compact Checklist

### 1. Primary Metadata Change

Identify what is actually changing:

- object or field model
- record type or picklist behavior
- validation logic
- tab, app, layout, FlexiPage, or page composition
- access model
- CumulusCI deployment flow

Keep the change additive unless the user explicitly asks for cleanup or restructuring.

### 2. Source Of Truth

Prefer local source first:

- object and field XML
- layouts, record types, validation rules, apps, tabs, FlexiPages
- permission sets and permission set groups
- `cumulusci.yml` flow/task wiring
- org-backed inspection only with an explicit alias or project-local target org

### 3. Automation And Validation

If save-time behavior changes, inspect existing validation rules, Flow, Apex, and page behavior before adding another rule.

If the metadata needs reusable deployment behavior, wire it into the correct CumulusCI phase instead of documenting a manual step.

### 4. Page And App Shell

When users or presenters need to see the change, decide whether the page also needs:

- tab visibility
- list view
- page layout or Dynamic Forms update
- FlexiPage placement
- Lightning app navigation
- utility bar item
- Experience Cloud route/view update

For a demo-critical app shell, define the bundle:

- named `CustomApplication`
- required tabs
- landing/home `FlexiPage`
- presenter permission set with app and tab visibility
- post-deploy assignment step
- launcher path the connected user will follow

### 5. Access Follow-Through

For new or changed objects and fields, decide:

- object CRUD
- field read/edit visibility
- Apex class, Flow, custom permission, and tab access
- permission set license or permission set group needs
- assignment step in `post_qbrix_deploy`

Hand detailed grant updates to `field-level-security`.

### 6. Exit Report

Report:

- metadata changed
- validation or automation implications
- page/layout/app implications
- permission and assignment follow-through
- CumulusCI flow changes needed, usually through `brix-cumulusci-qx-lifecycle`
- data, org capability, Agentforce, or validation packaging skills needed
- next owning skill or validation step
