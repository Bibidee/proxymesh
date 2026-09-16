# ProxyMesh

**Semantic liquid-delegation routing for GenLayer governance consumers.**

ProxyMesh solves a problem ordinary liquid democracy cannot solve safely: a voter may delegate treasury decisions to Alice, security decisions to Bob and protocol decisions to Carol, but a natural-language proposal does not arrive with a trustworthy domain label. Letting the proposal author choose the label lets them route voting authority strategically.

ProxyMesh freezes a bounded governance-domain ontology, uses GenLayer consensus to map each proposal into that ontology, and then resolves delegation routes deterministically. The model never chooses the representative and never decides the vote. If all implicated domain routes converge, a consumer can accept the resolved representative. If they split, ProxyMesh fails closed and the voter must act directly.

## Submission scope

This repository is intentionally **contract-only**. There is no frontend, dashboard, wallet UI, Next.js, React or Vite application.

- `contracts/proxymesh.py` — reusable primitive.
- `contracts/proxy_vote_book.py` — minimal consumer proving cross-contract reuse.
- `tests/` — deterministic model and source-invariant tests.
- `docs/` — architecture, security and live-lifecycle specification.

## Verified release

- Frozen contract commit: `1d05c56d9a772f929f1c8f0d6d341d8231674626`
- ProxyMesh: `0xd7425357192780DB4497716D25d7763dAa3de2CA`
- ProxyVoteBook: `0xA67CFE520C0a4Fa6bb685DD8330f4Adb27E255aC`
- Studionet chain ID: `61999`
- Submission status: READY

## Network

ProxyMesh is locked to stable GenLayer Studionet:

- chain ID: **61999**
- RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`
- CLI: **0.39.1**

Do not change this repository to a dev/preview chain and do not use the v0.40 RC CLI line.

## Core lifecycle

```text
create ontology
      ↓
add finite domains
      ↓
seal ontology + definition hash
      ↓
voters delegate by domain
      ↓
create natural-language proposal
      ↓
GenLayer validators independently classify exact domain bitmask
      ↓
deterministic route resolution
      ↓
CONVERGED → consumer may accept proxy
SPLIT     → fail closed; voter acts directly
```

## Consensus design

The leader receives only a frozen proposal and a frozen finite domain list. It may return `CLASSIFIED` with a domain bitmask or `AMBIGUOUS`. Validators independently rerun the same semantic task. Acceptance requires the exact verdict and exact mask to match; rationale wording does not drive state.

This avoids a format-only validator and keeps nondeterminism narrowly bounded.

## Local checks

```bash
python scripts/preflight.py
pytest -q
```

Before any real deployment:

```bash
npm install -g genlayer@0.39.1
genlayer --version
genlayer network set studionet
genlayer network info
```

The final deployment and live evidence steps are in `AGENT_HANDOFF.md` and `docs/LIVE_TEST_PLAN.md`.
