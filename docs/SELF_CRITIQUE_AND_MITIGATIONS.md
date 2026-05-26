# MCP-Cortex Self-Critique and Mitigation Plan

## Executive assessment

MCP-Cortex is directionally strong but the first design was too ambitious. It tried to solve context, agency, security, distributed cognition, simulation, self-improvement, and UI in one protocol. That makes it impressive conceptually but risky as a product or standard.

The mitigation is to turn MCP-Cortex from a replacement protocol into a **progressive overlay**. The v0.2 design keeps the core small and allows adoption in five stages:

1. Wrap existing MCP tools as capabilities.
2. Add deterministic effect and data-flow checks.
3. Add context cells and trace logging.
4. Add persistence and state handles.
5. Add optional simulators, belief mesh, and richer UX.

## Design and UX problems found

### 1. Too many planes and primitives

The original design had identity, context, capability, intent, policy, mesh/belief, and learning/evaluation planes. Each plane is plausible, but together they create a large conceptual surface.

**Risk:** developers will not adopt a protocol that requires understanding seven planes before wrapping one tool.

**Mitigation:** define a minimal kernel:

- `ContextCell`
- `CapabilityContract`
- `Intent`
- `PolicyDecision`
- `TraceEvent`

Everything else is optional. The belief ledger, simulator hooks, and learning loop become extension modules.

### 2. It could become yet another heavyweight standard

If MCP-Cortex demands new servers, new transports, new policy engines, and new UIs up front, it will lose to existing MCP adoption.

**Risk:** high migration friction and no near-term ecosystem path.

**Mitigation:** keep MCP as the transport/integration substrate. Cortex is an overlay that wraps existing MCP tools with conservative capability contracts. Native Cortex servers can exist later.

### 3. The word “world-state fabric” is too abstract

The concept is useful, but it sounds like a grand AI architecture rather than a buildable component.

**Risk:** vague architecture; difficult implementation choices; Codex may over-engineer.

**Mitigation:** implement it as an addressable store of `ContextCell` records with labels, provenance, summaries, payload handles, links, TTLs, and version numbers. Start with in-memory and SQLite/Postgres backends.

### 4. False sense of security from contracts

A signed capability contract does not guarantee the implementation obeys the contract.

**Risk:** users trust declarations that are not enforced.

**Mitigation:** introduce assurance levels:

- `A0`: self-declared, unverified
- `A1`: schema-validated
- `A2`: sandbox-attested
- `A3`: audited implementation
- `A4`: formally verified or independently certified

The policy engine must treat lower-assurance capabilities conservatively.

### 5. Policy UX can become alert fatigue

If every effect requires a human click, the system repeats MCP's consent fatigue problem.

**Risk:** users approve blindly or avoid the system.

**Mitigation:** use risk classes and approval bundles:

- Green: deterministic allow, no human interruption.
- Yellow: allowed with visible warning or scoped approval.
- Orange: requires explicit approval.
- Red: blocked.

Consent screens should show intent, requested effects, data labels involved, target system, reversibility, and why the policy reached its decision.

### 6. The user may not understand what an agent is about to do

Intent-first execution is safer than raw tool calls, but a poorly written intent can be vague.

**Risk:** users see abstract goals and cannot judge consequences.

**Mitigation:** require every high-risk intent to compile into a **human action card**:

```text
Goal: Make tests pass.
Will read: current repo files.
Will write: sandbox workspace only.
Will execute: local test runner.
Will not access: network, secrets, production.
Rollback: git checkpoint.
Approval needed: no.
```

### 7. Context fabric can become a privacy leak

A shared memory layer can accidentally preserve sensitive data, combine data across domains, or expose data to agents that should not see it.

**Risk:** PHI/PII leakage and cross-tenant contamination.

**Mitigation:** every context cell has data labels, scope, TTL, provenance, and payload indirection. Sensitive payloads should live behind access-controlled handles. The context compiler should materialize summaries/redacted views by default.

### 8. Prompt injection still exists

Cortex reduces blind tool execution but does not eliminate malicious instructions inside resources or tool outputs.

**Risk:** a model may treat untrusted context as instruction.

**Mitigation:** context cells include `trust_level` and `labels`. The context compiler separates instructions, data, claims, and untrusted text. Policy checks are deterministic and do not rely on LLM interpretation.

### 9. Simulators can be wrong

The first MCP-Cortex design leaned heavily on simulation.

**Risk:** predicted safety is mistaken for actual safety.

**Mitigation:** simulation results are evidence, not authorization. The policy engine decides whether action is allowed. Trace logs must store simulator uncertainty and post-execution deltas.

### 10. Belief ledger may feel alien to developers

A belief ledger is useful for multi-agent work, but many developers just want safer tool use.

**Risk:** unnecessary cognitive load.

**Mitigation:** make beliefs optional. Start with traces and context. Add belief claims only when multiple agents or verifiers need to record disagreement.

### 11. Generative interface negotiation is powerful but dangerous

Allowing agents to co-generate new interfaces can create unexpected capabilities and permission bypasses.

**Risk:** unsafe self-extension.

**Mitigation:** disable generative negotiation by default. Generated capabilities must enter as draft contracts with `A0` assurance and require review before invocation.

### 12. Effect vocabulary can fragment

If every server invents its own effects, policy enforcement becomes inconsistent.

**Risk:** policy bypass through naming ambiguity.

**Mitigation:** start with a small canonical effect vocabulary:

- `read:context`
- `read:file`
- `read:secrets`
- `write:sandbox`
- `write:workspace`
- `write:production`
- `execute:test`
- `execute:shell`
- `network:internal`
- `network:external`
- `deploy:production`
- `message:external`

Custom effects are allowed but treated as unknown risk until mapped.

### 13. State model could conflict with sessionless MCP direction

If Cortex depends on hidden sessions, it will diverge from current MCP evolution toward explicit state handles.

**Risk:** incompatibility with future MCP implementations.

**Mitigation:** Cortex state is referenced through explicit IDs and URIs, such as `ctx://...`, `intent://...`, `trace://...`, and capability handles. No hidden session state is required.

### 14. Too much audit logging can overwhelm users and systems

A trace for every action is useful, but logs can become huge and hard to inspect.

**Risk:** storage bloat and poor audit UX.

**Mitigation:** separate full trace events from materialized summaries. Provide filtering by intent, actor, risk class, capability, and time window. Retention policies should be explicit.

### 15. Clinical and high-stakes UX must not imply autonomy

The original concept referenced clinical workflows. That is useful but dangerous if framed as autonomous decision-making.

**Risk:** overreach in regulated domains.

**Mitigation:** high-stakes domains require constrained outputs: recommendation candidates, missing information, uncertainty, evidence, and explicit clinician review. No autonomous orders, diagnoses, medication changes, or external disclosure.

## Revised design stance

MCP-Cortex v0.2 should be described as:

> A compatibility overlay that makes MCP tool use intent-aware, policy-checked, context-grounded, and auditable.

Not:

> A replacement for MCP or a complete world model for AI.

## Success criteria

The design succeeds if a developer can:

1. Wrap one MCP tool in less than 30 minutes.
2. See a clear policy decision before the tool runs.
3. Get an audit trace after it runs.
4. Add persistence without changing the protocol shape.
5. Add richer simulators and belief tracking only when needed.
