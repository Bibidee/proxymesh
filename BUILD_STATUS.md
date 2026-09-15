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
- Classification-hash pinning and duplicate-voter protection in consumer.
- Deterministic model tests.
- Static source invariants and preflight checks.
- Studionet 61999 documentation.
- GenLayer CLI 0.39.1 lock/check scripts.

## Current verified status

The exact GenLayer CLI 0.39.1 is active on Studionet 61999 using the funded, unlocked deployment account. The pinned runner is `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`. Local preflight, tests, and GenVM lint/validation/schema/typecheck pass for both contracts.

Fresh hosted ProxyMesh deployment attempts still finalize with GenVM `contract_error: invalid_contract`; the returned addresses are not canonical because the authoritative RPC reports no contract code. Hosted bisection is therefore still in progress, and no live deployment or lifecycle evidence is claimed.

## CI and release evidence

The repository is pushed to `https://github.com/Bibidee/proxymesh`; remote source verification is required for each release commit. GitHub Actions runs the reproducible Python preflight, compile, and model/source-invariant test gate. The GenVM CLI/linter stack is host-provided rather than a reproducible package in this workflow, so its four checks are recorded from the verified deployment environment and are not replaced by a flaky CI installation.

Submission readiness remains blocked until both canonical contracts exist on Studionet, schema and view calls succeed, and the live lifecycle passes.
