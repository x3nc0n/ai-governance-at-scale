# Scenario 02 — Foundry Hosted Agent

This scenario deploys a rule-based policy-review demo in a lightweight Container App. It returns illustrative governance recommendations; it is not a Foundry-hosted agent, does not invoke a model, and does not evaluate live policy state.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F02-foundry-agent%2Finfra%2Fazuredeploy.json)

The agent exposes `/invoke` and returns a structured policy-review response that is easy to present in a demo.

Use the foundation resource names described in the [deployment guide](../../docs/deployment.md). Managed identity assignment alone does not provision an Entra Agent Identity or enforce caller authentication on the public demo endpoint.

For the shared identity model, see [docs/concepts/agent-identity-model.md](../../docs/concepts/agent-identity-model.md).
