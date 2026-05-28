---
name: salesforce-ux-designer
description: Applies role-based Salesforce UX design patterns for brix demos and PoCs across Lightning apps, tabs, FlexiPages, Dynamic Forms, Flow screens, LWC, utility bars, and Experience Cloud. Use when designing or reviewing visible Salesforce surfaces. Also triggers on "design this presenter path", "what should the home page look like", "Lightning app shell review", "UX critique for this demo surface", "presenter persona view". Do NOT use for: implementation/build work (use the matching installed sf-skill such as generating-lwc-components, flexipage-generator, lightning-app-generator, or layout-generator); branding/theme work on Experience Cloud (use experience-cloud-branding); narrative/story design (use demo-story-advisor).
---

# Salesforce UX Designer

## Workflow

1. Identify the user role, presenter/evaluator path, and first surface that must make sense.
2. Prefer Salesforce-native, low-maintenance UI:
   - Lightning apps and tabs for navigation
   - focused list views and record highlights
   - Dynamic Forms and conditional visibility
   - standard actions before custom buttons
   - base Lightning components and SLDS for LWC
   - Experience Cloud metadata-backed structure when sites are reusable
3. Design demo-critical app shells as a complete package:
   - app name
   - landing/home page
   - tab set
   - visible object/list/record path
   - presenter permission set
4. Keep pages scannable. Prefer fewer high-signal fields, clear actions, and credible data over dense admin-style pages.
5. For LWC, define states before implementation: empty, loading, error, success, and permission/data-limited views.
6. For Flow screens, minimize cognitive load and keep validation messages action-oriented.
7. Hand implementation to the matching installed Salesforce skill, then use local Brix skills for source placement, lifecycle wiring, and proof.

## Output Format

End with:

- target user role and presenter/evaluator path in one sentence
- first surface named (app + landing page + tab set + visible record/list)
- design recommendation per surface (app, tab, FlexiPage, Flow screen, LWC, Experience Cloud page)
- LWC states defined (empty / loading / error / success / permission-limited) when LWC is involved
- implementation handoff (which installed sf-skill owns each artifact: generating-lwc-components, flexipage-generator, lightning-app-generator, layout-generator, etc.)
- deployable-source caveats (any Builder-only or manual gap that must be called out)
- next safe step for the user

## Guardrails

- Do not design a surface that cannot be represented in deployable brix source without calling out the Builder/manual gap.
- Do not hide the launch path. A demo/PoC surface needs an obvious route from app/site entry to the target interaction.
- Do not add custom UI when a native Salesforce surface satisfies the scenario with less maintenance.
