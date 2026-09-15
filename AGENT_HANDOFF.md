# Agent handoff — finish ProxyMesh completely

Finish ProxyMesh completely from the repository folder I have opened for you.

Do not just review it, give me a plan, or return a checklist. Inspect the existing repository, run the actual checks, fix anything necessary, test it in the real GenLayer runtime, deploy it, collect live evidence, and push the finished repository to:

`https://github.com/Bibidee/proxymesh`

## Non-negotiable product scope

ProxyMesh is a **standalone GenLayer Intelligent Contract submission**.

It must NOT have a frontend.

Do not add Next.js, React, Vite, wallet UI, dashboard, landing page or product frontend. The main submission is the reusable contract primitive. `proxy_vote_book.py` is only a tiny consumer contract proving reuse.

## Non-negotiable network

Use only:

- network: `studionet`
- chain ID: `61999`
- RPC: `https://studio.genlayer.com/api`
- explorer: `https://explorer-studio.genlayer.com`

Do not migrate the project to any preview/dev chain. Before any transaction, verify the real network and stop if it is not chain 61999.

## Non-negotiable CLI

Use **GenLayer CLI 0.39.1**.

Do not use CLI 0.4.0 and do not use the v0.40 RC line for this repository. The CLI can be installed/used locally on this machine; it must not become a project dependency.

First run:

```powershell
./scripts/check-cli.ps1
```

or on bash:

```bash
./scripts/check-cli.sh
```

If the exact CLI is missing, install the exact stable version:

```bash
npm install -g genlayer@0.39.1
```

Then verify again. Do not silently substitute another version.

## Read these first, in full

1. `README.md`
2. `BUILD_STATUS.md`
3. `SUBMISSION.md`
4. `docs/ARCHITECTURE.md`
5. `docs/SECURITY_MODEL.md`
6. `docs/LIVE_TEST_PLAN.md`
7. `docs/NETWORK.md`
8. `contracts/proxymesh.py`
9. `contracts/proxy_vote_book.py`

## Preserve the architecture

Do not turn this into a generic voting app.

The primitive is:

- a finite ontology is created and sealed;
- proposal semantics are classified only into those frozen domain slots;
- validators independently rerun classification and must agree on exact verdict + bitmask;
- delegation is deterministic, domain-scoped, transitive, expiring and revocable;
- cycles/depth overflow fail closed;
- a multi-domain proposal is proxy-routable only if every implicated route converges to the same terminal representative;
- split authority does not let AI pick a winner; the consumer requires a direct vote;
- a voter can always override delegation by acting directly.

Do not weaken this into a thin `AI chooses delegate` design.

## Required checks before deployment

Run:

```bash
python scripts/preflight.py
pytest -q
```

Then run whatever GenLayer runtime/direct-mode tests are appropriate for CLI 0.39.1 and stable Studionet. Fix contract API or SDK incompatibilities you discover. Do not falsify pass results.

Pay special attention to:

- `TreeMap` access and compound keys;
- storage dataclasses;
- `gl.vm.run_nondet_default` custom validator behaviour;
- event emission syntax;
- `datetime`/message time behaviour in stable Studionet;
- Address serialization/comparison;
- consumer IC-to-IC view-call support on the stable 61999 runtime;
- ambiguous classification behaviour;
- expiry and revocation;
- cycle prevention;
- multi-domain convergence versus split;
- classification-hash pinning;
- duplicate-voter replay protection.

If stable Studionet cannot support one optional consumer feature exactly as written, preserve the main ProxyMesh primitive, document the exact runtime limitation, and make the smallest sound compatibility change. Do not migrate networks to make the test pass.

## Deployment

Deploy `contracts/proxymesh.py` first.

Deploy `contracts/proxy_vote_book.py` second with the real ProxyMesh address as constructor argument.

Use the stable Studionet endpoint. Do not guess addresses. Wait for finalization and save transaction hashes.

Create `deployment.json` only from real deployment data. It should include at minimum:

- network = studionet
- chain_id = 61999
- rpc
- explorer
- cli_version = 0.39.1
- ProxyMesh address + deployment transaction
- ProxyVoteBook address + deployment transaction
- deployed_at timestamp

## Live evidence

Execute every scenario in `docs/LIVE_TEST_PLAN.md`.

At minimum prove live:

1. ontology creation + sealing;
2. delegation A→Carol for treasury;
3. delegation A→Bob→Carol for security;
4. a proposal classified into both treasury + security;
5. converged authority resolves to Carol;
6. Carol successfully votes for A through the consumer;
7. changed security delegation creates split authority;
8. proxy vote fails for split authority;
9. A can still vote directly;
10. a cycle attempt is rejected;
11. revoked/expired delegation stops being used.

Record real transaction hashes, finalized status and explorer links in a new `docs/LIVE_EVIDENCE.md`.

## Final repository quality

Before pushing:

- remove temporary debug files, private keys and secrets;
- ensure README has the final contract addresses and explorer links only after real deployment;
- update `BUILD_STATUS.md` truthfully;
- ensure no reference to any dev/preview chain or forbidden CLI version has leaked into active configuration;
- keep all tests green;
- make sure the repository is understandable without a frontend;
- do not claim deployment/tests that were not actually completed.

Finally commit and push the finished repository to `Bibidee/proxymesh` and report the final commit SHA, both contract addresses, explorer links, test results and any remaining limitation.
