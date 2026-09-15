# ProxyMesh architecture

ProxyMesh is a contract-only semantic liquid-delegation primitive. It deliberately does not implement a governance frontend or a full DAO product.

## Primitive boundary

1. An ontology owner creates a finite domain ontology, for example `TREASURY`, `SECURITY`, `PROTOCOL`, `COMMUNITY`.
2. The ontology is sealed. The resulting definition hash is immutable for every proposal that references it.
3. Voters create domain-scoped delegation edges. Delegation can be transitive, expiring and revocable.
4. A proposal is created against one exact ontology hash.
5. GenLayer consensus classifies the proposal into a bounded domain bitmask. Validators independently rerun the classification and must agree on the exact bitmask.
6. ProxyMesh resolves each implicated domain's delegation route deterministically.
7. If all routes converge to one representative, a consumer may accept that representative. If routes split, ProxyMesh fails closed and recommends a direct vote.

## Why the LLM has limited power

The model cannot create domains, choose delegates, cast votes, change weights or decide governance outcomes. It can only select from the already sealed finite domain set. The selected domain IDs are converted into a deterministic bitmask.

## Cross-contract consumer

`contracts/proxy_vote_book.py` is intentionally small. It demonstrates the primitive boundary:

- a voter can always vote directly, overriding delegation;
- otherwise a caller may represent the voter only when `resolve_authority()` returns a converged route;
- the consumer pins the proposal `classification_hash` to prevent semantic substitution;
- one voter can only be represented once per proposal.

The consumer is evidence of reusability, not a frontend or a full governance application.
