from __future__ import annotations
from typing import Any, Dict
import torch
from langchain_core.tools import tool

@tool
def perform_engineering_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate maximum bending stress using PyTorch for a rectangular simply supported beam."""
    if data.get("status") != "PASS":
        return {"status": "FAIL", "error": "Input data has not passed processing."}
    p = torch.tensor(float(data["load_n"]), dtype=torch.float64)
    L = torch.tensor(float(data["length_m"]), dtype=torch.float64)
    b = torch.tensor(float(data["width_m"]), dtype=torch.float64)
    h = torch.tensor(float(data["height_m"]), dtype=torch.float64)
    moment = p * L / 4.0
    stress = 6.0 * moment / (b * h**2)
    allowable = torch.tensor(float(data["allowable_stress_pa"]), dtype=torch.float64)
    safety_factor = allowable / stress
    return {
        "status": "PASS",
        "moment_nm": float(moment.item()),
        "stress_pa": float(stress.item()),
        "safety_factor": float(safety_factor.item()),
    }
