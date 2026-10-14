# Local AI endpoint behavioral hunting pack

**Optional, analyst-run Microsoft Defender XDR advanced hunting queries.** These evaluate the 11 proposed local AI hunts; they do not deploy detections, enforce policy, or add Azure resources. Scenario 01 deploys a Container App developer knowledge-base back end through APIM. That deployment is **not** Defender for Endpoint onboarding or a native local AI-agent deployment.

Status: checked against public Microsoft Learn schemas and statically tested on 2026-10-14. **No live tenant compilation or execution was performed.** These are starting points for hunting, not production-ready detections or a supported agent discovery catalog.

## Prerequisites and availability

- Separately license and deploy Microsoft Defender for Endpoint (MDE) with the endpoint telemetry and advanced hunting entitlement required by your tenant. Confirm the [current licensing and platform requirements](https://learn.microsoft.com/en-us/defender-endpoint/microsoft-defender-endpoint) rather than assuming every plan includes every hunting capability. The four `Device*Events` tables are MDE-backed and do not work/return data without that service.
- Onboard the **actual developer endpoints**, verify healthy sensors and ingestion, and obtain least-privilege hunting access scoped to those devices. Neither APIM logs nor a Container App substitute for workstation telemetry. Agent 365, Entra Agent ID, Purview, and Defender for AI Services do not establish prerequisites or native attribution for these queries.
- Confirm table/column availability and `ActionType` values using the Defender portal's built-in schema reference. `ProcessCreated`, `FileCreated`, `FileModified`, and `FileRenamed` are expected filters to validate against your collected events; public table references defer action-type details to the portal.
- Windows, macOS, and Linux have different collection capabilities and process naming conventions. Windows registry hunting does not apply to Linux/macOS. Cross-platform executable names are included where useful, not a promise of table parity; versioned Python names, helpers, WSL guest processes, containers, and extensionless executables can be missed.
- Native Defender XDR advanced hunting supports up to **30 days** of raw data; onboarding date, sensor gaps, permissions, and actual retention further constrain visibility. Connected Sentinel analytics-tier retention is separately configured. A 30-day query cannot recover uncollected or expired records.
- Preview graph access requires the applicable Security Exposure Management availability, permissions, contributing services/connectors, and tenant schema. Do not assume access from MDE alone.

## Candidate assessment (all 11)

| # | Decision | Standalone file | Rationale / change from proposal |
|---|---|---|---|
| 1 | Revise | [01-process-discovery.kql](01-process-discovery.kql) | Separate own-process and direct-parent evidence. Exact executable candidates plus boundary-aware path/command-line hints replace blanket `has_any`; all remain heuristics. |
| 2 | Revise | [02-parent-tool-execution.kql](02-parent-tool-execution.kql) | Direct parent must match; a child's command line alone cannot identify an AI parent. Include Windows and Unix shell/runtime/tool names. |
| 3 | Accept intent, revise attribution | [03-parent-powershell.kql](03-parent-powershell.kql) | Dedicated PowerShell/pwsh slice of #2; no claim of script-block or prompt capture. |
| 4 | Revise / split | [04-process-network.kql](04-process-network.kql), [05-destination-wrapper-summary.kql](05-destination-wrapper-summary.kql) | Network actor evidence is separate from destination discovery. Remove broad RemoteUrl keyword OR conditions, especially `github`. |
| 5 | Revise | [05-destination-wrapper-summary.kql](05-destination-wrapper-summary.kql) | Normalize URL/FQDN hosts; use exact-or-dot-subdomain boundaries. Unclassified actors are investigation leads, not confirmed wrappers. No broad `github.com`/`googleapis.com` AI assertion. |
| 6 | Revise | [06-process-network-correlation.kql](06-process-network-correlation.kql) | Join on DeviceId + PID + process creation timestamp; deduplicate creation side; keep network event IDs and separately named creation metadata. No invented four-hour lifetime. |
| 7 | Accept intent, revise terminology | [07-process-file-activity.kql](07-process-file-activity.kql) | `InitiatingProcess` is the file actor, not necessarily an AI parent. Recorded file events only, not full file auditing. |
| 8 | Accept intent, revise scope | [08-script-executable-writes.kql](08-script-executable-writes.kql) | Selected create/modify/rename events by candidate actor, including previous extension on rename. Writes are not execution or proof of binary format/signature. |
| 9 | Accept intent, revise attribution | [09-process-registry.kql](09-process-registry.kql) | Windows registry events by candidate actor; retain event IDs and actor identity. No claim every change is collected. |
| 10 | Accept as hunting summary, revise | [10-process-inventory-summary.kql](10-process-inventory-summary.kql) | Approximate observed process activity, not installed agents. Executing `AccountUpn`, missing-UPN counts, bounded sample sets, and separate evidence buckets. |
| 11 | Defer correlation; gate preview inspection | [preview/11-exposure-graph-schema.kql](preview/11-exposure-graph-schema.kql), [preview/11-exposure-graph-identifiers.kql](preview/11-exposure-graph-identifiers.kql) | Public schemas establish edge/node columns, **not** `endpointAiAgent`, `runs on`, or TargetNodeId = MDE DeviceId. Inspect actual labels and `EntityIds`; do not join graph IDs to device processes without a documented, verified mapping. |

## Matching and interpretation

Each core query embeds its own small `Evidence` function so it can be pasted and run alone (no saved function dependencies).

- `image-name-candidate`: an exact, case-insensitive executable name from a deliberately small seed list. Higher specificity than command-line text, **not** authenticated identity. Renamed/spoofed binaries and collisions remain possible; corroborate image path, hash, installation provenance, and process tree.
- `path-or-commandline-candidate`: a boundary-aware regex over recorded path/command line. Handles `lmstudio`, `lm-studio`, and `LM Studio` without term-token assumptions. Package paths and command arguments may identify generic node/python/Electron wrappers, but are only hints. A document path, quoted example, or vendor domain in arguments can create a false positive.
- `none`: no evidence under this list, **not** proof that the process is unrelated to AI.

The supplied broad text terms `roo`, `poe`, `goose`, `warp`, and `devin` are intentionally not free-text seeds: short/common names and people/terminal names lack sufficient specificity here. `cline`, model/vendor terms such as `qwen`/`deepseek`, and other distinctive text remain lower-confidence hints. This is not an exhaustive claim about existing products or discovery hooks. Add locally verified executable/package paths and hashes after baselining; do not expand by speculation. Regex scanning can be expensive: start with a shorter time range and a device scope, and measure tenant cost.

In `DeviceProcessEvents`, `AccountUpn` is the **newly executing process** account; `InitiatingProcessAccountUpn` is its **direct parent** account. In network/file/registry tables, the `InitiatingProcess*` fields identify the event actor. A same-named parent/child or empty UPN must not be interpreted as a confirmed user/agent identity. The process hunts cover direct parents only, not all descendants or multi-hop tool chains; the other hunts do not automatically inherit ancestry.

The destination seed list covers `openai.com`, `chatgpt.com`, `anthropic.com`, `claude.ai`, and the narrowly scoped `generativelanguage.googleapis.com`. These are analyst-chosen discovery hints, not a complete list of service endpoints. Exact hosts and dot-delimited subdomains are matched **after** parsing an absolute URL (adding a scheme for FQDNs), lowercasing, and trimming terminal DNS dots. Paths/query strings/userinfo never substitute for the host. Even a matching host may be a website visit, update, or documentation access, not an inference request. Shared hosts, proxies, private gateways, Azure-hosted model endpoints, local inference, IP-only records, missing RemoteUrl, and custom domains can evade this list. GitHub traffic and arbitrary Google APIs are not labeled AI.

Query #5 summarizes **only actors without seed evidence** at those destinations. Browsers and generic runtimes will commonly appear. To triage original records, rerun #5 replacing its final `summarize`/`order by` with:

```kusto
| project Timestamp, DeviceId, DeviceName, ReportId, ActionType, RemoteUrl, RemoteHost,
    RemoteIP, RemotePort, InitiatingProcessFileName, InitiatingProcessFolderPath,
    InitiatingProcessId, InitiatingProcessCreationTime, InitiatingProcessCommandLine,
    InitiatingProcessAccountUpn, ActorEvidence
```

Query #6 associates network events with the **same observed candidate process instance**, not its children. DeviceId + PID + creation time prevents conflation from PID reuse; missing/unequal timestamps are excluded, never relaxed into PID-only joins. One creation row per composite key prevents fan-out; multiple original network events remain legitimate separate rows. Network `Timestamp`, `DeviceId`, `DeviceName`, and `ReportId` are kept unchanged; creation-side fields use `Created*` names. The 30-day creation and 7-day network windows are lookup limits, **not** process lifetime assumptions. Long-running processes whose creation is outside retention, missed creation events, or timestamp precision mismatches will not join. Where available and verified, Microsoft recommends process unique IDs on Windows; this cross-platform pack uses the documented timestamp tuple instead.

Summaries #5/#10 are hunting-only. `dcount` estimates vary; UPN estimates remove the empty-string bucket and expose missing-UPN event counts, not a reliable census of people. Sample sets are unordered and capped at 20, so absence in a sample proves nothing. FileName grouping can combine distinct products/binaries; investigate paths/hashes before conclusions.

## Telemetry and privacy boundaries

These tables show **conventional endpoint behavior**, not full prompts, reasoning, responses, tool-result payloads, or agent session transcripts. A command line may incidentally expose a prompt, secret, username, customer path, or URL; it does not provide dependable transcript coverage. File events are not full auditing of every file/read and do not expose full file contents. Registry coverage and network visibility depend on sensor/platform/configuration and ingestion. No query guarantees all agents, descendants, files, reads, or tool calls are covered.

Executable/script writes do not prove execution; extensions do not prove PE/script format. No signing assertion is inferred from names, hashes, or version metadata. `InitiatingProcessSignatureStatus` would describe the initiator, not a newly created child; certificate enrichment would require separately validated evidence.

Minimize access and exports, restrict device scope, redact command lines/paths/registry values before sharing, and apply approved retention and handling rules. Use synthetic examples for testing. No personal/internal conversations or customer anecdotes are included. There is **no automated response**, isolation, blocking, or enforcement in this pack.

## Running, validation, and detection eligibility

1. In Defender advanced hunting, verify the portal schema and collected action types; use a small authorized test-device/time scope.
2. Paste one complete core `.kql` file, run it, and validate results against known benign local activity. Confirm false positives and collection gaps before broadening.
3. Run [validation/host-boundaries.kql](validation/host-boundaries.kql). Expected result: **zero mismatch rows**. This exercises KQL URL parsing and host predicates with synthetic data; it has not been tenant-executed here.
4. Run graph inspection files **separately** only if preview access exists. Neither filters on guessed agent labels. Verify observed edge direction/labels and the typed identifier structure in `EntityIds`; establish a supported MDE identifier mapping and freshness before designing any later correlation. Even a valid device mapping would scope endpoint behavior, not establish that all device processes belong to an agent.
5. Local regression check (Python standard library; no dependencies):

   ```powershell
   python scripts\test-endpoint-ai-hunts.py
   git diff --check -- scenarios\01-endpoint-ai\README.md
   ```

   The regression checks candidate/file coverage, self-contained consistent helpers, executable/text evidence boundaries, host positives/negatives, same-instance correlation safeguards, identity fields, and event identifier projections. It runs Python fixture models and text/structure assertions, **not a KQL parser, compiler, or schema emulator**. No existing KQL test tooling was found; the repository Bicep compilation workflow does not validate hunts.

Event-level hunts #1–4 and #6–9 preserve the original `Timestamp`, `DeviceId`, `DeviceName`, and `ReportId` for triage. ReportId alone repeats; table references describe the original event using DeviceName + Timestamp + ReportId. These columns support future detection review but **do not automatically make these files eligible detection rules**. Summary and graph inspection files are not event-level detection candidates as shipped.

Before creating any custom detection, execute and tune in your tenant, confirm permission/device scope, impacted-asset identifiers, and the current detection wizard requirements. Preserve Timestamp and ReportId from the same original event plus DeviceId for endpoint device scope/process-tree enrichment. Do not fabricate event IDs from grouped rows. Microsoft's documented scheduled frequencies are hourly, every 3/12/24 hours, or Continuous (NRT) where eligible; first save checks up to 30 days. The service applies its own lookback: replace/review the manual 7/30-day hunting filters for that schedule rather than copying them as-is. The documented maximum is **150 alerts per rule per run**.

NRT has specific single-table/operator/column constraints, disallows joins/unions/externaldata and comments, and requires generally available supported columns. #6 cannot run NRT as written; none of these commented standalone files is claimed NRT-ready. Availability, false-positive handling, alert grouping, service quotas, ingestion delays, and schedule/lookback must be validated. Leave response actions disabled; any promotion/enforcement is a separately reviewed tenant decision, not part of this repository deployment.

## Official source evidence

Public pages fetched and reviewed on **2026-10-14** (public schemas do not replace tenant validation):

| Source | Evidence used / limitation |
|---|---|
| [DeviceProcessEvents](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceprocessevents-table) | Process/parent columns, creation timestamps, executing vs initiating accounts, original event IDs, and signing caveat. MDE-backed; action types verified in portal. |
| [DeviceNetworkEvents](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicenetworkevents-table) | RemoteUrl is URL or FQDN; initiating process creation time and actor account columns; MDE prerequisite. |
| [DeviceFileEvents](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-devicefileevents-table) | File create/modify/other events, previous name/path and actor fields. Hashes can be absent; not full read auditing. |
| [DeviceRegistryEvents](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-deviceregistryevents-table) | Registry current/previous values and actor fields; MDE prerequisite. |
| [Hunting best practices](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-best-practices#identify-unique-processes-with-process-ids) | PID recycling; DeviceId/PID/creation-time tuple remains valid, especially non-Windows; Windows unique IDs preferred when available; explicit inner joins avoid random left deduplication. |
| [Advanced hunting overview](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview) | RBAC/access, sensor ingestion, native 30-day retention, 100,000 rows, 64-MB results, and 10-minute query limit; partial results are possible. |
| [Custom detection rules](https://learn.microsoft.com/en-us/defender-xdr/custom-detection-rules) | Event/entity enrichment columns, schedule/lookback, 150-alert limit, NRT restrictions, permissions, and separate rule creation. |
| [ExposureGraphEdges](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-exposuregraphedges-table), [ExposureGraphNodes](https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-exposuregraphnodes-table) | Public-preview warning; graph labels are data, NodeId is a graph identifier, EntityIds is dynamic. No documented assumption that TargetNodeId equals MDE DeviceId or that the supplied AI labels exist. |
| [String operators](https://learn.microsoft.com/en-us/kusto/query/datatypes-string-operators), [parse_url](https://learn.microsoft.com/en-us/kusto/query/parse-url-function) | `has_any` matches alphanumeric terms, not arbitrary paths/substrings; parse_url requires an absolute URL and returns Host separately. |
| [inner join](https://learn.microsoft.com/en-us/kusto/query/join-inner), [arg_min](https://learn.microsoft.com/en-us/kusto/query/arg-min-aggregation-function) | Multiple equality join conditions and creation-side row deduplication semantics. |
| [dcount](https://learn.microsoft.com/en-us/kusto/query/dcount-aggregation-function), [make_set](https://learn.microsoft.com/en-us/kusto/query/make-set-aggregation-function) | Approximate distinct estimates and explicit bounded, unordered samples. |

Unresolved: tenant KQL compilation, actual event/action/column availability, performance, sensor/platform gaps, locally verified executable/package identities, and preview graph identifier mapping. No claims are made about an agent-native discovery catalog or prompt/API hooks.
