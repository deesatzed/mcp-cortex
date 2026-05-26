#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

try:
    import jsonschema
except ImportError as exc:
    raise SystemExit("jsonschema is required. Install with: pip install -e '.[dev]'") from exc

ROOT = Path(__file__).resolve().parents[1]

EXAMPLE_SCHEMA_MAP = {
    "context_cell_build_failure.json": "context_cell.schema.json",
    "sandbox_pytest_capability.json": "capability_contract.schema.json",
    "external_api_capability.json": "capability_contract.schema.json",
    "safe_patch_intent.json": "intent.schema.json",
    "phi_egress_intent.json": "intent.schema.json",
    "belief_claim_import_mismatch.json": "belief_claim.schema.json",
    "trace_event_policy_checked.json": "trace_event.schema.json",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    failures = []
    for example_name, schema_name in EXAMPLE_SCHEMA_MAP.items():
        example_path = ROOT / "examples" / example_name
        schema_path = ROOT / "schemas" / schema_name
        instance = load_json(example_path)
        schema = load_json(schema_path)
        try:
            jsonschema.validate(instance=instance, schema=schema)
        except jsonschema.ValidationError as exc:
            failures.append(f"{example_name} failed {schema_name}: {exc.message}")
        else:
            print(f"OK {example_name} -> {schema_name}")
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
