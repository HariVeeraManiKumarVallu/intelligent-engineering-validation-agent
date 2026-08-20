from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

import matplotlib.pyplot as plt


def create_metric_plot(
    metrics: Dict[str, float],
    output_dir: Path,
) -> None:

    labels = [
        "Task Completion",
        "Tool Selection",
        "Data Analysis",
        "Validation Detection",
        "Response Validity",
    ]

    keys = [
        "task_completion_rate",
        "tool_selection_accuracy",
        "data_analysis_accuracy",
        "validation_error_detection",
        "response_validity",
    ]

    values = [
        metrics.get(key, 0.0)
        for key in keys
    ]

    plt.figure(figsize=(11, 6))

    plt.bar(
        labels,
        values,
        width=0.6,
        label="Nemotron 3.5 Lightning",
    )

    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.title(
        "Nemotron 3.5 Lightning Evaluation Metrics"
    )
    plt.xticks(
        rotation=20,
        ha="right",
    )
    plt.legend()
    plt.tight_layout()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        output_dir / "nemotron_metric_evaluation.png",
        dpi=200,
    )

    plt.close()


def create_status_plot(
    results: List[Dict[str, Any]],
    output_dir: Path,
) -> None:

    valid = sum(
        r.get("final_status") == "VALID"
        for r in results
    )

    invalid = sum(
        r.get("final_status") == "INVALID"
        for r in results
    )

    labels = [
        "VALID",
        "INVALID",
    ]

    values = [
        valid,
        invalid,
    ]

    plt.figure(figsize=(8, 5))

    plt.bar(
        labels,
        values,
        width=0.6,
        label="Nemotron 3.5 Lightning",
    )

    plt.ylabel("Number of Cases")
    plt.title(
        "Nemotron 3.5 Lightning Validation Status"
    )
    plt.legend()
    plt.tight_layout()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        output_dir / "nemotron_validation_status.png",
        dpi=200,
    )

    plt.close()


def create_comparison_plot(
    nemotron_metrics: Dict[str, float],
    conventional_metrics: Dict[str, float],
    output_dir: Path,
) -> None:

    labels = [
        "Task Completion",
        "Tool Selection",
        "Data Analysis",
        "Validation Detection",
        "Response Validity",
    ]

    keys = [
        "task_completion_rate",
        "tool_selection_accuracy",
        "data_analysis_accuracy",
        "validation_error_detection",
        "response_validity",
    ]

    nemotron_values = [
        nemotron_metrics.get(key, 0.0)
        for key in keys
    ]

    conventional_values = [
        conventional_metrics.get(key, 0.0)
        for key in keys
    ]

    x = range(len(labels))
    width = 0.35

    plt.figure(figsize=(11, 6))

    plt.bar(
        [i - width / 2 for i in x],
        nemotron_values,
        width=width,
        label="Nemotron 3.5 Lightning",
    )

    plt.bar(
        [i + width / 2 for i in x],
        conventional_values,
        width=width,
        label="Conventional",
    )

    plt.xticks(
        list(x),
        labels,
        rotation=20,
        ha="right",
    )

    plt.ylabel("Score")
    plt.ylim(0, 1.05)
    plt.title(
        "Nemotron 3.5 Lightning vs Conventional Workflow"
    )
    plt.legend()
    plt.tight_layout()

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        output_dir / "agentic_vs_conventional_metrics.png",
        dpi=200,
    )

    plt.close()