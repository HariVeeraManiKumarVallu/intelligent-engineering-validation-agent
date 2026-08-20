from __future__ import annotations

import json
import os
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv


load_dotenv()


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


AVAILABLE_TOOLS = [
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


def _build_prompt(
    cases: List[Dict[str, Any]],
) -> str:
    """
    Build one compact planning prompt for all engineering cases.

    The Nemotron model only selects tools.
    All engineering calculations and validation
    are performed locally after the API request.
    """

    planning_cases = [
        {
            "case_id": case["case_id"],
            "material": case["material"],
            "load_n": case["load_n"],
            "length_m": case["length_m"],
            "width_m": case["width_m"],
            "height_m": case["height_m"],
            "allowable_stress_pa": case[
                "allowable_stress_pa"
            ],
        }
        for case in cases
    ]

    return (
        "You are an engineering-analysis task planner.\n\n"
        f"You will receive exactly {len(planning_cases)} engineering cases.\n\n"
        "For every case, return exactly one planning decision.\n\n"
        "Available tools:\n"
        f"{json.dumps(AVAILABLE_TOOLS, separators=(',', ':'))}\n\n"
        "Mandatory tools for every case:\n"
        f"{json.dumps(REQUIRED_TOOLS, separators=(',', ':'))}\n\n"
        "Return ONLY a JSON object in this exact structure:\n\n"
        '{"plans":[{"case_id":"CASE_001","tools":['
        '"process_engineering_data",'
        '"perform_engineering_analysis",'
        '"check_engineering_constraints",'
        '"run_cpp_validation",'
        '"validate_analysis_result"'
        "]}]}\n\n"
        "Rules:\n"
        "1. Return exactly one plan for every case.\n"
        "2. Preserve every case_id exactly.\n"
        "3. Every mandatory tool must be included.\n"
        "4. Only use tools from the available-tools list.\n"
        "5. retrieve_technical_knowledge may be included when useful.\n"
        "6. Do not include subtasks.\n"
        "7. Do not calculate engineering results.\n"
        "8. Do not include explanations.\n"
        "9. Do not return Markdown.\n"
        "10. Return only the JSON object.\n\n"
        "Engineering cases:\n"
        f"{json.dumps(planning_cases, separators=(',', ':'))}"
    )


def _format_http_error(
    response: requests.Response,
    model: str,
) -> str:
    """Extract useful information from an OpenRouter HTTP error."""

    try:
        data = response.json()
    except ValueError:
        data = response.text

    if isinstance(data, dict):

        error = data.get("error")

        if isinstance(error, dict):

            message = error.get(
                "message",
                "No error message returned.",
            )

            error_type = error.get(
                "type",
                "unknown",
            )

            error_code = error.get(
                "code",
                response.status_code,
            )

            return (
                "OpenRouter request failed.\n"
                f"Model: {model}\n"
                f"HTTP status: {response.status_code}\n"
                f"Error code: {error_code}\n"
                f"Error type: {error_type}\n"
                f"Message: {message}"
            )

    return (
        "OpenRouter request failed.\n"
        f"Model: {model}\n"
        f"HTTP status: {response.status_code}\n"
        f"Response: {data}"
    )


def _validate_plans(
    plans: List[Dict[str, Any]],
    cases: List[Dict[str, Any]],
    model: str,
) -> None:
    """Validate the complete Nemotron planning output."""

    if len(plans) != len(cases):

        raise RuntimeError(
            f"{model} returned {len(plans)} plans "
            f"for {len(cases)} cases."
        )

    expected_case_ids = {
        case["case_id"]
        for case in cases
    }

    returned_case_ids = {
        plan.get("case_id")
        for plan in plans
    }

    missing_case_ids = (
        expected_case_ids - returned_case_ids
    )

    unexpected_case_ids = (
        returned_case_ids - expected_case_ids
    )

    if missing_case_ids:

        raise RuntimeError(
            f"{model} omitted case IDs: "
            f"{sorted(missing_case_ids)}"
        )

    if unexpected_case_ids:

        raise RuntimeError(
            f"{model} returned unexpected case IDs: "
            f"{sorted(unexpected_case_ids)}"
        )

    for plan in plans:

        case_id = plan.get("case_id")

        tools = plan.get("tools")

        if not isinstance(tools, list):

            raise RuntimeError(
                f"{model} returned an invalid tools list "
                f"for {case_id}."
            )

        selected_tools = set(tools)

        missing_tools = (
            set(REQUIRED_TOOLS) - selected_tools
        )

        unexpected_tools = (
            selected_tools - set(AVAILABLE_TOOLS)
        )

        if missing_tools:

            raise RuntimeError(
                f"{model} plan for {case_id} "
                f"is missing mandatory tools: "
                f"{sorted(missing_tools)}"
            )

        if unexpected_tools:

            raise RuntimeError(
                f"{model} plan for {case_id} "
                f"contains unsupported tools: "
                f"{sorted(unexpected_tools)}"
            )


def _extract_json_content(
    content: str,
    model: str,
) -> Dict[str, Any]:
    """
    Parse the model's JSON response.

    Handles harmless surrounding whitespace and Markdown
    code fences, but does not attempt to repair truncated JSON.
    """

    text = content.strip()

    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    try:

        parsed = json.loads(text)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            f"{model} returned invalid JSON.\n\n"
            f"JSON error: {exc}\n\n"
            f"Response:\n{text}"
        ) from exc

    if not isinstance(parsed, dict):

        raise RuntimeError(
            f"{model} returned JSON, but the top-level "
            "value is not an object.\n\n"
            f"Response:\n{text}"
        )

    return parsed


