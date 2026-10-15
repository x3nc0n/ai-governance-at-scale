# Advanced AI Gateway prerequisites

This is a feasibility and execution contract for the **advanced governed-tool alpha**, not evidence that a tenant is configured. **Gateway resource CRUD IaC is implemented separately:** use the [Bicep/ARM entrypoint and Deploy to Azure button](../../infra/foundation/advanced/README.md), branch-bound pending merge. The full release still requires both Agent 365 individual-tool blocking and AI Gateway tool threat protection with effective cloud **Block** mode. Resource creation, APIM v2 server controls, HTTP demos, app-only credentials, or a working MCP discovery call are not substitutes.

Planning this profile does not authorize Azure deployment, tenant consent, paid changes, platform publishing, or Snowflake access. Use synthetic, non-sensitive data. The existing HTTP baseline remains separate.

## Contract status

| Gate | Status | Verified contract | Still required to exit |
|---|---|---|---|
| **F1 — resource, tools, policy, networking** | **PARTIAL — schema-backed gateway CRUD IaC implemented; runtime gate BLOCKED** | Separate `aigateways@2026-09-01-preview` Bicep/ARM provisions a gateway, example-supported `AIGateway` SKU, system identity and tags. Required `location` and `properties` are supplied; backend/subnet is optional and create-only in the pinned schema, so the minimal template omits networking. Compile/static checks are offline only. Learn documents MCP server publication, backend authentication and per-server pre/post tool-threat policies. | Live template deployment/readback and subscription availability remain unverified. Learn's `2026-05-01-preview` API recommendation and `Microsoft.Web/serverFarms` subnet guidance conflict with the pinned schema's `Microsoft.App/environments` delegation. Confirm the network contract before adding network resources; the minimal template provides no private boundary. The verified resource CRUD schema does not define tool/policy operations. Static MCP catalog edit/export/readback, policy coexistence/recreation and anti-bypass still need verified interfaces and live evidence. These gaps hold runtime governance, not gateway resource IaC. |
| **F2 — effective cloud protection** | **BLOCKED — tenant procedure/readback absent** | Learn says the tool-threat policy is configured for a server in AI Gateway and that policy mode is configured in Microsoft Defender, not at the gateway. Block mode is enforcement; Audit/Disabled do not meet acceptance. | The cited Defender setup link is endpoint/device runtime-protection guidance, not verified administration for this cloud gateway evaluator. A tenant Defender/Purview owner must provide the authoritative cloud Block-mode procedure, applicable entitlement, policy scope, authorized role, effective-state readback, pre/post behavior and failure evidence. Do not infer the procedure or claim feature impossibility. |
| **F3 — delegated evaluation for clients** | **BLOCKED — no gateway client proof** | Threat protection requires a delegated Entra user bearer issued for AI Gateway; the gateway uses OBO. App-only service-to-service calls are unsupported. Foundry documents a hosted-agent-to-Foundry-toolbox MCP flow using the `https://ai.azure.com/.default` scope. Copilot Studio documents user-authenticated tools for supported channels. | The Foundry toolbox scope is documented for the Foundry toolbox endpoint, not as the AI Gateway audience/scope; no source establishes that it supplies the separate AI Gateway delegated token. Studio's generic user-tool connection is not proof its token targets AI Gateway. For each intended client, document exact gateway audience/scope, app registration, consent, token acquisition/refresh and error handling, then prove an actual call. Do not copy a scope from another resource or substitute app-only/UAMI credentials. |
| **F4 — environment readiness** | **BLOCKED — not assessed in a tenant** | Public-preview Learn lists East US 2 and Sweden Central, with availability dependent on subscription, cloud, capacity and enrollment. | Named owner confirms approved tenant/subscription, enrollment, region/capacity, licenses, costs, data path/residency, required permissions, Foundry model access, Studio environment, and synthetic Snowflake estate. No region example is availability evidence. |
| **F5 — policy ownership and persistence** | **BLOCKED — no live/recreation proof** | Agent 365 applies managed server/tool blocks; gateway policy configuration is separately described. | Owners must define a supported division of authority and reconcile/read back baseline, managed blocks and threat policy. Demonstrate persistence across redeploy/reapply, tool/image changes and approved recreation, or a pre-write guard that stops before weakening protection. |
| **F6 — evidence and privacy** | **BLOCKED — no live evidence** | Learn documents portal MCP request/latency/error monitoring with Application Insights; MCP OTLP export is not currently documented as available. | Privacy/operations owners approve fields, data destinations, access, retention and minimization; prove correlated, redacted client/gateway/backend evidence and a supported alternative for missing fields. Do not invent a telemetry schema. |

**Current decision:** gateway resource provisioning is implemented as a separate infrastructure milestone, not a protected implementation. Full governed-tool alpha remains on HOLD: tool/policy contracts, live network behavior, tenant readiness, client delegation and actual enforcement are not established by resource IaC or portal documentation.

