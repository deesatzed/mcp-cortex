from mcp_cortex import CapabilityContract, Intent, PolicyEngine


def capability(**overrides):
    data = dict(
        capability="capability://sandbox/pytest",
        version="1.0.0",
        input_schema={"type": "object"},
        effects=["read:file", "write:sandbox", "execute:test"],
        forbidden_effects=["read:secrets", "write:production", "network:external", "deploy:production"],
        requires=[],
        assurance_level="A2",
    )
    data.update(overrides)
    return CapabilityContract(**data)


def intent(effects, constraints=None):
    return Intent.create(
        goal={"desired_state": "repo.tests.green"},
        requested_effects=effects,
        constraints=constraints or {"no_external_network": True},
        requester="agent://debugger",
    )


def test_safe_sandbox_execution_allowed():
    decision = PolicyEngine().check(
        intent(["read:file", "write:sandbox", "execute:test"]),
        capability(),
        context_labels=["code"],
    )
    assert decision.allowed is True
    assert decision.risk_class == "green"


def test_external_network_denied_when_constraint_forbids_it():
    cap = capability(effects=["read:file", "network:external"], forbidden_effects=[])
    decision = PolicyEngine().check(intent(["read:file", "network:external"]), cap, context_labels=["code"])
    assert decision.allowed is False
    assert decision.risk_class == "red"


def test_phi_external_network_denied():
    cap = capability(effects=["read:context", "network:external"], forbidden_effects=[])
    unsafe_intent = Intent.create(
        goal={"desired_state": "send patient summary"},
        requested_effects=["read:context", "network:external"],
        constraints={"no_external_network": False},
        requester="agent://clinical-assistant",
    )
    decision = PolicyEngine().check(unsafe_intent, cap, context_labels=["PHI"])
    assert decision.allowed is False
    assert decision.risk_class == "red"
    assert "PHI" in decision.redactions


def test_production_write_requires_approval_if_not_forbidden():
    cap = capability(
        effects=["write:production"],
        forbidden_effects=[],
        assurance_level="A3",
    )
    prod_intent = Intent.create(
        goal={"desired_state": "deploy patch"},
        requested_effects=["write:production"],
        constraints={"no_external_network": True},
        requester="agent://release-manager",
    )
    decision = PolicyEngine().check(prod_intent, cap, context_labels=["code"])
    assert decision.allowed is False
    assert decision.risk_class == "orange"
    assert "explicit_human_approval" in decision.required_approvals


def test_forbidden_effect_is_blocked_even_if_requested():
    cap = capability()
    decision = PolicyEngine().check(intent(["read:secrets"]), cap, context_labels=["code"])
    assert decision.allowed is False
    assert decision.risk_class == "red"
