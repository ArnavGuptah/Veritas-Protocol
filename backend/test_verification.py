import requests


URL = "http://127.0.0.1:8000/api/v1/query"


TEST_CASES = [
    {
        "question": "What is Tuberculosis?",
        "expected_verdict": "supported",
    },
    {
        "question": "What was the 2022 Nobel Prize in Physics awarded for?",
        "expected_verdict": "supported",
    },
    {
        "question": "What is the capital of Mars?",
        "expected_verdict": "unverifiable",
    },
]


def run_test(case):

    response = requests.post(
        URL,
        json={
            "question": case["question"]
        },
        timeout=120,
    )

    response.raise_for_status()

    result = response.json()

    print("\nQUESTION:")
    print(case["question"])

    print("EXPECTED:")
    print(case["expected_verdict"])

    print("ACTUAL:")
    print(result.get("confidence_level"))

    print("ANSWER:")
    print(result.get("answer"))

    return result