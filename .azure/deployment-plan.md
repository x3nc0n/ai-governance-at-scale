# Azure Deployment Plan

> **Status:** Validated

Generated: 2026-08-04T18:41:00-05:00
Last Updated: 2026-08-04T19:33:00-05:00

---

## 1. Project Overview

**Goal:** Deploy a monorepo of four Azure reference architectures for AI governance, sharing a common governed AI estate. Each scenario demonstrates governance patterns for a different AI ingress: endpoint/client AI, Azure AI Foundry hosted/prompted AI, Copilot Studio agents, and third-party agent platforms (Snowflake-led). All scenarios culminate in independent Deploy-to-Azure buttons backed by ARM compiled from Bicep.

**Path:** New Project

### Deployment Topology

```
Foundation (Deploy to Azure #1)
├── Shared Container Apps managed environment
├── APIM (Developer SKU)
├── AI Foundry / Azure AI Services + gpt-4.1-mini deployment
├── Log Analytics, App Insights, Key Vault, user-assigned identities
└── Foundation resource outputs (IDs/names consumed by scenarios)

Scenario 01 – Endpoint AI (Deploy to Azure #2, requires foundation outputs)
Scenario 02 – Foundry Agent (Deploy to Azure #3, requires foundation outputs)
Scenario 03 – Copilot Studio (Deploy to Azure #4, requires foundation outputs)
Scenario 04 – Snowflake Agent (Deploy to Azure #5, requires foundation outputs)
```

Each scenario deploys a small Container App into the shared managed environment plus scenario-specific supporting resources in its own resource group.

### Reproducible Validation and Teardown Rule

> **Hard rule:** Azure validation is template-driven. Mutating Azure through ad hoc CLI commands, portal edits, SDK calls, or other one-off interfaces is prohibited.

The validation loop is:

1. Compile the checked-in Bicep files to their checked-in ARM templates.
2. Deploy the foundation template.
3. Deploy all four scenario templates without manual resource changes.
4. Run read-only deployment and endpoint checks.
5. If a deployment or check fails, fix the Bicep, policies, application configuration, or repository scripts and redeploy.
6. After validation succeeds or is stopped, run the checked-in teardown script and confirm that all five validation resource groups are removed.

Azure CLI may be used to submit templates, read deployment state, run documented checks, and execute the repository-owned teardown script. It must not be used to patch resources into a state that the templates cannot reproduce.

### Scenarios

| # | Scenario | Description |
|---|----------|-------------|
| 1 | Endpoint / Client AI | Governance of AI consumed at the device or application edge |
| 2 | Azure AI Foundry Hosted / Prompted AI | Governance of models hosted in AI Foundry with prompt-based interaction |
| 3 | Copilot Studio Agents | Governance of agents built and deployed via Copilot Studio |
| 4 | Third-Party Agent Platforms (Snowflake) | Governance of agents on external platforms integrated into the Azure estate |

### Shared Governed AI Estate

| Service | Role | Deployment Method | Product Status |
|---------|------|-------------------|----------------|
| Agent 365 | Enterprise agent orchestration, agent lifecycle management | Non-ARM; M365 admin center / control plane | GA (per Microsoft Agent 365 overview / E7 announcement) |
| Microsoft Entra Agent ID | Identity for AI agents (see §1A) | Non-ARM; tenant-level prerequisite | GA for all Entra customers; E7/Agent 365 licensing for extended security/governance |
| Azure API Management | Central gateway, rate limiting, standard AI policies | ARM/Bicep — Developer SKU default | GA (Developer/Standard v2 AI policies) |
| APIM AI Gateway tier & MCP governance | Full MCP tool governance, advanced AI routing | Feature-flagged; document only | Public Preview |
| Azure AI Foundry | Model hosting, prompt management, evaluation | ARM/Bicep — shared AI Services resource + project | GA |
| Microsoft Purview DSPM for AI | Data governance, lineage, classification for AI | Non-ARM; tenant-level | Core capabilities available; individual preview-only expansions labeled per feature |
| Defender for AI Services | Threat detection, agent-specific protections | Subscription-level toggle | Public Preview (agent-specific protections) |
| Snowflake MCP | Third-party MCP server integration | Non-ARM; post-deploy config | External; documented from scratch |
| M365 MCP / Work IQ | Microsoft 365 tool/data surface for agents | Non-ARM; tenant-level | Per-capability status per Microsoft Learn |

