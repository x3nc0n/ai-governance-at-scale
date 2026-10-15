# Release policy

Release maturity belongs to a **scenario/deployment profile**, not to the repository as a whole. A profile identifies the implemented path, selected parameters and SKUs, required shared resources, and tenant/platform prerequisites. Microsoft feature availability, our implementation maturity, validation evidence, and support expectations are separate claims.

## Release rules

| Required dependencies | Implementation and evidence | Release decision |
|---|---|---|
| Any required preview feature, integration, or deployment API | Any implemented profile | **Alpha maximum**, even if the implementation works well |
| Any unknown/unverified lifecycle | Any implemented profile | Retain **alpha**; not beta eligible until verified |
| All required dependencies verified GA | Incomplete path, inaccurate claims, or insufficient evidence | Retain **alpha** |
| All required dependencies verified GA | All beta criteria met | **Eligible for explicit beta promotion**, not automatically beta |
| Optional preview extension isolated from a verified GA-only baseline | Baseline independently meets beta criteria | Baseline may be **beta**; extension remains **alpha** |
| Not implemented | Any vendor lifecycle | **Planned/not implemented**, not a released alpha capability |

Required dependencies include the selected service features, integrations, SKUs, resource API versions, enabled options, identity flows, and tenant/platform capabilities. Evaluate their transitive closure: a required shared preview dependency caps every consuming profile at alpha. Scenario 03 also depends on scenario 01. A bundle inherits the constraints of every required profile.

A generally available product can still expose a preview feature or resource API. Conversely, a non-preview API version is not sufficient evidence that the entire selected path is GA. Unknown means unverified, not proven preview.

An optional preview extension must be unnecessary for both baseline deployment and its advertised runtime path. A heading or feature flag alone does not prove isolation. Required provisioning, consent, licensing, or runtime calls make it a dependency. Keep a separate alpha label and explicit opt-in prerequisites for the extension; do not silently enable preview behavior in a baseline advertised as GA-only.

## Beta eligibility

All of the following are required for the specific profile:

1. **An honest, working end-to-end path.** Identify the exact advertised behavior, configuration and observable result. A deterministic HTTP demo can qualify on that bounded scope without becoming a native Foundry or Copilot Studio agent.
2. **Verified GA dependencies.** Record first-party lifecycle references applicable to the selected features, SKUs, APIs, enabled options and tenant requirements. Missing evidence blocks promotion.
3. **Repeatable deployment evidence.** Reference the reviewed revision, configuration, region/SKU, image/artifact identity, prerequisites, template-driven deployment steps, observed outcome and teardown procedure. A compile or historical "Validated" heading is not a successful live deployment record.
4. **Appropriate functional evidence.** Existing compile/drift and offline tests remain useful but are distinct from live checks. Verify the advertised success and relevant failure paths. Scenario 03 needs an actual broker-to-APIM-to-scenario-01 invocation; mocked upstream success is insufficient. Hunting profiles need authorized tenant compilation/execution and representative benign validation, not just static fixtures.
5. **Accurate capability boundaries.** Separate deployed resources, implemented behavior, manual/tenant prerequisites and roadmap integrations. Creating identities, Purview accounts or diagnostic settings does not prove Agent ID provisioning, classification, threat inspection, MCP enforcement or model use.
6. **Documented access, limits and intended use.** Explain public ingress, gateway bypass, credential handling, permissions/licensing, data restrictions, platform limitations, costs and teardown where applicable. Public unauthenticated demos can only qualify for an honestly bounded synthetic/non-sensitive use case; beta does not assert a production security boundary.
7. **Explicit maintainer review and promotion.** Review the evidence against the profile and record the promotion rationale. Unknowns or unresolved failures keep it alpha. No automatic promotion, arbitrary coverage thresholds or new mandatory tooling.

Collecting missing live or lifecycle evidence is separate work. Publishing this policy does not claim that evidence exists or promote current demos.

## Current profiles

All implemented profiles below remain **alpha**. Workflow definitions and test source identify available validation, not proof of a successful run. No verified GA-only baseline or beta release is established.

