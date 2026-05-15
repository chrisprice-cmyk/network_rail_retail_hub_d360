---
name: brix-agentforce-packaging
description: Packages Agentforce agents, topics/actions, Prompt Builder assets, permissions, org capability assumptions, manual activation checkpoints, and validation into a reusable Brix after installed Agentforce skills define or build the agent artifacts. Use when Agentforce is part of a demo/PoC solution stored in this repo.
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

## Guardrails

- Do not store real prompts containing confidential customer data unless approved for demo use.
- Do not store API keys, model credentials, auth URLs, or secrets in metadata, inputs, docs, tests, or logs.
- Do not automate Agentforce activation by default. Deploy assets and ask the user to activate manually when they are happy with the result.
