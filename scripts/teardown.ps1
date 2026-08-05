param(
  [switch]$WhatIf
)

$resourceGroups = @(
  'rg-aigov-foundation-demo',
  'rg-aigov-endpoint-ai-demo',
  'rg-aigov-foundry-agent-demo',
  'rg-aigov-copilot-studio-demo',
  'rg-aigov-snowflake-agent-demo'
)

foreach ($resourceGroup in $resourceGroups) {
  if ($WhatIf) {
    Write-Host "Would remove resource group $resourceGroup"
    continue
  }

  az group delete --name $resourceGroup --yes --no-wait
}
