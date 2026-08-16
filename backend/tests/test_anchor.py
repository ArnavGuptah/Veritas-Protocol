from app.blockchain.ledger import ledger, generate_signature

root_hash = "abc123"

signature = generate_signature(root_hash)

result = ledger.anchor(
    record_id="test-proof-001",
    root_hash=root_hash,
    verifier_signature=signature,
)

print(result)