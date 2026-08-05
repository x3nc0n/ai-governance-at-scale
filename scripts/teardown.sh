#!/usr/bin/env bash
set -euo pipefail

whatif=false
if [[ "${1:-}" == "--what-if" ]]; then
  whatif=true
fi

resource_groups=(
  'rg-aigov-foundation-demo'
  'rg-aigov-endpoint-ai-demo'
  'rg-aigov-foundry-agent-demo'
  'rg-aigov-copilot-studio-demo'
  'rg-aigov-snowflake-agent-demo'
)

for resource_group in "${resource_groups[@]}"; do
  if $whatif; then
    echo "Would remove resource group $resource_group"
  else
    az group delete --name "$resource_group" --yes --no-wait
  fi
done
