# MCP-Cortex

> Status: v0.2 alpha reference implementation. This repository is executable and tested, but it is not production authorization infrastructure.

MCP-Cortex is a compatibility-first policy, capability, context, and trace layer for Model Context Protocol (MCP) tools. MCP tells a host which tools exist; MCP-Cortex adds structured metadata about what those tools can do, which effects they request, what context they depend on, what policy decision was made, and how the result is traced.

## What This Is

This repo is a small Python reference harness for the MCP-Cortex object model and adoption path. It is meant to help MCP server and client authors experiment with capability contracts, deterministic policy checks, persistent context handles, and append-only trace events before building a full MCP proxy or production policy service.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
PYTHONPATH=src python scripts/validate_examples.py
PYTHONPATH=src python -m mcp_cortex.cli --help
```

Run the local policy-gate demo:

```bash
PYTHONPATH=src python examples/demo_policy_gate.py
```

## Implemented Now

- `ContextFabric`: in-memory publish/query/materialize store for context cells.
- `PolicyEngine`: deterministic checks for unknown effects, forbidden effects, PHI/PII egress, external network constraints, production writes, and human approval requirements.
- `wrap_mcp_tool_as_capability`: conservative adapter from MCP-style tool metadata to a `CapabilityContract`.
- `CortexGateway`: proposal, policy-check, placeholder invocation, and trace-recording path.
- `TraceLog`: append-only in-memory trace events with stable content digests.
- Dataclasses for core MCP-Cortex objects.
- JSON Schemas and example payloads for core object types.
- CLI commands:
  - `mcp-cortex validate ...`
  - `mcp-cortex check-policy ...`
- Tests for policy behavior, schema examples, fabric operations, adapter behavior, and trace digest stability.

## Not Implemented Yet

- Full MCP SDK proxy/adapter that forwards real MCP traffic.
- Production authorization, identity, secret management, sandboxing, or network egress enforcement.
- Persistent storage backend for context, traces, or belief claims.
- Signed capability manifests.
- Admin UI or approval UX.
- Formal verification or compliance certification.
- Clinical, legal, financial, or other regulated decision automation.

## MCP Compatibility

MCP-Cortex is designed as an overlay, not a replacement for MCP. Existing MCP tools can be wrapped with conservative defaults, then progressively enriched with reviewed effect metadata, assurance levels, rollback expectations, and data-flow rules.

The recommended adoption path is:

1. Wrap existing MCP tool metadata as a `CapabilityContract`.
2. Run a deterministic policy check before invocation.
3. Emit trace events for intent, policy decision, and result.
4. Add persistent storage and approval UX only after the local contract is understood.

## Safety And Security Boundary

This alpha does not make unsafe tools safe by itself. It gives host applications a structured way to describe effects and make auditable policy decisions. Production systems still need real authentication, authorization, sandboxing, secret handling, logging retention, egress control, and security review.

If a tool's effects are unknown, MCP-Cortex defaults toward review rather than silent trust.

## Relationship To CAM_Codx And agentmedq

MCP-Cortex was mined and exercised through a Codex-CAM showpiece. Codex-CAM recalled MCP-Cortex methodologies, cited provenance, applied a capability-profile pattern to the real `agentmedq` / `sci-stapler` MCP server, and recorded the outcome.

That showpiece demonstrates one adoption path: expose MCP-Cortex-style capability profiles through an existing MCP tool without adding a new public MCP tool or requiring a new server process. It is evidence of feasibility, not a production guarantee.

## Roadmap

### v0.3 - Usable Prototype

- SQLite storage backend.
- Gateway execution flow beyond placeholder invocation.
- Example MCP server adapter.
- Human action card formatter.
- Stronger unknown-effect handling and policy summaries.

### v0.4 - Integration Prototype

- MCP SDK integration.
- Streamable HTTP or stdio demo.
- Capability registry.
- Signed manifest placeholders.
- Trace export.
- Terminal approval UI or small UI mock.

### v0.5 - Safety Hardening

- Optional OPA/Rego, Cedar, or CEL policy backend.
- Network egress policy hooks.
- Sandbox attestation interface.
- Redaction/materialization policy.
- Multi-tenant context scoping.

### v1.0 - Production Candidate

- Tamper-evident persistent trace log.
- Capability manifest signing.
- Admin policy management.
- Integration tests across representative MCP servers.
- Updated threat model and external security review.

## Repository Layout

```text
.
├── CODEX_HANDOFF.md
├── README.md
├── docs/
├── examples/
├── schemas/
├── scripts/
├── src/mcp_cortex/
└── tests/
```

## Non-Production Disclaimer

MCP-Cortex v0.2 is an alpha reference harness. Do not use it as the sole enforcement layer for production systems, sensitive data, regulated workflows, or high-stakes actions.

## License

MIT.
