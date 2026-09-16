# Submission summary

ProxyMesh is a standalone reusable GenLayer Intelligent Contract primitive for **semantic liquid delegation**.

A participant can delegate different governance domains to different representatives. A proposal is pinned to a sealed domain ontology and GenLayer validators independently classify which domains the proposal materially affects. ProxyMesh then resolves delegation routes deterministically. It accepts proxy authority only when every implicated domain converges to the same terminal representative; otherwise it fails closed and requires direct participation.

The model cannot create domains, select delegates, cast votes, assign weights or decide proposal outcomes. Its only nondeterministic role is selecting a bounded subset from an immutable domain list. The repository includes cycle/depth protection, expiry/revocation, ontology and classification hashes, deterministic route commitments, terminal ambiguity, provider-failure propagation, strict domain-slot validation, adversarial fail-closed behaviour, tests, documentation and a minimal consumer contract that pins the classification hash, corrects proxy-to-direct overrides, and prevents duplicate representation.

Network target: Studionet, chain ID 61999. Required CLI: 0.39.1. No frontend.

Release status: SUBMISSION READY.

- Frozen contract commit: `1d05c56d9a772f929f1c8f0d6d341d8231674626`
- ProxyMesh: `0xd7425357192780DB4497716D25d7763dAa3de2CA`
- ProxyVoteBook: `0xA67CFE520C0a4Fa6bb685DD8330f4Adb27E255aC`
- Verification: 36 tests passed; 6 Direct Mode tests passed; the real-contract 15-edge/16th-edge boundary passed; canonical Studionet lifecycle passed.
