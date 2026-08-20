from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from agents.planner import plan_task
from agents.graph import build_graph

ROOT = Path(__file__).resolve().parent

def main():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key.")

    case_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "inputs" / "case_001.json"
    case = json.loads(case_path.read_text(encoding="utf-8"))

    plan = plan_task(case)
    app = build_graph()
    state = app.invoke({"case": case, "plan": plan})

    print(json.dumps({
        "plan": plan,
        "result": state["result"],
    }, indent=2))

if __name__ == "__main__":
    main()
