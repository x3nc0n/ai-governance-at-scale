# One AI Estate. Four Entry Points. One Governance Plane.

> **ai-governance-at-scale** is a customer-facing reference architecture and VBD accelerator that demonstrates enterprise AI governance across four real-world ingress patterns — all flowing through a single governed Azure AI estate.

---

## The Problem

Every enterprise reaches the same inflection point: AI is arriving from every direction — developer tools, internal agents, business-user agents, and third-party platforms. Each entry point brings its own identity model, authentication pattern, and data access risk. Without a common governance plane, each one becomes a shadow IT vector.

This repository shows how to close that gap without rewriting every agent.

---

## The Architecture

All four entry points terminate at the same governed control plane:

```
┌─────────────────────────────────────────────────────────┐
│                    Governance Plane                      │
│  Microsoft Entra Agent ID  │  Azure APIM  │  Purview    │
│  Agent 365 Lifecycle       │  Policy Enf. │  Defender   │
└────────────┬───────────────┴──────────────┴─────────────┘
             │  Unified identity, routing, observability
     ┌───────┴────────┐
     │  Azure AI Foundry  (AI Services + Projects)         │
     │  MCP Tool Layer  (M365 Work IQ, Snowflake, custom)  │
     └─────────────────────────────────────────────────────┘
             ▲                   ▲
   Four ingress points  →  Four scenarios
```

**Foundation first.** All four scenarios depend on a shared foundation deployment: Azure API Management, a Container Apps managed environment, Azure AI Foundry (AI Services + project), Log Analytics, Application Insights, Key Vault, and user-assigned managed identities. Deploy the foundation once, then add any combination of scenarios as independent add-ons.

---

## Foundation — Deploy First

> ⚠️ **All scenario Deploy to Azure buttons require the foundation to be deployed first.** Foundation outputs (resource IDs, endpoint URLs, identity principal IDs) are required inputs to every scenario template.

