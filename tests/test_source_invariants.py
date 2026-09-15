from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "contracts" / "proxymesh.py").read_text(encoding="utf-8")
CONSUMER = (ROOT / "contracts" / "proxy_vote_book.py").read_text(encoding="utf-8")


def test_genlayer_depends_header_is_first_and_only_leading_comment():
    expected = '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }'
    for name in ("proxymesh.py", "proxy_vote_book.py"):
        lines = (ROOT / "contracts" / name).read_text(encoding="utf-8").splitlines()
        assert lines[0] == expected, f"{name} must begin with the pinned Depends declaration"
        assert len(lines) > 1 and lines[1] == "", f"{name} must not have a second leading comment"


def test_no_frontend_tree():
    banned = ["package.json", "vite.config", "next.config", "src/App", "frontend/"]
    listing = "\n".join(str(p.relative_to(ROOT)) for p in ROOT.rglob("*"))
    for item in banned:
        assert item not in listing


def test_custom_consensus_present():
    tree = ast.parse(MAIN)
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Attribute)
        and isinstance(node.func.value.value, ast.Name)
        and node.func.value.value.id == "gl"
        and node.func.value.attr == "vm"
        and node.func.attr in {"run_nondet", "run_nondet_unsafe"}
    ]
    assert calls, "executable gl.vm.run_nondet call is required"
    assert "gl.vm.run_nondet_unsafe(leader_fn, validator_fn)" in MAIN
    default_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "run_nondet_default"
    ]
    assert not default_calls
    assert "validator_fn" in MAIN
    assert "gl.nondet.exec_prompt" in MAIN
    assert "independent = classify_once" in MAIN
    assert "except Exception" not in MAIN


def test_semantic_output_is_bounded():
    assert "domain_slots" in MAIN
    assert "slots_to_mask" in MAIN
    assert "MAX_DOMAINS = 12" in MAIN


def test_cycle_and_depth_protection_present():
    assert "delegation would create a cycle" in MAIN
    assert "MAX_DELEGATION_DEPTH" in MAIN
    assert "edges = 1" in MAIN
    assert "PROPOSAL_AMBIGUOUS = 3" in MAIN


def test_event_topic_safety_and_emission_shape():
    tree = ast.parse(MAIN)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and any(
            isinstance(base, ast.Attribute) and base.attr == "Event" for base in node.bases
        ):
            init = next(item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == "__init__")
            positional = [arg for arg in (init.args.posonlyargs + init.args.args) if arg.arg != "self"]
            assert len(positional) <= 3, f"{node.name} exceeds the three indexed-topic limit"
    assert "DelegationSet(int(ontology_id), int(domain_slot), delegator, delegate=" in MAIN


def test_ambiguous_and_direct_override_guards_present():
    assert "proposal.status = PROPOSAL_AMBIGUOUS" in MAIN
    assert "existing.caster == voter" in CONSUMER
    assert "DIRECT_OVERRIDE" in CONSUMER
    assert "tally underflow" in CONSUMER


def test_consumer_proves_cross_contract_use():
    assert "@gl.contract_interface" in CONSUMER
    assert "resolve_authority" in CONSUMER
    assert "DIRECT_OVERRIDE" in CONSUMER


def test_consumer_requires_classified_proposal_before_vote():
    assert "PROPOSAL_CLASSIFIED = 1" in CONSUMER
    assert 'proposal.get("status", -1)' in CONSUMER
    assert "proposal must be classified before voting" in CONSUMER
    assert "classification hash mismatch" in CONSUMER