def _call_openrouter(
    api_key: str,
    model: str,
    cases: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Make exactly ONE OpenRouter generation request.

    There is deliberately no retry.
    """

    prompt = _build_prompt(cases)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Intelligent Engineering Validation Agent",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Return only valid JSON. "
                    "Do not use Markdown. "
                    "Do not explain your answer."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "reasoning": {
            "enabled": False,
        },
        "max_tokens": 12000,
        "temperature": 0,
        "seed": 42,
    }

    print()
    print("Sending one request to OpenRouter...")
    print(f"Prompt characters: {len(prompt)}")
    print(f"Max output tokens: {payload['max_tokens']}")

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=180,
    )

    # ------------------------------------------------------
    # Never retry.
    # ------------------------------------------------------

    if response.status_code == 429:

        raise RuntimeError(
            _format_http_error(
                response,
                model,
            )
            + "\n\n"
            "No automatic retry was performed."
        )

    if not response.ok:

        raise RuntimeError(
            _format_http_error(
                response,
                model,
            )
            + "\n\n"
            "No automatic retry was performed."
        )

    # ------------------------------------------------------
    # Parse HTTP response.
    # ------------------------------------------------------

    try:

        data = response.json()

    except ValueError as exc:

        raise RuntimeError(
            f"{model} returned a non-JSON HTTP response.\n\n"
            f"Response:\n{response.text}"
        ) from exc

    choices = data.get("choices")

    if not isinstance(choices, list) or not choices:

        raise RuntimeError(
            f"{model} returned no choices.\n\n"
            f"Response:\n"
            f"{json.dumps(data, indent=2)}"
        )

    message = choices[0].get(
        "message",
        {},
    )

    if not isinstance(message, dict):

        raise RuntimeError(
            f"{model} returned an invalid message object."
        )

    content = message.get("content")

    if not isinstance(content, str):

        content = str(content)

    if not content.strip():

        raise RuntimeError(
            f"{model} returned empty content."
        )

    # ------------------------------------------------------
    # Check whether generation was truncated.
    # ------------------------------------------------------

    finish_reason = choices[0].get(
        "finish_reason"
    )

    if finish_reason not in (
        None,
        "stop",
    ):

        raise RuntimeError(
            f"{model} generation did not finish normally.\n"
            f"Finish reason: {finish_reason}\n\n"
            f"Response:\n{content}"
        )

    # ------------------------------------------------------
    # Parse model-generated JSON.
    # ------------------------------------------------------

    parsed = _extract_json_content(
        content,
        model,
    )

    plans = parsed.get("plans")

    if not isinstance(plans, list):

        raise RuntimeError(
            f"{model} response does not contain "
            "a valid 'plans' list.\n\n"
            f"Response:\n"
            f"{json.dumps(parsed, indent=2)}"
        )

    _validate_plans(
        plans,
        cases,
        model,
    )

    return {
        "model": model,
        "plans": plans,
        "raw_content": content,
        "usage": data.get("usage"),
        "finish_reason": finish_reason,
        "reasoning_details": message.get(
            "reasoning_details"
        ),
    }


# ==========================================================
# NEMOTRON
# ==========================================================


def run_nemotron_batch(
    cases: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Execute exactly ONE Nemotron generation request.

    No retry is performed.
    """

    api_key = os.getenv(
        "OPENROUTER_NEMOTRON_API_KEY"
    )

    model = os.getenv(
        "NEMOTRON_MODEL",
        "nvidia/nemotron-3.5-lightning:free",
    )

    if not api_key:

        raise RuntimeError(
            "OPENROUTER_NEMOTRON_API_KEY "
            "is not configured."
        )

    print()
    print("=" * 70)
    print("LLM CALL 1/1")
    print(f"Model: {model}")
    print("=" * 70)

    result = _call_openrouter(
        api_key=api_key,
        model=model,
        cases=cases,
    )

    print()
    print("Nemotron request completed.")
    print(
        f"Nemotron plans received: "
        f"{len(result['plans'])}"
    )

    return result
