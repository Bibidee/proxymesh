from dataclasses import dataclass

ROUTE_DIRECT = 1
ROUTE_CONVERGED = 2
ROUTE_SPLIT = 3
ROUTE_BROKEN = 4
MAX_DEPTH = 16


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
