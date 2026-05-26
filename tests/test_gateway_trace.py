from mcp_cortex import CapabilityContract, CortexGateway, Intent, TraceEvent


def test_gateway_records_intent_and_policy_trace_events():
    gateway = CortexGateway()
    capability = CapabilityContract(
        capability="capability://sandbox/pytest",
        version="1.0.0",
        input_schema={"type": "object"},
        effects=["read:file", "write:sandbox", "execute:test"],
        forbidden_effects=["network:external", "read:secrets", "write:production"],
        requires=[],
        assurance_level="A2",
    )
    intent = Intent.create(
        goal={"desired_state": "repo.tests.green"},
        requested_effects=["read:file", "write:sandbox", "execute:test"],
        constraints={"no_external_network": True},
        requester="agent://debugger",
    )

    decision = gateway.propose_and_check(intent, capability, context_labels=["code"])
    assert decision.allowed is True

    events = gateway.trace_log.all()
    assert [event.event_type for event in events] == ["intent.proposed", "policy.checked"]
    assert all(event.digest.startswith("sha256:") for event in events)


def test_trace_digest_changes_when_payload_changes():
    event_a = TraceEvent.create("test", "actor://a", ["ref://1"], {"value": 1})
    event_b = TraceEvent.create("test", "actor://a", ["ref://1"], {"value": 2})
    assert event_a.digest != event_b.digest
