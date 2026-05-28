---
name: brix-solution-completion
description: Checks whether a Salesforce demo/PoC solution is actually complete as a reusable Brix. Use before handoff, PR, commit, or demo readiness to verify source, lifecycle wiring, permissions, data, recommended validation, deploy proof, org assumptions, manual UI acceptance, and secret hygiene. Also triggers on "is this brix done", "completion check", "ready for handoff", "ready for demo", "PR ready", "demo readiness review". Do NOT use for: pre-completion build orchestration (use brix-solution-build); fixing failed builds or durable bug remediation (use diagnostic-refresh); authoring new validation assets (use brix-validation-authoring).
---

# Brix Solution Completion

## Completion Gates

1. Source is in the right place:
   - deployable metadata in `force-app/main/default/`
   - unmanaged pre/post metadata only in `unpackaged/pre/` or `unpackaged/post/`
   - local validation assets when they are useful and non-browser-based
   - runtime parameters in `qbrix_local/inputs/`
2. Artifact implementation used the matching installed Salesforce skills when the work was Apex, LWC, Flow, metadata, permissions, Agentforce, or integration-specific.
3. Lifecycle wiring is complete:
   - preconditions and settings in `prepare_org`
   - dependent brix in `source_dependencies`
   - post-deploy permissions, data, publish, favorites, and org shaping in `post_qbrix_deploy`
   - data work in `deploy_qbrix_data`
4. Access is repeatable:
   - permission sets are source-controlled
   - permission set licenses and groups are assigned when needed
   - app and tab visibility are included for presenter/evaluator paths
5. Data is repeatable:
   - no hardcoded org IDs, user IDs, URLs, or record IDs
   - External IDs, required inputs, cache values, or SOQL lookups handle org-specific values
6. Org capability assumptions are explicit:
   - scratch features and settings are in `orgs/dev.json` or documented
   - package and brix dependencies are declared
   - target-org license/PSL needs are recorded
7. Validation exists at the right level:
   - local tests for code
   - `validate_qbrix` is recommended when an org is available and the work is not a demo-only solution build
   - demo solution builds may skip `validate_qbrix` when speed is more valuable than reusable validation
   - UI acceptance is a manual end-user check; ask the user to inspect the target app/site/agent and confirm they are happy
8. Secret hygiene is clean:
   - no real keys, tokens, passwords, auth URLs, frontdoor URLs, private keys, org credentials, or customer-sensitive data in source, docs, tests, or artifacts.

## Output

Return `complete`, `complete with caveats`, or `not complete`, then list only the gates that remain open and the next owner.

## Guardrails

- Do not call a Brix complete because metadata exists locally.
- Do not call a demo/PoC path complete if permission assignment or data load is still only a hidden manual step.
- If `validate_qbrix`, UI acceptance, Experience Cloud publish, or Agentforce activation is skipped or manual, report it as an explicit caveat rather than a blocker by default.
