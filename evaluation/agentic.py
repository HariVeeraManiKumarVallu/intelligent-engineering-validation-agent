from __future__ import annotations

from typing import Any, Dict, Tuple

from agents.planner import plan_task
from agents.graph import build_graph


def run_agentic(
    case: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Run one engineering case through the agentic workflow.

    Returns:
        result: Final engineering validation result.
        plan: LLM-generated tool-selection plan.
    """

    plan = plan_task(case)

    app = build_graph()

    state = app.invoke(
        {
            "case": case,
            "plan": plan,
        }
    )

    result = state["result"]

    return result, plan