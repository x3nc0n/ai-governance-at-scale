# Deployment and validation

## Deployment sequence

1. Deploy the foundation template from `infra/foundation/azuredeploy.json`.
2. Build the shared demo image as described below.
3. Copy the foundation resource names into each scenario parameter file: `foundationManagedEnvironmentName`, `foundationContainerRegistryName`, and `foundationAiServicesName`. Scenarios 01 and 03 also require `foundationApimName`. These names are available in the foundation deployment outputs; the checked-in `replace-with-...` values are placeholders, not deployable defaults.
4. Set `foundationResourceGroupName` to the foundation group. `foundationSubscriptionId` defaults to the active deployment subscription and is used for all foundation references. Use the managed environment's region for the scenario apps. Cross-subscription deployment constraints and permissions must be validated in your target environment.
5. Deploy scenario 01 before scenario 03. For scenario 03, supply the required secure parameter `foundationApimSubscriptionKey` through a secure deployment parameter source or a Key Vault reference, never a committed plaintext file. The foundation's all-APIs APIM subscription can authorize this route. The broker stores the key as a Container App secret.

The alpha switches scenario inputs from explicit identity/registry credentials to foundation resource names. The deployment principal needs permission to read those resources, assign the user-assigned identity, retrieve ACR admin credentials, and (scenario 01) deploy the APIM API in the foundation group. Registry admin credentials are still used for image pulls; managed-identity image pulls are not implemented.

## Foundation defaults and optional toggles

The shared foundation is designed to be reproducible across a wide range of subscriptions. By default it deploys the governance plane resources (APIM, Container Apps environment, monitoring, Key Vault, AI Services, a shared Purview account, governance diagnostics, and scenario identities), but it does not create the Azure AI Foundry project or a default model deployment. Those features are optional and are controlled by the `createFoundryProject` and `deployModel` parameters. If your subscription or tenant does not yet expose the required Foundry/model deployment API path, leave these parameters at their defaults (`false`).

## Separate advanced gateway infrastructure

[Deploy the new gateway resource from Bicep/ARM](../infra/foundation/advanced/README.md), including a Deploy to Azure button targeting `x3nc0n-blog-announcement-integration` **pending merge** and a parameterized CLI example. This standalone entrypoint uses the pinned public `Microsoft.ApiManagement/aigateways@2026-09-01-preview` contract, not a new SKU on `Microsoft.ApiManagement/service`. It creates the gateway and system identity; it does not replace or modify the legacy foundation.

The minimal schema permits empty resource properties and optional backend networking. No subnet/private boundary is deployed; published delegation/API guidance discrepancies require live confirmation. Infrastructure compilation, static contract checks and ARM drift checks are distinct from provider acceptance. Resource creation is automated here, not a manual administrator prerequisite.

Tool publication, Agent 365 consent, individual-tool blocking, tool-threat policies/effective cloud Block mode, delegated client identity, backend authorization and telemetry remain separate unimplemented/unverified gates. A documented administrator checkpoint is permitted only for supported configuration interfaces not yet automated, with the ownership/readback/recreation requirements below. It is not permission to invent child resource schemas, manually create the gateway, or claim a protected alpha.

## Release profiles and evidence

All current profiles remain alpha under the [release policy](release-policy.md). Evaluate the actual selected configuration and required shared dependencies, not just product names. Direct foundation defaults enable Purview and diagnostics using preview resource APIs; bootstrap Purview selection differs as described below. No independently verified GA-only baseline is established, and disabling options alone does not prove one.

Required preview dependencies cap a consuming profile at alpha; unknown lifecycle blocks beta eligibility. All-GA dependencies allow beta consideration only with a working advertised path, repeatable deployment/runtime evidence and explicit review. Tenant setup is a separate prerequisite, not proof of implemented runtime integration. The gateway resource has its own entrypoint; no legacy foundation switch activates advanced MCP runtime governance.

Compile/offline results and historical "Validated" headings are not live deployment records. Promotion evidence must identify revision, configuration, region/SKU, image, prerequisites, reproducible deployment and runtime outcomes, limitations, teardown and reviewer decision. Missing evidence remains a blocker; this documentation change performs no cloud validation.

## Governance bootstrap

The foundation template covers the resource-group-level governance controls, but some controls remain tenant- or subscription-scoped. Use the bootstrap helper scripts for those steps:

### PowerShell

