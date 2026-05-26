from pathlib import Path
import json
import jsonschema

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


def load(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_all_examples_validate_against_schemas():
    for example_name, schema_name in EXAMPLE_SCHEMA_MAP.items():
        jsonschema.validate(
            instance=load(ROOT / "examples" / example_name),
            schema=load(ROOT / "schemas" / schema_name),
        )
