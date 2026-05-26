from __future__ import annotations

from typing import Iterable, List, Sequence, Set

from .models import CapabilityContract, Intent, PolicyDecision

SENSITIVE_LABELS: Set[str] = {"PHI", "PII", "secret", "credential", "financial", "legal"}
HIGH_RISK_EFFECTS: Set[str] = {"write:production", "deploy:production", "read:secrets"}
EXTERNAL_EFFECTS: Set[str] = {"network:external", "message:external"}
KNOWN_EFFECTS: Set[str] = {
    "read:context",
    "read:file",
    "read:secrets",
    "write:sandbox",
    "write:workspace",
    "write:production",
    "execute:test",
    "execute:shell",
    "network:internal",
    "network:external",
    "deploy:production",
    "message:external",
    "tool:call",
}


class PolicyEngine:
    """Small deterministic policy engine for the MCP-Cortex reference harness.

    Production systems should replace or augment this with a dedicated policy backend
    such as OPA/Rego, Cedar, CEL, or equivalent.
    """

    def __init__(self, *, strict_unknown_effects: bool = True) -> None:
        self.strict_unknown_effects = strict_unknown_effects

    def check(
        self,
        intent: Intent,
        capability: CapabilityContract,
        context_labels: Sequence[str] | None = None,
        actor: str | None = None,
    ) -> PolicyDecision:
        labels = set(context_labels or [])
        requested = set(intent.requested_effects or capability.effects)
        declared = set(capability.effects)
        forbidden = set(capability.forbidden_effects)
        reasons: List[str] = []
        approvals: List[str] = []
        redactions: List[str] = []

        unknown = sorted(effect for effect in requested if effect not in KNOWN_EFFECTS)
        if unknown:
            reasons.append(f"Unknown effect(s): {', '.join(unknown)}")
            if self.strict_unknown_effects:
                approvals.append("human_review_for_unknown_effects")

        undeclared = sorted(effect for effect in requested if effect not in declared)
        if undeclared:
            reasons.append(f"Intent requests effect(s) not declared by capability: {', '.join(undeclared)}")
            approvals.append("capability_owner_review")

        forbidden_requested = sorted(requested & forbidden)
        if forbidden_requested:
            return PolicyDecision(
                allowed=False,
                risk_class="red",
                reasons=[f"Requested forbidden effect(s): {', '.join(forbidden_requested)}"],
                required_approvals=[],
                redactions=[],
            )

        if intent.constraints.get("no_external_network") is True and requested & EXTERNAL_EFFECTS:
            return PolicyDecision(
                allowed=False,
                risk_class="red",
                reasons=["Intent forbids external network/message effects."],
                required_approvals=[],
                redactions=[],
            )

        if labels & SENSITIVE_LABELS and requested & EXTERNAL_EFFECTS:
            return PolicyDecision(
                allowed=False,
                risk_class="red",
                reasons=[
                    "Sensitive context label(s) cannot flow to external network/message effects: "
                    + ", ".join(sorted(labels & SENSITIVE_LABELS))
                ],
                required_approvals=[],
                redactions=sorted(labels & SENSITIVE_LABELS),
            )

        if requested & HIGH_RISK_EFFECTS:
            approvals.append("explicit_human_approval")
            reasons.append("High-risk effect requires approval: " + ", ".join(sorted(requested & HIGH_RISK_EFFECTS)))

        if capability.assurance_level in {"A0", "unknown"}:
            reasons.append("Capability is self-declared or unverified.")
            if requested - {"read:context", "read:file", "execute:test", "write:sandbox"}:
                approvals.append("review_unverified_capability")

        if any(req == "human_review_for_unknown_effects" for req in capability.requires):
            if "tool:call" in requested and capability.assurance_level == "A0":
                approvals.append("human_review_for_unknown_effects")
                reasons.append("Wrapped MCP tool has unknown concrete effects.")

        approvals = sorted(set(approvals))
        if approvals:
            return PolicyDecision(
                allowed=False,
                risk_class="orange",
                reasons=reasons or ["Approval required."],
                required_approvals=approvals,
                redactions=redactions,
            )

        risk = "green"
        if capability.assurance_level in {"A0", "A1"} or unknown:
            risk = "yellow"

        if not reasons:
            reasons.append("Policy allowed requested effects.")

        return PolicyDecision(
            allowed=True,
            risk_class=risk,
            reasons=reasons,
            required_approvals=[],
            redactions=redactions,
        )
