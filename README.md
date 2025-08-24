# Simple Tool-Using Agent

A modular tool-using agent with decorator-based tool creation and extensible architecture.

## Architecture

```ascii
+---------------------+      +---------------------+      +---------------------+
|      Orchestrator   |----->|    Tool Executor    |----->|     Tool Registry   |
+---------------------+      +---------------------+      +---------------------+
          |                            |                            |
          |                            |      +---------------------+
          v                            |      |       Tools         |
+---------------------+                |      | (Calculator, Weather, |
|      LLM Client     |<---------------+      |  Translator, etc.)  |
| (Fake, etc.)        |                       +---------------------+
+---------------------+
```

- **Orchestrator:** Coordinates workflow, interacts with LLM, executes plans
- **Tool Executor:** Executes tool calls with validation
- **Tool Registry:** Central repository for all tools
- **Tools:** Self-contained classes using `@tool` decorator
- **LLM Clients:** Adapters for different LLMs

## Features

- **Decorator-based Tool Creation:** `@tool` decorator creates schema-validated tools
- **Policy-Driven Execution:** Retry and execution policies for resilience
- **Input/Output Guardrails:** The system validates inputs and outputs at multiple layers, from tool arguments to LLM responses, ensuring robustness.
- **Extensibility:** Adding a new tool is as simple as creating a new function with the `@tool` decorator and registering it.

## Quick Start

### Prerequisites

- Python 3.10+

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd se1-agent-debug-assignment
    ```

2.  **Create and activate a virtual environment:**

    For Windows (PowerShell):

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    ```

    For macOS/Linux:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Agent

You can run the agent from the command line with a query:

```bash
# Basic calculations
python main.py "What is 12.5% of 243?"

# Weather information
python main.py "Summarize today's weather in Paris in 3 words"

# Knowledge-based questions
python main.py "Who is Ada Lovelace?"

# Multi-step tool use
python main.py "Add 10 to the average temperature in Paris and London right now."

# New tools: Translation
python main.py "Translate 'hello world' to Spanish"

# New tools: Unit Conversion
python main.py "Convert 100 degrees Celsius to Fahrenheit"
```

### Running Tests

The project includes a comprehensive test suite. To run the tests:

```bash
pytest -q
```

This will execute all unit and integration tests, ensuring that all components are working correctly.
