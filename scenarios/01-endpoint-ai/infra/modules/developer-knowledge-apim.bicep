targetScope = 'resourceGroup'

@description('Name of the shared APIM instance in the foundation resource group.')
param apimName string

@description('Fully qualified domain name of the developer knowledge base container app.')
param containerAppFqdn string

@description('Name of the APIM API to create.')
param apiName string = 'developer-knowledge-base'

@description('Path for the APIM API.')
param apiPath string = 'developer-kb'

resource apim 'Microsoft.ApiManagement/service@2022-08-01' existing = {
  name: apimName
}

resource developerKnowledgeApi 'Microsoft.ApiManagement/service/apis@2022-08-01' = {
  parent: apim
  name: apiName
  properties: {
    displayName: 'Developer Knowledge Base'
    path: apiPath
    protocols: [
      'https'
    ]
    serviceUrl: 'https://${containerAppFqdn}'
    subscriptionRequired: true
    type: 'http'
  }
}

resource developerKnowledgeOperation 'Microsoft.ApiManagement/service/apis/operations@2022-08-01' = {
  parent: developerKnowledgeApi
  name: 'invoke'
  properties: {
    displayName: 'Invoke developer knowledge base'
    method: 'POST'
    urlTemplate: '/invoke'
    responses: [
      {
        statusCode: 200
        description: 'Knowledge response'
      }
    ]
  }
}