| Profile / availability | Implementation maturity | Dependency lifecycle | Evidence and usage boundary |
|---|---|---|---|
| Shared foundation, current direct defaults | Alpha | Required preview resource APIs; remaining lifecycle closure unverified | Templates exist; no live evidence established by this policy change. Developer remains the APIM default. |
| [01: HTTP developer guidance](../scenarios/01-endpoint-ai/README.md), implemented | Alpha | Selected foundation plus scenario/APIM dependencies; not verified GA-only | Deterministic guidance and subscription-key HTTP API; direct app ingress bypasses APIM. |
| [02: HTTP policy review](../scenarios/02-foundry-agent/README.md), implemented | Alpha | Selected foundation plus unverified scenario dependency closure | Sample recommendations, not a native Foundry agent or live evaluator. |
| [03: HTTP broker](../scenarios/03-copilot-studio/README.md), implemented | Alpha | Selected foundation **and scenario 01** | HTTP contract/offline checks are not live-hop evidence; no published Copilot Studio or Agent2Agent integration. |
| [04: third-party demo shell](../scenarios/04-snowflake-agent/README.md), implemented shell | Alpha shell | Selected foundation plus unverified scenario dependency closure | Generic deterministic response. Snowflake, federation and MCP/APIM runtime integration are planned, not delivered. |
| [Core endpoint hunts](../scenarios/01-endpoint-ai/hunting/README.md), optional analyst pack | Alpha | MDE/XDR entitlement, telemetry and exact capability lifecycle require verification | Static checks, no live tenant execution evidence. Independent of the Azure app and preview graph extension. |
| Exposure-graph inspection, optional files in the hunting pack | Alpha | Required preview graph surface | Schema/identifier inspection only; correlation and agent attribution are not established. Does not downgrade independently runnable core hunts. |
| Optional Foundry project/model configuration, template options present | Alpha configuration | Exact enabled feature/model/API lifecycle unverified; inherits selected foundation constraints | Disabled by default. Resource creation does not prove scenario model use or native hosting. |
| Agent 365/APIM v2 MCP server-governance profile | Planned/not implemented; alpha-intended | Required integration preview | No MCP registration, tenant consent or block/unblock evidence. StandardV2 selection alone does not implement it. |
| [AI Gateway infrastructure / tool-governance profile](../infra/foundation/advanced/README.md) | Gateway IaC present (alpha); end-to-end tool governance planned/not verified | Required `aigateways@2026-09-01-preview` API and integration preview | Separate Bicep/ARM and branch-bound Deploy to Azure button; offline checks only, no live deployment proof. Individual-tool blocking, threat protection and native clients remain unimplemented; full governed-tool alpha remains on HOLD. |

### Selected foundation dependencies

The [foundation source](../infra/foundation/main.bicep) enables these resources by default in a direct deployment:

- `enablePurview=true`: `Microsoft.Purview/accounts@2023-05-01-preview`.
- `enableGovernanceDiagnostics=true`: AI Services and APIM `Microsoft.Insights/diagnosticSettings@2021-05-01-preview`.

These preview deployment APIs count as required dependencies for that selected profile, even when a parent service is GA. This does **not** classify the whole Purview or Azure Monitor product as preview. Disabling options does not by itself establish that the remaining dependency closure is GA.

The [bootstrap helpers](deployment.md#governance-bootstrap) opt into Purview separately, unlike direct foundation defaults; evaluate the actual invocation. Foundry project and model options stay disabled by default. No defaults or presets change with this policy.

For future profiles, the [Agent 365/APIM integration guide](https://learn.microsoft.com/azure/api-management/agent-365) and [AI Gateway tier overview](https://learn.microsoft.com/azure/api-management/ai-gateway-overview) document preview surfaces. Supported v2 server inventory/blocking and AI Gateway tier tool controls are different profiles. The Developer baseline is not that integration, and no `enableMcpGovernance` parameter is implemented here.

### Evidence record

For a proposed promotion, include the profile/configuration, implementation revision and image, required dependency inventory with lifecycle sources, deployment/runtime results, limitations and outstanding gaps, and reviewer decision in the change description or linked validation record. Do not include keys, tokens, sensitive prompts or tenant data. Keep this matrix current when that decision changes a profile's status.

The advanced governed-tool alpha has additional hard prerequisites and acceptance evidence: [advanced gateway prerequisites](prerequisites/advanced-gateway.md), [four-client compatibility](validation/client-compatibility.md), and the [release evidence template](validation/release-evidence-template.md). Documentation or portal instructions are not tenant execution proof; any required item not marked PASS keeps that release on HOLD.

## Stable and support boundaries

Stable requires beta criteria plus explicit maintainer review of deployment/runtime repeatability, known limitations, compatibility/upgrade expectations and ongoing maintenance for the defined reference-demo scope. Required preview or unknown dependencies remain ineligible.

Alpha, beta and stable are repository maturity labels, not Microsoft support commitments, SLAs, compliance certifications or production-readiness guarantees. Service support and preview terms must be assessed separately for the selected configuration.
