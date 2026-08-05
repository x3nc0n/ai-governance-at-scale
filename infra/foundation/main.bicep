targetScope = 'resourceGroup'

@description('Azure region for the shared foundation resources.')
param location string = resourceGroup().location

@description('Name of the shared API Management instance.')
param apimName string = 'apim-aigov-${uniqueString(resourceGroup().id)}'

@description('API Management pricing tier. Developer is the default demo SKU; StandardV2 is the production upgrade path.')
@allowed([
  'Developer'
  'StandardV2'
])
param apimSkuName string = 'Developer'

@description('Name of the shared Container Apps managed environment.')
param containerAppsEnvironmentName string = 'cae-aigov-${uniqueString(resourceGroup().id)}'

@description('Name of the Log Analytics workspace.')
param logAnalyticsName string = 'log-aigov-${uniqueString(resourceGroup().id)}'

@description('Name of the Application Insights resource.')
param appInsightsName string = 'appi-aigov-${uniqueString(resourceGroup().id)}'

@description('Name of the Key Vault used for runtime secrets.')
param keyVaultName string = 'kv-${take(replace(uniqueString(resourceGroup().id, subscription().subscriptionId), '-', ''), 16)}'

@description('Name of the Azure AI Services account.')
param aiServicesName string = 'ais-${take(uniqueString(resourceGroup().id), 12)}'

@description('Name of the shared Azure Container Registry used for the scenario demo images.')
param containerRegistryName string = 'acr${take(replace(toLower(uniqueString(resourceGroup().id, subscription().subscriptionId)), '-', ''), 20)}'

@description('Whether to create an Azure AI Foundry project under the shared AI Services account. Disabled by default to keep the foundation deployable on subscriptions that do not expose the full Foundry project path.')
param createFoundryProject bool = false

@description('Name of the Azure AI Foundry project.')
param aiProjectName string = 'aigov-foundry-project'

@description('Whether to create a default model deployment for the shared AI Services account. Disabled by default to keep the foundation deployable on subscriptions that do not expose the required model deployment API path.')
param deployModel bool = false

@description('Name of the default model deployment.')
param modelDeploymentName string = 'gpt-4.1-mini'

@description('Name of the model to deploy.')
param modelName string = 'gpt-4.1-mini'

@description('Model version to deploy.')
param modelVersion string = '2025-04-14'

@description('Capacity for the default model deployment.')
param modelSkuCapacity int = 10

@description('Name of the governed demo API exposed through APIM.')
param governedApiName string = 'aigov-governed-api'

@description('Path prefix for the governed demo API.')
param governedApiPath string = 'aigov'

@description('Whether the governed API requires an APIM subscription key.')
param requireSubscriptionKey bool = true

var identityNames = [
  'id-scenario-01'
  'id-scenario-02'
  'id-scenario-03'
  'id-scenario-04'
]

module monitoring './../modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    location: location
    logAnalyticsName: logAnalyticsName
    appInsightsName: appInsightsName
  }
}

module identities './../modules/identity.bicep' = {
  name: 'scenario-identities'
  params: {
    location: location
    identityNames: identityNames
  }
}

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppsEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: monitoring.outputs.workspaceCustomerId
        sharedKey: listKeys(resourceId('Microsoft.OperationalInsights/workspaces', logAnalyticsName), '2022-10-01').primarySharedKey
      }
    }
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      family: 'A'
      name: 'standard'
    }
    accessPolicies: []
    enableRbacAuthorization: true
    enableSoftDelete: true
    enablePurgeProtection: true
    softDeleteRetentionInDays: 90
    createMode: 'default'
    publicNetworkAccess: 'Enabled'
  }
}

