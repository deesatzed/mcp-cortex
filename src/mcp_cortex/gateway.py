from __future__ import annotations

from typing import Any, Dict, Sequence

from .fabric import ContextFabric
from .models import CapabilityContract, Intent, PolicyDecision, TraceEvent
from .policy import PolicyEngine
from .trace import TraceLog


class CortexGateway:
    """Coordinates intent, policy, and trace for a Cortex action path."""

    def __init__(
        self,
        *,
        policy_engine: PolicyEngine | None = None,
        fabric: ContextFabric | None = None,
        trace_log: TraceLog | None = None,
    ) -> None:
        self.policy_engine = policy_engine or PolicyEngine()
        self.fabric = fabric or ContextFabric()
        self.trace_log = trace_log or TraceLog()

    def propose_and_check(
        self,
        intent: Intent,
        capability: CapabilityContract,
        context_labels: Sequence[str] | None = None,
    ) -> PolicyDecision:
        self.trace_log.record(
            "intent.proposed",
            actor=intent.requester,
            refs=[intent.id, capability.capability, *intent.context_refs],
            payload={"intent": intent.to_dict(), "capability": capability.to_dict()},
        )
        decision = self.policy_engine.check(intent, capability, context_labels=context_labels)
        self.trace_log.record(
            "policy.checked",
            actor="policy://default",
            refs=[intent.id, capability.capability],
            payload={"decision": decision.to_dict()},
        )
        return decision

    def record_result(
        self,
        intent: Intent,
        capability: CapabilityContract,
        result: Dict[str, Any],
        *,
        actor: str | None = None,
    ) -> TraceEvent:
        return self.trace_log.record(
            "capability.result",
            actor=actor or capability.capability,
            refs=[intent.id, capability.capability],
            payload={"result": result},
        )

    def invoke_placeholder(
        self,
        intent: Intent,
        capability: CapabilityContract,
        args: Dict[str, Any],
        context_labels: Sequence[str] | None = None,
    ) -> Dict[str, Any]:
        """Placeholder execution path for future MCP integration.

        This does not call any external tool. It demonstrates the required order:
        policy check first, execution second, trace third.
        """
        decision = self.propose_and_check(intent, capability, context_labels=context_labels)
        if not decision.allowed:
            result = {"status": "blocked", "decision": decision.to_dict()}
            self.record_result(intent, capability, result, actor="gateway://placeholder")
            return result

        result = {"status": "not_implemented", "args": args, "decision": decision.to_dict()}
        self.record_result(intent, capability, result, actor="gateway://placeholder")
        return result
