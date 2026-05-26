from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

from .models import CapabilityContract

DEFAULT_FORBIDDEN = ["read:secrets", "write:production", "deploy:production"]


def _safe_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "-" for ch in name.strip())


def wrap_mcp_tool_as_capability(
    tool: Mapping[str, Any],
    *,
    effect_mapping: Optional[Iterable[str]] = None,
    forbidden_effects: Optional[Iterable[str]] = None,
    assurance_level: str = "A0",
) -> CapabilityContract:
    """Create a conservative Cortex CapabilityContract from MCP-style tool metadata.

    Expected MCP-style input:
      {"name": "run_tests", "description": "...", "inputSchema": {...}}
    """
    name = str(tool.get("name") or "unnamed_tool")
    effects = list(effect_mapping or ["tool:call"])
    forbidden = list(forbidden_effects or DEFAULT_FORBIDDEN)
    input_schema = dict(tool.get("inputSchema") or tool.get("input_schema") or {"type": "object"})
    description = str(tool.get("description") or "")

    requires: List[str] = []
    risk = "unknown"
    if effects == ["tool:call"] or assurance_level == "A0":
        requires.append("human_review_for_unknown_effects")
        risk = "medium"

    return CapabilityContract(
        capability=f"capability://wrapped/{_safe_name(name)}",
        version=str(tool.get("version") or "0.0.0"),
        input_schema=input_schema,
        effects=effects,
        forbidden_effects=forbidden,
        requires=requires,
        assurance_level=assurance_level,
        preconditions=[],
        postconditions=[],
        data_flow_rules=[],
        rollback={"mode": "unknown"},
        risk=risk,
        attestation={
            "wrapped_from": "mcp_tool",
            "tool_name": name,
            "description": description,
            "note": "Conservative wrapper; replace effect mapping after review.",
        },
    )
