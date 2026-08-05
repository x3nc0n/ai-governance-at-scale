# Architecture Reference

> **One AI Estate. Four Entry Points. One Governance Plane.**

This document describes the full reference architecture for `ai-governance-at-scale`. For deployment steps and button URLs, see [deployment.md](deployment.md). For the Entra Agent ID identity model, see [concepts/agent-identity-model.md](concepts/agent-identity-model.md).

---

## High-Level Architecture

```mermaid
graph TD
    subgraph Ingress["AI Entry Points"]
        E1["Scenario 01\nEndpoint / Client AI\n(Claude Code, Cursor, Windsurf,\nVS Code extensions)"]
        E2["Scenario 02\nFoundry Hosted Agent\n(Foundry-prompted model agent)"]
        E3["Scenario 03\nCopilot Studio Agent\n(Published Power Platform agent)"]
        E4["Scenario 04\nThird-Party Agent\n(Snowflake Cortex / external platforms)"]
    end

    subgraph Governance["Governance Plane (ARM-deployed)"]
        APIM["Azure API Management\nToken limits · Rate policies\nContent safety · Observability"]
        EID["Microsoft Entra Agent ID\nBlueprint → Blueprint Principal\n→ Agent Identity → Token"]
        OBS["Log Analytics + App Insights\nCentralized audit trail"]
    end

    subgraph Backend["AI Estate (ARM-deployed)"]
        AFO["Azure AI Foundry\n(AI Services + Project)\ngpt-4.1-mini"]
        MCP["MCP Tool Layer\nM365 Work IQ MCP\nSnowflake MCP\nCustom MCP servers"]
    end

    subgraph TenantLayer["Tenant / Platform Layer (non-ARM)"]
        AG365["Agent 365\nLifecycle orchestration"]
        PUR["Microsoft Purview DSPM for AI\nData governance · Lineage"]
        DEF["Defender for AI Services\n⚠ Agent protections Public Preview"]
        M365["M365 / Work IQ\nTenant-level MCP config"]
        SF["Snowflake\nExternal platform MCP"]
    end

    E1 --> EID --> APIM
    E2 --> EID
    E3 --> EID
    E4 --> EID
    APIM --> AFO
    APIM --> MCP
    AFO --> OBS
    APIM --> OBS
    AG365 -.->|lifecycle mgmt| EID
    PUR -.->|data policy| AFO
    DEF -.->|threat detection| APIM
    M365 -.->|MCP endpoint| MCP
    SF -.->|MCP endpoint| MCP
```

---

## Foundation Layer

The foundation is the permanent shared infrastructure that all scenarios depend on. It is deployed once into `rg-aigov-foundation-demo`.

### ARM-Deployed Resources

| Resource | Azure Service | SKU | Role |
|----------|--------------|-----|------|
| AI Gateway | Azure API Management | Developer (default); Standard v2 via parameter | Central policy enforcement point for all agent traffic |
| Container Apps Environment | Container Apps Managed Environment | Consumption | Shared runtime for all four scenario apps |
| AI Services | Microsoft.CognitiveServices/accounts (AI Services multi-model) | S0 | Shared model inference |
| Foundry Project | Microsoft.CognitiveServices/accounts/projects | — | Prompt management, evaluation, catalog |
| gpt-4.1-mini | CognitiveServices model deployment | Standard, 10K TPM | Default LLM; parameterized |
| Log Analytics Workspace | Microsoft.OperationalInsights/workspaces | Per-GB | Centralized logs |
| Application Insights | Microsoft.Insights/components | — | Distributed tracing |
| Key Vault | Microsoft.KeyVault/vaults | Standard | Secret storage |
| User-Assigned Identities (×4) | Microsoft.ManagedIdentity/userAssignedIdentities | — | Per-scenario workload identity |

### APIM Policy Architecture

```
Request → APIM Inbound Pipeline
  ├── Validate JWT (Entra Agent ID token)
  ├── Rate limit (per agent identity)
  ├── Token limit (per request / sliding window)
  ├── Content safety check (Azure AI Content Safety)
  └── Route to Foundry / MCP backend

Response → APIM Outbound Pipeline
  ├── Strip internal headers
  ├── Emit token consumption metrics → App Insights
  └── Return to agent
```

> **Developer SKU limitations:** No semantic caching, no VNet integration, no SLA. Set `apimSkuName=StandardV2` for production use. Semantic caching requires Standard v2 or higher.

> **MCP governance (Public Preview):** Controlled by `enableMcpGovernance` parameter (default: `false`). When enabled, adds MCP tool-level routing and governance policies. Requires an APIM tier that supports the AI Gateway preview feature.

---

## Scenario Architecture Overviews

### Scenario 01 — Endpoint / Client AI

Developer-facing AI tools authenticate as governed agents through APIM before reaching Foundry or MCP tools.

```mermaid
sequenceDiagram
    participant Dev as Developer Tool<br/>(Claude Code / Cursor / Windsurf / VS Code)
    participant SDK as Agent 365 SDK<br/>+ Entra Agent ID
    participant APIM as Azure APIM
    participant FND as AI Foundry
    participant MCP as MCP Tools

    Dev->>SDK: Authenticate (acquire Agent Identity token)
    SDK->>APIM: API call + Bearer token (Agent Identity)
    APIM->>APIM: Validate token, apply rate/token limits
    APIM->>FND: Forward to Foundry endpoint
    FND-->>APIM: Model response
    APIM-->>Dev: Response + policy headers
    APIM->>MCP: Tool call (if agent-initiated)
    MCP-->>APIM: Tool result
```

