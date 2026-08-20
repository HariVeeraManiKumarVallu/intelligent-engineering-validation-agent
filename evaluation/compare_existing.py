from __future__ import annotations

import json
from pathlib import Path

from evaluation.test_cases import load_cases, load_expected
from evaluation.conventional import run_conventional
from evaluation.metrics import calculate_all
from evaluation.plots import create_comparison_plot


ROOT = Path(__file__).resolve().parents[1]
NEMOTRON_DIR = ROOT / "evaluation" / "results" / "nemotron"
OUTPUT_DIR = ROOT / "evaluation" / "results" / "comparison"


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------
    # Load existing Nemotron results
    # --------------------------------------------------

    nemotron_results = json.loads(
        (NEMOTRON_DIR / "nemotron_results.json").read_text(
            encoding="utf-8"
        )
    )

    nemotron_metrics = json.loads(
        (NEMOTRON_DIR / "nemotron_metrics.json").read_text(
            encoding="utf-8"
        )
    )

    # --------------------------------------------------
    # Run conventional workflow locally
    # --------------------------------------------------

    cases = load_cases()
    expected = load_expected()

    conventional_results = [
        run_conventional(case)
        for case in cases
    ]

    conventional_metrics = calculate_all(
        results=conventional_results,
        plans=[],
        expected=expected,
    )

    conventional_metrics["tool_selection_accuracy"] = 1.0

    # --------------------------------------------------
    # Save conventional results
    # --------------------------------------------------

    (OUTPUT_DIR / "conventional_results.json").write_text(
        json.dumps(
            conventional_results,
            indent=2,
        ),
        encoding="utf-8",
    )

    (OUTPUT_DIR / "conventional_metrics.json").write_text(
        json.dumps(
            conventional_metrics,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Comparison
    # --------------------------------------------------

    metric_keys = [
        "task_completion_rate",
        "tool_selection_accuracy",
        "data_analysis_accuracy",
        "validation_error_detection",
        "response_validity",
    ]

    comparison = {
        "nemotron_model": "nvidia/nemotron-3.5-lightning:free",
        "test_cases": len(cases),
        "metrics": {},
    }

    for key in metric_keys:
        comparison["metrics"][key] = {
            "nemotron": nemotron_metrics.get(key, 0.0),
            "conventional": conventional_metrics.get(key, 0.0),
        }

    comparison["status"] = {
        "nemotron_valid": sum(
            r.get("final_status") == "VALID"
            for r in nemotron_results
        ),
        "nemotron_invalid": sum(
            r.get("final_status") == "INVALID"
            for r in nemotron_results
        ),
        "conventional_valid": sum(
            r.get("final_status") == "VALID"
            for r in conventional_results
        ),
        "conventional_invalid": sum(
            r.get("final_status") == "INVALID"
            for r in conventional_results
        ),
    }

    (OUTPUT_DIR / "agentic_vs_conventional.json").write_text(
        json.dumps(
            comparison,
            indent=2,
        ),
        encoding="utf-8",
    )

    # --------------------------------------------------
    # Plot
    # --------------------------------------------------

    create_comparison_plot(
        nemotron_metrics=nemotron_metrics,
        conventional_metrics=conventional_metrics,
        output_dir=OUTPUT_DIR,
    )

    # --------------------------------------------------
    # Print
    # --------------------------------------------------

    print("=" * 70)
    print("AGENTIC VS CONVENTIONAL")
    print("=" * 70)

    print()
    print(
        f"{'Metric':<35}"
        f"{'Nemotron':>12}"
        f"{'Conventional':>15}"
    )

    print("-" * 65)

    labels = {
        "task_completion_rate": "Task Completion Rate",
        "tool_selection_accuracy": "Tool Selection Accuracy",
        "data_analysis_accuracy": "Data Analysis Accuracy",
        "validation_error_detection": "Validation Error Detection",
        "response_validity": "Response Validity",
    }

    for key in metric_keys:
        print(
            f"{labels[key]:<35}"
            f"{nemotron_metrics.get(key, 0.0):>12.4f}"
            f"{conventional_metrics.get(key, 0.0):>15.4f}"
        )

    print()
    print("STATUS")
    print("-" * 65)

    print(
        f"Nemotron:      "
        f"{comparison['status']['nemotron_valid']} VALID / "
        f"{comparison['status']['nemotron_invalid']} INVALID"
    )

    print(
        f"Conventional:  "
        f"{comparison['status']['conventional_valid']} VALID / "
        f"{comparison['status']['conventional_invalid']} INVALID"
    )

    print()
    print(f"Saved to: {OUTPUT_DIR}")
    print("No LLM/API request was made.")


if __name__ == "__main__":
    main()
