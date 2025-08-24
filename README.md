# Simple Tool-Using Agent

A modular tool-using agent with decorator-based tool creation and extensible architecture.

## Architecture

```ascii
+---------------------+      +---------------------+      +---------------------+
|      Orchestrator   |----->|     Tool Registry   |----->|       Tools         |
| - Request handling  |      | - Auto-discovery    |      | - Class-based       |
| - LLM interaction   |      | - Validation        |      | - Decorator-based   |
| - Tool execution    |      | - Schema generation |      | - Legacy support    |
+---------------------+      +---------------------+      +---------------------+
          |                            |                            |
          |                            |      +---------------------+
          v                            |      |     Guardrails      |
+---------------------+                |      | - Input validation  |
|     LLM Client      |                |      | - Output validation |
| - Fake client       |                |      | - JSON repair       |
| - Extensible        |                       +---------------------+
+---------------------+                                     |
          |                                                 |
          v                                                 v
+---------------------+                       +---------------------+
|     Schemas         |                       |     Decorators      |
| - ToolCall          |                       | - @tool decorator   |
| - ToolResult        |                       | - Auto-registration |
| - Answer            |                       | - Schema generation |
+---------------------+                       +---------------------+
```

### Core Components

- **Orchestrator:** Coordinates the entire workflow - handles user requests, interacts with LLM, and executes tools directly with integrated validation
- **Tool Registry:** Enhanced registry with auto-discovery capabilities, tool validation, and schema generation
- **Tools:** Support for both class-based (legacy) and decorator-based (new) tool implementations
- **Guardrails:** Multi-layer validation system for inputs, outputs, and JSON repair functionality
- **Schemas:** Pydantic v2 models for type-safe data structures (ToolCall, ToolResult, Answer)
- **Decorators:** New `@tool` decorator system for easy tool creation with automatic registration

## Features

- **Dual Tool Creation Methods:**
  - **Class-based tools:** Traditional approach in `src/agent/adapters/tools/` for complex tools
  - **Decorator-based tools:** New `@tool` decorator in `src/agent/tools/` for simple, function-based tools
- **Auto-Discovery & Registration:** Tool registry automatically discovers and registers tools from specified modules
- **Enhanced Validation:** Multi-layer input/output validation with JSON repair capabilities
- **Type Safety:** Pydantic v2 schemas for all data structures (ToolCall, ToolResult, Answer)
- **Resilient Execution:** Comprehensive error handling and policy-driven execution
- **Extensible Architecture:** Adding new tools is as simple as creating a decorated function or implementing a class
- **Legacy Support:** Maintains backward compatibility with existing class-based tools
- **Comprehensive Logging:** Structured logging with performance metrics, debug information, and detailed request/response tracking

## Features

- **Dual Tool Creation Methods:**
  - **Class-based tools:** Traditional approach in `src/agent/adapters/tools/` for complex tools
  - **Decorator-based tools:** New `@tool` decorator in `src/agent/tools/` for simple, function-based tools
- **Auto-Discovery & Registration:** Tool registry automatically discovers and registers tools from specified modules
- **Enhanced Validation:** Multi-layer input/output validation with JSON repair capabilities
- **Type Safety:** Pydantic v2 schemas for all data structures (ToolCall, ToolResult, Answer)
- **Resilient Execution:** Comprehensive error handling and policy-driven execution
- **Extensible Architecture:** Adding new tools is as simple as creating a decorated function or implementing a class
- **Legacy Support:** Maintains backward compatibility with existing class-based tools
- **Production-Ready Logging:** Comprehensive structured logging with performance metrics, latency tracking, and detailed debug information

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

# New tools: Random Quotes
python main.py "Give me a motivational quote"

# View logging information
python main.py --log-summary

# Analyze log files for performance and debugging
python main.py --analyze-logs
```

### Running Tests

The project includes a comprehensive test suite. To run the tests:

```bash
pytest -q
```

This will execute all unit and integration tests, ensuring that all components are working correctly.

## Tool Development

### Creating New Tools

The system supports two approaches for creating tools:

#### 1. Decorator-based Tools (Recommended for simple tools)

Create function-based tools using the `@tool` decorator in `src/agent/tools/`:

```python
from agent.core.decorators import tool

@tool(name="my_tool", description="Description of what the tool does")
def my_tool(param1: str, param2: int = 10) -> str:
    """
    Tool function with proper docstring.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (optional)

    Returns:
        str: Description of return value
    """
    return f"Result: {param1} with {param2}"
```

#### 2. Class-based Tools (For complex tools with state)

Create class-based tools in `src/agent/adapters/tools/`:

```python
from typing import Any, Dict

class MyComplexTool:
    def __init__(self):
        # Initialize any required state
        self.state = {}

    def name(self) -> str:
        return "my_complex_tool"

    def description(self) -> str:
        return "Description of what the tool does"

    def execute(self, **kwargs) -> Any:
        # Tool implementation
        return "result"

    def to_json_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name(),
            "description": self.description(),
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Parameter description"}
                },
                "required": ["param1"]
            }
        }
