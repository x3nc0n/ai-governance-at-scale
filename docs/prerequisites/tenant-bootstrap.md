# Tenant bootstrap (optional)

The repository templates do not attempt to create tenant-level Agent ID objects. For real deployments, use an internal bootstrap script or a Microsoft Graph automation flow that provisions the blueprint, blueprint principal, and agent identities outside the Azure resource deployment.

## Suggested steps

Tenant setup is separate from [demo release maturity](../release-policy.md). Evaluate its lifecycle when required by the selected profile; completing these steps does not prove that a demo implements the corresponding runtime integration.

1. Create the Agent Identity Blueprint.
2. Provision the Blueprint Principal.
3. Create the Agent Identity for the target workload.
4. Add any delegated user account when required.
5. Store runtime secrets in Key Vault and bind the workload identity to the correct role assignments.
