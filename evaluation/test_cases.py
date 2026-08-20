from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict


ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = ROOT / "data" / "inputs"
EXPECTED_DIR = ROOT / "data" / "expected_results"


def load_cases() -> List[Dict]:
    """Load all engineering input cases."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(INPUT_DIR.glob("*.json"))
    ]


def load_expected() -> List[Dict]:
    """Load expected validation results."""
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(EXPECTED_DIR.glob("*.json"))
    ]