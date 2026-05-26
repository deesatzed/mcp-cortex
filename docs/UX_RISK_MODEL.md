# MCP-Cortex UX and Risk Model

## UX objective

Make safer agentic execution understandable without exposing users to protocol internals.

## User-facing risk classes

### Green — allowed

Example:

```text
The agent will read repository files and run tests in a sandbox. No network, secrets, or production writes.
```

### Yellow — allowed with notice

Example:

```text
The agent will call an unverified wrapped MCP tool. The tool has no declared production-write effect, but its behavior is not attested.
```

### Orange — approval required

Example:

```text
The agent wants to write to the workspace outside the sandbox. Review the proposed diff before approving.
```

### Red — blocked

Example:

```text
Blocked: PHI-labeled context cannot be sent to an external network capability.
```

## Human action card

Every non-green action should compile into this shape:

```text
Goal
  What the agent is trying to accomplish.

Will access
  Data/resources to be read.

Will change
  Files, systems, messages, or records to be modified.

Will execute
  Commands, code, or tools to be run.

Will not do
  Explicitly denied effects.

Data sensitivity
  PHI/PII/secret/untrusted labels involved.

Rollback
  Whether the action can be reversed and how.

Why approval is needed
  Short deterministic explanation.
```

## Developer UX guidelines

### Good

```python
intent = Intent(
    goal={"desired_state": "repo.tests.green"},
    requested_effects=["read:file", "write:sandbox", "execute:test"],
    constraints={"no_external_network": True},
    requester="agent://debugger"
)

decision = policy.check(intent, capability, context_labels=["code"])
```

### Bad

```python
run_tool("fix repo")
```

The goal of the API is to make the safe path only slightly more verbose than the unsafe path.

## Admin UX guidelines

Admins should manage:

- Trusted capability registries.
- Effect mappings for wrapped MCP tools.
- Approval policies by risk class.
- Sensitive data labels and redaction defaults.
- Trace retention policies.

## Audit UX guidelines

Audit views should answer:

1. Who/what proposed the intent?
2. What context was used?
3. Which capability was selected?
4. What effects were requested?
5. What did policy decide and why?
6. What actually happened?
7. Was rollback available or used?

## UX anti-patterns to avoid

- Showing raw JSON as the primary approval UI.
- Asking for approval for every trivial action.
- Hiding data sensitivity behind generic labels.
- Saying “safe” when the system only means “allowed by policy.”
- Treating simulator output as a guarantee.
