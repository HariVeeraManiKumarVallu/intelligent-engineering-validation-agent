# Intelligent Engineering Validation Agent


### A Hybrid Python/C++ Agentic AI Prototype for Engineering Validation

**LLM Planning** → **Local Engineering Analysis** → **Independent C++ Validation** → **Safety & Consistency Checks**

| Evaluation | Result |
|---|---:|
| Test Cases | **25** |
| Nemotron VALID | **22** |
| Nemotron INVALID | **3** |
| Conventional VALID | **22** |
| Conventional INVALID | **3** |
| Nemotron API Requests | **1** |
| Automated Tests | **3 / 3 passed** |


The project demonstrates how an LLM can be used to plan an engineering task and select the tools needed to solve it, while the actual engineering calculations and validation are performed locally using deterministic software.

For this prototype, the engineering problem is the bending-stress analysis of a simply supported rectangular beam with a central point load. The system processes the engineering input, retrieves relevant technical knowledge, calculates bending stress using PyTorch, checks the result against an allowable stress, independently validates the calculation using C++, and finally performs safety and consistency checks.

The project also evaluates an Agentic AI workflow against a fixed conventional workflow using 25 engineering test cases.

---

## What the Project Does

The system receives a structured engineering case containing values such as:

| Engineering Input | Description |
|---|---|
| Material | Material used for the beam |
| Applied load | Load applied to the beam |
| Beam length | Beam span |
| Beam width | Rectangular beam width |
| Beam height | Rectangular beam height |
| Allowable stress | Maximum permitted stress |

The Agentic workflow first uses the Nemotron 3.5 Lightning model through OpenRouter to create a tool-selection plan.

The generated plan identifies which engineering tools should be used. The plan is then validated locally before execution.

After the LLM planning step, the engineering work is performed locally:

| Step | Local Operation | Purpose |
|---:|---|---|
| 1 | Engineering input validation | Validate and normalize the input |
| 2 | Technical knowledge retrieval | Retrieve relevant engineering knowledge |
| 3 | PyTorch analysis | Calculate maximum bending stress |
| 4 | Constraint checking | Compare calculated stress with allowable stress |
| 5 | C++ validation | Independently repeat the engineering calculation |
| 6 | Python/C++ comparison | Check numerical consistency |
| 7 | Safety & consistency validation | Determine the final `VALID` / `INVALID` result |

The important design principle is that the LLM is responsible for task planning, while the engineering calculation and validation are handled by deterministic local tools.

---

## Engineering Problem

The prototype uses a simply supported rectangular beam with a central point load.

For:

- `P` = applied load
- `L` = beam span
- `b` = beam width
- `h` = beam height

the maximum bending moment is:

$$M = \frac{P \times L}{4}$$

and the maximum bending stress is:

$$\sigma = \frac{6 \times M}{b \times h^2}$$

The calculated stress is compared with the supplied allowable stress.

The prototype uses simplified engineering assumptions for software evaluation. The material values and engineering cases are intended for testing the software workflow and are not real structural design guidance.

---

## Architecture

The project separates probabilistic LLM planning from deterministic engineering execution.

``` 
                         ┌─────────────────────────┐
                         │    Engineering Case     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Nemotron 3.5 Lightning  │
                         │      OpenRouter         │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Tool Selection Plan   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │   Local Plan Validation │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    Local Execution      │
                         └────────────┬────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
     ┌────────────────┐     ┌──────────────────┐    ┌──────────────────┐
     │ Data Processing│     │Knowledge Retrieval│    │ PyTorch Analysis │
     └───────┬────────┘     └────────┬─────────┘    └────────┬─────────┘
             │                       │                       │
             └───────────────────────┼───────────────────────┘
                                     │
                                     ▼
                         ┌─────────────────────────┐
                         │  Constraint Checking   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ C++ Independent        │
                         │      Validation        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Safety & Consistency   │
                         │        Checks          │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                ┌────────────────┐        ┌────────────────┐
                │      VALID     │        │     INVALID    │
                └────────────────┘        └────────────────┘
```

The LLM does not perform the final engineering calculation.

The Nemotron model produces the plan, and the generated plan is then executed locally by the project's engineering tools.

## Agentic Workflow

The Agentic workflow is implemented using LangGraph and LangChain tools.

The main execution flow is:

