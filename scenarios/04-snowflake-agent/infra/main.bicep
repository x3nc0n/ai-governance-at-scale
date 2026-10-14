targetScope = 'resourceGroup'

@description('Azure region for the scenario deployment.')
param location string = resourceGroup().location

@description('Name of the scenario container app.')
param appName string = 'ca-snowflake-agent-${uniqueString(resourceGroup().id)}'

@description('Name of the foundation resource group that contains the shared governance estate.')
param foundationResourceGroupName string = 'rg-aigov-foundation-demo'

@description('Subscription ID that contains the foundation deployment. Defaults to the current subscription.')
param foundationSubscriptionId string = subscription().subscriptionId

@description('Name of the shared demo image to deploy for this scenario.')
param containerImageName string = 'aigov-demo-app:latest'

@description('Name of the shared managed environment in the foundation resource group.')
param foundationManagedEnvironmentName string

@description('Name of the shared container registry in the foundation resource group.')
param foundationContainerRegistryName string

@description('Name of the shared Azure AI Services account in the foundation resource group.')
param foundationAiServicesName string

var foundationIdentityName string = 'id-scenario-04'

resource managedEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  scope: resourceGroup(foundationSubscriptionId, foundationResourceGroupName)
  name: foundationManagedEnvironmentName
}

resource scenarioIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  scope: resourceGroup(foundationSubscriptionId, foundationResourceGroupName)
  name: foundationIdentityName
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  scope: resourceGroup(foundationSubscriptionId, foundationResourceGroupName)
  name: foundationContainerRegistryName
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${scenarioIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
      }
      secrets: [
        {
          name: 'acr-password'
          value: containerRegistry.listCredentials().passwords[0].value
        }
      ]
      registries: [
        {
          server: containerRegistry.properties.loginServer
          username: containerRegistry.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'snowflake-agent'
          image: '${containerRegistry.properties.loginServer}/${containerImageName}'
          env: [
            {
              name: 'SCENARIO_ID'
              value: '04-snowflake-agent'
            }
            {
              name: 'AZURE_AI_SERVICES'
              value: foundationAiServicesName
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: reference(scenarioIdentity.id, '2023-01-31').clientId
            }
            {
              name: 'SCENARIO_LABEL'
              value: 'Snowflake-Led Third-Party Agent'
            }
            {
              name: 'SCENARIO_DESCRIPTION'
              value: 'A third-party agent experience governed by the shared estate'
            }
          ]
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
        }
      ]
    }
  }
}

output containerAppName string = containerApp.name
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output identityPrincipalId string = reference(scenarioIdentity.id, '2023-01-31').principalId
