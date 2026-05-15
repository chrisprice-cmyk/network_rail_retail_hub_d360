---
name: field-level-security
description: Applies Brix-specific access follow-through after installed Salesforce permission skills define grants. Use for permission-set source placement, object/field/tab/app visibility, permission set licenses, permission set groups, and CumulusCI post-deploy assignment for brix features.
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

## Guardrails

- Do not treat object CRUD as sufficient when field visibility, tabs, or app visibility affect the user path.
- Do not leave permission assignment as a manual instruction when the brix should deploy repeatably.
- Demo brix can be permissive, but grants still need to align with the scenario and be explainable.
- Do not remove existing grants without an explicit request.
