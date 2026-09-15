from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "contracts" / "proxymesh.py").read_text(encoding="utf-8")
CONSUMER = (ROOT / "contracts" / "proxy_vote_book.py").read_text(encoding="utf-8")


def test_no_frontend_tree():
    banned = ["package.json", "vite.config", "next.config", "src/App", "frontend/"]
    listing = "\n".join(str(p.relative_to(ROOT)) for p in ROOT.rglob("*"))
    for item in banned:
        assert item not in listing


def test_custom_consensus_present():
    assert "gl.vm.run_nondet_default" in MAIN
    assert "validator_fn" in MAIN
    assert "gl.nondet.exec_prompt" in MAIN


def test_semantic_output_is_bounded():
    assert "domain_slots" in MAIN
    assert "slots_to_mask" in MAIN
    assert "MAX_DOMAINS = 12" in MAIN


def test_cycle_and_depth_protection_present():
    assert "delegation would create a cycle" in MAIN
    assert "MAX_DELEGATION_DEPTH" in MAIN


def test_consumer_proves_cross_contract_use():
    assert "@gl.contract_interface" in CONSUMER
    assert "resolve_authority" in CONSUMER
    assert "DIRECT_OVERRIDE" in CONSUMER
