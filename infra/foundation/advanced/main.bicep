targetScope = 'resourceGroup'

@description('Preview gateway region. Availability still depends on subscription enrollment and capacity.')
@allowed([
  'eastus2'
  'swedencentral'
])
param location string = 'eastus2'

@description('Gateway name: 3-24 lowercase letters, digits or hyphens; begin and end with a letter or digit. The resource provider enforces ^[a-z0-9][a-z0-9-]{1,22}[a-z0-9]$.')
@minLength(3)
@maxLength(24)
param gatewayName string = 'aigw-${uniqueString(resourceGroup().id)}'

type gatewayTags = {
  *: string
}

@description('Nonsecret resource tags. Do not include personal or tenant data.')
param tags gatewayTags = {
  workload: 'ai-governance'
  profile: 'gateway-infrastructure-alpha'
}

// Pinned REST contract permits empty properties; backend/subnet is optional and create-only.
resource gateway 'Microsoft.ApiManagement/aigateways@2026-09-01-preview' = {
  name: gatewayName
  location: location
  tags: tags
  sku: {
    name: 'AIGateway'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

@description('Resource ID of the gateway, not a runtime endpoint or proof of configured governance.')
output gatewayResourceId string = gateway.id

@description('Gateway resource name.')
output gatewayResourceName string = gateway.name

@description('Pinned gateway management API version.')
output gatewayApiVersion string = gateway.apiVersion