## Identity boundaries

Keep these independent; one identity does not prove another:

1. **Deployment identity** creates the Azure resource and may configure its supported settings.
2. **Agent 365 administrative consent** enables its tenant-level service identity and governance operations. Tenant administrator approves and owns scope/revocation.
3. **Gateway runtime credential** is the AI Gateway runtime access key (`api-key`), distinct from the legacy APIM subscription key.
4. **Delegated evaluation identity** is a user bearer issued for AI Gateway, used for OBO evaluation. App-only/managed identity alone is not accepted.
5. **Backend identity** is the separately configured credential or identity used by the gateway to call a tool backend.

An Entra Agent ID, blueprint, Blueprint Principal, optional Agent's User Account, UAMI, Foundry project identity, or connector connection does not by itself prove the required gateway delegated evaluation token. See [Entra Agent ID prerequisites](entra-agent-id.md) and the [identity model](../concepts/agent-identity-model.md).

## Supported manual administrator checkpoint

Manual work is allowed only for a **documented, supported portal or tenant/platform operation** that lacks a verified repository-owned automation interface. This exception does not permit hidden APIs, guessed scopes/roles, ad-hoc Azure patches, or treating portal clicks as repeatable IaC.

Before an approved checkpoint is accepted, record:

- operation and exact first-party source; reason automation is unavailable or unverified;
- named accountable administrator/owner, approval and intended tenant/resource scope;
- prerequisite licenses, permissions, consent and affected resources;
- nonsecret before/after configuration readback or supported export, version/revision and timestamp;
- drift detection/ownership, supported reapply and recreation procedure, rollback/restore steps and evidence;
- protected-state and backend behavior checked after the operation.

Never store access tokens, keys, secrets, sensitive arguments/results, or raw tenant data in this record. Missing readback or owner evidence leaves the gate blocked.

## Official source ledger

Content was retrieved from first-party documentation on **2026-10-15**. These sources document routes and requirements; none is tenant execution evidence.

| Source | Relevant verified content |
|---|---|
| [Agent 365 and APIM integration](https://learn.microsoft.com/azure/api-management/agent-365) | Tenant consent route; static allowed-tool prerequisite; individual-tool/server control behavior; tier capability distinction; gateway does not automatically route clients. |
| [AI Gateway tool threat protection](https://learn.microsoft.com/azure/api-management/ai-gateway-policy-tool-threat) | AI Gateway **Policies → Add policy → Security → Agent 365 tool threat protection**; per-server pre/post configuration; delegated bearer/OBO requirement; Block vs Audit/Disabled; evaluation errors and denial semantics. The article's Defender setup link is endpoint/device runtime-protection guidance, not verified cloud evaluator administration. |
| [Manage models and tools](https://learn.microsoft.com/azure/api-management/ai-gateway-manage-models-tools) | AI Gateway **MCP servers → Add MCP server** flow; remote MCP/OpenAPI/connector backends, authentication choices, endpoint and static operation publication. |
| [AI Gateway overview](https://learn.microsoft.com/azure/api-management/ai-gateway-overview) | Preview region and availability qualifications; runtime-key boundary; management API guidance `2026-05-01-preview`; preview limitations. |
| [AI Gateway private networking](https://learn.microsoft.com/azure/api-management/ai-gateway-configure-private-networking) | Current portal Networking page and outbound subnet guidance, including `Microsoft.Web/serverFarms`; remains in tension with the separately reviewed resource specification's `Microsoft.App/environments` contract. |
| [Foundry hosted agent with a toolbox](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/use-toolbox-hosted-agent) | Foundry hosted agent can connect to a Foundry toolbox over MCP; documented scope is `https://ai.azure.com/.default` for that toolbox endpoint, not proof of the AI Gateway delegated audience/scope. |
| [Copilot Studio user authentication for tools](https://learn.microsoft.com/microsoft-copilot-studio/configure-enduser-authentication) | User-authenticated tools use a user's connection; support is channel-specific. It does not establish the token audience/scope for this AI Gateway. |
| [Pinned AI Gateway resource specification](https://github.com/Azure/azure-rest-api-specs/blob/2335fe5db98171e7a78d08e712920b1869c536ce/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/preview/2026-09-01-preview/openapi.json) | Implemented resource CRUD contract; `location` and `properties` required, backend/subnet optional and backend create-only. Create example supplies `AIGateway` SKU and system identity. No MCP tool-server or threat-policy operations. Focused static contract fixture pins this source and inherited common types; live preview discrepancies remain explicit. |

## Exit rule

Gateway resource IaC is a delivered, offline-checked milestone. The remaining F1 runtime/network evidence and F2–F6 stay blocked until their specific evidence above is recorded by the named owners and reviewed. Do not claim protected runtime controls or release acceptance from resource provisioning. Follow the [four-client compatibility matrix](../validation/client-compatibility.md) and record all mandatory acceptance in the [release evidence template](../validation/release-evidence-template.md).
