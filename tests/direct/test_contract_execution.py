"""Official GenLayer direct-mode execution tests.

These tests are discovered only when the pinned project's `genlayer-test`
package is installed. They execute the real contract source in Direct Mode;
the model tests remain independent and continue to run in minimal CI.
"""

import json
import inspect
import os
import sys

import pytest

pytest.importorskip("gltest")
from gltest.direct import create_address

if sys.platform == "win32":
    _real_unlink = os.unlink

    def _unlink_after_direct_loader_releases_file(path):
        try:
            _real_unlink(path)
        except PermissionError:
            pass

    os.unlink = _unlink_after_direct_loader_releases_file


def _mesh(direct_deploy):
    # The contract's pinned runner is shipped in the v0.2.12 bundle.  Passing
    # this explicitly prevents gltest from probing the incompatible v0.3
    # release, whose legacy archive URL no longer exists.
    return direct_deploy(
        "contracts/proxymesh.py",
        sdk_version=os.environ.get("GENVM_VERSION", "v0.2.12"),
    )


def _contract_address(mesh, value):
    """Use the Address type from the injected pinned contract runtime."""
    address_type = inspect.getmodule(mesh.__class__).Address
    if isinstance(value, address_type):
        return value
    if hasattr(value, "as_bytes"):
        value = value.as_bytes
    return address_type(value)


def _seed_ontology(mesh, direct_vm, owner):
    direct_vm.sender = owner
    ontology_id = mesh.create_ontology(
        "Governance Domains",
        "Treasury, security, and protocol decisions for the governed system.",
    )
    mesh.add_domain(ontology_id, "TREASURY", "Spending, budgets, and asset allocation controls.")
    mesh.add_domain(ontology_id, "SECURITY", "Incident response and emergency permission controls.")
    mesh.add_domain(ontology_id, "PROTOCOL", "Protocol logic, upgrades, and technical consensus rules.")
    mesh.seal_ontology(ontology_id)
    return ontology_id


def _mock_classification(direct_vm, payload):
    direct_vm.clear_mocks()
    direct_vm.mock_llm(
        r".*PROXYMESH / PROPOSAL DOMAIN CLASSIFICATION.*",
        json.dumps(payload),
    )


