from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .models import CapabilityContract, Intent
from .policy import PolicyEngine


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _cmd_validate(args: argparse.Namespace) -> int:
    try:
        import jsonschema
    except ImportError as exc:
        raise SystemExit("jsonschema is required for validation. Install with pip install -e '.[dev]'.") from exc

    instance = _load_json(args.instance)
    schema = _load_json(args.schema)
    jsonschema.validate(instance=instance, schema=schema)
    print(f"OK: {args.instance} validates against {args.schema}")
    return 0


def _intent_from_json(data: Dict[str, Any]) -> Intent:
    return Intent(
        id=data["id"],
        goal=data["goal"],
        requested_effects=data["requested_effects"],
        constraints=data.get("constraints", {}),
        requester=data["requester"],
        context_refs=data.get("context_refs", []),
        success_metrics=data.get("success_metrics", []),
        deadline=data.get("deadline"),
        status=data.get("status", "proposed"),
    )


def _capability_from_json(data: Dict[str, Any]) -> CapabilityContract:
    return CapabilityContract(
        capability=data["capability"],
        version=data["version"],
        input_schema=data.get("input_schema", {"type": "object"}),
        effects=data.get("effects", []),
        forbidden_effects=data.get("forbidden_effects", []),
        requires=data.get("requires", []),
        assurance_level=data.get("assurance_level", "A0"),
        preconditions=data.get("preconditions", []),
        postconditions=data.get("postconditions", []),
        data_flow_rules=data.get("data_flow_rules", []),
        rollback=data.get("rollback"),
        risk=data.get("risk", "unknown"),
        attestation=data.get("attestation"),
    )


def _cmd_check_policy(args: argparse.Namespace) -> int:
    intent = _intent_from_json(_load_json(args.intent))
    capability = _capability_from_json(_load_json(args.capability))
    labels = args.context_label or []
    decision = PolicyEngine().check(intent, capability, context_labels=labels)
    status = "ALLOWED" if decision.allowed else "BLOCKED/NEEDS APPROVAL"
    print(f"{status} | risk={decision.risk_class}")
    for reason in decision.reasons:
        print(f"- {reason}")
    if decision.required_approvals:
        print("Approvals:")
        for approval in decision.required_approvals:
            print(f"- {approval}")
    return 0 if decision.allowed else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mcp-cortex")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Validate a JSON file against a JSON Schema")
    validate.add_argument("instance")
    validate.add_argument("--schema", required=True)
    validate.set_defaults(func=_cmd_validate)

    check = sub.add_parser("check-policy", help="Check an intent against a capability contract")
    check.add_argument("intent")
    check.add_argument("capability")
    check.add_argument("--context-label", action="append", default=[])
    check.set_defaults(func=_cmd_check_policy)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
