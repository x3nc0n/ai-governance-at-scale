$ErrorActionPreference = 'Stop'
$global:AzCalls = [Collections.Generic.List[string]]::new()
$global:FailCommand = ''
$global:EmptyRegistry = $false

function global:az {
    $command = $args -join ' '
    $global:AzCalls.Add($command)
    $global:LASTEXITCODE = 0
    if ($global:FailCommand -and $command.StartsWith($global:FailCommand)) {
        $global:LASTEXITCODE = 17
        return
    }
    if ($command.StartsWith('deployment group list')) { 'azuredeploy' }
    if ($command.StartsWith('deployment group show') -and -not $global:EmptyRegistry) { 'exampleacr' }
}

function Assert-True($Condition, $Message) {
    if (-not $Condition) { throw $Message }
}

function Assert-Fails([scriptblock]$Action) {
    $failed = $false
    try { & $Action } catch { $failed = $true }
    Assert-True $failed 'Expected helper to propagate the Azure CLI failure.'
}

& "$PSScriptRoot\bootstrap-governance.ps1" -ResourceGroupName example -SubscriptionId example -EnableDefender -WhatIf
Assert-True ($AzCalls.Count -eq 0) 'Dry run invoked Azure CLI.'

& "$PSScriptRoot\bootstrap-governance.ps1" -ResourceGroupName example -SubscriptionId example -DeployPurview -EnableDefender
Assert-True ($AzCalls.Count -eq 3) 'Expected resource group, deployment, and explicit pricing calls.'
Assert-True ($AzCalls[1] -match '--parameters location=eastus2 enablePurview=true enableGovernanceDiagnostics=true --subscription example') 'Deployment argument grouping is invalid.'
Assert-True (-not ($AzCalls -match 'account set')) 'Helper changed active subscription.'

foreach ($command in @('group create', 'deployment group create', 'security pricing create')) {
    $global:FailCommand = $command
    Assert-Fails { & "$PSScriptRoot\bootstrap-governance.ps1" -ResourceGroupName example -EnableDefender }
}
$global:FailCommand = ''
$AzCalls.Clear()
& "$PSScriptRoot\build-and-push-demo-image.ps1"
Assert-True ($AzCalls.Count -eq 3) 'Expected discovery, registry output, and image build calls.'
Assert-True ($AzCalls[1] -match '--name azuredeploy') 'Portal deployment name was not used.'

$AzCalls.Clear()
& "$PSScriptRoot\build-and-push-demo-image.ps1" -DeploymentName custom
Assert-True ($AzCalls.Count -eq 2) 'Custom deployment should bypass discovery.'
foreach ($command in @('deployment group list', 'deployment group show', 'acr build')) {
    $global:FailCommand = $command
    Assert-Fails { & "$PSScriptRoot\build-and-push-demo-image.ps1" }
}
$global:FailCommand = ''
$global:EmptyRegistry = $true
Assert-Fails { & "$PSScriptRoot\build-and-push-demo-image.ps1" }
Write-Host 'PowerShell helper regression checks passed.'
