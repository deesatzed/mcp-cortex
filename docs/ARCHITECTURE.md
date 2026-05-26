# MCP-Cortex Architecture

## Core components

```text
Host / Agent UI
      |
      v
Cortex Gateway
  - intent manager
  - MCP wrapper
  - policy check
  - context compiler
  - trace logger
      |
      +--> Context Fabric
      +--> Policy Engine
      +--> Trace Log
      +--> MCP Client Adapter
                 |
                 v
          Existing MCP Servers
```

## Cortex Gateway responsibilities

1. Accept or create an `Intent`.
2. Select or wrap a `CapabilityContract`.
3. Collect relevant context labels and handles.
4. Call the deterministic `PolicyEngine`.
5. Invoke the underlying capability only if allowed or approved.
6. Publish resulting context cells.
7. Append trace events.

## Implementation layers

### Layer 0 — Existing MCP

No changes to servers.

### Layer 1 — Wrapper

Create Cortex capability metadata from MCP tool metadata.

### Layer 2 — Policy

Check intent and effects before invocation.

### Layer 3 — Trace

Append auditable events.

### Layer 4 — Context

Persist context cells and compile relevant views for agents.

### Layer 5 — Native Cortex extensions

Add simulation, rollback, belief claims, and evaluation.

## Recommended module boundaries

```text
mcp_cortex.models      # dataclasses and serialization
mcp_cortex.policy      # deterministic policy checks
mcp_cortex.fabric      # context storage/query
mcp_cortex.trace       # trace event logging
mcp_cortex.adapter     # MCP wrapping and mapping
mcp_cortex.gateway     # orchestration API
mcp_cortex.cli         # developer CLI
```

## Design invariant

Every effectful action should have this chain:

```text
Intent -> CapabilityContract -> PolicyDecision -> Invocation -> TraceEvent -> ContextCell(s)
```

If any link is missing, the action should be treated as untrusted.
