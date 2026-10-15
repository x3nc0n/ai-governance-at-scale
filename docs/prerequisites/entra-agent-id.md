# Entra Agent ID prerequisites

The deployment templates in this repository provision the Azure governance plane, but tenant-level identity setup remains a prerequisite.

Tenant identity setup is separate from [demo release maturity](../release-policy.md). Verify the exact capabilities required by a selected profile; setup guidance and assigned workload identities do not prove implemented Agent ID runtime integration or beta eligibility.

## Prerequisites

- Microsoft Entra admin access
- Appropriate Agent ID roles (for example, Agent ID Developer or Agent ID Administrator)
- Licensing or feature availability for the identity capabilities you want to expose

## Recommended setup flow

1. Create or review the Agent Identity Blueprint.
2. Provision the Blueprint Principal that anchors the blueprint.
3. Issue or register the Agent Identity for each workload that will call APIM or downstream tools.
4. Add any optional Agent's User Account when delegated access is required.
5. Configure runtime credentials and token exchange flows for each scenario.

## Notes

- The repository templates do not attempt to automate tenant-level Agent ID provisioning. That remains a prerequisite step for real-world deployments.
- Keep the lifecycle terminology aligned with the shared identity model in `docs/concepts/agent-identity-model.md`.
- Agent ID objects, workload identities, and optional Agent's User Accounts do not by themselves prove a delegated user bearer for AI Gateway threat evaluation. The required gateway token audience, scopes, consent, acquisition, and refresh must be verified separately for each client; see [advanced gateway prerequisites](advanced-gateway.md).
