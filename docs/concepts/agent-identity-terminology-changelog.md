# Agent identity terminology changelog

This file records terminology updates as Microsoft documentation evolves.

## Initial version

- Adopted the five-object lifecycle model: Blueprint → Blueprint Principal → Agent Identity → optional Agent's User Account → tokens.
- Explicitly separated the Blueprint Principal from the Agent Identity to avoid confusion.
- Documented that an Agent Identity is an Entra service principal with Agent subtype while still retaining the broader lifecycle semantics of the Agent ID model.
