# Intelligent Engineering Validation Agent

A research prototype implementing a hybrid C++/Python Agentic AI workflow for engineering validation.

## Scope

- LangGraph-based task orchestration
- LangChain tools
- LLM-based task planning using Nemotron 3.5 Lightning
- Structured engineering data processing
- PyTorch numerical analysis
- Technical knowledge retrieval
- Six specialized engineering tools
- Independent C++ validation
- Rule-based safety and consistency checks
- Structured analysis results
- Agentic vs conventional evaluation on 25 engineering cases

## Engineering Problem

The prototype evaluates maximum bending stress for a simply supported rectangular beam with a central point load.

For load `P`, span `L`, width `b`, and height `h`:

    M = P * L / 4

    sigma = 6 * M / (b * h^2)

The engineering values are illustrative software-test assumptions, not real structural design guidance.

## Architecture

The system uses an LLM for task planning and local deterministic tools for engineering execution and validation.

    Engineering Case
           |
           v
    Nemotron 3.5 Lightning
           |
           | Tool-selection plan
           v
    LangGraph Agentic Workflow
           |
           +--> Process Engineering Data
           |
           +--> Retrieve Technical Knowledge
           |
           +--> Perform Engineering Analysis
           |
           +--> Check Engineering Constraints
           |
           +--> Run C++ Validation
           |
           +--> Safety & Consistency Validation
           |
           v
    Structured Validation Result

The LLM is used for planning. Engineering calculations, constraint checking, C++ validation, and safety/consistency validation are performed locally.

## Specialized Tools

The agent has six specialized tools:

1. `process_engineering_data`
2. `retrieve_technical_knowledge`
3. `perform_engineering_analysis`
4. `check_engineering_constraints`
5. `run_cpp_validation`
6. `validate_analysis_result`

The agentic planner selects the tools required for the engineering task. Mandatory validation tools are checked before execution.

## Technical Knowledge

The prototype contains local engineering knowledge documents covering:

- Beam bending
- Material assumptions
- Validation rules

These documents are used by the technical knowledge retrieval tool.

## C++ Validation

The engineering calculation is independently validated using a C++ implementation.

The Python/PyTorch analysis and C++ validation results are compared using the project's consistency checks.

The prototype requires the independent implementations to agree within the configured relative tolerance.

## Project Structure

    intelligent-engineering-validation-agent/
    |
    +-- agents/
    |   +-- graph.py
    |   +-- llm_provider.py
    |   +-- planner.py
    |
    +-- cpp/
    |   +-- validator.cpp
    |   +-- validator.hpp
    |   +-- CMakeLists.txt
    |
    +-- data/
    |   +-- inputs/
    |   +-- expected_results/
    |
    +-- evaluation/
    |   +-- agentic.py
    |   +-- batch_agentic.py
    |   +-- check_conventional.py
    |   +-- compare_existing.py
    |   +-- conventional.py
    |   +-- metrics.py
    |   +-- openrouter_batch.py
    |   +-- plots.py
    |   +-- run_evaluation.py
    |   +-- run_nemotron_evaluation.py
    |   +-- test_cases.py
    |   +-- results/
    |
    +-- knowledge/
    |
    +-- tools/
    |   +-- constraint_checker.py
    |   +-- cpp_validation.py
    |   +-- data_processor.py
    |   +-- engineering_analysis.py
    |   +-- knowledge_retrieval.py
    |   +-- safety_consistency.py
    |
    +-- tests/
    |
    +-- main.py
    +-- requirements.txt
    +-- pyproject.toml
    +-- README.md

## Setup

### 1. Create Environment

    python -m venv .venv

Windows:

    .venv\Scripts\activate

Linux/macOS:

    source .venv/bin/activate

### 2. Install Dependencies

Using pip:

    pip install -r requirements.txt

Or, with `uv`:

    uv sync

### 3. Configure OpenRouter

Create a `.env` file in the repository root.

    OPENROUTER_NEMOTRON_API_KEY=your_openrouter_api_key
    NEMOTRON_MODEL=nvidia/nemotron-3.5-lightning:free

The project uses a single Nemotron model path through OpenRouter.

No GLM or Gemma API configuration is required.

### 4. Build C++ Validator

