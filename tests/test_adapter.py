from mcp_cortex import PolicyEngine, Intent, wrap_mcp_tool_as_capability


def test_unknown_mcp_tool_wraps_conservatively():
    tool = {"name": "run_tests", "description": "Run tests", "inputSchema": {"type": "object"}}
    cap = wrap_mcp_tool_as_capability(tool)

    assert cap.capability == "capability://wrapped/run_tests"
    assert cap.effects == ["tool:call"]
    assert cap.assurance_level == "A0"
    assert "human_review_for_unknown_effects" in cap.requires

    intent = Intent.create(
        goal={"desired_state": "tests.green"},
        requested_effects=["tool:call"],
        constraints={},
        requester="agent://debugger",
    )
    decision = PolicyEngine().check(intent, cap, context_labels=["code"])
    assert decision.allowed is False
    assert decision.risk_class == "orange"
