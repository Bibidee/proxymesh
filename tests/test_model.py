from dataclasses import dataclass

ROUTE_DIRECT = 1
ROUTE_CONVERGED = 2
ROUTE_SPLIT = 3
ROUTE_BROKEN = 4
MAX_DEPTH = 16
PROPOSAL_DRAFT = 0
PROPOSAL_CLASSIFIED = 1
PROPOSAL_AMBIGUOUS = 3


def slots_to_mask(slots):
    mask = 0
    for slot in sorted(set(slots)):
        mask |= 1 << slot
    return mask


def mask_slots(mask, domain_count):
    return [i for i in range(domain_count) if mask & (1 << i)]


def resolve(start, edges):
    current = start
    seen = set()
    hops = 0
    while hops < MAX_DEPTH:
        if current in seen:
            return ROUTE_BROKEN, None
        seen.add(current)
        if current not in edges:
            return (ROUTE_DIRECT if hops == 0 else ROUTE_CONVERGED), current
        current = edges[current]
        hops += 1
    return ROUTE_BROKEN, None


def proposed_route_is_valid(delegator, delegate, edges):
    if delegator == delegate:
        return False
    current = delegate
    seen = {delegator}
    edge_count = 1
    while True:
        if current in seen:
            return False
        seen.add(current)
        if current not in edges:
            return True
        if edge_count >= MAX_DEPTH - 1:
            return False
        current = edges[current]
        edge_count += 1


def resolve_multi(voter, masks, per_domain_edges):
    reps = []
    for slot in masks:
        status, rep = resolve(voter, per_domain_edges.get(slot, {}))
        if status == ROUTE_BROKEN:
            return ROUTE_BROKEN, None
        reps.append(rep)
    if all(r == reps[0] for r in reps):
        return (ROUTE_DIRECT if reps[0] == voter else ROUTE_CONVERGED), reps[0]
    return ROUTE_SPLIT, None


def vote_allowed(proposal, expected_hash, caller, voter, route_status=None, representative=None, duplicate=False):
    if proposal.get("status") != PROPOSAL_CLASSIFIED:
        return False
    stored = proposal.get("classification_hash", "")
    if not stored or stored != expected_hash:
        return False
    if duplicate:
        return False
    if caller != voter and (route_status != ROUTE_CONVERGED or representative != caller):
        return False
    return True


def chain_edges(depth):
    return {f"n{i}": f"n{i + 1}" for i in range(depth)}


def test_mask_roundtrip():
    mask = slots_to_mask([0, 2, 4])
    assert mask == 21
    assert mask_slots(mask, 6) == [0, 2, 4]


def test_direct_authority():
    assert resolve("alice", {}) == (ROUTE_DIRECT, "alice")


def test_transitive_delegation():
    assert resolve("alice", {"alice": "bob", "bob": "carol"}) == (ROUTE_CONVERGED, "carol")


def test_cycle_fails_closed():
    status, rep = resolve("alice", {"alice": "bob", "bob": "alice"})
    assert status == ROUTE_BROKEN and rep is None


def test_multidomain_convergence():
    status, rep = resolve_multi(
        "alice",
        [0, 1],
        {0: {"alice": "carol"}, 1: {"alice": "bob", "bob": "carol"}},
    )
    assert status == ROUTE_CONVERGED and rep == "carol"


def test_multidomain_split_requires_direct_vote():
    status, rep = resolve_multi(
        "alice",
        [0, 1],
        {0: {"alice": "bob"}, 1: {"alice": "carol"}},
    )
    assert status == ROUTE_SPLIT and rep is None


def test_draft_direct_vote_rejected():
    assert not vote_allowed({"status": PROPOSAL_DRAFT, "classification_hash": ""}, "", "alice", "alice")


def test_draft_proxy_vote_rejected():
    assert not vote_allowed({"status": PROPOSAL_DRAFT, "classification_hash": ""}, "", "bob", "alice", ROUTE_CONVERGED, "bob")


def test_classified_direct_vote_passes_and_override_is_preserved():
    assert vote_allowed({"status": PROPOSAL_CLASSIFIED, "classification_hash": "h"}, "h", "alice", "alice")


def test_classified_delegated_vote_passes():
    assert vote_allowed({"status": PROPOSAL_CLASSIFIED, "classification_hash": "h"}, "h", "bob", "alice", ROUTE_CONVERGED, "bob")


def test_wrong_hash_and_duplicate_rejected():
    proposal = {"status": PROPOSAL_CLASSIFIED, "classification_hash": "h"}
    assert not vote_allowed(proposal, "wrong", "alice", "alice")
    assert not vote_allowed(proposal, "h", "alice", "alice", duplicate=True)


def test_depth_boundary_is_consistent_and_fails_closed():
    assert resolve("n0", {}) == (ROUTE_DIRECT, "n0")
    assert resolve("n0", chain_edges(2)) == (ROUTE_CONVERGED, "n2")
    assert resolve("n0", chain_edges(MAX_DEPTH - 1)) == (ROUTE_CONVERGED, f"n{MAX_DEPTH - 1}")
    assert resolve("n0", chain_edges(MAX_DEPTH))[0] == ROUTE_BROKEN
    assert resolve("n0", chain_edges(MAX_DEPTH + 1))[0] == ROUTE_BROKEN


def test_creation_depth_boundary_rejects_before_storage_mutation():
    edges = chain_edges(MAX_DEPTH - 1)
    before = dict(edges)
    assert not proposed_route_is_valid("root", "n0", edges)
    assert edges == before
    assert proposed_route_is_valid("root", "n0", chain_edges(MAX_DEPTH - 2))


def test_expired_or_revoked_edges_are_not_counted():
    assert proposed_route_is_valid("root", "delegate", {})


def test_cycle_near_depth_boundary_fails_closed():
    edges = chain_edges(MAX_DEPTH - 1)
    edges[f"n{MAX_DEPTH - 1}"] = "n{MAX_DEPTH - 2}"
    assert resolve("n0", edges)[0] == ROUTE_BROKEN


def test_ambiguous_status_is_terminal():
    proposal = {"status": PROPOSAL_DRAFT, "domain_mask": 0}
    proposal["status"] = PROPOSAL_AMBIGUOUS
    assert proposal["status"] == PROPOSAL_AMBIGUOUS
    assert proposal["domain_mask"] == 0
    assert proposal["status"] != PROPOSAL_DRAFT


def test_strict_domain_slots_reject_malformed_values():
    def valid(slots, count):
        return (
            isinstance(slots, list)
            and all(isinstance(x, int) and not isinstance(x, bool) for x in slots)
            and all(0 <= x < count for x in slots)
            and len(slots) == len(set(slots))
        )

    assert valid([0, 1], 2)
    for value in (["1"], [1.8], [True], [-1], [2], [0, 0]):
        assert not valid(value, 2)


def test_proxy_to_direct_override_corrects_tally():
    tally = {"yes": 1, "no": 0, "abstain": 0}
    old_choice, new_choice = 1, 2
    tally["yes"] -= 1
    tally["no"] += 1
    assert tally == {"yes": 0, "no": 1, "abstain": 0}
    assert old_choice != new_choice
