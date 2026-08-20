from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

from evaluation.test_cases import load_cases, load_expected
from evaluation.agentic import run_agentic
from evaluation.conventional import run_conventional
from evaluation.metrics import calculate_all


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "evaluation" / "results"


def main() -> None:
    load_dotenv()

    cases = load_cases()
    expected = load_expected()

    agentic_results = []
    agentic_plans = []
    conventional_results = []

    print("=" * 70)
    print("INTELLIGENT ENGINEERING VALIDATION AGENT")
    print("END-TO-END EVALUATION")
    print("=" * 70)

    print()
    print(f"Test cases: {len(cases)}")
    print()

    for index, case in enumerate(cases, start=1):
        case_id = case["case_id"]

        print(
            f"[{index}/{len(cases)}] "
            f"Running {case_id}..."
        )

        # Agentic workflow
        agentic_result, plan = run_agentic(case)

        agentic_results.append(agentic_result)
        agentic_plans.append(plan)

        # Conventional workflow
        conventional_result = run_conventional(case)

        conventional_results.append(
            conventional_result
        )

        print(
            f"    Agentic:      "
            f"{agentic_result.get('final_status')}"
        )

        print(
            f"    Conventional: "
            f"{conventional_result.get('final_status')}"
        )

    # --------------------------------------------------
    # Agentic metrics
    # --------------------------------------------------

    agentic_metrics = calculate_all(
        results=agentic_results,
        plans=agentic_plans,
        expected=expected,
    )

    # --------------------------------------------------
    # Conventional metrics
    # --------------------------------------------------

    conventional_metrics = calculate_all(
        results=conventional_results,
        plans=[],
        expected=expected,
    )

    # Tool selection is not applicable to the
    # conventional workflow.
    conventional_metrics["tool_selection_accuracy"] = 1.0

    # --------------------------------------------------
    # Save individual results
    # --------------------------------------------------

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    (RESULTS_DIR / "agentic_results.json").write_text(
        json.dumps(
            agentic_results,
            indent=2,
        ),
        encoding="utf-8",
    )

    (RESULTS_DIR / "agentic_plans.json").write_text(
        json.dumps(
            agentic_plans,
            indent=2,
        ),
        encoding="utf-8",
    )

    (RESULTS_DIR / "conventional_results.json").write_text(
        json.dumps(
            conventional_results,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Save metrics
    # --------------------------------------------------

    (RESULTS_DIR / "agentic_metrics.json").write_text(
        json.dumps(
            agentic_metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    (RESULTS_DIR / "conventional_metrics.json").write_text(
        json.dumps(
            conventional_metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Print final comparison
    # --------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL EVALUATION")
    print("=" * 70)

    print()
    print("Metric                         Agentic    Conventional")
    print("-" * 55)

    metric_names = [
        ("task_completion_rate", "Task Completion Rate"),
        ("tool_selection_accuracy", "Tool Selection Accuracy"),
        ("data_analysis_accuracy", "Data Analysis Accuracy"),
        ("validation_error_detection", "Validation Error Detection"),
        ("response_validity", "Response Validity"),
    ]

    for key, label in metric_names:
        print(
            f"{label:<30} "
            f"{agentic_metrics[key]:>8.4f}    "
            f"{conventional_metrics[key]:>8.4f}"
        )

    print()
    print("=" * 70)
    print("RESULT FILES")
    print("=" * 70)

    print(
        f"Results saved to: {RESULTS_DIR}"
    )


if __name__ == "__main__":
    main()