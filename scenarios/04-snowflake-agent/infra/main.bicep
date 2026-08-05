targetScope = 'resourceGroup'

@description('Azure region for the scenario deployment.')
param location string = resourceGroup().location

@description('Name of the scenario container app.')
param appName string = 'ca-snowflake-agent-${uniqueString(resourceGroup().id)}'

@description('Resource ID of the shared managed environment.')
param managedEnvironmentId string

@description('Resource ID of the user-assigned identity for this scenario.')
param identityResourceId string

@description('Client ID of the user-assigned identity for this scenario.')
param identityClientId string

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
      secrets: []
    }
    template: {
      containers: [
        {
          name: 'snowflake-agent'
          image: 'mcr.microsoft.com/k8se/quickstart:latest'
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
              value: identityClientId
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