| Step | Component | Purpose |
|---:|---|---|
| 1 | Process Engineering Data | Validate and normalize the engineering input |
| 2 | Retrieve Technical Knowledge | Retrieve relevant information from local documents |
| 3 | Perform Engineering Analysis | Calculate bending moment, stress, and safety factor using PyTorch |
| 4 | Check Engineering Constraints | Compare calculated stress with allowable stress |
| 5 | Run Independent C++ Validation | Independently calculate and validate the engineering result |
| 6 | Safety & Consistency Validation | Check safety, validity, and Python/C++ numerical consistency |
| 7 | Final Result | Produce the final `VALID` or `INVALID` result |

The LangGraph execution graph preserves the model-generated plan supplied to it. It does not generate another LLM plan during local execution.

This is important for evaluation because the exact plan produced by Nemotron is the plan that is evaluated.

## Main Components

### `agents/`

Contains the Agentic AI planning and LangGraph orchestration logic.

| File | Role |
|---|---|
| `agents/planner.py` | Defines the engineering planning task and required tools |
| `agents/llm_provider.py` | Creates the Nemotron/OpenRouter LLM client |
| `agents/graph.py` | Builds the LangGraph execution graph |

#### `agents/planner.py`

Defines the engineering planning task.

It provides Nemotron with:

- The engineering case
- The available tools
- The tools that are mandatory for every case

The planner returns a structured plan containing:

- `subtasks`
- `tools`

The mandatory tools are:

- `process_engineering_data`
- `perform_engineering_analysis`
- `check_engineering_constraints`
- `run_cpp_validation`
- `validate_analysis_result`

Technical knowledge retrieval is available as an additional tool.

#### `agents/llm_provider.py`

Creates the Nemotron LLM client through OpenRouter using LangChain's `ChatOpenAI` interface.

The default model is:

`nvidia/nemotron-3.5-lightning:free`

The API key is read from:

`OPENROUTER_NEMOTRON_API_KEY`

There is no Gemini fallback in the current implementation.

#### `agents/graph.py`

Builds the LangGraph execution graph.

The graph receives an already-generated plan and executes the local engineering workflow.

It contains nodes for:

- Plan input
- Data processing
- Knowledge retrieval
- Engineering analysis
- Constraint checking
- C++ validation
- Final validation

No additional LLM request is made inside this graph.

### `tools/`

Contains the specialized engineering tools used by both the Agentic and conventional workflows.

| File | Responsibility |
|---|---|
| `tools/data_processor.py` | Validate and normalize engineering input |
| `tools/knowledge_retrieval.py` | Retrieve relevant engineering knowledge |
| `tools/engineering_analysis.py` | Perform beam calculations using PyTorch |
| `tools/constraint_checker.py` | Check allowable-stress constraints |
| `tools/cpp_validation.py` | Execute independent C++ validation |
| `tools/safety_consistency.py` | Perform final deterministic validation |

#### `tools/data_processor.py`

Validates and normalizes the structured engineering input.

It checks that required fields are present and that the numerical engineering values are positive.

Required fields include:

- `case_id`
- `material`
- `load_n`
- `length_m`
- `width_m`
- `height_m`
- `allowable_stress_pa`

#### `tools/knowledge_retrieval.py`

Retrieves relevant engineering information from the local knowledge documents.

The implementation uses TF-IDF vectorization and cosine similarity to rank the local documents against the engineering query.

The current knowledge documents are:

- `beam_bending.txt`
- `materials.txt`
- `validation.txt`

#### `tools/engineering_analysis.py`

Performs the beam calculation using PyTorch.

It calculates:

- Maximum bending moment
- Maximum bending stress
- Safety factor

The calculation uses `float64` tensors.

#### `tools/constraint_checker.py`

Checks whether the calculated bending stress is within the supplied allowable stress.

If:

`calculated stress <= allowable stress`

the stress constraint passes.

Otherwise, the case fails the engineering constraint.

#### `tools/cpp_validation.py`

Runs the independent C++ validation executable.

The Python tool:

1. Locates `validator.exe`.
2. Passes the engineering values to the executable.
3. Reads the C++ result.
4. Returns the independently calculated stress and constraint result.

On Windows, the tool also adds the MSYS2 UCRT64 runtime directory to the subprocess `PATH` so that the compiled executable can run correctly.

#### `tools/safety_consistency.py`

Performs the final deterministic validation.

It checks:

- Input validity
- Analysis validity
- Constraint result
- C++ validation availability
- Python/C++ numerical consistency
- Safety result

The Python and C++ stress calculations must agree within a relative tolerance of:

`0.01%`

A failed safety or consistency check prevents the result from being marked `VALID`.

