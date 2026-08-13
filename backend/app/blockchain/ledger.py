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
import os
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / "backend" / ".env")

print("Loaded RPC:", os.getenv("SEPOLIA_RPC_URL"))
print("Loaded Contract:", os.getenv("CONTRACT_ADDRESS"))

def generate_signature(root_hash: str, verifier_key: str = "demo-verifier-key") -> str:
    """Stand-in HMAC-style signature. Replace with a real keypair (eth_account
    or similar) before a real deployment — the anchor schema doesn't change."""
    return hashlib.sha256((verifier_key + root_hash).encode()).hexdigest()[:32]


@dataclass
class MockLedger:
    """Local append-only chain. Good enough to demo the data shape and to
    let /verify work end-to-end without any external dependency."""

    chain: list[dict[str, str]] = field(default_factory=list)

    def anchor(self, record_id:str, root_hash:str, verifier_signature:str) -> dict:
        prev = self.chain[-1]["block_hash"] if self.chain else "0" * 64
        block = {
            "proof_id": record_id,
            "root_hash": root_hash,
            "timestamp": time.time(),
            "verifier_signature": verifier_signature,
            "prev_block_hash": prev,
        }
        blob = json.dumps(block, sort_keys=True, default=str)

        block["block_hash"] = hashlib.sha256(blob.encode()).hexdigest()

        self.chain.append(block)

        return block

    def verify(self, record_id: str, root_hash: str) -> bool:
        entry = self.get(record_id)

        if entry is None:
            return False

        return entry["root_hash"] == root_hash

    def get(self, record_id: str):

        for block in self.chain:
            if block["proof_id"] == record_id:
                return block

        return None

    def is_chain_intact(self)-> bool:
        """Re-walks the local chain to confirm no block was edited after the fact."""
        prev = "0" * 64
        for entry in self.chain:

            check = dict(entry)

            stored = check.pop("block_hash")

            blob = json.dumps(check, sort_keys=True, default=str)

            if check["prev_block_hash"] != previous:
                return False

            if hashlib.sha256(blob.encode()).hexdigest() != stored:
                return False

            previous = stored

        return True

class Web3Ledger:

    def __init__(self):

        self.rpc = os.getenv("SEPOLIA_RPC_URL")
        self.private_key = os.getenv("PRIVATE_KEY")
        self.contract_address = os.getenv("CONTRACT_ADDRESS")

        if not self.rpc:
            raise RuntimeError("Missing SEPOLIA_RPC_URL")

        if not self.private_key:
            raise RuntimeError("Missing PRIVATE_KEY")

        if not self.contract_address:
            raise RuntimeError("Missing CONTRACT_ADDRESS")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc))

        if not self.w3.is_connected():
            raise RuntimeError("Could not connect to Sepolia")

        self.account = Account.from_key(self.private_key)

        artifact_path = (
            PROJECT_ROOT
            / "contracts"
            / "artifacts"
            / "contracts"
            / "ProofRegistry.sol"
            / "VeritasProofAnchor.json"
        )

        print("Artifact:", artifact_path)
        print("Exists:", artifact_path.exists())

        with open(artifact_path, "r", encoding="utf-8",) as f:
            artifact = json.load(f)

        abi = artifact["abi"]

        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.contract_address),
            abi=abi,
        )

    def anchor(self, record_id: str, root_hash: str, verifier_signature: str,) -> dict:

        print("========== BLOCKCHAIN ANCHOR ==========")
        print("Proof ID:", record_id)
        print("Root hash:", root_hash)
        print("Submitting to contract:", self.contract_address)

        nonce = self.w3.eth.get_transaction_count(
            self.account.address,
            "pending"
        )

        tx = self.contract.functions.storeProof(
            record_id,
            Web3.keccak(text=root_hash),
            verifier_signature.encode(),
        ).build_transaction(
            {
                "from": self.account.address,
                "nonce": nonce,
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
                "chainId": self.w3.eth.chain_id,
            }
        )

        signed = self.account.sign_transaction(tx)

        tx_hash = self.w3.eth.send_raw_transaction(
            signed.raw_transaction
        )

        print("Transaction submitted:", tx_hash.hex())

        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            raise RuntimeError(
                f"Blockchain transaction failed: {tx_hash.hex()}"
            )

        print("Transaction confirmed.")
        print("Block:", receipt.blockNumber)
        print("========================================")

        return {
            "status": "anchored",
            "tx_hash": tx_hash.hex(),
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber
        }

    def verify(self, record_id: str, root_hash: str,) -> bool:

        expected = Web3.keccak(text=root_hash)

        exists = self.contract.functions.proofExists(record_id).call()

        if not exists:
            print("========== VERIFY ==========")
            print("Exists:", False)
            print("============================")
            return False

        stored = self.contract.functions.getProof(record_id).call()[0]

        result = self.contract.functions.verifyProof(
            record_id,
            expected,
        ).call()

        print("\n=======VERIFY=======")
        print("Exists   :", exists)
        print("Input    :", root_hash)
        print("Expected :", expected.hex())
        print("Stored   :", stored.hex())
        print("Equal    :", expected == stored)
        print("Contract :", result)
        print("====================\n")

        return result

    def get(self, record_id: str):

        exists = self.contract.functions.proofExists(
            record_id
        ).call()

        if not exists:
            return None

        root_hash, timestamp, signature, submitter = (
            self.contract.functions.getProof(
                record_id
            ).call()
        )

        return {
            "proof_id": record_id,
            "root_hash": root_hash.hex(),
            "timestamp": timestamp,
            "verifier_signature": signature.hex(),
            "submitter": submitter,
        }


# -------------------------------------------------------
# Choose backend
# -------------------------------------------------------

USE_WEB3 = True

if USE_WEB3:
    ledger = Web3Ledger()
else:
    ledger = MockLedger()

