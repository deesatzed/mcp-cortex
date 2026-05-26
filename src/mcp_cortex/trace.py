from __future__ import annotations

from typing import Dict, List, Sequence

from .models import TraceEvent


class TraceLog:
    """Append-only in-memory trace log."""

    def __init__(self) -> None:
        self._events: List[TraceEvent] = []

    def append(self, event: TraceEvent) -> TraceEvent:
        self._events.append(event)
        return event

    def record(self, event_type: str, actor: str, refs: Sequence[str], payload: Dict) -> TraceEvent:
        event = TraceEvent.create(event_type=event_type, actor=actor, refs=list(refs), payload=payload)
        return self.append(event)

    def by_ref(self, ref: str) -> List[TraceEvent]:
        return [event for event in self._events if ref in event.refs]

    def all(self) -> List[TraceEvent]:
        return list(self._events)