---

## C++ Validation

The C++ implementation provides an independent implementation of the same beam-stress calculation.

The C++ validator is located in:

`cpp/validator.cpp`

and its interface is defined in:

`cpp/validator.hpp`

The project uses CMake to build the executable.

The resulting executable is:

`cpp/build/validator.exe`

The C++ program receives:

| Input | Meaning |
|---|---|
| `load` | Applied load |
| `length` | Beam length |
| `width` | Beam width |
| `height` | Beam height |
| `allowable_stress` | Maximum permitted stress |

and returns the calculated stress, allowable stress, and whether the stress constraint passes.

The purpose of the C++ implementation is to provide an independent calculation against which the Python/PyTorch result can be checked.

---

## Knowledge Base

The local engineering knowledge is stored under:

`knowledge/documents/`

| Document | Purpose |
|---|---|
| `beam_bending.txt` | Contains the beam bending equations and the allowable-stress rule used by the prototype. |
| `materials.txt` | Contains simplified illustrative allowable stress values for steel and aluminum. |
| `validation.txt` | Contains the validation rules used by the prototype. |

### `beam_bending.txt`

Contains the beam bending equations and the allowable-stress rule used by the prototype.

### `materials.txt`

Contains simplified illustrative allowable stress values for steel and aluminum.

These values are explicitly intended for software evaluation and are not real structural design guidance.

### `validation.txt`

Contains the validation rules used by the prototype, including:

- Positive engineering inputs
- Positive calculated stress
- Allowable-stress constraint
- Python/C++ consistency
- Safety and consistency requirements for a `VALID` result

---

## Evaluation Dataset

The evaluation contains:

`25 engineering cases`

Each case has:

- An input JSON file under `data/inputs/`
- An expected-result JSON file under `data/expected_results/`

The evaluation includes both cases that should pass the engineering constraints and deliberately constructed cases that should fail them.

The three expected-invalid cases in the current dataset are:

| Case | Expected Result |
|---|---|
| `CASE_007` | `INVALID` |
| `CASE_014` | `INVALID` |
| `CASE_021` | `INVALID` |

The remaining 22 cases are expected to be valid.

---

## Evaluation Design

The project evaluates two approaches.

### 1. Nemotron Agentic Workflow

Nemotron receives all 25 engineering cases in a single planning request.

The model produces a tool-selection plan for each case.

The generated plans are then executed locally using the deterministic engineering tools.

The current evaluation makes exactly one Nemotron/OpenRouter API request for the complete batch.

After that request, the remaining execution is local.

### 2. Conventional Workflow

The conventional workflow follows the same engineering tools in a fixed order without using an LLM to select the workflow.

| Step | Conventional Workflow |
|---:|---|
| 1 | Process Engineering Data |
| 2 | Retrieve Technical Knowledge |
| 3 | Engineering Analysis |
| 4 | Constraint Checking |
| 5 | C++ Validation |
| 6 | Safety & Consistency Validation |

The conventional workflow is used as a baseline for comparison with the Agentic workflow.

## Evaluation Metrics

The project reports five metrics:

| Metric | What It Measures |
|---|---|
| Task Completion Rate | Measures whether the workflow produces a result for the evaluation cases. |
| Tool Selection Accuracy | Measures whether the Agentic workflow selected the required tools correctly. |
| Data Analysis Accuracy | Measures whether the engineering analysis agrees with the expected results. |
| Validation Error Detection | Measures whether expected constraint violations are correctly identified. |
| Response Validity | Measures whether the generated results satisfy the required result structure and validation conditions. |

### Task Completion Rate

Measures whether the workflow produces a result for the evaluation cases.

### Tool Selection Accuracy

Measures whether the Agentic workflow selected the required tools correctly.

For the conventional workflow, tool selection is fixed, so the comparison assigns this metric as `1.0`.

### Data Analysis Accuracy

Measures whether the engineering analysis agrees with the expected results.

### Validation Error Detection

Measures whether expected constraint violations are correctly identified.

### Response Validity

Measures whether the generated results satisfy the required result structure and validation conditions.

---

## Latest Evaluation Results

The current saved evaluation contains 25 cases.

### Nemotron Agentic Workflow

| Metric | Result |
|---|---:|
| Task Completion Rate | **1.0000** |
| Tool Selection Accuracy | **1.0000** |
| Data Analysis Accuracy | **1.0000** |
| Validation Error Detection | **1.0000** |
| Response Validity | **1.0000** |

