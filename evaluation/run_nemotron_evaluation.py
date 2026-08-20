from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from evaluation.test_cases import (
    load_cases,
    load_expected,
)

from evaluation.openrouter_batch import (
    run_nemotron_batch,
)

from evaluation.batch_agentic import (
    execute_model_plans,
)

from evaluation.metrics import (
    calculate_all,
)


ROOT = Path(__file__).resolve().parents[1]

RESULTS_DIR = (
    ROOT
    / "evaluation"
    / "results"
    / "nemotron"
)


def save_json(
    filename: str,
    data,
) -> None:
    """
    Save JSON output to the Nemotron results directory.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = RESULTS_DIR / filename

    path.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved: {path}"
    )


def validate_preflight(
    cases,
    expected,
) -> None:
    """
    Validate local evaluation data before making
    the single LLM request.
    """

    if not cases:

        raise RuntimeError(
            "No engineering test cases were found."
        )

    if not expected:

        raise RuntimeError(
            "No expected results were found."
        )

    case_ids = {
        case["case_id"]
        for case in cases
    }

    expected_ids = {
        item["case_id"]
        for item in expected
    }

    missing = (
        case_ids
        - expected_ids
    )

    unexpected = (
        expected_ids
        - case_ids
    )

    if missing:

        raise RuntimeError(
            "Missing expected results for: "
            f"{sorted(missing)}"
        )

    if unexpected:

        raise RuntimeError(
            "Unexpected expected-result cases: "
            f"{sorted(unexpected)}"
        )

    print(
        f"Preflight validation passed: "
        f"{len(cases)} cases / "
        f"{len(expected)} expected results."
    )


def validate_plans(
    plans,
    cases,
) -> None:
    """
    Verify that Nemotron returned exactly one
    plan for every test case.
    """

    if len(plans) != len(cases):

        raise RuntimeError(
            f"Nemotron returned "
            f"{len(plans)} plans for "
            f"{len(cases)} cases."
        )

    expected_ids = {
        case["case_id"]
        for case in cases
    }

    returned_ids = {
        plan.get("case_id")
        for plan in plans
    }

    missing = (
        expected_ids
        - returned_ids
    )

    unexpected = (
        returned_ids
        - expected_ids
    )

    if missing:

        raise RuntimeError(
            "Nemotron omitted case IDs: "
            f"{sorted(missing)}"
        )

    if unexpected:

        raise RuntimeError(
            "Nemotron returned unexpected case IDs: "
            f"{sorted(unexpected)}"
        )


def main() -> None:

    load_dotenv()

    # ======================================================
    # LOAD LOCAL DATA
    # ======================================================

    cases = load_cases()

    expected = load_expected()

    model = os.getenv(
        "NEMOTRON_MODEL",
        "nvidia/nemotron-3.5-lightning:free",
    )

    # ======================================================
    # HEADER
    # ======================================================

    print("=" * 70)
    print("NEMOTRON-ONLY AGENTIC EVALUATION")
    print("=" * 70)

    print()

    print(
        f"Test cases: {len(cases)}"
    )

    print()

    print("API budget:")

    print(
        f"  Model: {model}"
    )

    print(
        "  Nemotron API requests: 1"
    )

    print(
        "  Total API requests: 1"
    )

    print()

    # ======================================================
    # PREFLIGHT
    # ======================================================

    print("=" * 70)
    print("PREFLIGHT VALIDATION")
    print("=" * 70)

    validate_preflight(
        cases,
        expected,
    )

    print()

    print(
        "Local test-case data is valid."
    )

    print(
        "Expected-result data is valid."
    )

    print(
        "Ready for the single Nemotron API request."
    )

    # ======================================================
    # SINGLE NEMOTRON API REQUEST
    # ======================================================

    print()
    print("=" * 70)
    print("STARTING SINGLE NEMOTRON API REQUEST")
    print("=" * 70)

    print()

    batch = run_nemotron_batch(
        cases
    )

    # ======================================================
    # VALIDATE LLM OUTPUT
    # ======================================================

    plans = batch["plans"]

    print()

    print(
        f"Nemotron plans returned: "
        f"{len(plans)}"
    )

    validate_plans(
        plans,
        cases,
    )

    print(
        "Nemotron plan validation passed."
    )

    # ======================================================
    # SAVE LLM OUTPUT
    # ======================================================

    print()
    print("=" * 70)
    print("SAVING NEMOTRON OUTPUT")
    print("=" * 70)

    save_json(
        "nemotron_batch_output.json",
        batch,
    )

    save_json(
        "nemotron_plans.json",
        plans,
    )

    # ======================================================
    # EVERYTHING BELOW IS LOCAL
    # ======================================================

    print()
    print("=" * 70)
    print("LOCAL EXECUTION")
    print("=" * 70)

    print()

    print(
        "Executing Nemotron plans locally..."
    )

    nemotron_results = execute_model_plans(
        cases,
        plans,
    )

    print(
        f"Nemotron results: "
        f"{len(nemotron_results)}"
    )

    if len(nemotron_results) != len(cases):

        raise RuntimeError(
            f"Local execution returned "
            f"{len(nemotron_results)} results "
            f"for {len(cases)} cases."
        )

    print(
        "Local execution validation passed."
    )

    # ======================================================
    # METRICS
    # ======================================================

    print()
    print("=" * 70)
    print("CALCULATING METRICS")
    print("=" * 70)

    nemotron_metrics = calculate_all(
        results=nemotron_results,
        plans=plans,
        expected=expected,
    )

    # ======================================================
    # SAVE LOCAL RESULTS
    # ======================================================

    save_json(
        "nemotron_results.json",
        nemotron_results,
    )

    save_json(
        "nemotron_metrics.json",
        nemotron_metrics,
    )

    # ======================================================
    # STATUS SUMMARY
    # ======================================================

    valid_count = sum(
        result.get("final_status")
        == "VALID"
        for result in nemotron_results
    )

    invalid_count = sum(
        result.get("final_status")
        == "INVALID"
        for result in nemotron_results
    )

    # ======================================================
    # FINAL METRICS
    # ======================================================

    print()
    print("=" * 70)
    print("NEMOTRON EVALUATION RESULTS")
    print("=" * 70)

    print()

    metric_names = [
        (
            "task_completion_rate",
            "Task Completion Rate",
        ),
        (
            "tool_selection_accuracy",
            "Tool Selection Accuracy",
        ),
        (
            "data_analysis_accuracy",
            "Data Analysis Accuracy",
        ),
        (
            "validation_error_detection",
            "Validation Error Detection",
        ),
        (
            "response_validity",
            "Response Validity",
        ),
    ]

    print(
        f"{'Metric':<35}"
        f"{'Nemotron':>12}"
    )

    print("-" * 50)

    for key, label in metric_names:

        print(
            f"{label:<35}"
            f"{nemotron_metrics[key]:>12.4f}"
        )

    # ======================================================
    # STATUS
    # ======================================================

    print()
    print("STATUS SUMMARY")
    print("-" * 50)

    print(
        f"VALID cases:   {valid_count}"
    )

    print(
        f"INVALID cases: {invalid_count}"
    )

    print(
        f"Total cases:   {len(nemotron_results)}"
    )

    # ======================================================
    # API USAGE
    # ======================================================

    print()
    print("=" * 70)
    print("API USAGE")
    print("=" * 70)

    print(
        "Nemotron API calls: 1"
    )

    print(
        "Total API calls:    1"
    )

    # ======================================================
    # RESULTS
    # ======================================================

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    print()

    print(
        f"Results directory: "
        f"{RESULTS_DIR}"
    )

    print()

    print("Generated files:")

    print(
        f"  {RESULTS_DIR / 'nemotron_batch_output.json'}"
    )

    print(
        f"  {RESULTS_DIR / 'nemotron_plans.json'}"
    )

    print(
        f"  {RESULTS_DIR / 'nemotron_results.json'}"
    )

    print(
        f"  {RESULTS_DIR / 'nemotron_metrics.json'}"
    )

    print()

    print(
        "Nemotron-only evaluation completed."
    )


if __name__ == "__main__":
    main()