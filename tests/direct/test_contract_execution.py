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
    return direct_deploy("contracts/proxymesh.py")


def _contract_address(mesh, value):
    """Use the Address type from the injected pinned contract runtime."""
    address_type = inspect.getmodule(mesh.__class__).Address
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
    direct_vm.mock_llm(
        r".*PROXYMESH / PROPOSAL DOMAIN CLASSIFICATION.*",
        json.dumps({"verdict": "AMBIGUOUS", "domain_slots": [], "reason": "unclear scope"}),
    )
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
    direct_vm.mock_llm(
        r".*PROXYMESH / PROPOSAL DOMAIN CLASSIFICATION.*",
        json.dumps({"verdict": "CLASSIFIED", "domain_slots": ["1"], "reason": "bad type"}),
    )
    result = mesh.classify_proposal(proposal_id)
    assert result["status"] == "AMBIGUOUS"
