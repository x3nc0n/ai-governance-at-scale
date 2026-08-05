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
- a shared registry-backed demo app for visible metadata and health checks
- a common story of identity, security, monitoring, and auditability

## How to use this repo

1. Deploy the shared foundation.
2. Deploy one or more scenarios into the shared foundation environment.
3. Review the scenario endpoints for the governance metadata payload that confirms the scenario identity, route, and runtime context.
4. Use the APIM gateway and shared monitoring outputs to tell the unified story.
