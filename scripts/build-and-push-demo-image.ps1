param(
  [string]$ResourceGroupName = 'rg-aigov-foundation-demo',
  [string]$ImageName = 'aigov-demo-app:latest'
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

$deployment = az deployment group show --resource-group $ResourceGroupName --name main 2>$null
if (-not $deployment) {
  throw "No foundation deployment named 'main' was found for resource group '$ResourceGroupName'. Deploy the foundation template first."
}

$registryName = az deployment group show --resource-group $ResourceGroupName --name main --query properties.outputs.containerRegistryName.value -o tsv
if (-not $registryName) {
  throw "The foundation deployment did not expose a container registry name."
}

Write-Host "Building demo image '$ImageName' in registry '$registryName'..."
az acr build --registry $registryName --image $ImageName "$repoRoot/scenarios/shared/demo-app"
Write-Host "Image build completed."
