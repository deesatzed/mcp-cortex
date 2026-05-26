# MCP-Cortex v0.2 Draft Specification

## Status

Draft, compatibility-first overlay.

## Purpose

MCP-Cortex extends MCP-style tool/resource access with explicit intent, effect contracts, deterministic policy checks, persistent context references, and auditable traces.

## Compatibility rule

MCP-Cortex MUST NOT require existing MCP servers to change. A Cortex Gateway MAY wrap ordinary MCP servers and expose Cortex behavior to the host application.

## Minimal kernel

### ContextCell

A versioned, addressable unit of context.

Required fields:

- `id`: stable URI, usually `ctx://...`
- `schema`: schema identifier for the payload
- `summary`: short safe summary
- `labels`: data labels such as `code`, `PHI`, `PII`, `untrusted_text`
- `provenance`: source and timestamp
- `version`: integer or semantic version

Optional fields:

- `payload`: inline payload for small non-sensitive data
- `payload_ref`: external reference for large/sensitive data
- `links`: related context cells
- `confidence`: source confidence
- `ttl_seconds`: optional expiration
- `trust_level`: `trusted`, `verified`, `untrusted`, or `hostile`

### CapabilityContract

A machine-readable declaration of a capability's expected effects and safety requirements.

Required fields:

- `capability`: stable URI or name
- `version`
- `input_schema`
- `effects`
- `forbidden_effects`
- `requires`
- `assurance_level`

Optional fields:

- `preconditions`
- `postconditions`
- `data_flow_rules`
- `rollback`
- `risk`
- `attestation`

### Intent

A proposed goal-bounded state transition.

Required fields:

- `id`: stable URI, usually `intent://...`
- `goal`
- `requested_effects`
- `constraints`
- `requester`

Optional fields:

- `context_refs`
- `success_metrics`
- `deadline`
- `status`

### PolicyDecision

The deterministic result of checking an intent against capability, context labels, actor, and environment.

Required fields:

- `allowed`: boolean
- `risk_class`: `green`, `yellow`, `orange`, or `red`
- `reasons`: list of explanation strings
- `required_approvals`: list of approvals still required
- `issued_at`

### TraceEvent

Append-only audit record.

Required fields:

- `id`
- `event_type`
- `actor`
- `timestamp`
- `refs`
- `payload`
- `digest`

## Canonical operations

A Cortex Gateway SHOULD implement these high-level methods:

```text
context.publish
context.query
context.materialize
capability.attest
capability.wrap_mcp_tool
intent.propose
policy.check
trace.append
```

Native Cortex runtimes MAY add:

```text
capability.simulate
capability.invoke
capability.rollback
belief.publish
belief.challenge
eval.score
```

## Effect vocabulary

The initial canonical vocabulary is intentionally small:

```text
read:context
read:file
read:secrets
write:sandbox
write:workspace
write:production
execute:test
execute:shell
network:internal
network:external
deploy:production
message:external
tool:call
```

Unknown effects MUST be classified at least `yellow`. Unknown effects in combination with sensitive labels SHOULD require human review.

## Data labels

Recommended labels:

```text
code
untrusted_text
trusted_config
PHI
PII
secret
credential
financial
legal
clinical
public
internal
```

## Risk classes

- `green`: allowed automatically.
- `yellow`: allowed but visible to user/operator; may require scoped approval in strict mode.
- `orange`: blocked until approval.
- `red`: blocked; approval cannot override without policy exception.

## Assurance levels

- `A0`: self-declared only.
- `A1`: schema-validated.
- `A2`: sandbox-attested.
- `A3`: audited implementation.
- `A4`: formal or independent verification.

Policy engines SHOULD consider assurance level when deciding whether to permit high-impact effects.

## State handles

Cortex objects are referenced through explicit handles:

```text
ctx://...
intent://...
capability://...
trace://...
belief://...
txn://...
```

No hidden protocol session is required. Handles can be passed through MCP tool arguments or `_meta` fields by compatible hosts.

## Request metadata convention

When a host supports request metadata, it SHOULD include:

```json
{
  "_meta": {
    "io.mcp_cortex/intent": "intent://...",
    "io.mcp_cortex/context": ["ctx://..."],
    "io.mcp_cortex/risk_class": "yellow",
    "io.mcp_cortex/trace_parent": "trace://..."
  }
}
```

## Backward compatibility

An existing MCP tool with name, description, and input schema can be wrapped into a `CapabilityContract`:

- `capability`: `capability://wrapped/<tool-name>`
- `input_schema`: MCP `inputSchema`
- `effects`: `['tool:call']` unless mapped
- `forbidden_effects`: conservative defaults, including production writes and secret reads
- `assurance_level`: `A0`
- `requires`: `['human_review_for_unknown_effects']`

## Safety invariants

1. Policy checks MUST be deterministic for a fixed input.
2. Sensitive labels MUST NOT be sent to external networks unless explicitly allowed by policy.
3. Production writes and production deploys MUST require explicit approval unless a deployment-specific policy says otherwise.
4. Trace logging MUST occur for intent proposal, policy decision, and capability result.
5. Simulation MUST NOT be treated as proof of safety.
