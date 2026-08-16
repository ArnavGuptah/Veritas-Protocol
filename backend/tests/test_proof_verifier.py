from copy import deepcopy
from app.proof.verifier import verify_proof


def test_valid_proof(record_factory):
    record = record_factory()

    result = verify_proof(record)

    assert result["valid"] is True
    assert result["tampered_stage"] is None


def test_tampered_proof(record_factory):
    record = record_factory()

    tampered = deepcopy(record)

    tampered.generator_answer = (
        "This answer has been modified."
    )

    result = verify_proof(tampered)

    assert result["valid"] is False