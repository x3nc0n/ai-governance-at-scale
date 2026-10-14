# Squad Team

> ai-governance-at-scale

Team configuration lives in this repository's `.squad/` directory. Charter paths below are relative to `.squad/`; no external team root is required.

## Coordinator

| Name | Role | Notes |
|------|------|-------|
| Squad | Coordinator | Routes work, enforces handoffs and reviewer gates. |

## Members

| Name | Role | Charter | Status |
|------|------|---------|--------|
| Morpheus | Solution Lead | agents/morpheus/charter.md | Active |
| Trinity | Azure IaC Engineer | agents/trinity/charter.md | Active |
| Neo | AI Governance & Security Architect | agents/neo/charter.md | Active |
| Tank | Technical Storyteller | agents/tank/charter.md | Active |
| Switch | Deployment Validator | agents/switch/charter.md | Active |
| Scribe | Session Logger | agents/scribe/charter.md | Active |
| Ralph | Work Monitor | agents/ralph/charter.md | Active |
| Rai | RAI Reviewer | agents/Rai/charter.md | Active |
| Fact Checker | Fact Checker | agents/fact-checker/charter.md | Active |

## Coding Agent

<!-- copilot-auto-assign: false -->

| Name | Role | Charter | Status |
|------|------|---------|--------|
| @copilot | Coding Agent | — | 🤖 Coding Agent |

### Capabilities

**🟢 Good fit — auto-route when enabled:**
- Bug fixes with clear reproduction steps
- Test coverage (adding missing tests, fixing flaky tests)
- Lint/format fixes and code style cleanup
- Dependency updates and version bumps
- Small isolated features with clear specs
- Boilerplate/scaffolding generation
- Documentation fixes and README updates

**🟡 Needs review — route to @copilot but flag for squad member PR review:**
- Medium features with clear specs and acceptance criteria
- Refactoring with existing test coverage
- API endpoint additions following established patterns
- Migration scripts with well-defined schemas

**🔴 Not suitable — route to squad member instead:**
- Architecture decisions and system design
- Multi-system integration requiring coordination
- Ambiguous requirements needing clarification
- Security-critical changes (auth, encryption, access control)
- Performance-critical paths requiring benchmarking
- Changes requiring cross-team discussion

## Project Context

- **Project:** ai-governance-at-scale
- **Description:** Monorepo of four Azure-deployable reference architectures showing one governed AI estate across endpoint, Foundry, Copilot Studio, and third-party agent ingress patterns.
- **Stack:** Azure Bicep/ARM, Azure API Management AI Gateway, Azure AI Foundry, Entra Agent ID, Agent 365, Purview, Defender for AI Services, MCP, Snowflake, and Microsoft 365.
- **Created:** 2026-08-04
