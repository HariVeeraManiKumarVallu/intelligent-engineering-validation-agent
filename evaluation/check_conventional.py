from evaluation.test_cases import load_cases, load_expected
from evaluation.conventional import run_conventional


cases = load_cases()
expected_list = load_expected()

expected = {
    item["case_id"]: item
    for item in expected_list
}

correct = 0

print("CASE | ACTUAL | EXPECTED | MATCH")
print("-" * 45)

for case in cases:
    case_id = case["case_id"]

    result = run_conventional(case)

    actual_valid = result["final_status"] == "VALID"
    expected_valid = expected[case_id]["expected_valid"]

    match = actual_valid == expected_valid

    if match:
        correct += 1

    print(
        f"{case_id} | "
        f"{'VALID' if actual_valid else 'INVALID'} | "
        f"{'VALID' if expected_valid else 'INVALID'} | "
        f"{match}"
    )

accuracy = correct / len(cases)

print()
print(f"Correct: {correct}/{len(cases)}")
print(f"Accuracy: {accuracy:.4f}")