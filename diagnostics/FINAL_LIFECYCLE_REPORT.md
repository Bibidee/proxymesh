# ProxyMesh Final Lifecycle Report

## Release

- Frozen commit: `1d05c56d9a772f929f1c8f0d6d341d8231674626`
- Network: Studionet
- Chain ID: `61999`
- ProxyMesh: [`0xd7425357192780DB4497716D25d7763dAa3de2CA`](https://explorer-studio.genlayer.com/address/0xd7425357192780DB4497716D25d7763dAa3de2CA)
- ProxyVoteBook: [`0xA67CFE520C0a4Fa6bb685DD8330f4Adb27E255aC`](https://explorer-studio.genlayer.com/address/0xA67CFE520C0a4Fa6bb685DD8330f4Adb27E255aC)

## Automated verification

- GenVM check: PASS for both contracts
- Schema: PASS for both contracts
- Typecheck: PASS for both contracts
- Preflight: PASS
- Pytest: `36 passed`
- Direct Mode: `6 passed`, no skips
- Real-contract 15-edge boundary: PASS
- Real-contract 16th-edge rejection: PASS

## Real Studionet lifecycle

- Canonical ProxyMesh deployment: PASS — [`0x668930bbc1123447ede6e3b1a33826b7bee1466e2ab0fda58d42f2512581fe10`](https://explorer-studio.genlayer.com/tx/0x668930bbc1123447ede6e3b1a33826b7bee1466e2ab0fda58d42f2512581fe10)
- Canonical ProxyVoteBook deployment: PASS — [`0xfa28ee429c79f682eabfc99c0b02759b236c228a25ec5ad604a0afc0981e97d2`](https://explorer-studio.genlayer.com/tx/0xfa28ee429c79f682eabfc99c0b02759b236c228a25ec5ad604a0afc0981e97d2)
- Proposal 2 converged delegation: PASS
- Proposal 2 proxy vote: PASS
- Proposal 2 direct override: PASS — [`0x55259c22a7aab9f4d6bf348d2e0e3f9fe779b898be27575b8ed82f8ad0dbe07f`](https://explorer-studio.genlayer.com/tx/0x55259c22a7aab9f4d6bf348d2e0e3f9fe779b898be27575b8ed82f8ad0dbe07f)
- Proposal 2 tally: `{ yes: 0, no: 1, abstain: 0 }`
- Proposal 3 split route: PASS
- Proposal 3 failed proxy vote: PASS — [`0x9f673c44d8fbb59fd07e9b67f8b7c6f0676c412316ae3ec382f44de3ad61d767`](https://explorer-studio.genlayer.com/tx/0x9f673c44d8fbb59fd07e9b67f8b7c6f0676c412316ae3ec382f44de3ad61d767)
- Proposal 3 direct fallback: PASS — [`0xb00dda931108615eabd53f8e5a39b264b2f206ad282502fdcbbb78589f4d767a`](https://explorer-studio.genlayer.com/tx/0xb00dda931108615eabd53f8e5a39b264b2f206ad282502fdcbbb78589f4d767a)
- Proposal 3 tally: `{ yes: 1, no: 0, abstain: 0 }`
- Cycle prevention: PASS

## Depth boundary

The real `contracts/proxymesh.py` was exercised in Direct Mode with unique deterministic addresses:

```text
A0 → A1 → A2 → A3 → A4 → A5 → A6 → A7
   → A8 → A9 → A10 → A11 → A12 → A13 → A14 → A15
```

```text
15 edges:
ROUTE_CONVERGED
representative = A15
hops = 15
```

The attempted `NEW_ROOT → A0` edge was rejected with:

```text
EXPECTED: delegation path exceeds max depth
```

The failed write left no delegation for `NEW_ROOT`, and the original A0 route remained converged to A15 at 15 hops.

## Hosted Studionet RPC note

The redundant hosted 15-account stress test was not used as readiness evidence because Studionet intermittently returned `eth_getTransactionCount: fetch failed` and connection timeouts. The deterministic boundary is proven against the real contract in Direct Mode.

## Conclusion

SUBMISSION READY

## GenLayer Classification Evidence

This is real canonical Studionet judgment evidence against ProxyMesh.

- Proposal ID: `4`
- Proposal creation tx: `0x80b0043867512c9aee4b2ebd0c832ace253378c62e95f2fa937cb289c41da6fe`
- Classification tx: [`0xc657a1044e1d1ef29c599204480170827790f2affc93094fcd1877bae77cabeb`](https://explorer-studio.genlayer.com/tx/0xc657a1044e1d1ef29c599204480170827790f2affc93094fcd1877bae77cabeb)
- Target: `0xd7425357192780DB4497716D25d7763dAa3de2CA`
- Method: `classify_proposal(4)`
- Finality: `FINALIZED`
- Consensus: `MAJORITY_AGREE`
- GenVM execution: `SUCCESS`
- Proposal status: `1` (`PROPOSAL_CLASSIFIED`)
- Domain mask: `3`
- Domain slots: `[0, 1]`
- Classification hash: `ef2f3fe0c792f955467717c1c233a769ad7710fbe003fffc0f333d3247e4e785`
- Classification reason: `The proposal explicitly requests a treasury spending change (Treasury) and a security emergency permission update (Security).`

The classification transaction is finalized and the post-classification state was read from the canonical contract.
