# Entra Agent ID prerequisites

The deployment templates in this repository provision the Azure governance plane, but tenant-level identity setup remains a prerequisite.

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
