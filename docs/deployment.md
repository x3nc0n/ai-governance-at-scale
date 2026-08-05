# Deployment and validation

## Deployment sequence

1. Deploy the foundation template from `infra/foundation/azuredeploy.json`.
2. Record the shared outputs: APIM gateway URL, managed environment ID, AI Services endpoint, Key Vault name, the governed API name/path, the APIM subscription name, and the scenario identity resource IDs.
3. Deploy one or more scenario templates using those outputs as input parameters.

## Foundation defaults and optional toggles

The shared foundation is designed to be reproducible across a wide range of subscriptions. By default it deploys the governance plane resources (APIM, Container Apps environment, monitoring, Key Vault, AI Services, and scenario identities), but it does not create the Azure AI Foundry project or a default model deployment. Those features are optional and are controlled by the `createFoundryProject` and `deployModel` parameters. If your subscription or tenant does not yet expose the required Foundry/model deployment API path, leave these parameters at their defaults (`false`).

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
