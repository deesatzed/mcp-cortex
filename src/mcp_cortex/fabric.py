from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence

from .models import ContextCell


class ContextFabric:
    """In-memory context fabric.

    This is intentionally small. Codex should replace it with a storage backend
    interface and SQLite/Postgres implementation in the next iteration.
    """

    def __init__(self) -> None:
        self._cells: Dict[str, ContextCell] = {}

    def publish(self, cell: ContextCell) -> ContextCell:
        self._cells[cell.id] = cell
        return cell

    def get(self, cell_id: str) -> Optional[ContextCell]:
        return self._cells.get(cell_id)

    def query(
        self,
        *,
        labels: Sequence[str] | None = None,
        text: str | None = None,
        trust_level: str | None = None,
        limit: int = 20,
    ) -> List[ContextCell]:
        label_set = set(labels or [])
        text_lower = text.lower() if text else None
        results: List[ContextCell] = []
        for cell in self._cells.values():
            if label_set and not label_set.issubset(set(cell.labels)):
                continue
            if trust_level and cell.trust_level != trust_level:
                continue
            if text_lower and text_lower not in cell.summary.lower():
                continue
            results.append(cell)
            if len(results) >= limit:
                break
        return results

    def materialize(self, refs: Sequence[str], *, max_cells: int = 10) -> List[dict]:
        materialized: List[dict] = []
        for ref in refs[:max_cells]:
            cell = self.get(ref)
            if cell is not None:
                materialized.append(
                    {
                        "id": cell.id,
                        "schema": cell.schema,
                        "summary": cell.summary,
                        "labels": cell.labels,
                        "confidence": cell.confidence,
                        "trust_level": cell.trust_level,
                        "links": cell.links,
                    }
                )
        return materialized

    def all_ids(self) -> List[str]:
        return list(self._cells.keys())
