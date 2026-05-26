from examples.demo_policy_gate import run_demo


def test_demo_policy_gate_allows_local_read_and_records_trace():
    result = run_demo()

    assert result["allowed"] is True
    assert result["risk_class"] == "green"
    assert result["trace_event_count"] == 3
    assert result["result_event_type"] == "capability.result"
    assert result["result_digest"].startswith("sha256:")
