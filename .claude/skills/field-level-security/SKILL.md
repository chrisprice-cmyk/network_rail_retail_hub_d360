---
name: field-level-security
description: Applies Brix-specific access follow-through after installed Salesforce permission skills define grants. Use for permission-set source placement, object/field/tab/app visibility, permission set licenses, permission set groups, and CumulusCI post-deploy assignment for brix features. Also triggers on "assign this permset post-deploy", "make sure the demo user can see X", "wire permission set assignment into post_qbrix_deploy", "tab/app visibility for the presenter", "permission set group for this brix", "field is hidden — fix access". Do NOT use for: net-new permission set authoring (use installed sf-skill generating-permission-set); profile changes (template ignores retrieved profiles by default); schema/object/field design (use metadata-generator); broad org sharing model design.
---

# Field Level Security

## Workflow

1. Confirm the primary job is access follow-through, not schema design. Use installed Salesforce permission/metadata skills first when grant design or artifact generation is the main job.
2. Identify the changed surfaces:
   - objects and fields
   - Apex classes or flows
   - tabs and Lightning apps
   - FlexiPages or Experience Cloud surfaces
   - custom permissions or permission set groups
3. Prefer permission sets over profiles. This template ignores retrieved profiles by default, so profile-centric access is usually not reusable brix source.
4. Add access additively unless the user explicitly asks to remove grants.
5. For demo-critical launch paths, update the presenter permission set in the same pass for:
   - object and field permissions
   - class/flow/custom permission grants
   - tab visibility
   - `applicationVisibilities`
6. Ensure `post_qbrix_deploy` assigns the permission sets, permission set licenses, or permission set groups needed for the demo/PoC user.
7. Report changed access metadata, deployment assignment impact, and verification needed.

## Output Format

End with:

- access metadata changed (permission sets, permission set groups, PSLs) with paths
- coverage matrix per surface (object, field, tab, app, class/flow, custom permission)
- `post_qbrix_deploy` assignment step wired (task name + target user/permission set)
- demo user and permission context (which user the presenter logs in as, what they can now reach)
- verification needed and handoff (e.g., `salesforce-ui-verification` for visible UI access, `salesforce-deploy` for assignment proof)
- residual gaps (anything left manual or unverified)
- next safe step for the user

## Guardrails

- Do not treat object CRUD as sufficient when field visibility, tabs, or app visibility affect the user path.
- Do not leave permission assignment as a manual instruction when the brix should deploy repeatably.
- Demo brix can be permissive, but grants still need to align with the scenario and be explainable.
- Do not remove existing grants without an explicit request.
