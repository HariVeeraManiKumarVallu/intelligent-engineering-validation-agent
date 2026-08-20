from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict

from langchain_core.tools import tool


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "cpp" / "build"
MSYS2_BIN = Path(r"C:\msys64\ucrt64\bin")


def _binary() -> Path:
    """Locate the compiled C++ validator executable."""
    candidates = [
        BUILD / "validator.exe",
        BUILD / "validator",
        BUILD / "Release" / "validator.exe",
    ]

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "C++ validator not built. "
        "Run the CMake build first."
    )


def _subprocess_environment() -> dict[str, str]:
    """Create an environment containing the MSYS2 runtime libraries."""
    environment = os.environ.copy()

    if MSYS2_BIN.exists():
        current_path = environment.get("PATH", "")
        environment["PATH"] = (
            f"{MSYS2_BIN}{os.pathsep}{current_path}"
        )

    return environment


@tool
def run_cpp_validation(data: Dict[str, Any]) -> Dict[str, object]:
    """Run the independent C++ beam-stress validation routine."""

    if data.get("status") != "PASS":
        return {
            "status": "FAIL",
            "error": "Input data has not passed processing.",
        }

    try:
        binary = _binary()

        args = [
            str(binary),
            str(float(data["load_n"])),
            str(float(data["length_m"])),
            str(float(data["width_m"])),
            str(float(data["height_m"])),
            str(float(data["allowable_stress_pa"])),
        ]

        completed = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
            env=_subprocess_environment(),
        )

        output = completed.stdout.strip()
        parts = output.split()

        if len(parts) < 3:
            return {
                "status": "FAIL",
                "error": f"Unexpected C++ output: {output}",
            }

        stress_pa = float(parts[0])
        allowable_stress_pa = float(parts[1])
        constraint_pass = parts[2] == "PASS"

        return {
            "status": "PASS",
            "stress_pa": stress_pa,
            "allowable_stress_pa": allowable_stress_pa,
            "constraint_pass": constraint_pass,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "FAIL",
            "error": "C++ validator timed out.",
        }

    except (KeyError, ValueError) as exc:
        return {
            "status": "FAIL",
            "error": f"Invalid validation data: {exc}",
        }

    except Exception as exc:
        return {
            "status": "FAIL",
            "error": str(exc),
        }