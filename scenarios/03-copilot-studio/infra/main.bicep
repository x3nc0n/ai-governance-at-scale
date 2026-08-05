targetScope = 'resourceGroup'

@description('Azure region for the scenario deployment.')
param location string = resourceGroup().location

@description('Name of the scenario container app.')
param appName string = 'ca-copilot-studio-${uniqueString(resourceGroup().id)}'

@description('Resource ID of the shared managed environment.')
param managedEnvironmentId string

@description('Resource ID of the user-assigned identity for this scenario.')
param identityResourceId string

@description('Client ID of the user-assigned identity for this scenario.')
param identityClientId string

@description('Registry server for the shared demo image.')
param containerRegistryServer string

@description('Registry username for the shared demo image.')
param containerRegistryUsername string

@description('Registry password for the shared demo image.')
@secure()
param containerRegistryPassword string

@description('Name of the shared demo image to deploy for this scenario.')
param containerImageName string = 'aigov-demo-app:latest'

@description('Name of the shared Azure AI Services account.')
param foundationAiServicesName string = 'ai-services'

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identityResourceId}': {}
    }
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
      }
      secrets: [
        {
          name: 'acr-password'
          value: containerRegistryPassword
        }
      ]
      registries: [
        {
          server: containerRegistryServer
          username: containerRegistryUsername
          passwordSecretRef: 'acr-password'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'copilot-studio'
          image: '${containerRegistryServer}/${containerImageName}'
          env: [
            {
              name: 'SCENARIO_ID'
              value: '03-copilot-studio'
            }
            {
              name: 'AZURE_AI_SERVICES'
              value: foundationAiServicesName
            }
            {
              name: 'AZURE_CLIENT_ID'
              value: identityClientId
            }
            {
              name: 'SCENARIO_LABEL'
              value: 'Copilot Studio Agent'
            }
            {
              name: 'SCENARIO_DESCRIPTION'
              value: 'A low-code Copilot Studio agent with governed backend routing'
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
output identityPrincipalId string = reference(identityResourceId, '2023-01-31').principalId
