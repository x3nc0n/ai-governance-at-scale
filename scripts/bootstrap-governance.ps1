param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [string]$Location = 'eastus2',

    [string]$SubscriptionId,

    [string]$DeploymentName = 'main',

    [string]$PurviewAccountName,

    [switch]$DeployPurview,

    [switch]$EnableDefender,

    [switch]$WhatIf
)

$ErrorActionPreference = 'Stop'
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$templateFile = Join-Path $repoRoot 'infra/foundation/main.bicep'

$subscriptionArgs = @()
if ($SubscriptionId) {
    $subscriptionArgs = @('--subscription', $SubscriptionId)
}

Write-Host "Creating or updating resource group $ResourceGroupName in $Location"
if ($WhatIf) {
    Write-Host "[WhatIf] az group create --name $ResourceGroupName --location $Location"
}
else {
    az group create --name $ResourceGroupName --location $Location @subscriptionArgs | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Resource group creation failed.'
    }
}

$deploymentArgs = @(
    'deployment', 'group', 'create',
    '--name', $DeploymentName,
    '--resource-group', $ResourceGroupName,
    '--template-file', $templateFile,
    '--parameters', "location=$Location"
)

$enablePurview = ($DeployPurview -or -not [string]::IsNullOrWhiteSpace($PurviewAccountName))
if ($enablePurview) {
    $deploymentArgs += "enablePurview=true"
}
else {
    $deploymentArgs += "enablePurview=false"
}

if ($PurviewAccountName) {
    $deploymentArgs += "purviewAccountName=$PurviewAccountName"
}

$deploymentArgs += 'enableGovernanceDiagnostics=true'
$deploymentArgs += $subscriptionArgs

Write-Host 'Starting governance bootstrap deployment'
if ($WhatIf) {
    Write-Host "[WhatIf] az $($deploymentArgs -join ' ')"
}
else {
    & az @deploymentArgs
    if ($LASTEXITCODE -ne 0) {
        throw 'Foundation deployment failed.'
    }
}

if ($EnableDefender) {
    Write-Host 'Enabling Defender for Cloud posture pricing plan (subscription-level bootstrap)'
    if ($WhatIf) {
        Write-Host '[WhatIf] az security pricing create --name CloudPosture --tier Standard'
    }
    else {
        az security pricing create --name 'CloudPosture' --tier 'Standard' --output none @subscriptionArgs | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw 'Defender CloudPosture pricing update failed.'
        }
    }
}

Write-Host 'Governance bootstrap completed.'
if ($PurviewAccountName) {
    Write-Host "Purview account target: $PurviewAccountName"
}
