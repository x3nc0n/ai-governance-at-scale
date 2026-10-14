# Unified governance narrative

This repository demonstrates one governed AI estate with four entry points.

## One estate, four entry points

1. Endpoint / Client AI
   - Developer tools and desktop copilots that need a governed identity path.
   - The scenario shows how local or endpoint-based AI can be registered, routed, and observed through the shared estate.

2. Foundry-hosted or prompted AI
   - Foundry-hosted agents and prompt flows that use native Azure identity and backend governance.
   - The scenario shows how the governed estate provides consistent policy enforcement and monitoring.

3. Copilot Studio agent
   - Low-code agents that need enterprise identity, governance, and backend routing.
   - The scenario shows how a Copilot Studio experience can inherit common Entra and APIM controls.

4. Third-party agents (Snowflake-led)
   - External agents and platforms that still need to be governed through a shared control plane.
   - The scenario shows that governance is portable across platforms rather than tied to a single agent runtime.

## Shared control plane

All four scenarios share the same foundational controls:

- Microsoft Entra Agent ID lifecycle
- Azure API Management policy enforcement
- a shared container runtime and observability stack
- a shared registry-backed demo app with rule-based guidance and broker endpoints
- a common story of identity, security, monitoring, and auditability

## Demo agent behaviors

The first three scenarios deploy deterministic demonstrations, not LLM-backed agents or native Foundry/Copilot Studio integrations:

- Scenario 01 hosts a developer governance assistant that answers approved-tool and policy questions.
- Scenario 02 returns sample policy-review recommendations rather than inspecting live governance posture.
- Scenario 03 calls the scenario 01 knowledge base through APIM with a subscription key. This is an HTTP broker demonstration, not the Agent2Agent protocol.

Responses are sample guidance, not evidence of enforced policy, completed identity provisioning, Purview classification, or Defender inspection. Public Container App ingress is not caller-authenticated. These alpha endpoints must not receive sensitive data.

## How to use this repo

1. Deploy the shared foundation.
2. Deploy one or more scenarios into the shared foundation environment.
3. Review the scenario endpoints for the governance metadata payload that confirms the scenario identity, route, and runtime context.
4. Use the APIM gateway and shared monitoring outputs to tell the unified story.
