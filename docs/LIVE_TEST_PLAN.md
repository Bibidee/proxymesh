# Final live lifecycle plan

The final agent must execute this on **Studionet / chain 61999** with **GenLayer CLI 0.39.1**. Do not claim this file as completed until every write is finalized and explorer links/transaction hashes are saved.

## Deployment

1. Verify CLI and network using `scripts/check-cli.ps1` (Windows) or `scripts/check-cli.sh`.
2. Deploy `contracts/proxymesh.py` with no constructor args.
3. Deploy `contracts/proxy_vote_book.py` with the deployed ProxyMesh address as its constructor argument.
4. Record both addresses in `deployment.json`.

## Lifecycle A — converged delegation

Create ontology `Governance Domains` with at least:

- slot 0: TREASURY — spending, budgets, asset allocation and treasury controls.
- slot 1: SECURITY — incident response, security controls and emergency permissions.
- slot 2: PROTOCOL — protocol logic, upgrades and technical consensus rules.

Seal it.

Using three funded accounts:

- voter Alice delegates TREASURY to Carol;
- Alice delegates SECURITY to Bob;
- Bob delegates SECURITY to Carol.

Create a proposal materially affecting TREASURY + SECURITY. Classify it. Verify the domain mask includes both slots. `resolve_authority(proposal, Alice)` must converge to Carol.

Carol calls the consumer to cast Alice's vote. It must succeed.

## Lifecycle B — split delegation fails closed

Change Alice's SECURITY delegation to Dave. Create/classify another TREASURY + SECURITY proposal. Resolution must return split authority. Carol attempting to cast for Alice must fail. Alice voting directly must succeed.

## Lifecycle C — cycle prevention

Attempt A→B followed by B→A in one domain. The second write must fail.

## Lifecycle D — expiry/revocation

Create a short-lived delegation or revoke an edge. Confirm subsequent resolution ignores it.

## Evidence to save

- exact CLI version output;
- network info showing chain 61999;
- contract addresses;
- deployment transaction hashes;
- ontology/domain writes;
- classification transaction and final receipt;
- converged route read;
- successful proxy consumer vote;
- failed split proxy vote;
- successful direct override;
- failed cycle creation;
- explorer links.