| Status | Cases |
|---|---:|
| **VALID** | **22** |
| **INVALID** | **3** |
| **Total** | **25** |

### Conventional Workflow

| Metric | Result |
|---|---:|
| Task Completion Rate | **1.0000** |
| Tool Selection Accuracy | **1.0000** |
| Data Analysis Accuracy | **1.0000** |
| Validation Error Detection | **1.0000** |
| Response Validity | **1.0000** |

| Status | Cases |
|---|---:|
| **VALID** | **22** |
| **INVALID** | **3** |
| **Total** | **25** |

### Agentic vs Conventional

The latest comparison shows identical results for the two workflows on this 25-case evaluation dataset:

| Metric | Nemotron Agentic | Conventional |
|---|---:|---:|
| Task Completion Rate | **1.0000** | **1.0000** |
| Tool Selection Accuracy | **1.0000** | **1.0000** |
| Data Analysis Accuracy | **1.0000** | **1.0000** |
| Validation Error Detection | **1.0000** | **1.0000** |
| Response Validity | **1.0000** | **1.0000** |
| VALID | **22** | **22** |
| INVALID | **3** | **3** |

This result shows that, for the current 25-case dataset, the Nemotron-planned workflow successfully reaches the same final engineering classifications and evaluation scores as the fixed conventional workflow.

The purpose of the experiment is not to claim that the Agentic workflow is universally better. Instead, it demonstrates that an LLM-based planning layer can be placed in front of deterministic engineering tools while preserving the same validation behavior on the evaluated cases.

### Result Interpretation

| Observation | Meaning |
|---|---|
| **25 / 25 cases completed** | Both workflows produced results for every evaluation case. |
| **22 VALID / 3 INVALID** | Both workflows produced the expected validation split. |
| **1.0000 across all metrics** | Both workflows achieved full scores on the current evaluation dataset. |
| **1 Nemotron API request** | The complete Agentic batch was planned in a single LLM request. |
| **Same Agentic and Conventional results** | The LLM planning layer did not change the final validation outcome on these cases. |

---

## Evaluation Output Files

The Nemotron evaluation writes its results to:

`evaluation/results/nemotron/`

| Output | Purpose |
|---|---|
| `nemotron_batch_output.json` | Contains the batch response returned by Nemotron, including the generated plans and model response information. |
| `nemotron_plans.json` | Contains the validated tool-selection plans generated for the 25 cases. |
| `nemotron_results.json` | Contains the locally executed results for all 25 cases. |
| `nemotron_metrics.json` | Contains the five final Nemotron evaluation metrics. |
| `nemotron_metric_evaluation.png` | Visualizes the Nemotron evaluation metrics. |
| `nemotron_validation_status.png` | Visualizes the validation status distribution. |

### `nemotron_batch_output.json`

Contains the batch response returned by Nemotron, including the generated plans and model response information.

### `nemotron_plans.json`

Contains the validated tool-selection plans generated for the 25 cases.

### `nemotron_results.json`

Contains the locally executed results for all 25 cases.

Each result includes information such as:

- Case ID
- Material
- Engineering analysis
- Constraint result
- C++ validation
- Safety and consistency checks
- Final `VALID` or `INVALID` status
- Model-generated plan
- Plan validation information

### `nemotron_metrics.json`

Contains the five final Nemotron evaluation metrics.

The current file reports:

| Metric | Value |
|---|---:|
| Task Completion Rate | **1.0000** |
| Tool Selection Accuracy | **1.0000** |
| Data Analysis Accuracy | **1.0000** |
| Validation Error Detection | **1.0000** |
| Response Validity | **1.0000** |

### Nemotron Evaluation Graphs

The evaluation also generates:

- `nemotron_metric_evaluation.png`
- `nemotron_validation_status.png`

These visualize the Nemotron evaluation metrics and validation status distribution.

---

## Comparison Output Files

The Agentic vs Conventional comparison is stored under:

`evaluation/results/comparison/`

| Output | Purpose |
|---|---|
| `agentic_vs_conventional.json` | Contains the final comparison metrics and validation-status counts for both workflows. |
| `conventional_results.json` | Contains the locally generated results for the conventional workflow. |
| `conventional_metrics.json` | Contains the conventional workflow metrics. |
| `agentic_vs_conventional_metrics.png` | Contains the comparison plot between the Agentic and conventional workflows. |

### `agentic_vs_conventional.json`

Contains the final comparison metrics and validation-status counts for both workflows.

