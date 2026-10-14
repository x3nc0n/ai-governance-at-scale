#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AZ_CALLS_FILE="$(mktemp)"
export AZ_CALLS_FILE
trap 'rm -f "$AZ_CALLS_FILE"' EXIT
export FAIL_COMMAND=""

az() {
  printf '%s\n' "$*" >> "$AZ_CALLS_FILE"
  if [[ -n "$FAIL_COMMAND" && "$*" == "$FAIL_COMMAND"* ]]; then
    return 17
  fi
}
export -f az

bash "$script_dir/bootstrap-governance.sh" example --subscription-id example --enable-defender --what-if
test ! -s "$AZ_CALLS_FILE"
bash "$script_dir/bootstrap-governance.sh" example --subscription-id example --deploy-purview --enable-defender
test "$(wc -l < "$AZ_CALLS_FILE")" -eq 3
grep -q -- '--parameters location=eastus2 enablePurview=true enableGovernanceDiagnostics=true --subscription example' "$AZ_CALLS_FILE"
if grep -q 'account set' "$AZ_CALLS_FILE"; then
  echo 'Helper changed the active subscription.' >&2
  exit 1
fi
for command in 'group create' 'deployment group create' 'security pricing create'; do
  export FAIL_COMMAND="$command"
  if bash "$script_dir/bootstrap-governance.sh" example --enable-defender; then
    echo "Helper did not propagate failure: $command" >&2
    exit 1
  fi
done
echo 'Bash helper regression checks passed.'
