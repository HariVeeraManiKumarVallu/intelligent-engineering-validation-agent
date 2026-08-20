from __future__ import annotations

from typing import Any, Dict, List


REQUIRED_TOOLS = [
    "process_engineering_data",
    "perform_engineering_analysis",
    "check_engineering_constraints",
    "run_cpp_validation",
    "validate_analysis_result",
]

AVAILABLE_TOOLS = set(REQUIRED_TOOLS) | {
    "retrieve_technical_knowledge"
}

REQUIRED_RESULT_FIELDS = {
    "case_id",
    "analysis",
    "constraints",
    "cpp_validation",
    "safety_consistency",
    "final_status",
}


def task_completion_rate(
    results: List[Dict[str, Any]],
) -> float:

    if not results:
        return 0.0

    completed = sum(
        result.get("final_status") in {"VALID", "INVALID"}
        for result in results
    )

    return completed / len(results)


def tool_selection_accuracy(
    plans: List[Dict[str, Any]],
) -> float:
    """
    Measure whether the model selected all mandatory tools
    without selecting invalid tools.
    """

    if not plans:
        return 0.0

    required = set(REQUIRED_TOOLS)

    scores = []

    for plan in plans:

        selected = plan.get("tools", [])

        if not isinstance(selected, list):
            scores.append(0.0)
            continue

        selected = set(selected)

        missing = required - selected
        invalid = selected - AVAILABLE_TOOLS

        if missing or invalid:
            scores.append(0.0)
        else:
            scores.append(1.0)

    return sum(scores) / len(scores)


def data_analysis_accuracy(
    results: List[Dict[str, Any]],
    expected: List[Dict[str, Any]],
) -> float:
    """
    Compare calculated stress against expected stress.
    """

    if not results or not expected:
        return 0.0

    expected_by_case = {
        item["case_id"]: item
        for item in expected
    }

    scores = []

    for result in results:

        case_id = result.get("case_id")

        expected_case = expected_by_case.get(case_id)

        if expected_case is None:
            scores.append(0.0)
            continue

        actual_stress = (
            result.get("analysis", {})
            .get("stress_pa")
        )

        expected_stress = expected_case.get("stress_pa")

        if actual_stress is None or expected_stress is None:
            scores.append(0.0)
            continue

        relative_error = (
            abs(
                float(actual_stress)
                - float(expected_stress)
            )
            / max(abs(float(expected_stress)), 1e-12)
        )

        scores.append(
            max(0.0, 1.0 - relative_error)
        )

    return sum(scores) / len(scores)


def validation_error_detection(
    results: List[Dict[str, Any]],
    expected: List[Dict[str, Any]],
) -> float:
    """
    Measure how accurately the workflow identifies
    valid versus invalid engineering cases.
    """

    if not results or not expected:
        return 0.0

    expected_by_case = {
        item["case_id"]: item
        for item in expected
    }

    correct = 0

    for result in results:

        case_id = result.get("case_id")

        expected_case = expected_by_case.get(case_id)

        if expected_case is None:
            continue

        predicted_valid = (
            result.get("final_status") == "VALID"
        )

        expected_valid = bool(
            expected_case.get("expected_valid")
        )

        if predicted_valid == expected_valid:
            correct += 1

    return correct / len(results)


def response_validity(
    results: List[Dict[str, Any]],
) -> float:

    if not results:
        return 0.0

    valid = sum(
        REQUIRED_RESULT_FIELDS.issubset(result.keys())
        for result in results
    )

    return valid / len(results)


def calculate_all(
    results: List[Dict[str, Any]],
    plans: List[Dict[str, Any]],
    expected: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Calculate all evaluation metrics.
    """

    return {
        "task_completion_rate": task_completion_rate(
            results
        ),
        "tool_selection_accuracy": tool_selection_accuracy(
            plans
        ),
        "data_analysis_accuracy": data_analysis_accuracy(
            results,
            expected
        ),
        "validation_error_detection": validation_error_detection(
            results,
            expected
        ),
        "response_validity": response_validity(
            results
        ),
    }