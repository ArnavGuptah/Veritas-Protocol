"""
Feature 5: Blockchain Layer — kept deliberately minimal, per the brief:
only proof_id, hash, timestamp, verifier signature, source fingerprint go
on-chain. No documents, no embeddings, no vectors.

Two modes:
  - MockLedger: an append-only local hash chain (a "chain" in the literal
    sense, just not distributed). Fully offline, zero cost, demonstrates
    the exact data shape that goes on-chain. Use this for dev + rehearsal.
  - Web3Ledger: real submission to Polygon Amoy / Base Sepolia via the
    contract in contract.sol. Needs a funded testnet wallet + RPC URL,
    both external to this sandbox — wire this in once you have them
    (see the __main__ block at the bottom for the exact web3.py calls).

Swapping is a one-line change at the bottom of pipeline usage: anchor =
ledger.anchor(record) works identically for both.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field


@dataclass
class MockLedger:
    """Local append-only chain. Good enough to demo the data shape and to
    let /verify work end-to-end without any external dependency."""

    chain: list[dict[str, str]] = field(default_factory=list)

    def anchor(self, record_id:str, root_hash:str, verifier_signature:str) -> dict:
        prev_block_hash = self.chain[-1]["block_hash"] if self.chain else "0" * 64
        entry = {
            "proof_id": record_id,
            "root_hash": root_hash,
            "timestamp": time.time(),
            "verifier_signature": verifier_signature,
            "prev_block_hash": prev_block_hash,
        }
        block_blob = json.dumps(entry, sort_keys=True, default=str)
        entry["block_hash"] = hashlib.sha256(block_blob.encode()).hexdigest()
        self.chain.append(entry)
        return entry

    def verify(self, record_id: str, root_hash: str) -> bool:
        for entry in self.chain:
            if entry["proof_id"] == record_id:
                return entry["root_hash"] == root_hash
        return False

    def get(self, record_id: str):

        for block in self.chain:
            if block["proof_id"] == record_id:
                return block

        return None

    def is_chain_intact(self) -> bool:
        """Re-walks the local chain to confirm no block was edited after the fact."""
        prev = "0" * 64
        for entry in self.chain:
            check = dict(entry)
            stored_hash = check.pop("block_hash")
            blob = json.dumps(check, sort_keys=True, default=str)
            if check["prev_block_hash"] != prev:
                return False
            if hashlib.sha256(blob.encode()).hexdigest() != stored_hash:
                return False
            prev = stored_hash
        return True


def generate_signature(root_hash: str, verifier_key: str = "demo-verifier-key") -> str:
    """Stand-in HMAC-style signature. Replace with a real keypair (eth_account
    or similar) before a real deployment — the anchor schema doesn't change."""
    return hashlib.sha256((verifier_key + root_hash).encode()).hexdigest()[:32]

ledger = MockLedger()  # swap for Web3Ledger once you have a funded wallet + RPC URL


# ---------------------------------------------------------------------------
# Real deployment sketch (uncomment + fill in once you have a funded wallet):
#
# from web3 import Web3
#
# class Web3Ledger:
#     def __init__(self, rpc_url: str, contract_address: str, abi: list, private_key: str):
#         self.w3 = Web3(Web3.HTTPProvider(rpc_url))
#         self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
#         self.account = self.w3.eth.account.from_key(private_key)
#
#     def anchor(self, record_id: str, root_hash: str, verifier_signature: str) -> dict:
#         tx = self.contract.functions.storeProof(
#             record_id, bytes.fromhex(root_hash), verifier_signature
#         ).build_transaction({
#             "from": self.account.address,
#             "nonce": self.w3.eth.get_transaction_count(self.account.address),
#             "gas": 200000,
#         })
#         signed = self.account.sign_transaction(tx)
#         tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
#         receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
#         return {"tx_hash": tx_hash.hex(), "block_number": receipt.blockNumber}
# ---------------------------------------------------------------------------
