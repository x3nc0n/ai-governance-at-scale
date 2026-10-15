# One AI Estate. Four Entry Points. One Governance Plane.

> **ai-governance-at-scale** is a customer-facing reference architecture and VBD accelerator that demonstrates enterprise AI governance across four real-world ingress patterns — all flowing through a single governed Azure AI estate.

---

## The Problem

Every enterprise reaches the same inflection point: AI is arriving from every direction — developer tools, internal agents, business-user agents, and third-party platforms. Each entry point brings its own identity model, authentication pattern, and data access risk. Without a common governance plane, each one becomes a shadow IT vector.

This repository shows how to close that gap without rewriting every agent.

---

## The Architecture

The target architecture brings all four entry points to the same governed control plane. The current alpha demos implement only the bounded paths documented below, not every control in this diagram:

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

**Separate advanced gateway infrastructure (alpha):** [Deploy the schema-backed AI Gateway Bicep/ARM entrypoint](infra/foundation/advanced/README.md). Its Deploy to Azure button targets the current feature branch **pending merge**. It provisions the gateway resource and system identity, not tool policies, consent, threat protection or native clients; the existing HTTP foundation below is unchanged.

> ⚠️ **All scenario Deploy to Azure buttons require the foundation to be deployed first.** Foundation outputs (resource IDs, endpoint URLs, identity principal IDs) are required inputs to every scenario template.

[![Deploy Foundation to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Finfra%2Ffoundation%2Fazuredeploy.json)

> **Note:** The Deploy to Azure button above links to `infra/foundation/azuredeploy.json` in this repository. This ARM file is compiled from `infra/foundation/main.bicep` by CI on every merge. **The button works only when that ARM file is publicly readable at the raw GitHub URL.** The CI workflow in `.github/workflows/bicep-compile.yml` keeps the compiled ARM synchronized with the Bicep source. If you fork this repository, update the button URL to point to your fork.

**Foundation deploys to resource group:** `rg-aigov-foundation-demo` (default, overridable)

**Foundation provisions (ARM-deployed):**
| Azure Resource | Purpose |
|----------------|---------|
| API Management (Developer SKU) | Shared HTTP gateway with sample rate-limit and correlation policies; AI token controls are target capabilities |
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

## Release status

**All current demo profiles remain alpha.** Under the [release policy and current profile matrix](docs/release-policy.md), required preview features or deployment APIs cap a profile at alpha; unknown lifecycle blocks beta eligibility. Verified GA-only dependencies make a working, validated profile eligible for beta, not automatically beta. Independently isolated preview extensions retain their own alpha status. The current default foundation uses preview resource APIs, so a GA-only baseline has not been established.

Scenario 04 is a deterministic demo shell, not an implemented Snowflake integration. AI Gateway resource IaC is present and offline checked; end-to-end Agent 365/APIM MCP and gateway tool governance remain planned/not verified, not released capabilities. Maturity labels do not imply production support or an SLA.

---

## Scenarios

| # | Scenario | Target Entry Point (not current implementation) | Deploy |
|---|----------|------------|--------|
| 01 | [Endpoint / Client AI](scenarios/01-endpoint-ai/README.md) | Claude Code, Cursor, Windsurf, VS Code extensions → Agent 365 SDK / Entra Agent ID → APIM → Foundry / MCP | [![Deploy Scenario 01](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F01-endpoint-ai%2Finfra%2Fazuredeploy.json) |
| 02 | [Foundry Hosted Agent](scenarios/02-foundry-agent/README.md) | Foundry-prompted/hosted agent → Entra Agent ID → APIM → Snowflake MCP + M365 MCP | [![Deploy Scenario 02](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F02-foundry-agent%2Finfra%2Fazuredeploy.json) |
| 03 | [Copilot Studio Agent](scenarios/03-copilot-studio/README.md) | Published Copilot Studio agent → Entra Agent ID → APIM → Foundry backend → MCP data | [![Deploy Scenario 03](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F03-copilot-studio%2Finfra%2Fazuredeploy.json) |
| 04 | [Snowflake-Led Third-Party Agent](scenarios/04-snowflake-agent/README.md) | Snowflake Cortex agent → Agent 365 / Entra federation → APIM → Foundry / M365 MCP | [![Deploy Scenario 04](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F04-snowflake-agent%2Finfra%2Fazuredeploy.json) |

> **Button prerequisite:** Each scenario button requires `azuredeploy.json` to be publicly readable at the corresponding raw GitHub URL. CI compiles and commits these files on every merge to `main`. Do not delete or gitignore the compiled ARM files.

---

## Why Foundation First?

The foundation supplies shared gateway, runtime, identity and monitoring resources for the target governance plane. The current sample policies do not implement the full token-limit/content-safety pipeline, and public app ingress can bypass APIM. Foundry project/model deployment is optional and does not establish runtime evaluation or model use. Resource sharing is not proof of end-to-end enforcement; evaluate the selected [release profile](docs/release-policy.md) and its documented limitations.

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
  release-policy.md     # Per-profile maturity, lifecycle and promotion evidence
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

Vendor lifecycle is not implementation maturity. Except for the sourced preview profiles in the [release policy](docs/release-policy.md), exact feature/configuration lifecycle remains unverified here and must be established before beta eligibility.

| Target capability | Mechanism | Repository availability |
|-------------------|-----------|-------------------------|
| Agent identity lifecycle | Microsoft Entra Agent ID | Tenant setup guidance; runtime integration not demonstrated |
| HTTP gateway policies | Azure APIM | Sample rate-limit/correlation policies and scenario 01 subscription-key route |
| Token metering / content safety | APIM AI policies / Content Safety | Target controls, not implemented in sample policies |
| Semantic caching | APIM | Not implemented; changing SKU alone does not enable it |
| MCP server inventory/blocking | Agent 365 + supported APIM v2 | Planned integration preview, not implemented |
| Individual-tool governance | AI Gateway tier | Separate gateway resource IaC present; runtime tool governance planned/not verified |
| Classification and lineage | Purview DSPM for AI | Optional account resource is not classification or DSPM configuration |
| Threat inspection | Defender / Purview evaluation | Not implemented; bootstrap CSPM is not runtime protection |
| Agent lifecycle orchestration | Agent 365 | Tenant prerequisite/target integration, not deployed by templates |

---

## Contributing and Validation Rules

All Azure changes must flow through templates. See [`docs/deployment.md`](docs/deployment.md) for the enforced validation loop and the explicit prohibition on one-off Azure mutations.

Release claims and promotions must follow the [per-profile release policy](docs/release-policy.md); compile/offline checks alone do not establish beta eligibility.

## License and Use

This repository is a Microsoft VBD reference architecture intended for customer-facing use. See LICENSE for terms.
