# Build status

## Completed in this package

- Contract-only repository structure; no frontend.
- ProxyMesh ontology lifecycle and immutable definition hash.
- Bounded semantic proposal classification with independent validator rerun.
- Domain bitmask representation.
- Domain-scoped transitive delegation.
- Delegation expiry, revocation, max-depth protection and cycle prevention.
- Multi-domain convergence and fail-closed split authority.
- Direct-vote override demonstrated in a minimal consumer contract.
- Direct-vote override replaces an earlier proxy receipt with exact tally correction.
- Ambiguous classifications are terminal; provider failures are not semantic ambiguity.
- Delegation creation and resolution share a 15-edge maximum.
- Classification-hash pinning and duplicate-voter protection in consumer.
- Deterministic model tests.
- Static source invariants and preflight checks.
- Studionet 61999 documentation.
- GenLayer CLI 0.39.1 lock/check scripts.

## Current verified status

The exact GenLayer CLI 0.39.1 is active on Studionet 61999 using the funded, unlocked deployment account. The pinned runner is `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`.

Canonical deployments:

- ProxyMesh: `0xd7425357192780DB4497716D25d7763dAa3de2CA`
- ProxyVoteBook: `0xA67CFE520C0a4Fa6bb685DD8330f4Adb27E255aC`

## CI and release evidence

The repository is pushed to `https://github.com/Bibidee/proxymesh`; remote source verification is required for each release commit. GitHub Actions pins and downloads GenVM v0.2.12, installs `genlayer-test==0.29.2` and `genvm-linter==0.11.0`, and runs preflight, compile, AST safety check, validate, schema, typecheck, model/source-invariant tests and Direct Mode execution tests.

CI PASS; GenVM check PASS; schema PASS; typecheck PASS; 36 tests PASS; 6 Direct Mode PASS; canonical Studionet lifecycle PASS. Final readiness: SUBMISSION READY.
