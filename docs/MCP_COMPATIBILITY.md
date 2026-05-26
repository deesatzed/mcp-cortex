# MCP Compatibility Strategy

## Principle

MCP-Cortex should complement MCP, not fork it. Existing MCP servers should remain usable.

## Mapping

| MCP primitive | Cortex overlay |
|---|---|
| Resource | `ContextCell` or `payload_ref` |
| Tool | `CapabilityContract` |
| Prompt | Intent template or workflow recipe |
| Sampling | Agent/model delegation event in trace |
| Server | Capability/context provider |
| Client/Host | Cortex Gateway or policy-aware host |

## Wrapping existing MCP tools

When a tool lacks explicit effect metadata, the wrapper should assign conservative defaults:

```json
{
  "effects": ["tool:call"],
  "forbidden_effects": ["read:secrets", "write:production", "deploy:production"],
  "assurance_level": "A0",
  "requires": ["human_review_for_unknown_effects"]
}
```

Developers can then add mappings:

```json
{
  "tool": "run_tests",
  "effects": ["read:file", "execute:test"],
  "forbidden_effects": ["network:external", "read:secrets", "write:production"],
  "assurance_level": "A2"
}
```

## Metadata convention

Cortex-aware clients can pass handles through metadata where supported:

```json
{
  "_meta": {
    "io.mcp_cortex/intent": "intent://make-tests-green/42",
    "io.mcp_cortex/trace_parent": "trace://abc123"
  }
}
```

If metadata is unavailable, handles can be stored in the gateway trace and not sent to the underlying MCP server.

## Sessionless compatibility

Cortex uses explicit handles for state. It does not depend on hidden MCP sessions. This aligns with the direction of explicit state handles.

## Transport compatibility

Cortex does not require a new transport. It can run over:

- stdio MCP
- Streamable HTTP MCP
- host-local in-process adapters
- native Cortex transports in future implementations

## Migration path

### Stage 1 — Wrap

Wrap MCP tools and emit capability contracts.

### Stage 2 — Check

Run policy checks before tool calls.

### Stage 3 — Trace

Log intent, decision, call, and result.

### Stage 4 — Context

Publish tool results and relevant resources as context cells.

### Stage 5 — Native Cortex

Add simulation hooks, richer effect metadata, and better UI.
