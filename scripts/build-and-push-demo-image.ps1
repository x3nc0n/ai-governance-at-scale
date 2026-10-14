param(
  [string]$ResourceGroupName = 'rg-aigov-foundation-demo',
  [string]$ImageName = 'aigov-demo-app:latest',
  [string]$DeploymentName
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not $DeploymentName) {
  $DeploymentName = [string](& az deployment group list --resource-group $ResourceGroupName --query "sort_by([?name=='main' || name=='azuredeploy'], &properties.timestamp)[-1].name" -o tsv)
  if ($LASTEXITCODE -ne 0) {
    throw "Unable to enumerate deployments for resource group '$ResourceGroupName'."
  }
}

if ([string]::IsNullOrWhiteSpace($DeploymentName)) {
  throw "No foundation deployment named 'main' or 'azuredeploy' was found for resource group '$ResourceGroupName'. Deploy the foundation template first."
}

$registryOutput = & az deployment group show --resource-group $ResourceGroupName --name $DeploymentName.Trim() --query properties.outputs.containerRegistryName.value -o tsv
$registryExitCode = $LASTEXITCODE
$registryName = ([string]$registryOutput).Trim()
if ($registryExitCode -ne 0 -or -not $registryName) {
  throw "The foundation deployment did not expose a container registry name."
}

Write-Host "Building demo image '$ImageName' in registry '$registryName'..."
& az acr build --registry $registryName --image $ImageName "$repoRoot/scenarios/shared/demo-app"
if ($LASTEXITCODE -ne 0) {
  throw "The demo image build failed."
}
Write-Host "Image build completed."