[![Deploy Foundation to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Finfra%2Ffoundation%2Fazuredeploy.json)

> **Note:** The Deploy to Azure button above links to `infra/foundation/azuredeploy.json` in this repository. This ARM file is compiled from `infra/foundation/main.bicep` by CI on every merge. **The button works only when that ARM file is publicly readable at the raw GitHub URL.** The CI workflow in `.github/workflows/bicep-compile.yml` keeps the compiled ARM synchronized with the Bicep source. If you fork this repository, update the button URL to point to your fork.

**Foundation deploys to resource group:** `rg-aigov-foundation-demo` (default, overridable)

**Foundation provisions (ARM-deployed):**
| Azure Resource | Purpose |
|----------------|---------|
| API Management (Developer SKU) | Central AI gateway with token metering, rate limits, and a sample governed API policy set |
| Container Apps Managed Environment | Shared runtime for all four scenario apps |
| Azure Container Registry | Shared registry for the scenario demo images and governance metadata app |
| Azure AI Services (S0 multi-model) | Shared model inference endpoint |
| Azure AI Foundry Project (optional) | Prompt management, evaluation, model catalog; disabled by default |
| Default model deployment (optional) | Default LLM deployment; disabled by default and can be enabled via parameters |
| Log Analytics Workspace | Centralized log aggregation |
| Application Insights | Distributed tracing and metrics |
| Azure Key Vault | Secret storage; Azure RBAC authorization |
| Microsoft Purview account | Optional account resource; classification, lineage, and DSPM configuration remain separate |
| Governance diagnostics | AI Services and APIM diagnostic settings flowing into Log Analytics for the shared governance story |
| User-Assigned Managed Identities (×4) | Per-scenario workload identities for RBAC bindings |

**Optional foundation toggles (disabled by default):**
- `createFoundryProject` — creates an Azure AI Foundry project under the shared AI Services account.
- `deployModel` — creates a default model deployment (for example, `gpt-4.1-mini`) under the shared AI Services account.

These are intentionally off by default to keep the foundation deployable on subscriptions and tenants that do not yet expose the full Foundry/model deployment path.

**Not deployed by the foundation button — tenant/platform prerequisites:**
- Microsoft Entra Agent ID (blueprints and agent identities) — see [`docs/prerequisites/entra-agent-id.md`](docs/prerequisites/entra-agent-id.md)
- Agent 365 — M365 admin center provisioning required
- Purview DSPM for AI — tenant-level; core capabilities available, some features in Public Preview
- Defender for AI Services — subscription-level toggle; agent-specific protections in **Public Preview**

**Bootstrapping the governance plane:**
- The foundation template now deploys a Purview account and governance diagnostics by default.
- Use [`scripts/bootstrap-governance.ps1`](scripts/bootstrap-governance.ps1) or [`scripts/bootstrap-governance.sh`](scripts/bootstrap-governance.sh) for the remaining tenant/subscription-level bootstrap steps such as enabling Defender for Cloud posture pricing and providing a named Purview target for the current subscription.

**Alpha implementation:** The first three scenario apps return deterministic sample guidance; scenario 03 also calls scenario 01 through APIM. They are not native Foundry/Copilot Studio agents, do not invoke an LLM, and do not demonstrate full enforcement of the architectural capabilities listed below. Public app ingress is not caller-authenticated. See [deployment parameters and limitations](docs/deployment.md); do not send sensitive data.

---

## Scenarios

| # | Scenario | Entry Point | Deploy |
|---|----------|------------|--------|
| 01 | [Endpoint / Client AI](scenarios/01-endpoint-ai/README.md) | Claude Code, Cursor, Windsurf, VS Code extensions → Agent 365 SDK / Entra Agent ID → APIM → Foundry / MCP | [![Deploy Scenario 01](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F01-endpoint-ai%2Finfra%2Fazuredeploy.json) |
| 02 | [Foundry Hosted Agent](scenarios/02-foundry-agent/README.md) | Foundry-prompted/hosted agent → Entra Agent ID → APIM → Snowflake MCP + M365 MCP | [![Deploy Scenario 02](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F02-foundry-agent%2Finfra%2Fazuredeploy.json) |
| 03 | [Copilot Studio Agent](scenarios/03-copilot-studio/README.md) | Published Copilot Studio agent → Entra Agent ID → APIM → Foundry backend → MCP data | [![Deploy Scenario 03](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F03-copilot-studio%2Finfra%2Fazuredeploy.json) |
| 04 | [Snowflake-Led Third-Party Agent](scenarios/04-snowflake-agent/README.md) | Snowflake Cortex agent → Agent 365 / Entra federation → APIM → Foundry / M365 MCP | [![Deploy Scenario 04](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F04-snowflake-agent%2Finfra%2Fazuredeploy.json) |

> **Button prerequisite:** Each scenario button requires `azuredeploy.json` to be publicly readable at the corresponding raw GitHub URL. CI compiles and commits these files on every merge to `main`. Do not delete or gitignore the compiled ARM files.

---

## Why Foundation First?

The foundation is not boilerplate — it is the governance plane. APIM enforces token limits, rate policies, and content-safety checks for every request regardless of where it originates. The shared Foundry project provides audit trails and evaluation pipelines. The Container Apps environment gives each scenario a governed runtime with consistent identity and networking. Deploying a scenario into a different environment removes those guarantees.

**Deployment sequence:**
1. Deploy foundation → note the output values (APIM gateway URL, Container Apps environment resource ID, AI Services endpoint, Key Vault name, identity principal IDs)
2. Satisfy prerequisites listed in each scenario README (Entra Agent ID, scenario-specific tenant setup)
3. Deploy one or more scenarios using the foundation output values as parameters

---

## Repository Structure

```
infra/
  foundation/           # Foundation Bicep + compiled azuredeploy.json
  modules/              # Shared Bicep modules (APIM, Container Apps, AI Services, etc.)
scenarios/
  01-endpoint-ai/       # Endpoint / client AI
  02-foundry-agent/     # Foundry hosted agent
  03-copilot-studio/    # Copilot Studio agent
  04-snowflake-agent/   # Snowflake-led third-party agent
docs/
  architecture.md       # Full architecture reference
  deployment.md         # Deployment operations, validation, and teardown rules
  prerequisites/        # Tenant-level setup guides (Entra Agent ID, bootstrapping)
  concepts/             # Identity model, terminology, governance concepts
scripts/
  teardown.ps1          # Remove all five demo resource groups (supports -WhatIf)
  teardown.sh           # Cross-platform equivalent
.github/workflows/
  bicep-compile.yml     # CI: compile Bicep → ARM, detect drift
```

---

## Unified Governance Narrative

The repo is designed to tell one customer-facing story: one governed AI estate with four entry points. The four scenarios are intentionally aligned so they can be presented together as a single architecture story: identity, policy, security, and monitoring are shared across every path.

For the full narrative, see [docs/scenario-narrative.md](docs/scenario-narrative.md).

## Governance Capabilities at a Glance

| Capability | Mechanism | Status |
|-----------|-----------|--------|
| Agent identity lifecycle | Microsoft Entra Agent ID | GA (all Entra customers); extended governance requires E7/Agent 365 |
| API gateway policy enforcement | Azure APIM (Developer SKU) | GA |
| Token metering and rate limiting | APIM AI policies | GA |
| Content safety | APIM + Azure AI Content Safety integration | GA |
| Semantic caching | APIM Standard v2 or higher | Not on Developer SKU default; upgrade via parameter |
| MCP tool governance | APIM AI Gateway tier | **Public Preview** — feature-flagged (`enableMcpGovernance=true`) |
| Data classification and lineage | Microsoft Purview DSPM for AI | Core capabilities available; individual features vary — see scenario docs |
| Threat detection | Microsoft Defender for AI Services | Agent-specific protections in **Public Preview** |
| Agent lifecycle orchestration | Agent 365 | GA |

---

## Contributing and Validation Rules

All Azure changes must flow through templates. See [`docs/deployment.md`](docs/deployment.md) for the enforced validation loop and the explicit prohibition on one-off Azure mutations.

## License and Use

This repository is a Microsoft VBD reference architecture intended for customer-facing use. See LICENSE for terms.
