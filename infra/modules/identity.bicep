targetScope = 'resourceGroup'

@description('Azure region for the identities.')
param location string

@description('Identity names to create.')
param identityNames array = []

resource identities 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = [for name in identityNames: {
  name: name
  location: location
}]

output identityResourceIds array = [for (name, i) in identityNames: identities[i].id]
output identityPrincipalIds array = [for (name, i) in identityNames: identities[i].properties.principalId]
output identityNames array = identityNames
