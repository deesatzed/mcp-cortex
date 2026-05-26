# MCP-Cortex Security Model

## Threat model

MCP-Cortex assumes:

- Tool descriptions can be misleading or incomplete.
- Tool outputs and resources may contain prompt injection.
- Servers may overclaim or underdeclare effects.
- Agents may make planning mistakes.
- Users may suffer approval fatigue.
- Attackers may combine individually harmless tools to exfiltrate data.
- Hidden session state is unreliable and hard to audit.

## Security goals

1. Make effects explicit before execution.
2. Prevent sensitive data from flowing to unauthorized sinks.
3. Bind tool use to user intent and actor identity.
4. Preserve auditability through append-only traces.
5. Allow conservative wrapping of existing MCP servers.
6. Keep high-risk actions gated by deterministic policy and human/institutional approval.

## Non-goals

- MCP-Cortex does not eliminate prompt injection.
- MCP-Cortex does not prove arbitrary code is safe.
- MCP-Cortex does not replace OAuth, mTLS, sandboxing, or endpoint security.
- MCP-Cortex does not turn LLM reasoning into a formally verified planner.

## Main controls

### 1. Capability contracts

Every action path has a `CapabilityContract` with effects, forbidden effects, data-flow rules, assurance level, and rollback metadata.

### 2. Deterministic policy checks

The policy engine evaluates intent, capability, data labels, actor, and environment. The result is a `PolicyDecision`.

The LLM may propose intents, but it does not decide whether the action is allowed.

### 3. Context labels and trust levels

Context cells carry labels such as `PHI`, `PII`, `secret`, and `untrusted_text`. Context compilers should materialize the least sensitive view needed for the task.

### 4. Explicit state handles

Cortex avoids hidden session state. Long-running work is referenced by handles such as `ctx://...`, `intent://...`, and `trace://...`.

### 5. Trace log

Every major event is appended with a digest. The initial implementation uses local hashing; a production version should support tamper-evident logs and signing.

## Default denial rules

The reference policy engine denies:

- `read:secrets` unless explicitly allowed.
- Any `PHI` or `PII` flow to `network:external`.
- External network use when an intent says `no_external_network=true`.
- Effects listed in a capability's `forbidden_effects`.

It requires approval for:

- `write:production`
- `deploy:production`
- `message:external` when sensitive labels are present
- Unknown wrapped MCP tools in strict mode

## Production hardening checklist

- Use a real authorization layer; do not rely on Cortex policy alone.
- Store credentials outside the context fabric.
- Use signed capability manifests.
- Run effectful tools in sandboxes.
- Add egress controls at network level.
- Separate policy decision from policy enforcement.
- Store traces in an append-only or tamper-evident backend.
- Red-team prompt injection and tool-combination attacks.
- Add retention policies for sensitive context cells.
