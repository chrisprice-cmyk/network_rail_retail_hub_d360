---
name: brix-agentforce-packaging
description: Packages Agentforce agents, topics/actions, Prompt Builder assets, permissions, org capability assumptions, manual activation checkpoints, and validation into a reusable Brix after installed Agentforce skills define or build the agent artifacts. Use when Agentforce is part of a demo/PoC solution stored in this repo. Also triggers on "package the agent as a brix", "wire the agent into deploy_qbrix", "agent permissions and activation", "make the agent reusable across orgs". Do NOT use for: agent design, .agent file authoring, topics/actions definition, or prompt template authoring (use installed Agentforce skills such as developing-agentforce); test spec authoring (use testing-agentforce).
---

# Brix Agentforce Packaging

## Workflow

1. Use installed Agentforce skills for agent design, `.agent`/metadata authoring, topics/actions, prompt templates, testing, and observability.
2. Return here to package the agent as a Brix:
   - source-controlled metadata under the right package path
   - org capabilities and licenses captured by `brix-org-capability-planning`
   - permissions assigned by `post_qbrix_deploy`
   - required inputs for endpoints, model choices, or environment-specific values
   - deployable setup steps wired where they can be automated
   - a manual activation checkpoint for the user after they are happy with the deployed result
3. Keep secrets out of source. Use Named Credentials, External Credentials, protected metadata, environment variables, or required inputs with safe placeholders.
4. Validate deployable assets technically where practical.
5. Add reusable validation through `brix-validation-authoring` when the agent behavior must survive template reuse.
6. End with what is packaged, what must be manually activated, and what target org capabilities are required.

## Output Format

End with:

- packaged metadata (paths under `force-app/main/default/` and any `unpackaged/*` placement)
- required inputs added (`qbrix_local/inputs/*.json`) and what each substitutes
- target org capabilities and licenses (handoff to `brix-org-capability-planning`)
- permission set assignment wired into `post_qbrix_deploy`
- manual activation checkpoint for the user
- validation assets added or deferred (handoff to `brix-validation-authoring`)
- next safe step for the user

## Guardrails

- Do not store real prompts containing confidential customer data unless approved for demo use.
- Do not store API keys, model credentials, auth URLs, or secrets in metadata, inputs, docs, tests, or logs.
- Do not automate Agentforce activation by default. Deploy assets and ask the user to activate manually when they are happy with the result.
