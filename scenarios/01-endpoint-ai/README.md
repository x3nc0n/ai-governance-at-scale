# Scenario 01 — Endpoint / Client AI

This scenario demonstrates how endpoint-based AI tools such as Claude Code, Cursor, or VS Code extensions can be governed through a single Azure entry point.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F01-endpoint-ai%2Finfra%2Fazuredeploy.json)

For the shared identity model, see [docs/concepts/agent-identity-model.md](../../docs/concepts/agent-identity-model.md).

## Optional endpoint behavioral hunting

The [local AI endpoint hunting pack](hunting/README.md) evaluates process, network, file, and registry telemetry in Microsoft Defender XDR. It requires separately licensed, onboarded, healthy Microsoft Defender for Endpoint devices and hunting permissions. Deploying this scenario's Container App/APIM back end does **not** onboard endpoints, deploy a native local AI process, or install these hunts. The pack provides conservative behavioral candidates, not full prompt/reasoning transcripts or verified agent-native attribution.