```powershell
./scripts/bootstrap-governance.ps1 -ResourceGroupName rg-aigov-foundation-demo -Location eastus2 -SubscriptionId <subscription-id> -DeployPurview -EnableDefender -PurviewAccountName pview-aigov-demo
```

### Bash

```bash
bash ./scripts/bootstrap-governance.sh rg-aigov-foundation-demo --location eastus2 --subscription-id <subscription-id> --deploy-purview --enable-defender --purview-name pview-aigov-demo
```

These scripts create or update the target resource group and deploy the full foundation (not just incremental governance settings). `-DeployPurview` / `--deploy-purview` opts into a Purview account; the scripts otherwise disable that account even though a direct foundation deployment enables it by default. Diagnostic settings are enabled by default. Account creation does not configure Purview classification, lineage, or DSPM for AI.

`-EnableDefender` / `--enable-defender` explicitly enables the paid, subscription-wide **Defender CSPM CloudPosture** plan using Azure CLI. This is a bootstrap exception to template-only resource-group changes, not activation of Defender for AI Services runtime protection or M365 tenant controls. Review scope and cost before opting in. No subscription-wide Defender plan changes occur by default. Explicit subscription arguments do not change the CLI's active subscription.

Use `-WhatIf` / `--what-if` to print commands without Azure calls or account-context changes. Native CLI failures terminate the script rather than reporting completion. The default deployment name is `main`; PowerShell `-DeploymentName` or Bash `DEPLOYMENT_NAME` can override it.

## Building the shared demo image

The scenario container apps use a shared image that is built into the foundation-managed Azure Container Registry. After the foundation deployment completes, build and push the shared image with:

```powershell
./scripts/build-and-push-demo-image.ps1
```

This script reads the foundation deployment outputs, uses Azure Container Registry build support, and publishes the `aigov-demo-app:latest` image for the scenario apps.

It accepts either the usual `main` or portal `azuredeploy` foundation deployment name. For a custom name, pass `-DeploymentName <name>`. The image must be built before deploying the scenario Container Apps.

## Alpha runtime limitations

These limitations remain in force regardless of vendor product availability or SKU selection; see [beta eligibility](release-policy.md#beta-eligibility). Scenario 04 is an alpha deterministic shell, not an implemented Snowflake/federation/MCP integration.

The first three apps implement deterministic sample guidance, not model inference, native Foundry hosting, Copilot Studio publishing, or the Agent2Agent protocol. `GET /health` is process health, not an upstream readiness check. `POST /invoke`, `/chat`, and `/` accept a JSON object with a string `message`, `prompt`, or `question`; invalid input returns 400 and bodies larger than 64 KiB return 413. Broker upstream failures return 502.

The new `/developer-kb/invoke` APIM operation requires an APIM subscription key. Container Apps still have public, unauthenticated ingress, so clients can bypass APIM by using an app's direct URL. Do not send sensitive data; caller authentication and a private/locked-down backend are prerequisites for production use. Assigned managed identities do not automatically provision Entra Agent IDs or establish end-user authorization.

Compilation, regression tests, and ARM drift checks do not prove successful deployment, diagnostics category availability, tenant readiness, or live Defender/Purview coverage. Validate those separately in an authorized target environment before a demo.

## Template-only validation rule

Azure resource validation must flow through checked-in Bicep/ARM templates and repository-owned scripts. Do not patch Azure resources by hand. If a validation run fails, update the templates or repository-owned scripts and re-run the same validation path.

**Narrow, user-approved administrator checkpoint exception:** a supported tenant/platform/preview operation may be performed manually only when its supported interface is documented and no verified repository-owned automation path is available. Before proceeding, name the accountable administrator and scope, cite the first-party procedure, record a nonsecret configuration readback/export, and document drift ownership, recreation/reapply and rollback evidence. This is not authorization for hidden APIs, guessed roles/scopes, or ad-hoc Azure resource changes. Missing evidence remains blocking. See [advanced gateway prerequisites](prerequisites/advanced-gateway.md#supported-manual-administrator-checkpoint), [client compatibility](validation/client-compatibility.md), and the [release evidence template](validation/release-evidence-template.md).

## Teardown

After validation, run the repository-owned teardown scripts to remove the validation resource groups.

### PowerShell

```powershell
./scripts/teardown.ps1 -WhatIf
./scripts/teardown.ps1
```

### Bash

```bash
bash ./scripts/teardown.sh --what-if
bash ./scripts/teardown.sh
```
