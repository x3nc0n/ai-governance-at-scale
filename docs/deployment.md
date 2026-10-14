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

The first three apps implement deterministic sample guidance, not model inference, native Foundry hosting, Copilot Studio publishing, or the Agent2Agent protocol. `GET /health` is process health, not an upstream readiness check. `POST /invoke`, `/chat`, and `/` accept a JSON object with a string `message`, `prompt`, or `question`; invalid input returns 400 and bodies larger than 64 KiB return 413. Broker upstream failures return 502.

The new `/developer-kb/invoke` APIM operation requires an APIM subscription key. Container Apps still have public, unauthenticated ingress, so clients can bypass APIM by using an app's direct URL. Do not send sensitive data; caller authentication and a private/locked-down backend are prerequisites for production use. Assigned managed identities do not automatically provision Entra Agent IDs or establish end-user authorization.

Compilation, regression tests, and ARM drift checks do not prove successful deployment, diagnostics category availability, tenant readiness, or live Defender/Purview coverage. Validate those separately in an authorized target environment before a demo.

## Template-only validation rule

All validation must flow through checked-in Bicep and ARM templates. Do not patch Azure resources by hand. If a validation run fails, update the templates or repository-owned scripts and re-run the same validation path.

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