---

## 1A. Microsoft Entra Agent ID — Identity Model

> **Directive:** The Entra Agent ID lifecycle is a first-class, maintained concept across all four scenarios. It must be documented, diagrammed, and referenced consistently before any Bicep or ARM implementation begins.
>
> **Sources (accessed 2026-08-04):**
> - [What is Microsoft Entra Agent ID](https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id)
> - [What are Agent Identities](https://learn.microsoft.com/en-us/entra/agent-id/what-are-agent-identities)
> - [What is Agent ID platform](https://learn.microsoft.com/en-us/entra/agent-id/what-is-agent-id-platform)
> - [Agent ID creation channels](https://learn.microsoft.com/en-us/entra/agent-id/agent-id-creation-channels)
> - [Copilot Studio: Use Entra Agent Identities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-use-entra-agent-identities)
> - [Copilot Studio: Requirements, certificates, configuration values](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-certificates-configuration-values)

### Object Lifecycle (Authoritative)

```
Agent Identity Blueprint
  └─► Agent Identity Blueprint Principal  (service principal of the blueprint)
        └─► Agent Identity  (child identity issued from the blueprint)
              └─► [optional] Agent's User Account  (delegated-user context)
                    └─► OAuth 2.0 / OIDC access tokens (runtime credential)
```

| Object | Purpose | Provisioning Channel |
|--------|---------|---------------------|
| **Agent Identity Blueprint** | Declarative template: capabilities, permissions, metadata for a class of agents | Entra admin center, Microsoft Graph, CLI/PowerShell, IaC (Bicep/Terraform via Graph) |
| **Agent Identity Blueprint Principal** | The Entra service principal instantiated from the blueprint; trust anchor for child identities | Created automatically by managed experiences (portal, Copilot Studio); must be created explicitly when blueprint is created via Graph/CLI/IaC |
| **Agent Identity** | Individual runtime identity for a specific agent instance (Entra service principal with Agent subtype) | Issued by the platform from the blueprint principal |
| **Agent's User Account** (optional) | User-like account paired one-to-one with an Agent Identity when a workload requires access to systems designed for users | Entra admin center or Microsoft Graph with the documented Agent ID roles and permissions |
| **Access Tokens** | OAuth 2.0 / OIDC tokens presented at runtime | Platform-specific application-only or delegated flow; exact grant and claims must be documented per scenario |

### Service Principal Mental Model vs. Agent ID Object Model

> **⚠️ MANDATORY SECTION — must be prominently included in `docs/concepts/agent-identity-model.md`**

Copilot Studio documentation describes Entra Agent IDs as "Microsoft Entra service principals with an Agent subtype." This is architecturally accurate at the Entra directory layer — an Agent Identity *is* a service principal. However, the **Agent ID object model** adds hierarchy and lifecycle semantics that a bare service principal does not have:

| Concept | Service Principal mental model | Agent ID object model |
|---------|-------------------------------|----------------------|
| Template / class | App Registration | Agent Identity Blueprint |
| Trust anchor | Service Principal (from app reg) | Agent Identity Blueprint Principal |
| Instance identity | (same SP, or multi-tenant SP) | Agent Identity (child SP with Agent subtype) |
| User delegation | OBO token | Agent's User Account + OBO token |

**Key distinction:** The Blueprint Principal is NOT the same object as an Agent Identity. The Blueprint Principal is the parent trust anchor created from the Blueprint; individual Agent Identities are child service principals issued from it. Documentation must never conflate these two objects.

### Terminology Drift Checks (Execution-Phase Verification)

The following terms must be validated against current Microsoft documentation at execution time and reconciled if naming has evolved:

| Term in this plan | Check against | Action if drift detected |
|-------------------|---------------|--------------------------|
| Agent Identity Blueprint | Entra Agent ID docs, Graph API schema | Update plan + all generated docs |
| Agent Identity Blueprint Principal | Creation-channel docs, Graph API | Update plan + all generated docs |
| Agent Identity | What-are-agent-identities page | Update plan + all generated docs |
| Agent's User Account | Agent ID platform page | Update plan + all generated docs |
| Agent subtype | Copilot Studio admin docs | Update plan + all generated docs |

### Creation Channels & Required Permissions

| Channel | Blueprint created | Blueprint Principal | Notes |
|---------|-------------------|---------------------|-------|
| Entra admin center | Manual | Auto-created | Portal UX handles both |
| Microsoft Graph API | Explicit API call | Must be created separately | Blueprint: `AgentIdentityBlueprint.Create`; identities: `AgentIdentity.Create.All`, `AgentIdentity.ReadWrite.All`, or `AgentIdentity.ReadWrite.ManagedBy`, depending on actor and ownership |
| CLI / PowerShell | Explicit command | Must be created separately | Uses the same Entra roles and Microsoft Graph permissions as the underlying API |
| IaC (Bicep/ARM or Terraform through Graph-backed tooling) | Explicit resource or API operation | Must be created separately | Creation is documented as supported through IaC channels; exact resource types and Deploy to Azure compatibility must be validated before implementation |
| Copilot Studio | Auto on first agent | Auto-created (Copilot Studio blueprint + principal) | Post-July 2026 rollout |
| Azure AI Foundry | Listed in creation-channel docs | Implementation details are execution-phase verification | Foundry-to-Agent-ID integration path |

**Roles:** Agent ID Developer, Agent ID Administrator (per creation-channel docs).

### Copilot Studio Integration

- After the July 2026 rollout, Copilot Studio automatically creates Entra Agent IDs for new agents.
- Existing Copilot Studio agents continue using app registrations pending migration.
- First agent creation triggers the Copilot Studio blueprint and its corresponding blueprint principal.
- Scenario 3 documentation must distinguish between legacy (app registration) and current (Agent ID) paths.

### Availability & Licensing

- **Entra Agent ID** is available to all Entra customers (all SKUs).
- **Extended security and governance capabilities** (advanced lifecycle management, compliance controls) require E7 or Agent 365 licensing.

### Automation Boundary

> **Decision:** Do NOT claim that Deploy to Azure can fully automate Agent ID provisioning until execution-phase validation proves a specific Microsoft.Graph Bicep resource type or ARM extension supports it. Plan a separate optional tenant-bootstrap artifact (PowerShell/Graph script) and treat identity provisioning as prerequisite/manual by default.

### Planned Documentation Deliverables

| Deliverable | Scope | Status |
|-------------|-------|--------|
| `docs/concepts/agent-identity-model.md` | Authoritative explainer: lifecycle (5-object model), object relationships, SP mental model section, terminology glossary, drift changelog | ⏳ Planning |
| `docs/concepts/agent-identity-terminology-changelog.md` | Source-of-truth for terminology changes detected during execution | ⏳ Planning |
| Architecture diagram (Excalidraw) | Visual: Blueprint → Blueprint Principal → Agent Identity → User Account → Tokens with provisioning/runtime boundary | ⏳ Planning |
| Per-scenario identity mapping table | Shows how each scenario's agents map to the lifecycle model | ⏳ Planning |
| `docs/prerequisites/entra-agent-id.md` | Tenant-level steps: blueprint creation, principal provisioning, role assignments, licensing | ⏳ Planning |
| `docs/prerequisites/tenant-bootstrap.md` | Optional PowerShell/Graph script for automated tenant-level identity setup | ⏳ Planning |
| Change maintenance runbook section | How to rotate, revoke, re-provision agent identities post-deploy | ⏳ Planning |

### Cross-Scenario Usage

| Scenario | Agent Type | Identity Model Usage |
|----------|-----------|---------------------|
| 1 — Endpoint/Client AI | Client-side AI (e.g., Copilot extensions) | Agent Identity presented to APIM gateway for policy enforcement |
| 2 — AI Foundry Hosted | Foundry-deployed model agent | Agent Identity scoped to Foundry workspace; runtime tokens for tool calls |
| 3 — Copilot Studio | Copilot Studio agent | Entra Agent ID (post-July 2026); legacy app-reg path documented for migration |
| 4 — Third-Party (Snowflake) | External platform agent | Federated identity or credential exchange; Blueprint Principal as trust anchor |

### Validation / Acceptance Criteria

- [ ] All documentation uses the five-object lifecycle terminology consistently
- [ ] "Service principal mental model vs. Agent ID object model" section exists and is prominent
- [ ] Diagram clearly separates provisioning-time vs. runtime identity flows
- [ ] Each scenario README cross-references the shared identity model doc
- [ ] Prerequisites section lists exact Entra portal / PowerShell / Graph API steps
- [ ] Terminology drift changelog is initialized and process documented
- [ ] Blueprint Principal is never conflated with Agent Identity in any doc

---

## 2. Requirements

| Attribute | Value |
|-----------|-------|
| Classification | Reference Architecture / POC |
| Scale | Medium (four scenarios, shared services) |
| Budget | Cost-Optimized (reference/demo workloads) |
| **Subscription** | SC-OnlineLZ-00 (`6a170127-f4d5-4706-af95-e957af9cbcff`) |
| **Tenant** | `ef4ecf0b-a160-444b-a405-ce3bf1f98752` |
| **Location** | East US 2 (`eastus2`) |
| **Deployment User** | `jospaid@MngEnvMCAP643271.onmicrosoft.com` |

---

## 3. Components Detected

| Component | Type | Technology | Path |
|-----------|------|------------|------|
| (repo is currently empty — no application code detected) | — | — | — |

> The repository contains only Squad orchestration files and GitHub Copilot instructions. No application source, infrastructure code, or configuration has been committed yet.

---

## 4. Recipe Selection

**Selected:** Bicep

**Rationale:** User requirement explicitly states "Deploy to Azure button backed by deployable ARM generated from Bicep." Bicep is the native Azure IaC language that compiles to ARM templates. Each Deploy to Azure button targets a compiled `azuredeploy.json` on the repo's default branch.

---

## 5. Architecture

**Stack:** Azure Container Apps (shared managed environment, four small scenario apps)

### Resource Group Strategy

| Resource Group (parameterized default) | Contents |
|----------------------------------------|----------|
| `rg-aigov-foundation-demo` | APIM, Container Apps environment, AI Foundry/AI Services, Log Analytics, App Insights, Key Vault, user-assigned identities |
| `rg-aigov-endpoint-ai-demo` | Scenario 01 Container App + scenario-specific resources |
| `rg-aigov-foundry-agent-demo` | Scenario 02 Container App + scenario-specific resources |
| `rg-aigov-copilot-studio-demo` | Scenario 03 Container App + scenario-specific resources |
| `rg-aigov-snowflake-agent-demo` | Scenario 04 Container App + scenario-specific resources |

All names are parameters with these defaults. Users may override via Bicep parameters.

### Service Mapping

| Component | Azure Service | SKU / Config | Notes |
|-----------|---------------|--------------|-------|
| AI Gateway (shared) | API Management | **Developer** (default); Standard v2 parameterized for production | Developer lacks semantic caching, VNet integration, and SLA. AI Gateway preview tier is NOT default. |
| Container Apps environment (shared) | Container Apps Managed Environment | Consumption plan | Single shared environment; four scenario apps target ≤1 vCPU total at baseline |
| Scenario Container Apps (×4) | Container Apps | Consumption (0.25 vCPU / 0.5 GiB each) | Small demo workloads |
| AI Services (shared) | Microsoft.CognitiveServices/accounts | S0 (AI Services multi-model) | Shared Foundry resource |
| AI Foundry Project | Microsoft.CognitiveServices/accounts/projects | — | Foundry project created under the shared AI Services account |
| gpt-4.1-mini deployment | CognitiveServices model deployment | Standard, capacity 10 | Parameterized; optional |
| Monitoring | Log Analytics + Application Insights | Per-GB / free tier | Foundation RG |
| Secrets | Key Vault | Standard | Foundation RG |
| Identity | User-Assigned Managed Identity | — | Per-scenario; used for RBAC bindings |

### APIM Policy Approach

- **Default deployable route:** APIM AI policies supported by the selected tier, including token limits, metrics, content-safety integration, and rate limiting. Semantic caching is enabled only for Standard v2 or another verified supporting tier.
- **Developer SKU limitations (documented):** No semantic caching, no VNet integration, no SLA.
- **MCP governance capabilities (public preview):** Feature-flagged in Bicep (`enableMcpGovernance` parameter, default `false`). Execution-phase validation will map each preview capability to the APIM tiers that support it; the plan does not assume the separate AI Gateway preview tier is mandatory.
- **Production upgrade path:** Parameter `apimSkuName` defaults to `Developer`; set to `StandardV2` for production with semantic caching and VNet.

### External / Existing Resource Integration

| Resource | Default Behavior | Override |
|----------|-----------------|----------|
| Snowflake MCP endpoint | Not provisioned; documented from scratch; accept endpoint URL + auth as secure parameters or post-deploy config | Parameter `snowflakeMcpEndpoint` + Key Vault secret |
| M365/Work IQ MCP endpoints | Not provisioned; prerequisite/manual | Parameter `m365McpEndpoint` for post-deploy wiring |
| Existing APIM / Foundry / etc. | Net-new dedicated demo resources | Parameters to supply external resource IDs if user has existing resources |

### Prerequisites / Manual Configuration (Non-ARM)

| Item | Reason | Status Guardrail |
|------|--------|-----------------|
| Microsoft Entra Agent ID (blueprint + identities) | Tenant-level; no confirmed ARM resource type (see §1A) | GA (all Entra customers); extended capabilities require E7/Agent 365 |
| Agent 365 | M365 admin-center / control plane provisioned | GA |
| Copilot Studio agents | Power Platform provisioned; auto-creates Agent IDs post-July 2026 | GA (Copilot Studio); Agent ID integration GA |
| M365 MCP / Work IQ | Tenant-level M365 configuration | Per-capability per Microsoft Learn |
| Snowflake MCP server | External platform; documented from scratch; endpoint + auth accepted as parameters | External |
| Purview DSPM for AI | Tenant-level; policies non-ARM | Core available; preview-only expansions individually labeled |
| Defender agent-specific protections | Subscription-level toggle | Public Preview |

> **Assumption:** Do not assume any tenant services are pre-enabled. All prerequisites documented as setup-from-scratch.

---

## 6. Provisioning Limit Checklist

> **Source:** Quota checks performed by `jospaid@MngEnvMCAP643271.onmicrosoft.com` against subscription SC-OnlineLZ-00 (`6a170127-f4d5-4706-af95-e957af9cbcff`) in East US 2 on 2026-08-04.

### Subscription-Level Quotas

| Resource | Current Usage | Deploying | Total After | Quota Limit | Source | Status |
|----------|--------------|-----------|-------------|-------------|--------|--------|
| Resource Groups | 27 | 5 | 32 | 980 | ARM subscription limit | ✅ Within limits |
| Container Apps Managed Environments (eastus2) | 4 | 1 | 5 | 50 | `az quota` — ManagedEnvironmentCount, 2026-08-04 | ✅ Within limits |
| Azure OpenAI S0 Accounts (eastus2) | 4 | 1 | 5 | 30 | Microsoft.CognitiveServices usage API — OpenAI.S0.AccountCount, 2026-08-04 | ✅ Within limits |
| gpt-4.1-mini Standard capacity (eastus2) | 0 | 10 units | 10 | 5,000 units | Cognitive Services usage API — OpenAI.Standard.gpt4.1-mini, 2026-08-04 | ✅ Within limits |

### Per-Resource-Group Limits (New Dedicated RGs)

| Resource Type | Current in New RG | Deploying | Total | Limit | Notes |
|---------------|-------------------|-----------|-------|-------|-------|
| Microsoft.ApiManagement/service | 0 | 1 | 1 | 800 per type per RG | Service-specific runtime limits validated separately |
| Microsoft.CognitiveServices/accounts/projects | 0 | 1 | 1 | 800 per type per RG | AI Foundry project under the shared account |
| Microsoft.App/containerApps | 0 | 1 per scenario RG | 1 | 800 per type per RG | One app per scenario RG |
| Microsoft.App/managedEnvironments | 0 | 1 | 1 | 800 per type per RG | Foundation RG |
| Microsoft.Insights/components | 0 | 1 | 1 | 800 per type per RG | Foundation RG |
| Microsoft.OperationalInsights/workspaces | 0 | 1 | 1 | 800 per type per RG | Foundation RG |
| Microsoft.KeyVault/vaults | 0 | 1 | 1 | 800 per type per RG | Foundation RG |
| Microsoft.ManagedIdentity/userAssignedIdentities | 0 | 4 | 4 | 800 per type per RG | Foundation RG; one per scenario |
| Microsoft.CognitiveServices/accounts | 0 | 1 | 1 | 800 per type per RG | Foundation RG |

> ARM limit of 800 resources per resource type per resource group applies to all above. Service-specific runtime limits (connections, throughput, etc.) are validated separately during execution.

### APIM Operations Capacity

| Metric | Planned | Limit (Developer SKU) | Source |
|--------|---------|----------------------|--------|
| API operations | ~8 | 3,000 per instance | [Azure APIM service limits](https://learn.microsoft.com/en-us/azure/api-management/service-limits) |

### Container Apps Consumption-Core Quota (Runtime Acceptance Check)

> Container Apps environment-scoped consumption-core quota does not exist until the managed environment is deployed. This is handled as a **mandatory post-foundation deployment check**:
>
> 1. After foundation deployment succeeds, run: `az containerapp env list-usages --name <env-name> --resource-group rg-aigov-foundation-demo`
> 2. Verify available vCPU cores ≥ 1 (four demos designed for 0.25 vCPU each = 1 vCPU total baseline).
> 3. If insufficient, scale down individual app CPU or request quota increase before deploying scenarios.
>
> This is a runtime acceptance check by design, not a gap in planning.

### Overall Checklist Status: ✅ Within known limits

---

## 7. Execution Checklist

### Phase 1: Planning
- [x] Analyze workspace (empty repo — New Project)
- [x] Gather requirements (from user intent + confirmed decisions)
- [x] Confirm subscription and location (SC-OnlineLZ-00, eastus2)
- [x] Prepare resource inventory
- [x] Fetch quotas and validate capacity (all within limits)
- [x] Scan codebase (no application code present)
- [x] Select recipe (Bicep)
- [x] Plan architecture (finalized)
- [x] **User approved this plan** — 2026-08-04

### Phase 2: Execution
- [ ] Research components (load references, invoke skills)
- [ ] Generate infrastructure files (foundation Bicep + per-scenario Bicep)
- [ ] Compile ARM templates (azuredeploy.json per deployable unit)
- [ ] Apply APIM policies (standard AI policies; MCP governance feature-flagged)
- [ ] Generate application configuration (Container App manifests)
- [ ] Generate Deploy-to-Azure buttons (one per deployable unit)
- [ ] Generate documentation (agent identity model, prerequisites, tenant bootstrap)
- [ ] Generate teardown scripts with exact resource-group targeting, confirmation, and dry-run support
- [ ] Set up CI to compile Bicep → ARM and detect drift
- [ ] ⛔ Update plan status to "Ready for Validation"

### Phase 3: Validation
- [x] Invoke azure-validate skill
- [x] All validation checks pass
- [x] Update plan status to "Validated"

### Phase 4: Deployment
- [ ] Invoke azure-deploy skill (foundation first)
- [ ] Post-foundation acceptance check (Container Apps env quota)
- [ ] Deploy scenarios (in any order after foundation)
- [ ] Make any required fixes only in checked-in templates/scripts, then redeploy
- [ ] Run repository teardown script after validation
- [ ] Verify all five validation resource groups are removed
- [ ] Update plan status to "Deployed"

---

## 9. Files to Generate

| File | Purpose | Status |
|------|---------|--------|
| `.azure/deployment-plan.md` | This plan | ✅ |
| `infra/foundation/main.bicep` | Foundation deployment: APIM, Container Apps env, AI Services, Foundry project, monitoring, KV, identities | ⏳ |
| `infra/foundation/azuredeploy.json` | Compiled ARM for foundation Deploy to Azure button | ⏳ |
| `infra/modules/apim.bicep` | Shared APIM module (Developer default, Standard v2 param) | ⏳ |
| `infra/modules/container-apps-env.bicep` | Shared managed environment module | ⏳ |
| `infra/modules/ai-services.bicep` | AI Services account + gpt-4.1-mini deployment | ⏳ |
| `infra/modules/foundry-project.bicep` | AI Foundry project linked to AI Services | ⏳ |
| `infra/modules/monitoring.bicep` | Log Analytics + App Insights | ⏳ |
| `infra/modules/keyvault.bicep` | Key Vault + Azure RBAC authorization | ⏳ |
| `infra/modules/identity.bicep` | User-assigned managed identities | ⏳ |
| `infra/modules/container-app.bicep` | Reusable Container App module (used by all scenarios) | ⏳ |
| `scenarios/01-endpoint-ai/infra/main.bicep` | Scenario 01 Bicep | ⏳ |
| `scenarios/01-endpoint-ai/infra/azuredeploy.json` | Compiled ARM for scenario 01 button | ⏳ |
| `scenarios/01-endpoint-ai/README.md` | Scenario 01 overview + Deploy to Azure button | ⏳ |
| `scenarios/02-foundry-agent/infra/main.bicep` | Scenario 02 Bicep | ⏳ |
| `scenarios/02-foundry-agent/infra/azuredeploy.json` | Compiled ARM for scenario 02 button | ⏳ |
| `scenarios/02-foundry-agent/README.md` | Scenario 02 overview + Deploy to Azure button | ⏳ |
| `scenarios/03-copilot-studio/infra/main.bicep` | Scenario 03 Bicep | ⏳ |
| `scenarios/03-copilot-studio/infra/azuredeploy.json` | Compiled ARM for scenario 03 button | ⏳ |
| `scenarios/03-copilot-studio/README.md` | Scenario 03 overview + Deploy to Azure button | ⏳ |
| `scenarios/04-snowflake-agent/infra/main.bicep` | Scenario 04 Bicep | ⏳ |
| `scenarios/04-snowflake-agent/infra/azuredeploy.json` | Compiled ARM for scenario 04 button | ⏳ |
| `scenarios/04-snowflake-agent/README.md` | Scenario 04 overview + Deploy to Azure button | ⏳ |
| `docs/concepts/agent-identity-model.md` | Authoritative explainer: 5-object lifecycle, SP mental model section, glossary | ⏳ |
| `docs/concepts/agent-identity-terminology-changelog.md` | Terminology drift tracking | ⏳ |
| `docs/diagrams/agent-identity-lifecycle.excalidraw` | Provisioning vs. runtime identity flow diagram | ⏳ |
| `docs/prerequisites/entra-agent-id.md` | Tenant-level Entra Agent ID enablement steps | ⏳ |
| `docs/prerequisites/tenant-bootstrap.md` | Optional PowerShell/Graph script for automated identity setup | ⏳ |
| `scripts/teardown.ps1` | Remove the four scenario resource groups, then the foundation resource group; supports `-WhatIf` and explicit confirmation | ⏳ |
| `scripts/teardown.sh` | Cross-platform equivalent of the PowerShell teardown script | ⏳ |
| `.github/workflows/bicep-compile.yml` | CI: compile Bicep → ARM, detect drift between .bicep and .json | ⏳ |

### Deploy to Azure Button URLs (Template)

Each button targets the scenario's compiled ARM template on the default branch:

```
Foundation:  https://portal.azure.com/#create/Microsoft.Template/uri/{encoded-raw-url}/infra/foundation/azuredeploy.json
Scenario 01: https://portal.azure.com/#create/Microsoft.Template/uri/{encoded-raw-url}/scenarios/01-endpoint-ai/infra/azuredeploy.json
Scenario 02: https://portal.azure.com/#create/Microsoft.Template/uri/{encoded-raw-url}/scenarios/02-foundry-agent/infra/azuredeploy.json
Scenario 03: https://portal.azure.com/#create/Microsoft.Template/uri/{encoded-raw-url}/scenarios/03-copilot-studio/infra/azuredeploy.json
Scenario 04: https://portal.azure.com/#create/Microsoft.Template/uri/{encoded-raw-url}/scenarios/04-snowflake-agent/infra/azuredeploy.json
```

---

## 10. Execution-Phase Verification Tasks

> These are non-blocking unknowns converted from former open questions. They do not block plan approval but must be resolved during Phase 2 execution.

| # | Verification Task | Resolution Approach |
|---|-------------------|---------------------|
| V1 | Confirm whether `Microsoft.Graph` Bicep extension can create Agent Identity Blueprints / Blueprint Principals | Test in execution; if unsupported, tenant-bootstrap script remains the only path |
| V2 | Validate Foundry-to-Agent-ID integration path (listed in creation-channel docs) | Attempt during Scenario 02 implementation; document findings |
| V3 | Confirm exact Graph API permissions for Agent ID Developer/Administrator roles | Validate against live Graph during tenant-bootstrap script development |
| V4 | Post-foundation Container Apps consumption-core quota acceptance check | Run `az containerapp env list-usages` after foundation deploy |
| V5 | Validate standard APIM AI policies function correctly on Developer SKU (subset without semantic caching) | Test during Scenario 01 implementation |
| V6 | Confirm Copilot Studio Agent ID auto-creation behavior in test tenant | Manual verification during Scenario 03 |
| V7 | Validate Snowflake MCP endpoint connectivity pattern with APIM backend | Test during Scenario 04 with documented auth parameters |
| V8 | Terminology drift check: compare plan terminology against live Microsoft Learn pages | First check at execution start; repeat before docs finalization |
| V9 | Prove teardown is complete and safely scoped | Dry-run both teardown scripts, execute one after validation, then verify the five exact resource groups no longer exist |
| V10 | Prove no one-off Azure mutations were required | Review the validation command log; only template deployments, read-only checks, and repository teardown commands may mutate lifecycle state |

---

## 7. Validation Proof

| Check | Command | Result |
|---|---|---|
| Bicep compilation | `az bicep build --file infra/foundation/main.bicep` and the four scenario entrypoint Bicep files | Passed; generated `azuredeploy.json` files for the foundation and all four scenarios |
| Template validation | `az deployment group validate --resource-group rg-aigov-foundation-demo --template-file infra/foundation/azuredeploy.json --parameters @infra/foundation/main.parameters.json` and the equivalent commands for the four scenario templates | Passed for foundation and all four scenario templates |
| Linting | `az bicep lint --file ...` for each template | Passed; only non-blocking Bicep type warnings remained for the `Microsoft.CognitiveServices/accounts/projects` resource |
| Teardown dry run | `pwsh -NoProfile -File .\scripts\teardown.ps1 -WhatIf` | Passed; listed all five validation resource groups |

## 8. Next Steps

> **Current: Approved — Phase 2 execution**

**→ Next action: Generate the foundation, scenario templates, documentation, teardown scripts, and CI workflow.**

After approval, execution proceeds:
1. Generate foundation Bicep + compile ARM
2. Generate scenario Bicep modules + compile ARM
3. Generate documentation (agent identity model, prerequisites, tenant bootstrap)
4. Generate and dry-run teardown scripts
5. Set up CI workflow
6. Deploy foundation → acceptance check → deploy scenarios
7. Fix only repository artifacts and redeploy as needed
8. Tear down all validation resources and verify cleanup
