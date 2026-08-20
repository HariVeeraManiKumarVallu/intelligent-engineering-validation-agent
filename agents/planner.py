from __future__ import annotations

import json
from typing import Any, Dict

from agents.llm_provider import invoke_llm


TOOLS = [
    "process_engineering_data",
    "retrieve_technical_knowledge",
    "perform_engineering_analysis",
    "check_engineering_constraints",
    "run_cpp_validation",
    "validate_analysis_result",
]

REQUIRED_TOOLS = [
    "process_engineering_data",
    "perform_engineering_analysis",
    "check_engineering_constraints",
    "run_cpp_validation",
    "validate_analysis_result",
]


def plan_task(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decompose an engineering task and select the tools
    required to complete it.
    """

    prompt = f"""
You are an engineering-analysis task planner.

Your task is to decompose the engineering problem and
select the appropriate tools.

Return ONLY valid JSON with exactly these keys:

{{
    "subtasks": [...],
    "tools": [...]
}}

Available tools:
{TOOLS}

The following tools are mandatory for every engineering case:
{REQUIRED_TOOLS}

Include retrieve_technical_knowledge when technical
knowledge is useful for the case.

Do not select tools outside the available tool list.

Engineering case:
{json.dumps(case, indent=2)}
"""

    response = invoke_llm(prompt)

    text = (
        response.content
        if isinstance(response.content, str)
        else str(response.content)
    )

    try:
        plan = json.loads(text)

    except json.JSONDecodeError:
        plan = {
            "subtasks": [
                "Process structured engineering data",
                "Perform engineering analysis",
                "Check engineering constraints",
                "Validate using C++",
                "Perform safety and consistency checks",
            ],
            "tools": REQUIRED_TOOLS.copy(),
        }

    selected_tools = plan.get("tools", [])

    if not isinstance(selected_tools, list):
        selected_tools = []

    selected_tools = [
        tool for tool in selected_tools
        if tool in TOOLS
    ]

    for required_tool in REQUIRED_TOOLS:
        if required_tool not in selected_tools:
            selected_tools.append(required_tool)

    plan["tools"] = selected_tools

    if not isinstance(plan.get("subtasks"), list):
        plan["subtasks"] = []

    return plan