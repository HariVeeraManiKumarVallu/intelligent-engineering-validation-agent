from __future__ import annotations

from typing import Any, Dict

from langchain_core.tools import tool


@tool
def check_engineering_constraints(
    analysis: Dict[str, Any],
    data: Dict[str, Any],
) -> Dict[str, object]:
    """Check bending stress against the supplied allowable stress."""

    if analysis.get("status") != "PASS" or data.get("status") != "PASS":
        return {
            "status": "FAIL",
            "error": "Analysis or input validation failed.",
        }

    stress = float(analysis["stress_pa"])
    allowable = float(data["allowable_stress_pa"])

    passed = stress <= allowable

    return {
        "status": "PASS" if passed else "FAIL",
        "stress_pa": stress,
        "allowable_stress_pa": allowable,
        "violation": not passed,
    }