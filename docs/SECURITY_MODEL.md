# Security model

## Protected invariants

- Ontologies are mutable only before sealing.
- Proposal classification is pinned to the sealed ontology hash.
- Semantic classification is bounded to at most 12 existing domain slots.
- Validators independently rerun classification and require exact verdict + bitmask agreement.
- Provider/runtime failures propagate instead of being converted into semantic ambiguity.
- An ambiguous classification is terminal and cannot be rerolled.
- Delegation cannot self-reference or create a cycle at creation time.
- Delegation traversal is depth-bounded to 15 active edges and fails closed on broken/cyclic routes.
- Expired or revoked edges are ignored.
- Multi-domain proposals are proxy-routable only if every implicated domain converges to the same terminal representative.
- Split authority never lets the model choose which delegate wins; consumers should require a direct vote.
- The example consumer lets the voter replace an earlier proxy receipt by voting directly; a direct receipt cannot be replaced.
- Consumer receipts pin the exact classification hash and prevent duplicate representation.

## Trust boundaries

ProxyMesh does not assert that an ontology is politically correct or complete. The ontology owner chooses the domain vocabulary. Consensus only maps proposal semantics into that frozen vocabulary.

ProxyMesh does not assign voting weight, quorum, proposal outcomes or treasury authority. Those belong to consumer contracts.

## Fail-closed cases

- ambiguous semantic classification;
- unknown or changed ontology hash;
- empty classified domain set;
- delegation cycle/depth overflow;
- split terminal representatives across implicated domains;
- consumer classification-hash mismatch.
