# Advanced gateway infrastructure — alpha

[![Deploy gateway infrastructure to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fx3nc0n-blog-announcement-integration%2Finfra%2Ffoundation%2Fadvanced%2Fazuredeploy.json)

**Branch-bound pending merge:** this button targets `x3nc0n-blog-announcement-integration`, not `main`. It becomes available when that branch's [compiled template](https://raw.githubusercontent.com/x3nc0n/ai-governance-at-scale/x3nc0n-blog-announcement-integration/infra/foundation/advanced/azuredeploy.json) is pushed. Retarget the button and regression test together after merge.

This separate resource-group entrypoint provisions **one AI Gateway resource**, `Microsoft.ApiManagement/aigateways@2026-09-01-preview`, with the example-supported `AIGateway` SKU, system-assigned identity and nonsecret tags. It does not change the existing Developer APIM foundation or connect the HTTP demos to this gateway. It can be deployed independently; the legacy foundation is not a prerequisite.

**Live resource creation observed; ARM deployment completion blocked by preview provider polling (2026-10-15).** This is a resource-only preview milestone, not ready advanced protection or a release of the full governed-tool alpha. Review enrollment, region/capacity, permissions, preview terms and cost before deploying. East US 2 is the default; Sweden Central is also documented by the [first-party overview](https://learn.microsoft.com/azure/api-management/ai-gateway-overview) (retrieved 2026-10-15). Neither the example region nor successful compilation guarantees availability.

## Deploy the checked-in template

The button opens the resource-group-scoped Azure deployment form. Select an approved subscription/resource group and review parameters. Alternatively, use an already authorized CLI context and an existing approved resource group:

```powershell
$subscriptionId = '<approved-subscription-id>'
$resourceGroupName = '<approved-resource-group>'
az deployment group create --subscription $subscriptionId --resource-group $resourceGroupName --name advanced-gateway --template-file infra\foundation\advanced\azuredeploy.json --parameters '@infra\foundation\advanced\main.parameters.json'
```

The safe parameter example omits `gatewayName` so ARM uses `aigw-${uniqueString(resourceGroup().id)}`. To supply a name, append `gatewayName=aigw-synthetic-demo` to the command. Names must match `^[a-z0-9][a-z0-9-]{1,22}[a-z0-9]$` (3–24 lowercase letters/digits/hyphens, alphanumeric endpoints); the provider enforces the regex, while template parameter constraints enforce length. The generated name is stable per resource group and collision-resistant, not a global uniqueness guarantee.

Outputs are resource ID, name and management API version only. No keys, tenant/principal IDs or inferred hostnames are returned. The schema defines the runtime hostname as read-only `properties.frontend.defaultHostname`; this template neither writes it nor reconstructs it.

## Isolated subscription-scope test

`test-deployment.bicep` / `test-deployment.json` creates a dedicated resource group and invokes the **same** gateway module. It does not deploy the legacy foundation or any clients, backend, networking or role assignments. Supply a new group name; the wrapper deliberately has no group-name default. Verify the approved tenant and subscription before each stage, and do not reuse an unrelated group.

```powershell
$subscriptionId = '<approved-subscription-id>'
$resourceGroupName = '<new-isolated-test-group>'
$deploymentName = '<unique-test-deployment-name>'
az account show --subscription $subscriptionId
az group exists --subscription $subscriptionId --name $resourceGroupName
# Continue only if false and the tenant/subscription match the approved target.
az deployment sub validate --subscription $subscriptionId --location eastus2 --name $deploymentName --template-file infra\foundation\advanced\test-deployment.json --parameters resourceGroupName=$resourceGroupName location=eastus2
az deployment sub what-if --subscription $subscriptionId --location eastus2 --name $deploymentName --template-file infra\foundation\advanced\test-deployment.json --parameters resourceGroupName=$resourceGroupName location=eastus2
# Continue only after successful validation and an isolated-create-only preview.
az deployment sub create --subscription $subscriptionId --location eastus2 --name $deploymentName --template-file infra\foundation\advanced\test-deployment.json --parameters resourceGroupName=$resourceGroupName location=eastus2
az deployment sub show --subscription $subscriptionId --name $deploymentName --query properties.provisioningState
az deployment group show --subscription $subscriptionId --resource-group $resourceGroupName --name advanced-gateway --query properties.provisioningState
az resource list --subscription $subscriptionId --resource-group $resourceGroupName
```

Use `az deployment operation sub list` / `az deployment operation group list` with the corresponding explicit subscription and deployment/group names to inspect failures. Fix confirmed request-shape problems in Bicep, rebuild both ARM files, revalidate and redeploy; do not patch live resources or weaken policy. Registration/enrollment/access failures require the responsible subscription/service owner, not guessed API versions or portal-created replacement resources.

### Observed live test — 2026-10-15

- Pinned Bicep compilation, 11 focused tests, live subscription validation and create-only what-if passed in East US 2. The fresh group was created only through the checked-in subscription wrapper. Normal ARM deployment registered `Microsoft.ApiManagement`; no separate registration command was run.
- Read-only gateway GET using `2026-09-01-preview` returned `properties.provisioningState: Succeeded`, `SystemAssigned` identity and a service-provided `frontend.defaultHostname`. The isolated group contains exactly one gateway and no legacy foundation resources. An unauthenticated HTTPS request to that returned hostname responded **404**; that proves an HTTP response, not runtime authentication, model/tool routing or protection.
- **Deployment completion blocker:** the nested ARM create operation reports `NoRegisteredProviderFound`: “No registered resource provider found for location 'eastus2' and API version '2026-09-01-preview' for type 'locations/operationsStatuses'.” Subscription and nested deployments remained `Running` during observation despite successful resource GET. Do not treat resource success as a successful terminal deployment.
- Live `az provider show --namespace Microsoft.ApiManagement --subscription <approved-subscription>` metadata advertises `2026-09-01-preview` for `aigateways`, but only versions through `2025-09-01-preview` for `locations/operationsStatuses`. The pinned first-party REST specification publishes the gateway contract under `AIGateway/preview/2026-09-01-preview`; no compatible older gateway contract was found in the bounded checked-schema investigation. The overview's `2026-05-01-preview` recommendation also does not match the advertised gateway versions. No speculative API downgrade, polling patch or duplicate deployment was applied.
- Post-create read-only what-if succeeded but was **not** a clean no-change result: group `NoChange`, gateway `Modify` for a request SKU omitted by GET and the read-only frontend returned by GET. No reapply was attempted while the original deployment was still running; no idempotence or mutable-frontend claim is made.
- **Next owner action:** the API Management resource-provider owner must correct or confirm the supported long-running-operation status API/registration for this gateway contract. Provide private deployment correlation evidence when opening the support case; then revalidate and monitor the same IaC deployment. No tenant identifiers or correlation/resource IDs are stored here.

The live gateway is left provisioned for follow-up, not automatically deleted. Preview pricing can change; retaining it can incur charges under applicable terms. After explicit cleanup approval, delete **only the recorded isolated test group** using `az group delete --subscription <approved-subscription> --name <recorded-isolated-test-group> --yes`, then verify that exact group no longer exists. This is a future destructive action, not part of the completed test.

## Exact schema boundary

The contract is pinned to Azure REST API specifications commit [`2335fe5db98171e7a78d08e712920b1869c536ce`](https://github.com/Azure/azure-rest-api-specs/blob/2335fe5db98171e7a78d08e712920b1869c536ce/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/preview/2026-09-01-preview/openapi.json) and its [create example](https://github.com/Azure/azure-rest-api-specs/blob/2335fe5db98171e7a78d08e712920b1869c536ce/specification/apimanagement/resource-manager/Microsoft.ApiManagement/AIGateway/preview/2026-09-01-preview/examples/AiGatewayCreate.json), inspected 2026-10-15.

- `AiGatewayResource` requires `properties`; inherited `TrackedResource` requires `location`. `identity`, `sku` and `tags` are optional in the schema; the template includes the create example's `SystemAssigned` identity and `AIGateway` SKU. The common SKU schema requires its `name` when supplied; it does not enumerate gateway SKU names.
- `AiGatewayProperties` has **no required fields**. This resource-only template sends `{}`. It intentionally does not create a VNet, subnet, backend or private boundary.
- Optional `backend` is **create-only** (`read`, `create` mutability). Optional `backend.subnet`, if supplied, requires an `id`; the pinned schema says same region and delegation to `Microsoft.App/environments`. Current [Learn networking instructions](https://learn.microsoft.com/azure/api-management/ai-gateway-configure-private-networking) instead describe `Microsoft.Web/serverFarms`, and the overview recommends a different management API version. These are live preview validation caveats, not reasons to omit supported resource IaC. Do not add networking later as an assumed mutable patch. If the provider requires a subnet despite the published optional contract, fix the template from confirmed provider evidence and redeploy; do not silently hand-create resources.
- Read-only `eTag`, provisioning state, frontend, identity principal/tenant IDs and ARM response metadata are omitted from the request.

The verified resource CRUD schema does **not** define MCP tool-server/catalog publication, runtime-key issuance, model/backend credentials, Agent 365 consent or individual-tool policies, tool-threat policies, cloud Block mode, delegated client tokens, telemetry configuration or native Foundry/Studio/Snowflake clients. None is implemented by this entrypoint; no guessed child resources, role GUIDs or threat flags are emitted. Supported administrator checkpoints for missing configuration interfaces remain subject to the [prerequisite contract](../../../docs/prerequisites/advanced-gateway.md), not a request to manually create the gateway. Backend reachability/authentication, anti-bypass and all runtime enforcement remain unverified.

## Offline checks and lifecycle

Compile with the same **Bicep 0.44.1** pinned in CI; do not regenerate unrelated ARM with a different compiler:

```powershell
az bicep build --file infra\foundation\advanced\main.bicep --outfile infra\foundation\advanced\azuredeploy.json
az bicep build --file infra\foundation\advanced\test-deployment.bicep --outfile infra\foundation\advanced\test-deployment.json
python -B scripts\test-advanced-gateway.py
```

CI installs the exact pin and checks compilation/drift plus the focused writable-schema fixture and button target. If that catalog lacks the preview resource, BCP081 is expected: the Bicep declaration still names the real resource type, with static checks against the pinned REST contract. Offline checks do not prove provider acceptance or enforcement.

The original resource-group artifacts were offline-only; the subsequent authorized live test is qualified above. No login/account switching, runtime-key access, backend configuration or consent changes were performed. Keep private resource/correlation evidence separate from repository documentation. Existing teardown helpers do not discover the isolated test wrapper's additional group; cleanup requires separate explicit approval. Do not delete shared groups or tenant controls. The [release policy](../../../docs/release-policy.md) continues to hold full governed-tool alpha until all required gates pass.