### `conventional_results.json`

Contains the locally generated results for the conventional workflow.

### `conventional_metrics.json`

Contains the conventional workflow metrics.

### `agentic_vs_conventional_metrics.png`

Contains the comparison plot between the Agentic and conventional workflows.

---

## Reproducibility and API Usage

The evaluation separates the LLM step from the local engineering execution.

The process is:

| Stage | Execution |
|---:|---|
| 1 | 25 Engineering Cases |
| 2 | One Nemotron API Request |
| 3 | 25 Tool-Selection Plans |
| 4 | Local Plan Validation |
| 5 | Local Engineering Execution |
| 6 | Data Processing |
| 7 | Knowledge Retrieval |
| 8 | PyTorch Analysis |
| 9 | Constraint Checking |
| 10 | C++ Validation |
| 11 | Safety & Consistency Checks |
| 12 | Evaluation Metrics |

This design prevents additional LLM requests during the local execution of the generated plans.

The current Nemotron batch evaluation uses:

`1 API request`

The comparison command does not make an LLM/API request. It loads the existing Nemotron results and runs the conventional workflow locally.

## Project Structure

```
intelligent-engineering-validation-agent/
│
├── agents/
│   ├── __init__.py
│   ├── graph.py
│   ├── llm_provider.py
│   └── planner.py
│
├── cpp/
│   ├── CMakeLists.txt
│   ├── validator.cpp
│   ├── validator.hpp
│   └── build/
│       └── validator.exe
│
├── data/
│   ├── inputs/
│   │   ├── case_001.json
│   │   ├── ...
│   │   └── case_025.json
│   │
│   └── expected_results/
│       ├── case_001.json
│       ├── ...
│       └── case_025.json
│
├── evaluation/
│   ├── __init__.py
│   ├── batch_agentic.py
│   ├── compare_existing.py
│   ├── conventional.py
│   ├── metrics.py
│   ├── openrouter_batch.py
│   ├── plots.py
│   ├── run_nemotron_evaluation.py
│   ├── test_cases.py
│   │
│   └── results/
│       ├── nemotron/
│       └── comparison/
│
├── knowledge/
│   └── documents/
│       ├── beam_bending.txt
│       ├── materials.txt
│       └── validation.txt
│
├── src/
│   └── intelligent_engineering_validation_agent/
│       └── __init__.py
│
├── tests/
│   ├── __init__.py
│   └── test_core.py
│
├── tools/
│   ├── __init__.py
│   ├── constraint_checker.py
│   ├── cpp_validation.py
│   ├── data_processor.py
│   ├── engineering_analysis.py
│   ├── knowledge_retrieval.py
│   └── safety_consistency.py
│
├── .env
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
└── uv.lock
```

The `cpp/build/` and `evaluation/results/` directories are generated locally and are ignored by Git.

Python cache files and the local virtual environment are also ignored.

---

## Requirements

The project requires:

| Requirement | Purpose |
|---|---|
| Python 3.11 or newer | Python runtime |
| `uv` | Environment and dependency management |
| CMake | C++ build configuration |
| A working C++17 compiler | Build the C++ validator |
| MSYS2/UCRT64 on Windows | Current Windows C++ build setup |
| An OpenRouter API key | Nemotron evaluation |

Python dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

The project uses `uv` for environment and dependency management.

---

## Setup

### 1. Install Dependencies

From the repository root:

```powershell
uv sync
```

For a clean installation using the existing lock file:

```powershell
uv sync --locked
```

The virtual environment is created as:

`.venv/`

There is no need to manually install the dependencies using `pip` when using the project's `uv` setup.

### 2. Configure the Nemotron API Key

Create a `.env` file in the project root.

Set:

```dotenv
OPENROUTER_NEMOTRON_API_KEY=your_openrouter_api_key
NEMOTRON_MODEL=nvidia/nemotron-3.5-lightning:free
```

Do not commit the `.env` file or an actual API key.

### 3. Build the C++ Validator

The C++ validator must be built before running workflows that use C++ validation.

On Windows with the current MSYS2/UCRT64 setup, make sure the MSYS2 UCRT64 binary directory is available in the current terminal:

```powershell
$env:PATH = "C:\msys64\ucrt64\bin;$env:PATH"
```

Then configure the CMake build:

```powershell
cmake -S cpp -B cpp/build -G "MinGW Makefiles" -DCMAKE_CXX_COMPILER="C:\msys64\ucrt64\bin\g++.exe" -DCMAKE_MAKE_PROGRAM="C:\msys64\ucrt64\bin\mingw32-make.exe"
```

