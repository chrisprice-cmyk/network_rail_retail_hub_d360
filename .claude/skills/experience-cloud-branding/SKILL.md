---
name: experience-cloud-branding
description: Guides metadata-backed Experience Cloud branding and theming in a brix project. Use when changing community/site colors, theme references, branding sets, asset references, or CSS/theme metadata that must deploy through Salesforce DX and CumulusCI. Also triggers on "rebrand this site", "update the community theme", "swap the branding set", "apply customer colors to the experience site", "publish branding refresh". Do NOT use for: routes/views/page-shell/runtime structure (use experience-cloud-lwr); net-new site provisioning beyond branding (use experience-cloud-lwr); generic Salesforce branding outside an Experience Cloud site; Builder-only changes that cannot be retrieved as source.
---

# Experience Cloud Branding

## Supported Scope

- Metadata-backed branding edits to retrieved Experience Cloud source.
- Asset-reference updates where the asset is already available as source metadata or a static resource.
- CSS/theme tweaks that can be deployed and validated through the brix lifecycle.

Use `experience-cloud-lwr` instead for routes, views, page shell structure, runtime behavior, or DigitalExperienceBundle/LWR implementation.

## Workflow

1. Confirm the target site, site type, and whether the source of truth is metadata-backed, Builder-only, or ambiguous.
2. Use installed Salesforce Experience Cloud or metadata skills for artifact-specific guidance when needed; keep this skill focused on Brix source packaging, publish wiring, and validation.
3. Require an explicit org alias or project-local target org before retrieve, deploy, preview, or publish.
4. Retrieve and inspect the current site metadata before editing. Do not assume Aura and LWR surfaces share the same file shape.
5. Keep assets deployable:
   - static resources for reusable images/CSS/fonts
   - clear metadata references
   - no unapproved copying of external customer assets
6. Keep edits narrow and source-controlled. If Builder is the only safe source of truth, make or request one minimal Builder change, retrieve, and inspect the diff before automating more.
7. Deploy through `deploy_qbrix` or a scoped validation path, then publish/refresh the site with the appropriate CumulusCI/QX task when required.
8. Use non-browser checks where practical, then ask the user to inspect the site and confirm they are happy with the result. Note any Builder-side publish step that still needs manual confirmation.

## Output Format

End with:

- target site, site type, and source-of-truth verdict (metadata-backed / Builder-only / mixed)
- branding metadata files changed (theme, branding set, asset references, CSS) with paths
- static resources added or updated
- deploy command/flow run (or recommended) and target org
- publish/refresh status and any manual Builder step still required
- non-browser checks performed
- user acceptance status (path to inspect + cues to confirm)

## Guardrails

- Do not claim Builder-only changes are source-backed until a retrieve proves it.
- Do not create broad redesign work inside a branding skill.
- Do not leave publish state implicit after branding changes.
- Do not point metadata at assets that are not included in the brix or already guaranteed in the target org.
- Do not add browser-based verification unless the user explicitly asks for it.
