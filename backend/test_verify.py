# backend/test_verify.py

from app.blockchain.ledger import ledger

print(
    ledger.verify(
        "test-proof-001",
        "abc123",
    )
)