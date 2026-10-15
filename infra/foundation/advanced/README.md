# Advanced gateway infrastructure — alpha

[![Deploy gateway infrastructure to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fx3nc0n-blog-announcement-integration%2Finfra%2Ffoundation%2Fadvanced%2Fazuredeploy.json)

**Branch-bound pending merge:** this button targets `x3nc0n-blog-announcement-integration`, not `main`. It becomes available when that branch's [compiled template](https://raw.githubusercontent.com/x3nc0n/ai-governance-at-scale/x3nc0n-blog-announcement-integration/infra/foundation/advanced/azuredeploy.json) is pushed. Retarget the button and regression test together after merge.

This separate resource-group entrypoint provisions **one AI Gateway resource**, `Microsoft.ApiManagement/aigateways@2026-09-01-preview`, with the example-supported `AIGateway` SKU, system-assigned identity and nonsecret tags. It does not change the existing Developer APIM foundation or connect the HTTP demos to this gateway. It can be deployed independently; the legacy foundation is not a prerequisite.

**Implemented and offline checked, not live validated.** This is a resource-only preview milestone, not ready advanced protection or a release of the full governed-tool alpha. Review enrollment, region/capacity, permissions, preview terms and cost before deploying. East US 2 is the default; Sweden Central is also documented by the [first-party overview](https://learn.microsoft.com/azure/api-management/ai-gateway-overview) (retrieved 2026-10-15). Neither the example region nor successful compilation guarantees availability.

## Deploy the checked-in template

The button opens the resource-group-scoped Azure deployment form. Select an approved subscription/resource group and review parameters. Alternatively, use an already authorized CLI context and an existing approved resource group:

```powershell
$subscriptionId = '<approved-subscription-id>'
$resourceGroupName = '<approved-resource-group>'
az deployment group create --subscription $subscriptionId --resource-group $resourceGroupName --name advanced-gateway --template-file infra\foundation\advanced\azuredeploy.json --parameters '@infra\foundation\advanced\main.parameters.json'
```

The safe parameter example omits `gatewayName` so ARM uses `aigw-${uniqueString(resourceGroup().id)}`. To supply a name, append `gatewayName=aigw-synthetic-demo` to the command. Names must match `^[a-z0-9][a-z0-9-]{1,22}[a-z0-9]$` (3–24 lowercase letters/digits/hyphens, alphanumeric endpoints); the provider enforces the regex, while template parameter constraints enforce length. The generated name is stable per resource group and collision-resistant, not a global uniqueness guarantee.

Outputs are resource ID, name and management API version only. No keys, tenant/principal IDs or inferred hostnames are returned. The schema defines the runtime hostname as read-only `properties.frontend.defaultHostname`; this template neither writes it nor reconstructs it.

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
python -B scripts\test-advanced-gateway.py
```

CI installs the exact pin and checks compilation/drift plus the focused writable-schema fixture and button target. If that catalog lacks the preview resource, BCP081 is expected: the Bicep declaration still names the real resource type, with static checks against the pinned REST contract. Offline checks do not prove provider acceptance or enforcement.

No deployment, Azure validation, login or consent was performed to produce these artifacts. For an authorized live run, record sanitized resource creation/readback and cleanup evidence separately. Use a dedicated disposable resource group; existing teardown helpers do not discover this additional group. After the approved run, remove that explicitly scoped group using the supported resource-group deletion operation and verify completion; do not delete shared groups or tenant controls. The [release policy](../../../docs/release-policy.md) continues to hold full governed-tool alpha until all required gates pass.
