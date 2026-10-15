# Scenario 01 — Endpoint / Client AI

This scenario deploys a rule-based developer governance demo that returns sample guidance about tools, policy posture, and data handling. It is the "developer knowledge base" back end for the broader estate and is exposed through APIM so the scenario 03 broker can call it.

## Release status

**Alpha HTTP demo.** It inherits the selected foundation's dependency constraints; no GA-only baseline or beta promotion is established. See the [release policy and current profiles](../../docs/release-policy.md). Vendor lifecycle does not imply implementation readiness or production support.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fx3nc0n%2Fai-governance-at-scale%2Fmain%2Fscenarios%2F01-endpoint-ai%2Finfra%2Fazuredeploy.json)

The lightweight Container App exposes `/invoke` and is published under the APIM route `/developer-kb/invoke`, which requires an APIM subscription key. See [deployment parameters and limitations](../../docs/deployment.md) before deploying. The app itself has public ingress; the sample is not an authenticated production boundary and must not receive sensitive data. It does not use an LLM or install a native endpoint agent.

For the shared identity model, see [docs/concepts/agent-identity-model.md](../../docs/concepts/agent-identity-model.md).

## Optional endpoint behavioral hunting

Core hunts and the optional preview graph extension have separate alpha profiles under the [release policy](../../docs/release-policy.md#current-profiles); neither is activated by this Azure deployment.

The [local AI endpoint hunting pack](hunting/README.md) evaluates process, network, file, and registry telemetry in Microsoft Defender XDR. It requires separately licensed, onboarded, healthy Microsoft Defender for Endpoint devices and hunting permissions. Deploying this scenario's Container App/APIM back end does **not** onboard endpoints, deploy a native local AI process, or install these hunts. The pack provides conservative behavioral candidates, not full prompt/reasoning transcripts or verified agent-native attribution.
