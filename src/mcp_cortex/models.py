from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_digest(value: Any) -> str:
    """Return a deterministic sha256 digest for JSON-compatible values."""
    if is_dataclass(value):
        value = asdict(value)
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return "sha256:" + sha256(encoded).hexdigest()


@dataclass(frozen=True)
class Provenance:
    source: str
    timestamp: str = field(default_factory=now_iso)
    actor: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContextCell:
    id: str
    schema: str
    summary: str
    labels: List[str]
    provenance: Provenance
    version: int = 1
    payload: Optional[Dict[str, Any]] = None
    payload_ref: Optional[str] = None
    links: List[str] = field(default_factory=list)
    confidence: float = 1.0
    ttl_seconds: Optional[int] = None
    trust_level: str = "untrusted"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["provenance"] = self.provenance.to_dict()
        return data


@dataclass
class CapabilityContract:
    capability: str
    version: str
    input_schema: Dict[str, Any]
    effects: List[str]
    forbidden_effects: List[str]
    requires: List[str]
    assurance_level: str = "A0"
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    data_flow_rules: List[Dict[str, Any]] = field(default_factory=list)
    rollback: Optional[Dict[str, Any]] = None
    risk: str = "unknown"
    attestation: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Intent:
    id: str
    goal: Dict[str, Any]
    requested_effects: List[str]
    constraints: Dict[str, Any]
    requester: str
    context_refs: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    deadline: Optional[str] = None
    status: str = "proposed"

    @classmethod
    def create(
        cls,
        goal: Dict[str, Any],
        requested_effects: List[str],
        constraints: Dict[str, Any],
        requester: str,
        context_refs: Optional[List[str]] = None,
        success_metrics: Optional[List[str]] = None,
    ) -> "Intent":
        return cls(
            id=f"intent://{uuid4()}",
            goal=goal,
            requested_effects=requested_effects,
            constraints=constraints,
            requester=requester,
            context_refs=context_refs or [],
            success_metrics=success_metrics or [],
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PolicyDecision:
    allowed: bool
    risk_class: str
    reasons: List[str]
    required_approvals: List[str] = field(default_factory=list)
    redactions: List[str] = field(default_factory=list)
    issued_at: str = field(default_factory=now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEvent:
    id: str
    event_type: str
    actor: str
    refs: List[str]
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=now_iso)
    digest: str = ""

    @classmethod
    def create(cls, event_type: str, actor: str, refs: List[str], payload: Dict[str, Any]) -> "TraceEvent":
        event = cls(
            id=f"trace://{uuid4()}",
            event_type=event_type,
            actor=actor,
            refs=refs,
            payload=payload,
        )
        event.digest = stable_digest(
            {
                "id": event.id,
                "event_type": event.event_type,
                "actor": event.actor,
                "refs": event.refs,
                "payload": event.payload,
                "timestamp": event.timestamp,
            }
        )
        return event

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BeliefClaim:
    id: str
    claim: str
    confidence: float
    evidence: List[str]
    publisher: str
    counterevidence: List[str] = field(default_factory=list)
    review_status: str = "unreviewed"
    validity: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, claim: str, confidence: float, evidence: List[str], publisher: str) -> "BeliefClaim":
        return cls(
            id=f"belief://{uuid4()}",
            claim=claim,
            confidence=confidence,
            evidence=evidence,
            publisher=publisher,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
