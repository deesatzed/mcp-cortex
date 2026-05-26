from __future__ import annotations

import json

from mcp_cortex import CortexGateway, Intent, wrap_mcp_tool_as_capability


def run_demo() -> dict:
    """Run a deterministic local policy-gate demo.

    The wrapped tool is MCP-style metadata only. No MCP host, network, shell,
    Docker, secrets, or external services are used.
    """

    mcp_tool = {
        "name": "list_project_files",
        "description": "List local project files without reading file contents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "root": {"type": "string"},
            },
            "required": ["root"],
        },
        "version": "1.0.0",
    }
    capability = wrap_mcp_tool_as_capability(
        mcp_tool,
        effect_mapping=["read:file"],
        forbidden_effects=["network:external", "read:secrets", "write:production"],
        assurance_level="A2",
    )
    intent = Intent.create(
        goal={"desired_state": "project.files.listed"},
        requested_effects=["read:file"],
        constraints={"no_external_network": True},
        requester="agent://demo",
        success_metrics=["returns structured file metadata"],
    )

    gateway = CortexGateway()
    decision = gateway.propose_and_check(
        intent,
        capability,
        context_labels=["code", "local"],
    )
    result = gateway.record_result(
        intent,
        capability,
        {
            "status": "not_invoked",
            "reason": "demo validates policy and trace path only",
        },
        actor="gateway://demo",
    )

    return {
        "capability": capability.capability,
        "allowed": decision.allowed,
        "risk_class": decision.risk_class,
        "reasons": decision.reasons,
        "trace_event_count": len(gateway.trace_log.all()),
        "result_event_type": result.event_type,
        "result_digest": result.digest,
    }


def main() -> int:
    print(json.dumps(run_demo(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
