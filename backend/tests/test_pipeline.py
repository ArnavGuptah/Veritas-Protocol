import pytest


TEST_CASES = [
    {
        "question": "What is Tuberculosis?",
        "expected_verdict": "supported",
    },
    {
        "question": "Which bacterium causes tuberculosis?",
        "expected_verdict": "supported",
    },
    {
        "question": "What is the cure for Tuberculosis?",
        "expected_verdict": "supported",
    },
    {
        "question": "Who won the 2022 Nobel Prize in Physics?",
        "expected_verdict": "supported",
    },
    {
        "question": "What is the capital of Mars?",
        "expected_verdict": "unverifiable",
    },
]


@pytest.mark.parametrize(
    "case",
    TEST_CASES,
)
def test_pipeline_verdict(case):
    # We'll connect this to the ReasoningEngine after
    # the proof verification layer is finalized.
    assert case["expected_verdict"] in {
        "supported",
        "unverifiable",
        "refuted",
    }