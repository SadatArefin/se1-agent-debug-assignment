# Refactored & Extended: Simple Tool-Using Agent

This project is a refactored and extended version of a simple tool-using agent. The original brittle code has been transformed into a robust, production-quality system that is typed, tested, and easily extensible. This was completed as an assignment for Optimizely.

## Architecture Overview

The agent's architecture is designed to be modular and scalable, separating core logic from specific implementations.

```ascii
+---------------------+      +---------------------+      +---------------------+
|      Orchestrator   |----->|    Tool Executor    |----->|     Tool Registry   |
+---------------------+      +---------------------+      +---------------------+
          |                            |                            |
          |                            |      +---------------------+
          v                            |      |       Tools         |
+---------------------+                |      | (Calculator, Weather, |
|      LLM Client     |<---------------+      |  Translator, etc.)  |
| (OpenAI, Fake, etc.)|                       +---------------------+
+---------------------+
```

- **Orchestrator (`agent/core/orchestrator.py`):** The central component that coordinates the agent's workflow. It takes user input, interacts with the LLM to create a plan, and uses the `ToolExecutor` to execute the plan.
- **Tool Executor (`agent/core/tool_executor.py`):** Responsible for executing tool calls from the plan. It validates tool names and arguments.
- **Tool Registry (`agent/registry.py`):** A central repository for all available tools. Tools are registered at startup, making it easy to add new ones.
- **Tools (`agent/adapters/tools/`):** Individual tools that the agent can use. Each tool is a self-contained class created from a function using the `@tool` decorator, which simplifies creation and validation.
- **LLM Clients (`agent/adapters/llm/`):** Adapters for different Large Language Models. The system can switch between a `FakeClient` for testing and a real `OpenAIClient`.

## Key Features & Patterns

- **Decorator-based Tool Creation:** The `@tool` decorator in `agent/core/decorators.py` turns simple Python functions into full-fledged, schema-validated tools.
- **Policy-Driven Execution:** Policies for `retries` and `execution` control how tools are run, making the system more resilient.
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