def test_real_contract_event_writes_and_terminal_classification(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    direct_alice = create_address("alice")
    direct_bob = create_address("bob")
    direct_charlie = create_address("charlie")
    mesh = _mesh(direct_deploy)
    ontology_id = _seed_ontology(mesh, direct_vm, direct_alice)

    direct_vm.sender = direct_alice
    direct_bob = _contract_address(mesh, direct_bob)
    mesh.set_delegation(ontology_id, 0, direct_bob, 0)
    direct_vm.sender = direct_bob
    direct_charlie = _contract_address(mesh, direct_charlie)
    mesh.set_delegation(ontology_id, 0, direct_charlie, 0)
    direct_vm.sender = direct_alice
    mesh.clear_delegation(ontology_id, 0)

    proposal_id = mesh.create_proposal(
        ontology_id,
        "Treasury security controls",
        "Change treasury spending controls and security permissions for the protocol.",
    )
    _mock_classification(direct_vm, {"verdict": "AMBIGUOUS", "domain_slots": [], "reason": "unclear scope"})
    result = mesh.classify_proposal(proposal_id)
    assert result["status"] == "AMBIGUOUS"
    with direct_vm.expect_revert("not draft"):
        mesh.classify_proposal(proposal_id)


def test_real_contract_strict_classification_slots(direct_vm, direct_deploy, direct_alice):
    direct_alice = create_address("alice")
    mesh = _mesh(direct_deploy)
    ontology_id = _seed_ontology(mesh, direct_vm, direct_alice)
    direct_vm.sender = direct_alice
    proposal_id = mesh.create_proposal(
        ontology_id,
        "Protocol treasury change",
        "Change protocol treasury spending and security authorization controls.",
    )
    _mock_classification(direct_vm, {"verdict": "CLASSIFIED", "domain_slots": ["1"], "reason": "bad type"})
    result = mesh.classify_proposal(proposal_id)
    assert result["status"] == "AMBIGUOUS"


def test_real_proxymesh_authorization_and_timestamp(direct_vm, direct_deploy):
    owner = create_address("owner-auth")
    other = create_address("other-auth")
    mesh = _mesh(direct_deploy)
    ontology_id = _seed_ontology(mesh, direct_vm, owner)
    runtime = inspect.getmodule(mesh.__class__)
    raw_datetime = direct_vm.get_message_raw()["datetime"]
    expected_ts = int(runtime.datetime.fromisoformat(raw_datetime.replace("Z", "+00:00")).timestamp())
    assert runtime.now_ts() == expected_ts

    direct_vm.sender = owner
    proposal_id = mesh.create_proposal(
        ontology_id, "Authorization check", "Change treasury and security authorization controls."
    )
    before = mesh.get_proposal(proposal_id)
    direct_vm.sender = other
    with direct_vm.expect_revert("proposer only"):
        mesh.classify_proposal(proposal_id)
    assert mesh.get_proposal(proposal_id) == before

    direct_vm.sender = owner
    _mock_classification(direct_vm, {"verdict": "CLASSIFIED", "domain_slots": [0], "reason": "treasury"})
    assert mesh.classify_proposal(proposal_id)["status"] == "CLASSIFIED"
    with direct_vm.expect_revert("not draft"):
        mesh.classify_proposal(proposal_id)


def test_real_proxymesh_delegation_boundaries(direct_vm, direct_deploy):
    mesh = _mesh(direct_deploy)
    owner = _contract_address(mesh, create_address("boundary-owner"))
    direct_vm.sender = owner
    draft_id = mesh.create_ontology("Duplicate test", "A separate draft ontology for duplicate testing.")
    mesh.add_domain(draft_id, "TREASURY", "Spending, budgets, and asset allocation controls.")
    with direct_vm.expect_revert("duplicate domain"):
        mesh.add_domain(draft_id, "treasury", "Another treasury description for duplicate testing.")
    ontology_id = _seed_ontology(mesh, direct_vm, owner)
    direct_vm.sender = create_address("not-owner")
    with direct_vm.expect_revert("ontology owner only"):
        mesh.add_domain(ontology_id, "OTHER", "A non-owner must not mutate the ontology.")

    chain = [_contract_address(mesh, create_address(f"A{i}")) for i in range(16)]
    new_root = _contract_address(mesh, create_address("NEW_ROOT"))
    for i in range(15):
        direct_vm.sender = chain[i]
        mesh.set_delegation(ontology_id, 0, chain[i + 1], 0)
    resolved = mesh.resolve_domain(ontology_id, 0, chain[0])
    assert resolved["status"] == 2
    assert resolved["representative"].lower() == str(chain[15]).lower()
    assert resolved["hops"] == 15
    before_root = mesh.get_delegation(ontology_id, 0, new_root)
    assert before_root == {"exists": False}
    direct_vm.sender = new_root
    with direct_vm.expect_revert("max depth"):
        mesh.set_delegation(ontology_id, 0, chain[0], 0)
    assert mesh.get_delegation(ontology_id, 0, new_root) == before_root
    resolved_after = mesh.resolve_domain(ontology_id, 0, chain[0])
    assert resolved_after["status"] == 2
    assert resolved_after["representative"].lower() == str(chain[15]).lower()
    assert resolved_after["hops"] == 15

    self_delegate = _contract_address(mesh, create_address("self-delegate"))
    direct_vm.sender = self_delegate
    with direct_vm.expect_revert("self-delegation"):
        mesh.set_delegation(ontology_id, 1, self_delegate, 0)
    direct_vm.sender = owner
    expiry = int(expected_ts_for_vm(direct_vm)) + 60
    mesh.set_delegation(ontology_id, 2, _contract_address(mesh, create_address("expiring")), expiry)
    assert mesh.get_delegation(ontology_id, 2, owner)["active"] is True
    direct_vm.warp("2035-01-01T00:00:00Z")
    inspect.getmodule(mesh.__class__).gl.message_raw["datetime"] = "2035-01-01T00:00:00Z"
    assert mesh.get_delegation(ontology_id, 2, owner)["active"] is False
    direct_vm.warp("2026-09-16T07:00:00Z")
    inspect.getmodule(mesh.__class__).gl.message_raw["datetime"] = "2026-09-16T07:00:00Z"
    direct_vm.sender = owner
    mesh.set_delegation(ontology_id, 2, _contract_address(mesh, create_address("revoked")), 0)
    mesh.clear_delegation(ontology_id, 2)
    assert mesh.get_delegation(ontology_id, 2, owner)["active"] is False


def expected_ts_for_vm(direct_vm):
    value = direct_vm.get_message_raw()["datetime"]
    return int(__import__("datetime").datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())


def _consumer(direct_deploy, mesh):
    _reset_runtime_contract_registry()
    return direct_deploy(
        "contracts/proxy_vote_book.py",
        mesh.address,
        sdk_version=os.environ.get("GENVM_VERSION", "v0.2.12"),
    )


def _reset_runtime_contract_registry():
    import genlayer.gl.genvm_contracts as contracts_runtime
    contracts_runtime.__known_contract__ = None


def test_real_proxymesh_classification_paths_and_routes(direct_vm, direct_deploy):
    alice = create_address("route-alice")
    bob = create_address("route-bob")
    carol = create_address("route-carol")
    dave = create_address("route-dave")
    mesh = _mesh(direct_deploy)
    alice = _contract_address(mesh, alice)
    bob = _contract_address(mesh, bob)
    carol = _contract_address(mesh, carol)
    dave = _contract_address(mesh, dave)
    ontology_id = _seed_ontology(mesh, direct_vm, alice)
    direct_vm.sender = alice
    mesh.set_delegation(ontology_id, 0, carol, 0)
    mesh.set_delegation(ontology_id, 1, bob, 0)
    direct_vm.sender = bob
    mesh.set_delegation(ontology_id, 1, carol, 0)
    direct_vm.sender = alice
    proposal_id = mesh.create_proposal(
        ontology_id, "Treasury security proposal", "Change treasury spending and security controls together."
    )
    _mock_classification(direct_vm, {"verdict": "CLASSIFIED", "domain_slots": [0, 1], "reason": "both domains"})
    classified = mesh.classify_proposal(proposal_id)
    assert classified["status"] == "CLASSIFIED"
    route = mesh.resolve_authority(proposal_id, alice)
    assert route["status"] == 2 and route["representative"].lower() == str(carol).lower()

    direct_vm.sender = alice
    split_id = mesh.create_proposal(
        ontology_id, "Split route proposal", "Change treasury spending and security controls together."
    )
    _mock_classification(direct_vm, {"verdict": "CLASSIFIED", "domain_slots": [0, 1], "reason": "both domains"})
    mesh.classify_proposal(split_id)
    direct_vm.sender = alice
    mesh.set_delegation(ontology_id, 1, dave, 0)
    assert mesh.resolve_authority(split_id, alice)["status"] == 3

    ambiguous_id = mesh.create_proposal(
        ontology_id, "Unclear proposal", "This proposal does not identify a safe domain decision."
    )
    _mock_classification(direct_vm, {"verdict": "CLASSIFIED", "domain_slots": ["0"], "reason": "malformed"})
    assert mesh.classify_proposal(ambiguous_id)["status"] == "AMBIGUOUS"
    with direct_vm.expect_revert("not draft"):
        mesh.classify_proposal(ambiguous_id)

    failed_id = mesh.create_proposal(
        ontology_id, "Provider failure", "A provider failure must not consume this proposal attempt."
    )
    direct_vm.clear_mocks()
    direct_vm.strict_mocks = True
    with direct_vm.expect_revert():
        mesh.classify_proposal(failed_id)
    direct_vm.strict_mocks = False
    assert mesh.get_proposal(failed_id)["status"] == 0


def test_real_proxy_vote_book_constructor_guard_and_deployment(direct_vm, direct_deploy):
    mesh = _mesh(direct_deploy)
    _reset_runtime_contract_registry()
    with direct_vm.expect_revert("zero"):
        direct_deploy("contracts/proxy_vote_book.py", mesh.address.__class__(bytes(20)), sdk_version=os.environ.get("GENVM_VERSION", "v0.2.12"))
    vote_book = _consumer(direct_deploy, mesh)
    assert vote_book is not None
