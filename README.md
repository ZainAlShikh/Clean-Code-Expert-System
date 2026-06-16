# Clean Code Expert System

## Overview
This project is an intelligent, rule-based expert system designed to automate the analysis of JavaScript source code. It evaluates the codebase against established Clean Code and Refactoring principles (based on the work of Robert C. Martin and Martin Fowler) to detect design flaws, code smells, and structural inefficiencies.

## Key Capabilities
- **Abstract Syntax Tree (AST) Parsing:** Converts raw JavaScript code into a structured AST using `pyjsparser`.
- **Project-Wide Analysis:** Evaluates multiple interrelated files concurrently, enabling the detection of cross-file issues such as dead code and data clumps.
- **Inference Engine:** Utilizes the `experta` library to execute forward-chaining rules against the extracted code facts.
- **Execution Modes:** Supports both a graphical user interface (Web UI) and a Command-Line Interface (CLI) for automated integration.

## Supported Rules
The knowledge base currently implements the following analysis rules:
1. **Cyclomatic Complexity:** Identifies functions with excessive branching and control flow complexity (Threshold > 10).
2. **Control Flow Nesting:** Detects the Arrow Anti-Pattern where conditional or loop statements are nested excessively (Threshold > 3).
3. **Dead Code Elimination:** Identifies functions that are declared but never invoked across the entire analyzed project.
4. **Data Clumps:** Detects functions in different files that share identical, lengthy parameter lists, indicating a missing domain concept.
5. **Magic Numbers:** Flags unexplained numeric literals hardcoded into the source code.
6. **Method Length:** Detects functions exceeding optimal length constraints (Threshold > 20 lines).
7. **Parameter Count:** Flags functions with an excessive number of parameters (Threshold > 3).
8. **Variable Naming:** Identifies uninformative or overly abbreviated variable names.

## Installation

1. Clone the repository.
2. Create and activate a Python Virtual Environment.
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage Instructions

### Web Interface
To launch the graphical user interface:

```powershell
# 1. Bypass Execution Policy if restricted (Windows only)
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 2. Activate the virtual environment
.\.venv\Scripts\activate

# 3. Start the application server
python app.py
```
Navigate to `http://127.0.0.1:5000` in your web browser. Input the absolute path to your JavaScript project directory to initiate the analysis.

### Command-Line Interface (CLI)
To run the analysis directly from the terminal without the web interface:

```powershell
.\.venv\Scripts\python.exe main.py "C:\absolute\path\to\javascript\project"
```

## System Architecture
- `analyzer/`: Responsible for parsing the JavaScript code into an AST and extracting formal logical facts (`FactExtractor`).
- `core/`: Contains the `experta` KnowledgeEngine, fact definitions, and the rule configurations.
- `models/`: Defines data structures for the refactoring recommendations.
- `utils/`: Handles the formatting and generation of the final analysis reports.
- `app.py` / `main.py`: The entry points for the Web and CLI applications respectively.
