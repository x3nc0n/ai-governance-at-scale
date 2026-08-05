# Entra Agent ID Lifecycle Model

> This document is the authoritative identity narrative for the repository. The shared architecture uses a five-object model:
>
> Agent Identity Blueprint → Blueprint Principal → Agent Identity → optional Agent's User Account → runtime access tokens

## Why this matters

Customers often conflate the blueprint principal with the runtime agent identity. That confusion creates risk in both architecture discussions and deployment planning. The model below keeps those concepts separate.

## Lifecycle model

| Object | Purpose | Notes |
|---|---|---|
| Agent Identity Blueprint | Declarative template for a class of agents | Defines capabilities, metadata, and permissions |
| Agent Identity Blueprint Principal | Trust anchor created from the blueprint | This is the service principal backing the blueprint |
| Agent Identity | Individual runtime identity for one agent instance | Represented as a child service principal with Agent subtype |
| Agent's User Account | Optional delegated-user context | Used when a workload needs user-style access |
| Access Tokens | Runtime credentials presented to downstream systems | Acquired through OAuth 2.0 / OIDC flows |

## Service principal mental model vs. Agent ID object model

A service principal is the Entra object that authenticates. The Agent ID model adds lifecycle semantics:

| Concept | Service principal model | Agent ID model |
|---|---|---|
| Template | App registration | Agent Identity Blueprint |
| Trust anchor | Service principal | Blueprint Principal |
| Instance identity | Single service principal | Agent Identity |
| Delegation | OBO flow | Agent's User Account + delegated tokens |

Key rule: the Blueprint Principal is not the same object as an Agent Identity.

## Scenario mapping

| Scenario | Identity pattern |
|---|---|
| Endpoint / client AI | Agent Identity presented to APIM as the calling principal |
| Foundry-hosted agent | Agent Identity scoped to the Foundry-backed runtime |
| Copilot Studio agent | Entra Agent Identity where available; legacy app registration path documented separately |
| Third-party agent | Federated or exchanged credential path anchored by the blueprint principal |

## Documentation guardrails

- Use the five-object model consistently.
- Never call the Blueprint Principal an Agent Identity.
- Separate provisioning-time identity objects from runtime token flows.
- Update this doc when Microsoft documentation changes.