```

### Auto-Discovery

Tools are automatically discovered and registered when the application starts. The registry searches:

- `src.agent.tools` - For decorator-based tools
- `src.agent.adapters.tools` - For class-based tools

Manual registration is also supported if needed.

## Logging & Monitoring

### Comprehensive Logging System

The agent includes a production-ready logging system that captures detailed information about every request, tool execution, and system operation.

#### Log Files

All logs are stored in the `logs/` directory with the following structure:

- **`agent_YYYYMMDD.log`** - Main application logs with request flow and debug information
- **`performance_YYYYMMDD.log`** - Performance metrics including latency, success rates, and timing data
- **`tools_YYYYMMDD.log`** - Detailed tool execution logs with arguments, results, and timing
- **`errors_YYYYMMDD.log`** - Error logs with full context and stack traces

#### What Gets Logged

**Request Level:**

- Unique request ID for tracking
- Query text and length
- Full request/response cycle timing
- Success/failure status
- Session information

**Tool Execution:**

- Tool name and arguments
- Execution time and results
- Success/failure status
- Error details if applicable

**Performance Metrics:**

- End-to-end latency
- LLM call timing
- Tool execution timing
- Input/output validation timing

**Debug Information:**

- Component-level debug messages
- Registry operations
- Validation results
- Error context and stack traces

#### Log Analysis

Use the built-in log analyzer to get insights:

```bash
# Get comprehensive analysis report
python main.py --analyze-logs

# View current session information
python main.py --log-summary
```

The analyzer provides:

- Performance statistics (latency, success rates)
- Tool usage patterns and performance
- Error analysis and trends
- Recent request history

#### Configuration

Control logging behavior with environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=DEBUG

# Control console output
export ENABLE_CONSOLE_LOGGING=true

# Enable/disable telemetry
export ENABLE_TELEMETRY=true

# Custom log directory
export LOG_DIR=./custom_logs
```

## Available Tools

The system comes with the following built-in tools:

### Calculator (`calc`)

- **Description:** Evaluate mathematical expressions including percentages
- **Examples:**
  - `"What is 12.5% of 243?"`
  - `"Add 10 to 15"`
  - `"What is 2 + 2?"`

### Weather (`weather`)

- **Description:** Get temperature information for cities
- **Examples:**
  - `"What's the weather in Paris?"`
  - `"Temperature in London"`

### Knowledge Base (`kb`)

- **Description:** Look up information from the knowledge base
- **Examples:**
  - `"Who is Ada Lovelace?"`
  - `"Tell me about Einstein"`

### Unit Converter (`unit_converter`)

- **Description:** Convert between different units of measurement (currently supports temperature)
- **Examples:**
  - `"Convert 100 degrees Celsius to Fahrenheit"`
  - `"Convert 32°F to Celsius"`

### Translator (`translator`)

- **Description:** Translate text between different languages (supports basic Spanish, French, German ↔ English)
- **Examples:**
  - `"Translate 'hello world' to Spanish"`
  - `"What does 'hola' mean?"`

### Random Quote (`random_quote`)

- **Description:** Get inspirational quotes from different categories
- **Examples:**
  - `"Give me a motivational quote"`
  - `"Random tech quote"`

## Technical Implementation

### Key Improvements

1. **Modular Architecture:** Clear separation of concerns with dedicated modules for orchestration, tool management, validation, and schemas

2. **Enhanced Tool Registry:**

   - Auto-discovery of tools from multiple module paths
   - Tool validation and schema generation
   - Search functionality
   - Support for both registration patterns

3. **Robust Validation:**

   - Input sanitization and length limits
   - Output validation and formatting
   - JSON repair for malformed LLM responses
   - Tool call validation

4. **Type Safety:**

   - Pydantic v2 models for all data structures
   - Type hints throughout the codebase
   - Runtime validation of tool parameters

5. **Error Resilience:**

   - Comprehensive error handling in tool execution
   - Graceful degradation when tools fail
   - Detailed error reporting and logging

6. **Extensibility:**

   - Plugin-style tool architecture
   - Minimal boilerplate for new tools
   - Backward compatibility with existing tools

7. **Production-Ready Logging:**
   - Structured JSON logging with multiple log levels
   - Separate log files for different concerns (performance, tools, errors)
   - Request tracking with unique IDs
   - Comprehensive performance metrics and latency tracking
   - Built-in log analysis and reporting tools

### Architecture Decisions

- **Integrated Tool Execution:** Rather than a separate Tool Executor component, tool execution is integrated into the Orchestrator for simplicity and reduced complexity
- **Dual Tool Patterns:** Support both class-based tools (for complex stateful tools) and decorator-based tools (for simple functions) to accommodate different use cases
- **Auto-Discovery:** Tools are automatically registered at startup, reducing manual configuration and making the system more maintainable
- **Pydantic Integration:** Use of Pydantic v2 for all data models ensures type safety and automatic validation throughout the system

## Troubleshooting

### Common Issues

1. **Tool not found errors:**

   - Ensure your tool is properly decorated with `@tool` or registered manually
   - Check that the module containing your tool is being imported
   - Verify the tool name matches what you're trying to call

2. **Import errors:**

   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check that you're running from the correct directory
   - Ensure your Python environment is activated

3. **Test failures:**
   - Run tests with verbose output: `pytest -v`
   - Check individual test files: `pytest tests/test_specific_file.py`
   - Ensure test dependencies are installed

### Debug Mode

The system provides comprehensive logging and debugging capabilities:

**Real-time Monitoring:**

- All requests are logged with unique IDs for tracking
- Performance metrics are captured for every operation
- Tool executions are timed and logged with full context

**Log Analysis:**

```bash
# View detailed performance and usage analysis
python main.py --analyze-logs

# Check current logging configuration
python main.py --log-summary

# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py "your query here"
```

**Log Files Location:**

- Default: `./logs/` directory
- Contains separate files for different log types (agent, performance, tools, errors)
- Files are organized by date for easy management

**Debugging Steps:**

1. Run your query normally to generate logs
2. Use `--analyze-logs` to get insights
3. Check error logs for detailed failure information
4. Increase log level to DEBUG for more verbose output
5. Monitor performance logs for latency issues
