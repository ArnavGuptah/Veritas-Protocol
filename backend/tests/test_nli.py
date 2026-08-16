from app.verification.nli import check_entailment


claim = "The capital of Mars is Olympus City."

evidence = (
    "Tuberculosis (TB) is an infectious disease caused "
    "by the bacterium Mycobacterium tuberculosis."
)

result = check_entailment(
    claim,
    evidence,
)

print("\n========== NLI TEST ==========")
print(result)
print("==============================")