---
name: experience-cloud-lwr
description: Guides Enhanced/LWR Experience Cloud site work in a brix project, including DigitalExperienceBundle retrieval, route/view edits, page shell changes, static-resource references, deploy, publish, and validation. Use for Experience Cloud structure or runtime changes, not pure branding. Also triggers on "add a route to this site", "build an LWR page", "DigitalExperienceBundle retrieve", "publish the experience site", "spin up a new community shell for the brix". Do NOT use for: pure color/theme/branding-set edits (use experience-cloud-branding); Aura ExperienceBundle sites (out of scope unless user explicitly confirms); LWC component implementation inside the site (use installed sf-skills such as generating-lwc-components); branding-only refresh after a build (use experience-cloud-branding).
---

# Experience Cloud LWR

## Supported Scope

- Enhanced/LWR site structure or runtime changes retrieved as `DigitalExperienceBundle`.
- Routes, views, theme layout wiring, page shell/layout work, navigation, and static-resource references.
- Creating or adapting a brix-owned LWR site when the source can be represented as metadata plus assets.

Use `experience-cloud-branding` for pure visual branding or theme polish on an existing site.

## Workflow

1. Confirm the request is LWR/Enhanced Experience Cloud structure, runtime behavior, replication, or DigitalExperienceBundle implementation.
2. Use installed Salesforce Experience Cloud or metadata skills for artifact-specific guidance when needed; keep this skill focused on Brix source packaging, publish wiring, and validation.
3. Require an explicit org alias or project-local target org before retrieve, deploy, preview, or publish.
4. Verify the site surface before editing:
   - Enhanced/LWR versus Aura
   - site API name used in retrieved source
   - whether unpublished Builder changes may exist
5. Retrieve current metadata first. Inspect the real folder shape under `force-app/main/default/` before assuming paths or member names.
6. Branch intentionally:
   - existing site: retrieve, diff, edit narrow metadata, deploy, publish
   - new site: establish minimal shell, route/view structure, navigation, assets, then validation
   - external reference replication: capture structure and approved assets first, then build a source-backed approximation
7. Package reusable assets as static resources and keep provenance clear.
8. Wire publish or refresh steps into `post_qbrix_deploy` with `community_publisher`, `experience_manager`, or another existing brix task when the site must be reusable after deploy.
9. Use non-browser checks where practical, then ask the user to inspect the site and confirm they are happy with the result.

## Output Format

End with:

- site name, API name, site type (Enhanced/LWR confirmed)
- DigitalExperienceBundle members touched (routes, views, theme layout, navigation) with paths
- static resources added or referenced and provenance note
- deploy and publish wiring (`post_qbrix_deploy` step or recommended flow)
- non-browser checks performed and what remains for manual user acceptance
- next safe step for the user

## Guardrails

- Do not assume DigitalExperienceBundle member names from the site label.
- Do not apply Aura ExperienceBundle habits to Enhanced/LWR sites without inspecting retrieved source.
- Do not skip publish or publish-state confirmation after route, view, navigation, or asset changes.
- Do not add browser-based verification unless the user explicitly asks for it.
- Do not assume optional third-party component packages are installed.
- If site type, source of truth, or asset provenance is unclear, stop and clarify.
