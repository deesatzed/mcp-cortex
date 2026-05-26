# Test Results

Generated during standalone alpha publication hardening.

```text
$ python -m pytest -q
...........                                                              [100%]
11 passed

$ PYTHONPATH=src python scripts/validate_examples.py
OK context_cell_build_failure.json -> context_cell.schema.json
OK sandbox_pytest_capability.json -> capability_contract.schema.json
OK external_api_capability.json -> capability_contract.schema.json
OK safe_patch_intent.json -> intent.schema.json
OK phi_egress_intent.json -> intent.schema.json
OK belief_claim_import_mismatch.json -> belief_claim.schema.json
OK trace_event_policy_checked.json -> trace_event.schema.json

$ PYTHONPATH=src python -m mcp_cortex.cli --help
usage: mcp-cortex [-h] {validate,check-policy} ...

$ PYTHONPATH=src python examples/demo_policy_gate.py
"allowed": true
"risk_class": "green"
"trace_event_count": 3
```
