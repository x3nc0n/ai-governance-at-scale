#!/usr/bin/env bash
set -euo pipefail

resource_group="${1:-}"
location="${LOCATION:-eastus2}"
subscription_id="${SUBSCRIPTION_ID:-}"
purview_account_name="${PURVIEW_ACCOUNT_NAME:-}"
deployment_name="${DEPLOYMENT_NAME:-main}"
deploy_purview="${DEPLOY_PURVIEW:-false}"
enable_defender="${ENABLE_DEFENDER:-false}"
what_if="${WHAT_IF:-false}"

usage() {
  echo "Usage: bash scripts/bootstrap-governance.sh <resource-group> [--location <location>] [--subscription-id <sub-id>] [--purview-name <name>] [--deploy-purview] [--enable-defender] [--what-if]"
}

if [ -z "$resource_group" ]; then
  usage
  exit 1
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --location)
      location="$2"
      shift 2
      ;;
    --subscription-id)
      subscription_id="$2"
      shift 2
      ;;
    --purview-name)
      purview_account_name="$2"
      shift 2
      ;;
    --deploy-purview)
      deploy_purview="true"
      shift
      ;;
    --enable-defender)
      enable_defender="true"
      shift
      ;;
    --what-if)
      what_if="true"
      shift
      ;;
    *)
      if [ "$resource_group" = "$1" ]; then
        shift
      else
        echo "Unknown argument: $1"
        usage
        exit 1
      fi
      ;;
  esac
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
template_file="$repo_root/infra/foundation/main.bicep"

subscription_args=()
if [ -n "$subscription_id" ]; then
  subscription_args=(--subscription "$subscription_id")
fi

echo "Creating or updating resource group $resource_group in $location"
if [ "$what_if" = "true" ]; then
  echo "[WhatIf] az group create --name $resource_group --location $location"
else
  az group create --name "$resource_group" --location "$location" "${subscription_args[@]}" >/dev/null
fi

deployment_args=(deployment group create --name "$deployment_name" --resource-group "$resource_group" --template-file "$template_file" --parameters "location=$location")
if [ "$deploy_purview" = "true" ] || [ -n "$purview_account_name" ]; then
  deployment_args+=("enablePurview=true")
else
  deployment_args+=("enablePurview=false")
fi
if [ -n "$purview_account_name" ]; then
  deployment_args+=("purviewAccountName=$purview_account_name")
fi
deployment_args+=("enableGovernanceDiagnostics=true")
deployment_args+=("${subscription_args[@]}")

echo "Starting governance bootstrap deployment"
if [ "$what_if" = "true" ]; then
  printf '[WhatIf] az %s\n' "${deployment_args[*]}"
else
  az "${deployment_args[@]}"
fi

if [ "$enable_defender" = "true" ]; then
  echo "Enabling Defender for Cloud posture pricing plan (subscription-level bootstrap)"
  if [ "$what_if" = "true" ]; then
    echo '[WhatIf] az security pricing create --name CloudPosture --tier Standard'
  else
    az security pricing create --name 'CloudPosture' --tier 'Standard' --output none "${subscription_args[@]}" >/dev/null
  fi
fi

echo 'Governance bootstrap completed.'
if [ -n "$purview_account_name" ]; then
  echo "Purview account target: $purview_account_name"
fi
