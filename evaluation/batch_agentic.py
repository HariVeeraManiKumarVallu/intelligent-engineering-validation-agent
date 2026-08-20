from __future__ import annotations

from typing import Any, Dict, List

from tools.data_processor import process_engineering_data
from tools.knowledge_retrieval import retrieve_technical_knowledge
from tools.engineering_analysis import perform_engineering_analysis
from tools.constraint_checker import check_engineering_constraints
from tools.cpp_validation import run_cpp_validation
from tools.safety_consistency import validate_analysis_result


REQUIRED_TOOLS = {
    "process_engineering_data",
    "perform_engineering_analysis",
    "check_engineering_constraints",
    "run_cpp_validation",
    "validate_analysis_result",
}

AVAILABLE_TOOLS = REQUIRED_TOOLS | {
    "retrieve_technical_knowledge",
}


def evaluate_plan(
    plan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate the tool selection produced by the LLM.

    This function is completely local.
    No LLM is called.
    """

    selected = plan.get("tools", [])

    if not isinstance(selected, list):
        selected = []

    selected_set = set(selected)

    missing_tools = sorted(
        REQUIRED_TOOLS - selected_set
    )

    invalid_tools = sorted(
        selected_set - AVAILABLE_TOOLS
    )

    return {
        "required_tools_present": (
            len(missing_tools) == 0
        ),
        "missing_tools": missing_tools,
        "invalid_tools": invalid_tools,
        "tool_selection_valid": (
            len(missing_tools) == 0
            and len(invalid_tools) == 0
        ),
    }


def normalize_plans(
    plans: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Convert the list of model plans into a case_id lookup.

    Example:

        [
            {
                "case_id": "CASE_001",
                "tools": [...]
            }
        ]

    becomes:

        {
            "CASE_001": {
                "case_id": "CASE_001",
                "tools": [...]
            }
        }
    """

    normalized: Dict[str, Dict[str, Any]] = {}

    for plan in plans:

        if not isinstance(plan, dict):
            continue

        case_id = plan.get("case_id")

        if not case_id:
            continue

        tools = plan.get("tools", [])

        if not isinstance(tools, list):
            tools = []

        subtasks = plan.get(
            "subtasks",
            [],
        )

        if not isinstance(subtasks, list):
            subtasks = []

        normalized[case_id] = {
            "case_id": case_id,
            "subtasks": subtasks,
            "tools": tools,
        }

    return normalized


def _execute_local_tools(
    case: Dict[str, Any],
    plan: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Execute the tools selected by the already-generated plan.

    IMPORTANT:

    This function does NOT call any LLM.

    The LLM has already produced the plan.
    Everything from this point onward is deterministic/local
    engineering execution.
    """

    selected_tools = set(
        plan.get("tools", [])
    )

    # ------------------------------------------------------
    # 1. Process engineering data
    # ------------------------------------------------------

    if "process_engineering_data" not in selected_tools:

        raise RuntimeError(
            "Plan is missing "
            "'process_engineering_data'."
        )

    processed = process_engineering_data.invoke(
        {
            "case": case,
        }
    )

    # ------------------------------------------------------
    # 2. Optional technical knowledge retrieval
    # ------------------------------------------------------

    knowledge_documents = []

    if "retrieve_technical_knowledge" in selected_tools:

        knowledge = retrieve_technical_knowledge.invoke(
            {
                "query": (
                    "Beam bending validation for "
                    f"{case.get('material', 'material')}"
                )
            }
        )

        knowledge_results = knowledge.get(
            "results",
            [],
        )

        if isinstance(
            knowledge_results,
            list,
        ):

            for item in knowledge_results:

                if isinstance(item, dict):

                    document = item.get(
                        "document"
                    )

                    if document is not None:
                        knowledge_documents.append(
                            document
                        )

    # ------------------------------------------------------
    # 3. Engineering analysis
    # ------------------------------------------------------

    if "perform_engineering_analysis" not in selected_tools:

        raise RuntimeError(
            "Plan is missing "
            "'perform_engineering_analysis'."
        )

    analysis = perform_engineering_analysis.invoke(
        {
            "data": processed,
        }
    )

    # ------------------------------------------------------
    # 4. Constraint checking
    # ------------------------------------------------------

    if "check_engineering_constraints" not in selected_tools:

        raise RuntimeError(
            "Plan is missing "
            "'check_engineering_constraints'."
        )

    constraints = check_engineering_constraints.invoke(
        {
            "analysis": analysis,
            "data": processed,
        }
    )

    # ------------------------------------------------------
    # 5. C++ validation
    # ------------------------------------------------------

    if "run_cpp_validation" not in selected_tools:

        raise RuntimeError(
            "Plan is missing "
            "'run_cpp_validation'."
        )

    cpp = run_cpp_validation.invoke(
        {
            "data": processed,
        }
    )

    # ------------------------------------------------------
    # 6. Safety and consistency validation
    # ------------------------------------------------------

    if "validate_analysis_result" not in selected_tools:

        raise RuntimeError(
            "Plan is missing "
            "'validate_analysis_result'."
        )

    validation = validate_analysis_result.invoke(
        {
            "processed": processed,
            "analysis": analysis,
            "constraints": constraints,
            "cpp": cpp,
        }
    )

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    final_status = (
        "VALID"
        if validation.get("status") == "PASS"
        else "INVALID"
    )

    return {
        "case_id": case["case_id"],
        "material": case["material"],
        "analysis": analysis,
        "constraints": constraints,
        "cpp_validation": cpp,
        "safety_consistency": validation,
        "knowledge_documents": knowledge_documents,
        "final_status": final_status,
    }


def execute_model_plans(
    cases: List[Dict[str, Any]],
    plans: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Execute already-generated LLM plans locally.

    IMPORTANT:

    There is NO build_graph() here.

    There is NO planner_node() here.

    There is NO plan_task() here.

    There is NO invoke_llm() here.

    Therefore this function performs ZERO additional
    LLM/API requests.
    """

    plans_by_case = normalize_plans(
        plans
    )

    results: List[Dict[str, Any]] = []

    for case in cases:

        case_id = case["case_id"]

        print(
            f"  Executing {case_id}..."
        )

        plan = plans_by_case.get(
            case_id
        )

        # --------------------------------------------------
        # Missing plan
        # --------------------------------------------------

        if plan is None:

            results.append(
                {
                    "case_id": case_id,
                    "material": case.get(
                        "material"
                    ),
                    "final_status": "INVALID",
                    "error": (
                        "Model did not return "
                        "a plan for this case."
                    ),
                    "plan_evaluation": {
                        "required_tools_present": False,
                        "missing_tools": sorted(
                            REQUIRED_TOOLS
                        ),
                        "invalid_tools": [],
                        "tool_selection_valid": False,
                    },
                }
            )

            continue

        # --------------------------------------------------
        # Validate model plan
        # --------------------------------------------------

        plan_evaluation = evaluate_plan(
            plan
        )

        # --------------------------------------------------
        # Do not execute an invalid plan
        # --------------------------------------------------

        if not plan_evaluation[
            "tool_selection_valid"
        ]:

            results.append(
                {
                    "case_id": case_id,
                    "material": case.get(
                        "material"
                    ),
                    "final_status": "INVALID",
                    "error": (
                        "Invalid model-generated "
                        "tool plan."
                    ),
                    "plan": plan,
                    "plan_evaluation": (
                        plan_evaluation
                    ),
                }
            )

            continue

        # --------------------------------------------------
        # Execute tools locally
        # --------------------------------------------------

        try:

            result = _execute_local_tools(
                case=case,
                plan=plan,
            )

            result["plan"] = plan

            result["plan_evaluation"] = (
                plan_evaluation
            )

            results.append(
                result
            )

        except Exception as exc:

            results.append(
                {
                    "case_id": case_id,
                    "material": case.get(
                        "material"
                    ),
                    "final_status": "INVALID",
                    "error": str(exc),
                    "plan": plan,
                    "plan_evaluation": (
                        plan_evaluation
                    ),
                }
            )

    return results