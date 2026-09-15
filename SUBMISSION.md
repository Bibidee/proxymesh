# Submission summary

ProxyMesh is a standalone reusable GenLayer Intelligent Contract primitive for **semantic liquid delegation**.

A participant can delegate different governance domains to different representatives. A proposal is pinned to a sealed domain ontology and GenLayer validators independently classify which domains the proposal materially affects. ProxyMesh then resolves delegation routes deterministically. It accepts proxy authority only when every implicated domain converges to the same terminal representative; otherwise it fails closed and requires direct participation.

The model cannot create domains, select delegates, cast votes, assign weights or decide proposal outcomes. Its only nondeterministic role is selecting a bounded subset from an immutable domain list. The repository includes cycle/depth protection, expiry/revocation, ontology and classification hashes, deterministic route commitments, adversarial fail-closed behaviour, tests, documentation and a minimal consumer contract that pins the classification hash and prevents duplicate representation.

Network target: Studionet, chain ID 61999. Required CLI: 0.39.1. No frontend.