resource aiServices 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiServicesName
  location: location
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    customSubDomainName: toLower(aiServicesName)
    disableLocalAuth: false
  }
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
  }
}

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = if (createFoundryProject) {
  parent: aiServices
  name: aiProjectName
  location: location
  properties: {
    displayName: aiProjectName
  }
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = if (deployModel) {
  parent: aiServices
  name: modelDeploymentName
  sku: {
    name: 'Standard'
    capacity: modelSkuCapacity
    tier: 'Standard'
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

resource apim 'Microsoft.ApiManagement/service@2022-08-01' = {
  name: apimName
  location: location
  sku: {
    name: apimSkuName
    capacity: 1
  }
  properties: {
    publisherEmail: 'admin@example.com'
    publisherName: 'AI Governance Demo'
    publicNetworkAccess: 'Enabled'
  }
}

resource apimProduct 'Microsoft.ApiManagement/service/products@2022-08-01' = {
  parent: apim
  name: 'aigov-product'
  properties: {
    displayName: 'AI Governance Demo'
    description: 'Shared product for the governed AI estate demo APIs.'
    subscriptionRequired: requireSubscriptionKey
    approvalRequired: false
    state: 'published'
  }
}

resource apimSubscription 'Microsoft.ApiManagement/service/subscriptions@2022-08-01' = {
  parent: apim
  name: 'aigov-demo-subscription'
  properties: {
    displayName: 'AI Governance Demo Subscription'
    scope: '/products/${apimProduct.name}'
    state: 'active'
    allowTracing: true
  }
}

resource apimApi 'Microsoft.ApiManagement/service/apis@2022-08-01' = {
  parent: apim
  name: governedApiName
  properties: {
    displayName: 'Governed AI Estate API'
    path: governedApiPath
    protocols: [
      'https'
    ]
    serviceUrl: aiServices.properties.endpoint
    subscriptionRequired: requireSubscriptionKey
    type: 'http'
  }
}

resource apiOperation 'Microsoft.ApiManagement/service/apis/operations@2022-08-01' = {
  parent: apimApi
  name: 'health'
  properties: {
    displayName: 'Health Check'
    method: 'get'
    urlTemplate: '/health'
    responses: [
      {
        statusCode: 200
        description: 'Healthy'
      }
    ]
  }
}

resource apiPolicy 'Microsoft.ApiManagement/service/apis/policies@2022-08-01' = {
  parent: apimApi
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: '''<policies>
  <inbound>
    <base />
    <rate-limit-by-key calls="60" renewal-period="60" counter-key="@(context.Subscription?.Id ?? context.Request.Headers.GetValueOrDefault(&quot;x-request-id&quot;, &quot;anonymous&quot;))" />
    <set-header name="x-aigov-policy" exists-action="override">
      <value>apim-rate-limit-and-log</value>
    </set-header>
    <set-header name="x-aigov-correlation-id" exists-action="override">
      <value>@(context.Request.Headers.GetValueOrDefault(&quot;x-correlation-id&quot;, Guid.NewGuid().ToString()))</value>
    </set-header>
    <set-header name="x-request-id" exists-action="override">
      <value>@(context.Request.Headers.GetValueOrDefault(&quot;x-request-id&quot;, Guid.NewGuid().ToString()))</value>
    </set-header>
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
    <set-header name="x-aigov-response-policy" exists-action="override">
      <value>apim-response</value>
    </set-header>
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>'''
  }
}

output apimName string = apim.name
output apimGatewayUrl string = 'https://${apim.name}.azure-api.net'
output managedEnvironmentId string = managedEnvironment.id
output managedEnvironmentName string = managedEnvironment.name
output appInsightsConnectionString string = monitoring.outputs.appInsightsConnectionString
output logAnalyticsWorkspaceId string = monitoring.outputs.workspaceId
output aiServicesName string = aiServices.name
output aiServicesEndpoint string = aiServices.properties.endpoint
output containerRegistryName string = containerRegistry.name
output containerRegistryLoginServer string = containerRegistry.properties.loginServer
output aiProjectName string = createFoundryProject ? aiProject.name : ''
output keyVaultName string = keyVault.name
output keyVaultResourceId string = keyVault.id
output governedApiName string = apimApi.name
output governedApiPath string = governedApiPath
output apimSubscriptionName string = apimSubscription.name
output scenarioIdentityResourceIds array = identities.outputs.identityResourceIds
output scenarioIdentityNames array = identities.outputs.identityNames
output scenarioIdentityPrincipalIds array = identities.outputs.identityPrincipalIds