### Scenario 02 — Foundry Hosted Agent

An agent running inside Azure AI Foundry carries its own Entra Agent Identity and routes all tool calls through APIM.

```mermaid
sequenceDiagram
    participant FND as AI Foundry Agent
    participant EID as Entra Agent ID
    participant APIM as Azure APIM
    participant SF as Snowflake MCP
    participant M365 as M365 Work IQ MCP

    FND->>EID: Acquire Agent Identity token
    FND->>APIM: Tool call + Bearer token
    APIM->>APIM: Validate token, enforce policy
    APIM->>SF: Snowflake MCP request
    SF-->>APIM: Snowflake data
    APIM->>M365: M365 MCP request
    M365-->>APIM: M365 data
    APIM-->>FND: Aggregated tool results
```

### Scenario 03 — Copilot Studio Agent

A published Copilot Studio agent carries an Entra Agent ID (post-July 2026 rollout) and routes backend AI calls through APIM to Foundry, with MCP for data tools.

```mermaid
sequenceDiagram
    participant CS as Copilot Studio Agent<br/>(published)
    participant EID as Entra Agent ID<br/>(auto-provisioned post-July 2026)
    participant APIM as Azure APIM
    participant FND as AI Foundry
    participant MCP as MCP Tools

    CS->>EID: Agent Identity token
    CS->>APIM: Backend API call + token
    APIM->>APIM: Validate Entra Agent ID, apply policy
    APIM->>FND: Foundry inference call
    FND-->>APIM: Model response
    APIM->>MCP: Tool calls
    MCP-->>APIM: Tool results
    APIM-->>CS: Response
```

### Scenario 04 — Snowflake-Led Third-Party Agent

A Snowflake Cortex agent federates its identity into Entra, acquires an Agent Identity token, and calls Azure services through APIM.

```mermaid
sequenceDiagram
    participant SF as Snowflake Cortex Agent
    participant FED as Entra Federation<br/>(Agent 365 integration)
    participant APIM as Azure APIM
    participant FND as AI Foundry
    participant M365 as M365 Work IQ MCP

    SF->>FED: OIDC/credential exchange → Entra Agent Identity token
    SF->>APIM: API call + Bearer token
    APIM->>APIM: Validate federated token, apply policy
    APIM->>FND: Foundry inference / chat call
    FND-->>APIM: Model response
    APIM->>M365: M365 MCP tool call
    M365-->>APIM: M365 data
    APIM-->>SF: Response
```

---

## Identity Architecture

All agent identities follow the five-object Microsoft Entra Agent ID lifecycle model. See [`concepts/agent-identity-model.md`](concepts/agent-identity-model.md) for the authoritative explainer.

```
Agent Identity Blueprint
  └─► Blueprint Principal  (Entra service principal; trust anchor)
        └─► Agent Identity  (child SP with Agent subtype; runtime identity)
              └─► [optional] Agent's User Account  (delegated-user context)
                    └─► OAuth 2.0 / OIDC access tokens
```

**Key rule:** The Blueprint Principal is NOT the same object as an Agent Identity. Never conflate these two objects in architecture discussions or code.

---

## Observability Architecture

All scenarios emit telemetry to the shared foundation Log Analytics workspace and Application Insights instance.

| Signal | Source | Destination |
|--------|--------|------------|
| API gateway logs (requests, latency, policy hits) | APIM | Log Analytics |
| Token consumption metrics | APIM | App Insights |
| Container App runtime logs | Container Apps | Log Analytics |
| Agent evaluation traces | AI Foundry | Log Analytics |
| Security alerts | Defender for AI Services (Preview) | Microsoft Defender portal |
| Data governance events | Purview DSPM for AI | Purview portal |

---

## Deployment Regions and Sizing

| Parameter | Default | Notes |
|-----------|---------|-------|
| Location | East US 2 (`eastus2`) | All resources |
| APIM SKU | Developer | No SLA, no semantic caching. Use `StandardV2` for production |
| Container Apps vCPU | 0.25 per scenario app | 1 vCPU total at baseline |
| gpt-4.1-mini capacity | 10K TPM | Parameterized; adjust for load |

---

## Governance, Security, and Compliance Capabilities

| Capability | Product | Status |
|-----------|---------|--------|
| Agent identity and lifecycle | Microsoft Entra Agent ID | GA |
| Agent lifecycle orchestration | Agent 365 | GA |
| API policy enforcement | Azure APIM | GA |
| Content safety | APIM + Azure AI Content Safety | GA |
| Semantic caching | APIM Standard v2+ | GA (not available on Developer SKU) |
| MCP tool governance | APIM AI Gateway tier | **Public Preview** |
| Data governance and lineage | Purview DSPM for AI | Core GA; individual features vary |
| Threat detection (agents) | Defender for AI Services | **Public Preview** |

---

## Related Documentation

- [Deployment Operations and Rules](deployment.md)
- [Entra Agent ID Prerequisites](prerequisites/entra-agent-id.md)
- [Tenant Bootstrap Guide](prerequisites/tenant-bootstrap.md)
- [Agent Identity Model (Authoritative)](concepts/agent-identity-model.md)
- [Scenario 01 — Endpoint / Client AI](../scenarios/01-endpoint-ai/README.md)
- [Scenario 02 — Foundry Hosted Agent](../scenarios/02-foundry-agent/README.md)
- [Scenario 03 — Copilot Studio Agent](../scenarios/03-copilot-studio/README.md)
- [Scenario 04 — Snowflake-Led Third-Party Agent](../scenarios/04-snowflake-agent/README.md)