Build the validator:

```powershell
cmake --build cpp/build
```

The executable should be created at:

`cpp/build/validator.exe`

The Python C++ validation tool also adds `C:\msys64\ucrt64\bin` to the subprocess environment when it runs the validator.

---

## Running the Tests

Run the automated test suite with:

```powershell
uv run pytest
```

The current test suite contains three core tests covering:

- Engineering input processing
- PyTorch bending-stress calculation
- Constraint-failure detection

The current project state passes:

**3 passed**

---

## Running the Main Application

The main application can be started with:

```powershell
uv run python main.py
```

or with a specific engineering case:

```powershell
uv run python main.py data/inputs/case_001.json
```

The application creates an LLM plan and then passes the case and plan to the LangGraph execution workflow.

The current `main.py` entry point expects the environment variable:

`OPENAI_API_KEY`

for the direct application path.

The dedicated Nemotron evaluation path uses:

`OPENROUTER_NEMOTRON_API_KEY`

and the Nemotron model configured in `NEMOTRON_MODEL`.

---

## Running the Nemotron Evaluation

The dedicated evaluation command is:

```powershell
uv run python -m evaluation.run_nemotron_evaluation
```

The evaluation:

| Step | Operation |
|---:|---|
| 1 | Loads the 25 engineering cases. |
| 2 | Validates the expected-result data. |
| 3 | Sends one batch request to Nemotron through OpenRouter. |
| 4 | Receives the 25 tool-selection plans. |
| 5 | Validates the plans locally. |
| 6 | Executes the plans locally. |
| 7 | Runs the Python/PyTorch engineering analysis. |
| 8 | Runs the constraint checks. |
| 9 | Runs the independent C++ validator. |
| 10 | Performs safety and consistency validation. |
| 11 | Calculates the evaluation metrics. |
| 12 | Saves the generated evaluation outputs. |

The current implementation intentionally does not retry the OpenRouter request.

---

## Comparing Agentic and Conventional Workflows

After Nemotron results have been generated, the existing Nemotron results can be compared with the conventional workflow using:

```powershell
uv run python -m evaluation.compare_existing
```

This command:

- Loads the existing Nemotron results.
- Runs the conventional workflow locally.
- Calculates conventional metrics.
- Creates the Agentic vs Conventional comparison JSON.
- Generates the comparison plot.

It does not make another Nemotron/OpenRouter API request.

The comparison is written to:

`evaluation/results/comparison/`

---

## Git and Generated Files

The following local files and directories are intentionally ignored:

```gitignore
.env
.venv/
__pycache__/
*.pyc
cpp/build/
evaluation/results/
```

This keeps secrets, the local Python environment, compiled C++ artifacts, and generated evaluation outputs out of Git.

The source code, test cases, expected results, knowledge documents, configuration files, and evaluation scripts remain part of the project.

---

## Current Project Status

The current project state has successfully demonstrated:

- Agentic task planning with Nemotron
- LangGraph-based workflow orchestration
- LangChain tool integration
- Structured engineering-data processing
- Local technical knowledge retrieval
- PyTorch engineering analysis
- Engineering constraint checking
- Independent C++ validation
- Python/C++ consistency checking
- Deterministic safety validation
- Agentic vs conventional evaluation
- 25-case evaluation
- One-request Nemotron batch evaluation
- Automated testing

### Current Validation Status

| Workflow | VALID | INVALID | Total |
|---|---:|---:|---:|
| **Nemotron Agentic** | **22** | **3** | **25** |
| **Conventional** | **22** | **3** | **25** |

### Current Evaluation Metrics

| Metric | Nemotron Agentic | Conventional |
|---|---:|---:|
| Task Completion Rate | **1.0000** | **1.0000** |
| Tool Selection Accuracy | **1.0000** | **1.0000** |
| Data Analysis Accuracy | **1.0000** | **1.0000** |
| Validation Error Detection | **1.0000** | **1.0000** |
| Response Validity | **1.0000** | **1.0000** |

The three invalid cases are:

| Invalid Case |
|---|
| `CASE_007` |
| `CASE_014` |
| `CASE_021` |

These cases represent the expected constraint-violation cases in the current evaluation dataset.

Overall, the prototype demonstrates a clear separation between LLM-based planning and deterministic engineering validation: Nemotron decides how the task should be approached, while the local Python and C++ components perform and verify the engineering computation.
