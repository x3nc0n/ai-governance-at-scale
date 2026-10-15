# Advanced gateway client compatibility

This matrix is a feasibility/evidence contract, not a support statement. All four routes are **blocked/not run** until they demonstrate delegated evaluation against the actual advanced gateway. A runtime key, successful discovery, maker test, mock, or backend-only check does not pass.

[Gateway resource IaC is implemented](../../infra/foundation/advanced/README.md) as a separate offline-checked infrastructure milestone. It does not configure or verify any of these client routes; client and runtime acceptance remain blocked independently of resource provisioning.

## Required client profiles

| Profile | Required implementation boundary | Current status |
|---|---|---|
| **Endpoint MCP client — exact product/version not selected** | One named, versioned real endpoint client connects to the gateway MCP endpoint and supplies both its runtime key and supported delegated user bearer. No claim for all editors or generic clients. | **BLOCKED / NOT RUN** — candidate is unselected; exact auth/header support, audience, scopes, consent, refresh, denial rendering and live call are unverified. |
| **Native Microsoft Foundry agent** | Actual Foundry-hosted agent/model run calls the protected gateway tool; no external orchestrator silently substitutes for native hosting. | **BLOCKED / NOT RUN** — Learn documents Foundry hosted agents using a Foundry toolbox and the `https://ai.azure.com/.default` scope for that endpoint. That is not an AI Gateway audience/scope or proof of the required gateway delegated bearer. Native gateway invocation and refresh are unverified. |
| **Published Copilot Studio end-user agent** | Published agent in an approved test environment, using a supported user-authenticated tool/connection and an explicitly supported channel; capture end-user, not maker-only, execution. | **BLOCKED / NOT RUN** — Learn documents user-authenticated tools for selected channels, but does not establish a connection/token for this gateway audience/scope. Actual published-agent delegated call, supported connector/MCP shape and refresh are unverified. |
| **Snowflake read-only data adapter** | Explicitly named adapter/caller uses a least-privilege, read-only synthetic Snowflake view and bounded query/tool; do not claim native Snowflake/Cortex ingress. | **BLOCKED / NOT RUN** — no adapter, account, caller, Entra delegated flow, Snowflake role/query evidence or gateway invocation has been selected or tested. |

## Identity and configuration facts to verify per client

Record sanitized metadata only:

- client/platform product, exact version, hosting mode and supported MCP transport/version;
- published/native profile revision and end-user versus maker/runtime identity;
- gateway endpoint, static server/tool catalog revision and separate gateway runtime-key provisioning path;
- token issuer/tenant and nonsecret claim summary; exact delegated audience/resource and scopes from an authoritative source;
- client registration, required API permissions/consent, credential ownership and approved token acquisition/refresh route;
- whether the call actually carries both the gateway runtime key and delegated bearer, without logging either value;
- refresh/expiry behavior, wrong-audience/tenant and app-only rejection behavior;
- backend principal and authorization, data boundary, expected effect/result and correlation link;
- platform publication/environment/channel and adapter version if any.

Do not write credentials, bearer tokens, private claims, prompts, sensitive tool arguments/results, or customer data to evidence. Do not invent registration IDs, role IDs, scopes, API operations, or portal names.

## Required compatibility proof cases

For each profile, run in an authorized synthetic environment and correlate the client result to gateway/evaluator and backend evidence:

| Case | Expected proof |
|---|---|
| Allowed tool | Correct delegated identity and runtime key; approved tool runs exactly once; bounded result reaches the intended client. |
| Server blocked | Client presents the documented server-level denial; backend effect count is zero. |
| Individual tool blocked | MCP HTTP 200 with `result.isError: true` and denial metadata is treated as failure; blocked tool has zero backend effects while a separate allowed tool still works. |
| Threat pre-deny | Effective Block mode; denied before execution and zero backend effects. |
| Threat post-deny | Bounded disposable action runs once, result is withheld, no automatic retry and no claim that execution was reversed. |
| Identity negatives | Missing, expired, wrong-audience, wrong-tenant and app-only-only bearer do not yield a successful protected invocation; distinguish auth rejection from evaluator result. |
| Refresh and evaluator failure | Supported refresh path and controlled token/evaluator error behavior are observed; denied/withheld results are not retried. Exact supported fault method is documented before use. |
| Backend/correlation | One client call maps to the expected gateway/tool/backend request; no credentials or sensitive payloads appear in logs. |

MCP `initialize`, discovery (`tools/list`), and session-management operations are not invocation-evaluation proof. Tool threat protection docs say evaluation errors are MCP error results over HTTP 200 and post-invocation denial can follow a completed action; clients must preserve those semantics and not retry blindly.

## Source boundary

- [AI Gateway threat protection](https://learn.microsoft.com/azure/api-management/ai-gateway-policy-tool-threat): gateway delegated bearer/OBO requirement and error semantics.
- [Foundry hosted agent with a toolbox](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/use-toolbox-hosted-agent): Foundry toolbox uses `https://ai.azure.com/.default` for the **toolbox endpoint**; compatibility with AI Gateway token audience is not stated.
- [Copilot Studio user authentication for tools](https://learn.microsoft.com/microsoft-copilot-studio/configure-enduser-authentication): user connections are supported only on listed channels; no AI Gateway audience/scope contract is stated.
- See [advanced gateway prerequisites](../prerequisites/advanced-gateway.md) for the source ledger and unresolved F1–F6 gates.
