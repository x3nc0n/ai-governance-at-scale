# Advanced governed-tool alpha — release evidence record

Copy this template for an authorized candidate release. It is a human-readable, nonsecret record, not a validator or evidence of live coverage. Record only sanitized metadata and links to approved restricted artifacts. Never commit credentials, tokens, sensitive prompts/arguments/results, or raw customer/tenant data.

The [gateway infrastructure entrypoint](../../infra/foundation/advanced/README.md) has separate compile/static checks. Those results may support the resource-build portion of a record, but do not mark live creation, the complete F1 gate or any runtime/client acceptance below as PASS.

## Record identity and authorization

| Field | Value |
|---|---|
| Profile/release candidate and revision | |
| Git revision; clean/dirty state | |
| Approving owner(s), tenant/resource scope, approval reference | |
| Environment ID alias; subscription/tenant aliases | |
| Gateway resource generation/API/SKU/region and preview enrollment | |
| Toolchain/Bicep version; source and generated artifact hashes | |
| Runtime image/config/catalog and client/platform artifact revisions | |
| Synthetic data/tool fixture revision | |
| Evidence location/access/retention | |

Use only these statuses for every row: **PASS**, **FAIL**, **BLOCKED**, **NOT RUN**. Include date/time, expected/observed result, sanitized artifact/correlation references, owner and notes. A blank status is not a pass.

## Feasibility and administrative prerequisites

| Gate | Status | Owner | Sanitized evidence / artifact reference | Notes |
|---|---|---|---|---|
| F1 resource, static tool catalog, policy, network and supported configuration/readback contract | NOT RUN | | | |
| F2 entitlement, cloud Block-mode procedure, scope and effective readback | NOT RUN | | | |
| F3 delegated audience/scope/registration/consent/token-refresh proof for each client | NOT RUN | | | |
| F4 approved tenant/subscription, preview enrollment, region/capacity, data path and cost owner | NOT RUN | | | |
| F5 policy ownership, drift/reapply, persistence and recreation/rollback evidence | NOT RUN | | | |
| F6 approved telemetry, privacy, access and retention evidence | NOT RUN | | | |
| Every supported manual administrator checkpoint has owner, first-party procedure, readback/export, drift/recreation and rollback evidence | NOT RUN | | | |

## Mandatory acceptance

All rows are mandatory for the four-solution advanced alpha. `BLOCKED`, `NOT RUN`, missing evidence, or an unsupported case means **release HOLD**. Do not substitute a v2-only control, an HTTP baseline, app-only identity, a mock, or successful discovery.

| Acceptance item | Status | Owner | Sanitized evidence / artifact reference | Notes |
|---|---|---|---|---|
| Reproducible pinned build, generated-template drift, image/config/catalog hashes and immutable artifact identities | NOT RUN | | | |
| Legacy HTTP baseline remains independently labeled; no alternate legacy/public route reaches protected capability | NOT RUN | | | |
| Agent 365 discovers actual gateway/server/static tools; consent principal/role/scope and cleanup owner are verified | NOT RUN | | | |
| Server block returns documented denial and produces zero backend effects; unblock restores allowed call | NOT RUN | | | |
| Individual-tool block returns HTTP 200 MCP error (`isError: true`) with denial metadata, zero effects, and no retry; separate allowed tool still succeeds | NOT RUN | | | |
| Static tool/catalog drift cannot silently become governed coverage | NOT RUN | | | |
| Gateway runtime key, delegated evaluation user bearer and backend authorization independently verified | NOT RUN | | | |
| Missing/invalid key; missing/expired/wrong-audience/wrong-tenant/app-only bearer; unauthorized backend principal tested | NOT RUN | | | |
| Effective cloud Block mode and policy scope/readback proven; both pre- and post-invocation enabled | NOT RUN | | | |
| Benign allowed tool runs once; pre-deny has zero effects; post-deny withholds result after one bounded effect without retry/reversal claim | NOT RUN | | | |
| Tool error result receives post-evaluation; controlled supported evaluator/token-exchange failures have expected Block behavior | NOT RUN | | | |
| Disabled/Audit cannot be misreported as enforcement; drift in required protection is detected | NOT RUN | | | |
| MCP HTTP-200 semantic errors are treated as failures; discovery/session actions are not counted as evaluated calls | NOT RUN | | | |
| Exact endpoint client product/version — allowed, server/tool/threat denies, identity negatives, refresh/error/no-retry, backend correlation | NOT RUN | | | |
| Native Foundry agent — same client-specific cases and actual native run | NOT RUN | | | |
| Published Copilot Studio end-user agent — same cases, approved channel and end-user connection | NOT RUN | | | |
| Named Snowflake read-only adapter — same cases, real bounded synthetic query and verified read-only principal | NOT RUN | | | |
| Direct protected backend, alternate legacy/public route and unauthorized network/identity anti-bypass tests | NOT RUN | | | |
| Server/tool blocks and threat settings persist through reapply, image/config updates and approved recreation, or pre-write guard prevents gap | NOT RUN | | | |
| Supported client/gateway/backend correlation and privacy review; no keys, tokens, sensitive arguments/results or unnecessary personal data in evidence | NOT RUN | | | |
| Fault behavior, safe rollback to a known-good advanced state without disabling protection or routing to an unprotected path | NOT RUN | | | |
| Dependency-aware cleanup completed; owned-resource residuals and tenant/platform/grant/billing restoration or approved retention recorded | NOT RUN | | | |

## Decision

**Default: HOLD.** Release only when every mandatory acceptance item is `PASS`, evidence is complete and sanitized, and authorized maintainers review the record.

- Final decision (`HOLD` unless all required rows pass):
- Reviewer and review reference:
- Explicit unresolved limitations/unsupported cases:
- Rollback owner and approved stop-traffic/server-block action:
- Cleanup and residual-evidence reference:
