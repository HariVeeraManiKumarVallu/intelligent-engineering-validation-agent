from __future__ import annotations
from typing import Dict
from langchain_core.tools import tool

@tool
def validate_analysis_result(
    processed: Dict[str, object],
    analysis: Dict[str, object],
    constraints: Dict[str, object],
    cpp: Dict[str, object],
) -> Dict[str, object]:
    """Apply deterministic safety and Python/C++ consistency rules."""
    checks = {}
    checks["input_valid"] = processed.get("status") == "PASS"
    checks["analysis_valid"] = analysis.get("status") == "PASS"
    checks["constraint_valid"] = constraints.get("status") in {"PASS", "FAIL"}
    checks["cpp_valid"] = cpp.get("status") == "PASS"

    if checks["analysis_valid"] and checks["cpp_valid"]:
        py_stress = float(analysis["stress_pa"])
        cpp_stress = float(cpp["stress_pa"])
        rel_error = abs(py_stress - cpp_stress) / max(abs(py_stress), 1e-12)
        checks["python_cpp_consistent"] = rel_error <= 0.0001
    else:
        rel_error = None
        checks["python_cpp_consistent"] = False

    checks["safety_pass"] = (
        checks["input_valid"]
        and checks["analysis_valid"]
        and constraints.get("status") == "PASS"
    )
    final_valid = all(checks.values())
    return {
        "status": "PASS" if final_valid else "FAIL",
        "checks": checks,
        "relative_error": rel_error,
    }
