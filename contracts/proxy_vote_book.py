# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
# v0.1.0

import genlayer as gl
from genlayer import *
from dataclasses import dataclass
import typing

ROUTE_DIRECT = 1
ROUTE_CONVERGED = 2
ROUTE_SPLIT = 3
PROPOSAL_CLASSIFIED = 1


@gl.contract_interface
class IProxyMesh:
    class View:
        def get_proposal(self, proposal_id: u256) -> dict: ...
        def resolve_authority(self, proposal_id: u256, voter: Address) -> dict: ...
    class Write:
        pass


@allow_storage
@dataclass
class VoteReceipt:
    voter: Address
    caster: Address
    proposal_id: u256
    choice: u8
    classification_hash: str
    route_commitment: str


class ProxyVoteBook(gl.Contract):
    """Minimal consumer: direct vote overrides delegation; otherwise only converged proxy authority may cast."""

    proxymesh_address: Address
    votes: TreeMap[str, VoteReceipt]
    yes_count: TreeMap[u256, u256]
    no_count: TreeMap[u256, u256]
    abstain_count: TreeMap[u256, u256]

    def __init__(self, proxymesh_address: Address):
        self.proxymesh_address = proxymesh_address

    def _key(self, proposal_id: int, voter: Address) -> str:
        return f"{int(proposal_id)}:{str(voter).lower()}"

    @gl.public.write
    def cast_vote(self, proposal_id: u256, voter: Address, expected_classification_hash: str, choice: u8) -> None:
        if int(choice) not in (1, 2, 3):
            raise gl.vm.UserError("EXPECTED: choice must be 1=yes, 2=no, 3=abstain")
        mesh = IProxyMesh(self.proxymesh_address)
        proposal = mesh.view().get_proposal(proposal_id)
        stored_hash = str(proposal.get("classification_hash", ""))
        if int(proposal.get("status", -1)) != PROPOSAL_CLASSIFIED or not stored_hash:
            raise gl.vm.UserError("EXPECTED: proposal must be classified before voting")
        if stored_hash != str(expected_classification_hash):
            raise gl.vm.UserError("EXPECTED: classification hash mismatch")
        key = self._key(int(proposal_id), voter)
        if key in self.votes:
            raise gl.vm.UserError("EXPECTED: voter already represented in this ballot")
        caller = gl.message.sender_address
        route_commitment = "DIRECT_OVERRIDE"
        if caller != voter:
            route = mesh.view().resolve_authority(proposal_id, voter)
            if int(route.get("status", 0)) != ROUTE_CONVERGED:
                raise gl.vm.UserError("EXPECTED: delegation is not converged for this proposal; voter must vote directly")
            if str(route.get("representative", "")).lower() != str(caller).lower():
                raise gl.vm.UserError("EXPECTED: caller is not the resolved representative")
            route_commitment = str(route.get("route_commitment", ""))
        self.votes[key] = VoteReceipt(
            voter=voter, caster=caller, proposal_id=int(proposal_id), choice=int(choice),
            classification_hash=str(expected_classification_hash), route_commitment=route_commitment
        )
        if int(choice) == 1:
            current = int(self.yes_count[int(proposal_id)]) if int(proposal_id) in self.yes_count else 0
            self.yes_count[int(proposal_id)] = current + 1
        elif int(choice) == 2:
            current = int(self.no_count[int(proposal_id)]) if int(proposal_id) in self.no_count else 0
            self.no_count[int(proposal_id)] = current + 1
        else:
            current = int(self.abstain_count[int(proposal_id)]) if int(proposal_id) in self.abstain_count else 0
            self.abstain_count[int(proposal_id)] = current + 1

    @gl.public.view
    def get_tally(self, proposal_id: u256) -> dict[str, int]:
        yes = int(self.yes_count[int(proposal_id)]) if int(proposal_id) in self.yes_count else 0
        no = int(self.no_count[int(proposal_id)]) if int(proposal_id) in self.no_count else 0
        abstain = int(self.abstain_count[int(proposal_id)]) if int(proposal_id) in self.abstain_count else 0
        return {"yes": yes, "no": no, "abstain": abstain}
