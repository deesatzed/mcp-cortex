# Codex Handoff: Continue MCP-Cortex Alpha

You are receiving the v0.2 alpha reference implementation of MCP-Cortex. It is a working, tested seed package, not production authorization infrastructure.

## Desired outcome

A small, runnable reference implementation currently has:

1. Schema-validated MCP-Cortex objects.
2. A compatibility adapter for MCP tools/resources.
3. Deterministic policy checks before capability invocation.
4. A trace log for every intent, policy decision, capability call, and result.
5. Tests showing allow, deny, require-approval, trace, adapter, and schema flows.
6. A deterministic local demo at `examples/demo_policy_gate.py`.

## Constraints

- Preserve compatibility with existing MCP servers wherever possible.
- Do not require existing MCP servers to know about MCP-Cortex.
- Treat all wrapped MCP tools as untrusted until attested.
- Keep the developer-facing API small and ergonomic.
- Do not implement autonomous high-stakes actions. Human approval must remain explicit for high-risk effects.

## First tasks for the next development pass

1. Run the current tests:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e '.[dev]'
   pytest -q
   python scripts/validate_examples.py
   python -m mcp_cortex.cli --help
   ```

2. Inspect the docs:

   - `docs/SELF_CRITIQUE_AND_MITIGATIONS.md`
   - `docs/SPECIFICATION.md`
   - `docs/MCP_COMPATIBILITY.md`
   - `docs/SECURITY_MODEL.md`
   - `docs/UX_RISK_MODEL.md`

3. Implement these issues in order after preserving the current green baseline:

   ### Issue 1 — Persistence interface

   Add a `StorageBackend` protocol with implementations:

   - `InMemoryStorageBackend`
   - `SQLiteStorageBackend`

   Update `ContextFabric` and `TraceLog` to use it. Add `BeliefLedger` only if it stays small and tested.

   ### Issue 2 — MCP adapter skeleton

   Extend the existing adapter that consumes MCP-style tool metadata:

   ```json
   {
     "name": "run_tests",
     "description": "Run test suite",
     "inputSchema": { "type": "object", "properties": {} }
   }
   ```

   It already produces a `CapabilityContract` with conservative default effects. Next, add richer effect-review affordances and examples.

   ### Issue 3 — Gateway execution path

   Extend the existing `CortexGateway` methods:

   ```python
   gateway.propose_and_check(intent, capability, context_labels) -> PolicyDecision
   gateway.record_result(intent, capability, result) -> TraceEvent
   ```

   Then replace the placeholder invocation path with an optional real MCP adapter/proxy, gated by tests.

   ### Issue 4 — Test matrix

   Add tests for:

   - Safe sandbox code execution allowed.
   - External network blocked when `no_external_network=true`.
   - PHI/PII cannot flow to external network.
   - Production write requires human approval.
   - Unknown wrapped MCP tool defaults to `requires_human_review`.
   - Trace event digest changes when payload changes.

   ### Issue 5 — Developer UX

   Implement a small CLI:

   ```bash
   mcp-cortex validate examples/safe_patch_intent.json --schema schemas/intent.schema.json
   mcp-cortex check-policy examples/safe_patch_intent.json examples/sandbox_pytest_capability.json
   ```

   The CLI output should be a concise risk summary, not a wall of JSON.

## Acceptance criteria

- `pytest -q` passes.
- `python scripts/validate_examples.py` passes.
- README quick start works.
- A developer can understand the core concept within 10 minutes.
- A host application can adopt Cortex in stages: wrap MCP tool -> add policy check -> add trace -> add persistence -> add UI.

## Recommended implementation stance

Be conservative. If the contract does not know a capability's effects, classify it as medium or high risk and require review. It is better for the first prototype to be slightly annoying than silently unsafe.
