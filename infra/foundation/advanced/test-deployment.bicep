targetScope = 'subscription'

@description('New, isolated test resource group. Check that it does not already exist before deploying.')
@minLength(1)
@maxLength(90)
param resourceGroupName string

@description('Approved gateway and resource group region.')
@allowed([
  'eastus2'
  'swedencentral'
])
param location string = 'eastus2'

type testTags = {
  *: string
}

@description('Nonsecret test ownership tags. Never include personal or tenant data.')
param tags testTags = {
  workload: 'ai-governance'
  profile: 'gateway-infrastructure-alpha-test'
}

resource testGroup 'Microsoft.Resources/resourceGroups@2025-04-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module gateway './main.bicep' = {
  name: 'advanced-gateway'
  scope: testGroup
  params: {
    location: location
    tags: tags
  }
}

output resourceGroupName string = testGroup.name
output gatewayResourceId string = gateway.outputs.gatewayResourceId
output gatewayResourceName string = gateway.outputs.gatewayResourceName
output gatewayApiVersion string = gateway.outputs.gatewayApiVersion
