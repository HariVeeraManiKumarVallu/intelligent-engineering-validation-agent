from __future__ import annotations
from typing import Any, Dict
from langchain_core.tools import tool

REQUIRED = ("case_id", "material", "load_n", "length_m", "width_m", "height_m", "allowable_stress_pa")

@tool
def process_engineering_data(case: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize structured beam-engineering input."""
    missing = [k for k in REQUIRED if k not in case]
    if missing:
        return {"status": "FAIL", "error": f"Missing fields: {missing}"}
    try:
        values = {k: float(case[k]) for k in REQUIRED if k not in ("case_id", "material")}
    except (TypeError, ValueError) as exc:
        return {"status": "FAIL", "error": f"Non-numeric engineering field: {exc}"}
    for key in ("load_n", "length_m", "width_m", "height_m", "allowable_stress_pa"):
        if values[key] <= 0:
            return {"status": "FAIL", "error": f"{key} must be positive"}
    return {
        "status": "PASS",
        "case_id": str(case["case_id"]),
        "material": str(case["material"]),
        **values,
    }
