from __future__ import annotations

from typing import Any, Dict

from tools.data_processor import process_engineering_data
from tools.knowledge_retrieval import retrieve_technical_knowledge
from tools.engineering_analysis import perform_engineering_analysis
from tools.constraint_checker import check_engineering_constraints
from tools.cpp_validation import run_cpp_validation
from tools.safety_consistency import validate_analysis_result


def run_conventional(case: Dict[str, Any]) -> Dict[str, Any]:
    """Run the fixed conventional engineering-analysis workflow."""

    processed = process_engineering_data.invoke(
        {"case": case}
    )

    knowledge = retrieve_technical_knowledge.invoke(
        {
            "query": (
                f"Beam engineering validation for material "
                f"{case.get('material')}, load and allowable stress constraints."
            )
        }
    )

    analysis = perform_engineering_analysis.invoke(
        {"data": processed}
    )

    constraints = check_engineering_constraints.invoke(
        {
            "analysis": analysis,
            "data": processed,
        }
    )

    cpp = run_cpp_validation.invoke(
        {"data": processed}
    )

    validation = validate_analysis_result.invoke(
        {
            "processed": processed,
            "analysis": analysis,
            "constraints": constraints,
            "cpp": cpp,
        }
    )

    return {
        "case_id": case["case_id"],
        "material": case["material"],
        "analysis": analysis,
        "constraints": constraints,
        "cpp_validation": cpp,
        "safety_consistency": validation,
        "knowledge_documents": [
            r["document"]
            for r in knowledge.get("results", [])
        ],
        "final_status": (
            "VALID"
            if validation["status"] == "PASS"
            else "INVALID"
        ),
    }