# Scenario 03 — Copilot Studio Agent

This scenario deploys a rule-based HTTP broker in a lightweight Container App. It calls the scenario 01 developer knowledge base through APIM; it is not a published Copilot Studio agent and does not implement the Agent2Agent protocol.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F03-copilot-studio%2Finfra%2Fazuredeploy.json)

The broker exposes `/invoke` and requires scenario 01 plus an APIM subscription key supplied securely as `foundationApimSubscriptionKey`. It calls `/developer-kb/invoke` and returns HTTP 502 for configuration, connectivity, or response errors instead of presenting local fallback text as a successful remote call. See the [deployment guide](../../docs/deployment.md). Public demo ingress is not caller-authenticated; do not submit sensitive data.

For the shared identity model, see [docs/concepts/agent-identity-model.md](../../docs/concepts/agent-identity-model.md).