From the repository root:

    cmake -S cpp -B cpp/build
    cmake --build cpp/build --config Release

## Running the Agent

Run the main application:

    python main.py

Or provide an individual engineering case:

    python main.py data/inputs/case_001.json

With `uv`:

    uv run python main.py

## Running Tests

Run the automated test suite:

    pytest

The current test suite validates the core engineering workflow and tool behavior.

## Evaluation

The evaluation compares two workflows:

1. Conventional fixed workflow
2. Nemotron-planned agentic workflow

The evaluation dataset contains 25 engineering cases.

The cases include both valid engineering configurations and deliberately constructed constraint-violation cases.

### Evaluation Metrics

The evaluation reports:

- Task Completion Rate
- Tool Selection Accuracy
- Data Analysis Accuracy
- Validation Error Detection
- Response Validity

### Nemotron Evaluation

The Nemotron evaluation uses a single OpenRouter generation request to produce planning decisions for the complete batch of engineering cases.

The generated plans are then executed locally.

Run:

    uv run python -m evaluation.run_nemotron_evaluation

The generated Nemotron results are stored under:

    evaluation/results/nemotron/

Including:

    nemotron_batch_output.json
    nemotron_plans.json
    nemotron_results.json
    nemotron_metrics.json

### Agentic vs Conventional Comparison

The stored Nemotron results can be compared with the conventional workflow without making another LLM/API request.

Run:

    uv run python -m evaluation.compare_existing

The comparison is stored under:

    evaluation/results/comparison/

Including:

    agentic_vs_conventional.json
    agentic_vs_conventional_metrics.png
    conventional_metrics.json
    conventional_results.json

## Evaluation Results

The current evaluation contains 25 engineering cases.

### Agentic vs Conventional

| Metric | Nemotron Agentic | Conventional |
|---|---:|---:|
| Task Completion Rate | 1.0000 | 1.0000 |
| Tool Selection Accuracy | 1.0000 | 1.0000 |
| Data Analysis Accuracy | 1.0000 | 1.0000 |
| Validation Error Detection | 1.0000 | 1.0000 |
| Response Validity | 1.0000 | 1.0000 |

### Validation Status

| Workflow | VALID | INVALID | Total |
|---|---:|---:|---:|
| Nemotron Agentic | 22 | 3 | 25 |
| Conventional | 22 | 3 | 25 |

Both workflows correctly identified all 25 expected validation outcomes.

The three intentionally invalid cases are:

- `CASE_007`
- `CASE_014`
- `CASE_021`

These cases fail because their calculated bending stress exceeds the supplied allowable stress.

### Invalid Case Validation

    CASE_007
    Calculated stress: 16.204 MPa
    Allowable stress:  12.963 MPa
    Result: INVALID

    CASE_014
    Calculated stress: 26.343 MPa
    Allowable stress:  21.074 MPa
    Result: INVALID

    CASE_021
    Calculated stress: 52.734 MPa
    Allowable stress: 42.188 MPa
    Result: INVALID

Therefore:

    22 VALID + 3 INVALID = 25/25 correctly classified cases

## Generated Evaluation Graphs

The Nemotron evaluation graphs are stored under:

    evaluation/results/nemotron/

Current graphs:

    nemotron_metric_evaluation.png
    nemotron_validation_status.png

The Agentic vs Conventional comparison graph is stored under:

    evaluation/results/comparison/

    agentic_vs_conventional_metrics.png

## Reproducibility

The evaluation separates LLM planning from deterministic engineering execution.

    LLM Planning
         |
         v
    Stored Plans
         |
         v
    Local Tool Execution
         |
         +--> Python/PyTorch Analysis
         +--> Constraint Checking
         +--> C++ Validation
         +--> Safety/Consistency Validation
         |
         v
    Evaluation Metrics

This allows the stored Nemotron plans and results to be analyzed and compared without repeatedly calling the LLM API.

## Current Validation Status

- 25 engineering test cases evaluated
- 22 valid cases correctly classified
- 3 invalid constraint-violation cases correctly classified
- Agentic workflow evaluated
- Conventional baseline evaluated
- Agentic vs conventional comparison completed
- Python and C++ validation included
- Safety and consistency checks included
- Evaluation graphs generated
- Automated tests: 3/3 passed