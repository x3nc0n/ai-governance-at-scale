# Scenario 04 — Snowflake-Led Third-Party Agent

This scenario deploys a Container App demo shell with a generic deterministic response. An external Snowflake-led agent governed through the shared Microsoft control plane is the target architecture, not the current implementation. Snowflake calls, federation, MCP and APIM runtime integration are not implemented by this path.

## Release status

**Alpha demo shell; third-party integration planned/not implemented.** The shell inherits selected foundation dependencies and has no verified GA-only or beta status. See the [release policy and current profiles](../../docs/release-policy.md). Public demo ingress is not caller-authenticated; do not submit sensitive data.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F04-snowflake-agent%2Finfra%2Fazuredeploy.json)

For the shared identity model, see [docs/concepts/agent-identity-model.md](../../docs/concepts/agent-identity-model.md).
