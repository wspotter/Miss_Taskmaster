# Multi-Agent System Design for LLM-Driven Development

## 1. Introduction

This document outlines the design for a multi-agent system aimed at enhancing LLM-driven software development. The core challenge addressed is the tendency of Large Language Models (LLMs) to deviate from complex, multi-step plans when exposed to the entire plan at once. By introducing a hierarchical agent structure, we aim to maintain strict adherence to a long-term development roadmap, ensuring compliance and efficient task execution. This system will feature a 'Gatekeeper' agent responsible for strategic planning and task orchestration, and a 'Coding Agent' focused solely on executing individual, well-defined tasks. The design will also consider integration with popular development environments like VSCode and OpenWebUI, and its potential applicability to other long-duration AI assistant tasks.

## 2. System Goal and Core Problem

The primary goal of this multi-agent system is to enable LLMs to execute complex, multi-chapter software development projects or long-duration AI assistant tasks with high fidelity to a predefined plan. The core problem it solves is the 'LLM deviation' phenomenon, where an LLM, when presented with a large, intricate plan, tends to get sidetracked, lose context, or prematurely optimize, leading to incomplete or incorrect task execution. This system mitigates this by:

*   **Encapsulating Complexity:** The detailed, long-term plan is managed by a dedicated agent, shielding the execution-focused agent from overwhelming information.
*   **Enforcing Compliance:** Tasks are dispensed incrementally, and the execution agent is constrained to operate strictly within the bounds of the current task.
*   **Maintaining Context:** The Gatekeeper agent maintains the overarching project context and ensures that each dispensed task aligns with the broader strategic objectives.

## 3. Overall Architecture: A Hierarchical Multi-Agent Approach

The proposed system adopts a hierarchical multi-agent architecture, consisting of at least two primary agents: the **Gatekeeper Agent** and the **Coding Agent**. This structure mirrors human project management, where a project manager (Gatekeeper) breaks down a large project into smaller, manageable tasks for a developer (Coding Agent) and oversees progress.

### 3.1. Agent Roles and Responsibilities

#### 3.1.1. The Gatekeeper Agent (Strategic Planner & Orchestrator)

The Gatekeeper Agent is the brain of the operation, holding the complete, detailed project plan. Its responsibilities include:

*   **Plan Management:** Storing, parsing, and managing the multi-chapter, detailed development plan. This plan will be a structured document (e.g., Markdown, JSON, or a custom format) outlining the project's phases, milestones, and individual tasks.
*   **Task Dispensing:** Providing the Coding Agent with one, and only one, task at a time. This task will be a highly specific, actionable instruction derived from the larger plan.
*   **Progress Monitoring:** Receiving updates from the Coding Agent on task completion status, output, and any encountered issues.
*   **Validation & Review:** Performing high-level validation of the Coding Agent's output against the task requirements and the overall plan.
*   **Context Provisioning:** Providing necessary context (e.g., relevant code snippets, design documents, previous task outcomes) to the Coding Agent for the current task, without revealing the entire project plan.
*   **Error Handling & Re-planning:** If the Coding Agent encounters an unresolvable issue or deviates, the Gatekeeper intervenes, potentially re-planning the current task or adjusting subsequent tasks.
*   **Human Interaction Layer:** Serving as the primary interface for human users, allowing them to review progress, inject new requirements, or modify the plan.

#### 3.1.2. The Coding Agent (Tactical Executor)

The Coding Agent is the workhorse, focused on executing the specific task provided by the Gatekeeper. Its responsibilities are strictly limited to the current task:

*   **Task Execution:** Interpreting the given task and using its tools (e.g., code interpreter, file system access, web browsing, LLM API calls) to complete it.
*   **Output Generation:** Producing the required output for the task (e.g., code, documentation, test results).
*   **Status Reporting:** Communicating task completion, partial progress, or encountered errors back to the Gatekeeper Agent.
*   **Limited Context:** Operating with a deliberately constrained view of the overall project, receiving only the context relevant to its current task from the Gatekeeper.
*   **Compliance:** Adhering strictly to the task instructions and the enforcement mechanisms provided by the system (similar to the `llm-task-enforcer2`'s `LLMGuard`).

### 3.2. Communication and Control Flow

Communication between the agents will be structured and explicit, likely via a message queue or a shared state mechanism that both agents can access and update. The control flow will be primarily driven by the Gatekeeper:

1.  **Initialization:** Human user provides the comprehensive project plan to the Gatekeeper.
2.  **Task Selection:** Gatekeeper parses the plan, identifies the next logical task, and prepares the necessary context.
3.  **Task Dispatch:** Gatekeeper sends the specific task and relevant context to the Coding Agent.
4.  **Execution Loop (Coding Agent):** The Coding Agent attempts to complete the task, utilizing its tools and reporting progress/status.
5.  **Monitoring & Validation (Gatekeeper):** Gatekeeper continuously monitors the Coding Agent's status. Upon task completion (or failure), it validates the output.
6.  **Iteration/Advancement:** Based on validation, the Gatekeeper either dispatches the next task, requests revisions from the Coding Agent, or intervenes for re-planning.
7.  **Project Completion:** Once all tasks in the plan are completed and validated, the Gatekeeper signals project completion to the human user.

This hierarchical approach ensures that the LLM's cognitive load is managed effectively, preventing 


deviation and maintaining focus on the current, immediate objective.

### 3.3. State Management and Persistence

Given the long-running nature of these tasks, robust state management and persistence are crucial. The system's state will encompass:

*   **Gatekeeper State:** The complete project plan, current task index, history of dispensed tasks, their statuses, validation results, and any re-planning decisions. This state must be persistent across sessions.
*   **Coding Agent State:** Primarily ephemeral, representing the current task it's working on, its internal thought process, and any temporary files. The critical outputs are reported back to the Gatekeeper.

**Persistence Mechanism:** A structured data format (e.g., JSON, YAML, or a simple database like SQLite) will be used to store the Gatekeeper's state. This will allow the system to be paused and resumed, and for human inspection or modification of the plan. The `SESSION_STATE.json` concept from the original `llm-task-enforcer2` can be evolved into a more comprehensive project state file managed by the Gatekeeper.

## 4. Detailed Design: The Gatekeeper Agent

The Gatekeeper Agent is the cornerstone of this multi-agent system. Its design requires careful consideration of its internal logic, data structures, and interaction patterns.

### 4.1. Core Components of the Gatekeeper Agent

#### 4.1.1. Plan Parser and Manager

This component is responsible for ingesting the initial, comprehensive project plan and breaking it down into actionable tasks. It will:

*   **Input Formats:** Support various structured input formats for the plan, such as:
    *   **Markdown:** A human-readable format, potentially with custom YAML front matter for metadata and specific task markers (e.g., `## Task: Implement User Authentication`).
    *   **JSON/YAML:** For more programmatic and strict plan definitions, allowing for nested tasks, dependencies, and detailed task parameters.
    *   **Custom DSL (Domain-Specific Language):** A simplified language tailored for defining development tasks, potentially allowing for more expressive and less verbose plans.
*   **Task Extraction:** Automatically identify and extract individual tasks, their descriptions, dependencies, estimated effort, and success criteria from the plan.
*   **Plan Validation:** Validate the integrity and consistency of the plan (e.g., no circular dependencies, all tasks have clear objectives).
*   **Plan State Tracking:** Maintain the current status of each task (e.g., `pending`, `in_progress`, `completed`, `blocked`, `skipped`).

#### 4.1.2. Task Dispatcher

This component selects the next task to be given to the Coding Agent based on the plan's logic and current progress. It will:

*   **Dependency Resolution:** Ensure that prerequisite tasks are completed before a dependent task is dispatched.
*   **Priority Queue:** Potentially prioritize tasks based on user-defined importance, estimated effort, or critical path analysis.
*   **Context Generation:** Assemble all necessary context for the current task, including:
    *   Task description and objectives.
    *   Relevant code snippets or file paths.
    *   Previous task outputs that are inputs to the current task.
    *   Specific instructions or constraints for the Coding Agent.

#### 4.1.3. Progress Monitor and Validator

This component receives updates from the Coding Agent and assesses the quality and completeness of its work. It will:

*   **Output Ingestion:** Receive structured output from the Coding Agent (e.g., new code, test results, documentation).
*   **Task-Specific Validation:** Perform automated checks based on the task's defined success criteria (e.g., running unit tests, checking file existence, linting code).
*   **LLM-based Validation:** Utilize its own LLM capabilities to perform semantic validation of the Coding Agent's output (e.g., 


assessing if the generated code truly implements the requested feature, or if the documentation is comprehensive and accurate).
*   **Human Review Flagging:** For high-risk tasks or when automated validation fails, flag the task for human review.
*   **Audit Trail:** Maintain a detailed log of all tasks, their outcomes, validation results, and any human interventions.

#### 4.1.4. Human Interaction Layer (HIL)

This component provides the interface for human users to interact with the Gatekeeper Agent. It will support:

*   **Dashboard/Reporting:** A clear overview of project progress, active tasks, completed tasks, and any blocked or pending tasks.
*   **Plan Modification:** Allowing human users to modify the overall project plan, add new tasks, re-prioritize, or mark tasks as complete/skipped.
*   **Intervention & Override:** Providing mechanisms for humans to intervene when the system gets stuck, override automated decisions, or provide direct feedback to the agents.
*   **Contextual Information:** Displaying relevant context for human review, such as the task description, Coding Agent's output, and automated validation results.

### 4.2. Data Structures for the Gatekeeper Agent

The Gatekeeper Agent will manage several key data structures to maintain the project state and plan progression.

#### 4.2.1. Project Plan Data Structure

This will be the central repository for the entire project roadmap. It could be represented as a nested dictionary or a list of task objects.

```python
{
    "project_name": "LLM-Driven Development System",
    "version": "1.0.0",
    "description": "A multi-agent system for robust LLM-driven coding.",
    "current_phase": "Design",
    "tasks": [
        {
            "task_id": "P1.1",
            "title": "Understand and formalize the multi-agent system architecture",
            "description": "Outline the roles, responsibilities, and communication flow.",
            "status": "completed",
            "assigned_to": "Gatekeeper",
            "dependencies": [],
            "risk_level": "low",
            "output_expected": "Architectural overview document",
            "validation_criteria": "Review by human",
            "start_time": "2025-09-09T10:00:00Z",
            "end_time": "2025-09-09T12:00:00Z",
            "subtasks": []
        },
        {
            "task_id": "P1.2",
            "title": "Design the 'Gatekeeper' agent's functionalities and data structures",
            "description": "Detail the internal components and data models for the Gatekeeper.",
            "status": "in_progress",
            "assigned_to": "Gatekeeper",
            "dependencies": ["P1.1"],
            "risk_level": "medium",
            "output_expected": "Gatekeeper design document section",
            "validation_criteria": "Internal consistency check, human review",
            "start_time": "2025-09-09T12:00:00Z",
            "end_time": null,
            "subtasks": [
                {
                    "task_id": "P1.2.1",
                    "title": "Define Plan Parser and Manager",
                    "description": "Specify input formats and parsing logic.",
                    "status": "completed",
                    "assigned_to": "Coding Agent",
                    "dependencies": [],
                    "output_expected": "Design section for Plan Parser",
                    "validation_criteria": "Textual analysis",
                    "agent_instructions": "Write a detailed section on the Plan Parser and Manager, including supported input formats and functionalities."
                },
                {
                    "task_id": "P1.2.2",
                    "title": "Define Task Dispatcher",
                    "description": "Specify task selection, dependency resolution, and context generation.",
                    "status": "pending",
                    "assigned_to": "Coding Agent",
                    "dependencies": ["P1.2.1"],
                    "output_expected": "Design section for Task Dispatcher",
                    "validation_criteria": "Textual analysis",
                    "agent_instructions": "Write a detailed section on the Task Dispatcher, covering task selection, dependency resolution, and context generation."
                }
            ]
        }
        // ... more tasks and subtasks
    ]
}
```

**Key Fields for Each Task:**
*   `task_id`: Unique identifier (e.g., `P1.2.1`).
*   `title`: Brief, human-readable title.
*   `description`: Detailed explanation of the task.
*   `status`: Current state (`pending`, `in_progress`, `completed`, `blocked`, `skipped`).
*   `assigned_to`: Which agent is responsible (`Gatekeeper`, `Coding Agent`, `Human`).
*   `dependencies`: List of `task_id`s that must be completed before this task can start.
*   `risk_level`: (e.g., `low`, `medium`, `high`) Influences validation rigor.
*   `output_expected`: What the task is expected to produce.
*   `validation_criteria`: How the output will be validated (e.g., `unit_tests`, `human_review`, `textual_analysis`).
*   `start_time`, `end_time`: Timestamps for tracking progress.
*   `subtasks`: Nested list of subtasks, allowing for hierarchical planning.
*   `agent_instructions`: (Crucial for Coding Agent tasks) Specific, concise instructions for the Coding Agent, tailored to its limited context.

#### 4.2.2. Task Queue

A dynamic queue of tasks ready to be dispatched to the Coding Agent, ordered by priority and dependencies.

#### 4.2.3. Validation History Log

An immutable log of all validation attempts, their results, and associated outputs. This serves as an audit trail and can be used for analytics.

```python
[
    {
        "timestamp": "2025-09-09T12:30:00Z",
        "task_id": "P1.2.1",
        "agent_output_summary": "Generated design section for Plan Parser.",
        "validation_result": "approved",
        "validation_details": {"automated_checks": "passed", "llm_review": "positive"},
        "human_intervention": false
    },
    {
        "timestamp": "2025-09-09T13:15:00Z",
        "task_id": "P1.2.2",
        "agent_output_summary": "Attempted design section for Task Dispatcher, but missing dependency context.",
        "validation_result": "blocked",
        "validation_details": {"reason": "Missing prerequisite information from P1.2.1"},
        "human_intervention": false
    }
]
```

### 4.3. Gatekeeper Agent Workflow

1.  **Load Project State:** On startup, load the `Project Plan Data Structure` and `Validation History Log` from persistent storage.
2.  **Identify Next Task:** Iterate through the `tasks` list, identifying the next `pending` task whose `dependencies` are all `completed`.
3.  **Prepare Task for Coding Agent:** Extract the `task_id`, `title`, `description`, and crucially, the `agent_instructions` for the selected task. Gather any necessary context (e.g., relevant code files, previous outputs) based on the task description.
4.  **Dispatch Task:** Send the prepared task and context to the Coding Agent via a defined communication channel.
5.  **Monitor Coding Agent:** Wait for the Coding Agent to report its status (e.g., `in_progress`, `completed`, `failed`).
6.  **Receive Output & Validate:** Once the Coding Agent reports `completed`, receive its output. Perform automated validation based on `validation_criteria`.
    *   If `approved`: Update task status to `completed` in the `Project Plan Data Structure`, log the validation, and proceed to identify the next task.
    *   If `rejected` (e.g., automated checks fail): Update task status to `blocked`, log the validation, and potentially trigger a re-planning sub-task for the Gatekeeper itself, or flag for human intervention.
    *   If `pending_human_review`: Update task status to `pending_human_review`, log the validation, and notify the human user via the HIL.
7.  **Handle Coding Agent Failure:** If the Coding Agent reports `failed` or times out, update the task status to `blocked`, log the failure, and trigger a re-planning sub-task or human intervention.
8.  **Persist State:** Regularly save the updated `Project Plan Data Structure` and `Validation History Log` to persistent storage.

This detailed workflow ensures that the Gatekeeper maintains tight control over the project's progression, reacting intelligently to the Coding Agent's performance and ensuring adherence to the overall plan. The next section will detail the Coding Agent.




## 5. Detailed Design: The Coding Agent

The Coding Agent is the tactical executor in this multi-agent system. Its design prioritizes focus, compliance, and efficient task completion. It operates with a deliberately limited scope, receiving one task at a time from the Gatekeeper and using its tools to accomplish it.

### 5.1. Core Components of the Coding Agent

#### 5.1.1. Task Interpreter

This component receives the task instructions from the Gatekeeper and breaks them down into a sequence of actions. It will:

*   **Parse Task Instructions:** Interpret the `agent_instructions` provided by the Gatekeeper, which will be a concise, natural language description of the task.
*   **Action Planning:** Generate a step-by-step plan to accomplish the task. This plan is internal to the Coding Agent and is not the same as the Gatekeeper's high-level project plan.
*   **Tool Selection:** Based on its internal plan, select the appropriate tools for each step (e.g., file system operations, code execution, web browsing).

#### 5.1.2. Toolset

The Coding Agent will be equipped with a comprehensive set of tools to perform its tasks. These tools will be similar to those available in a standard development environment, but with an enforcement layer provided by a system like `llm-task-enforcer2`.

*   **File System Tools:** Read, write, create, and delete files and directories.
*   **Code Execution Tools:** Execute code in various languages (e.g., Python, JavaScript), run shell commands, and install dependencies.
*   **Web Browsing Tools:** Access web pages, extract information, and interact with web elements.
*   **LLM API Tools:** Make calls to other LLMs for specific sub-tasks, such as generating code snippets, writing documentation, or translating text.

#### 5.1.3. Enforcement Layer (LLMGuard)

This is a critical component that ensures the Coding Agent stays on task. It will be a refined and integrated version of the `llm-task-enforcer2` concept, providing:

*   **Task-Scoped Operations:** All tool usage will be automatically validated against the current task's scope. Any action that deviates from the task will be blocked.
*   **Justification Requirement:** For certain actions (e.g., file modifications, API calls), the Coding Agent will be required to provide a justification, which is then validated by the enforcement layer.
*   **Resource Constraints:** The enforcement layer can impose resource constraints on the Coding Agent, such as limiting the number of API calls, execution time, or file system access.

#### 5.1.4. Status Reporter

This component communicates the Coding Agent's progress and status back to the Gatekeeper. It will report:

*   **Task Acceptance:** Confirmation that the task has been received and understood.
*   **Progress Updates:** Periodic updates on the internal plan's progress (e.g., "Step 2 of 5 completed").
*   **Task Completion:** A signal that the task is complete, along with the generated output.
*   **Errors and Blockers:** Detailed reports on any errors encountered or if the task is blocked for any reason.

### 5.2. Interaction Protocol with the Gatekeeper

The communication between the Coding Agent and the Gatekeeper will follow a strict protocol:

1.  **Receive Task:** The Coding Agent listens for a new task from the Gatekeeper. The task will be a structured message containing the `task_id`, `agent_instructions`, and any necessary context.
2.  **Acknowledge Task:** The Coding Agent sends an acknowledgment message to the Gatekeeper, confirming receipt of the task.
3.  **Execute Task:** The Coding Agent executes the task, using its tools within the constraints of the enforcement layer.
4.  **Report Progress (Optional):** For long-running tasks, the Coding Agent can send periodic progress updates to the Gatekeeper.
5.  **Report Completion:** Upon successful completion, the Coding Agent sends a `completed` message to the Gatekeeper, along with the task's output (e.g., code, file paths, or a summary of changes).
6.  **Report Failure:** If the task cannot be completed, the Coding Agent sends a `failed` message to the Gatekeeper, including a detailed error report.

### 5.3. Coding Agent Workflow

1.  **Idle State:** The Coding Agent is in an idle state, waiting for a task from the Gatekeeper.
2.  **Task Reception:** Receives a task and context from the Gatekeeper.
3.  **Internal Planning:** The Task Interpreter creates a step-by-step plan to accomplish the task.
4.  **Execution Loop:** The Coding Agent iterates through its internal plan:
    *   Selects the appropriate tool for the current step.
    *   Provides justification if required by the enforcement layer.
    *   Executes the tool.
    *   If the tool execution is successful, proceeds to the next step.
    *   If the tool execution is blocked by the enforcement layer or fails, the Coding Agent attempts to recover (e.g., by re-planning or trying a different approach). If recovery is not possible, it reports a failure to the Gatekeeper.
5.  **Output Generation:** Once all steps in the internal plan are complete, the Coding Agent assembles the final output for the task.
6.  **Reporting:** Sends the final output and a `completed` status to the Gatekeeper.
7.  **Return to Idle:** The Coding Agent returns to its idle state, ready for the next task.

This focused workflow, combined with the enforcement layer, ensures that the Coding Agent remains a reliable and compliant executor of the Gatekeeper's plan.





## 6. Integration with Development Environments

To maximize the utility of this multi-agent system, it should be seamlessly integrated into popular development environments like VSCode and web-based interfaces like OpenWebUI. This will allow developers to leverage the system within their existing workflows.

### 6.1. VSCode Integration

Integration with VSCode can be achieved by developing a dedicated extension. This extension will serve as the Human Interaction Layer (HIL) for the Gatekeeper Agent.

**Features of the VSCode Extension:**
*   **Project Plan View:** A custom view that displays the entire project plan (from the Gatekeeper) in a tree-like structure, showing the status of each task.
*   **Task Management:** Allow developers to interact with the plan directly from VSCode, such as:
    *   Creating new tasks or modifying existing ones.
    *   Re-prioritizing tasks.
    *   Marking tasks as complete or skipped.
    *   Triggering the Gatekeeper to dispatch the next task.
*   **Coding Agent Output Display:** Display the output of the Coding Agent (e.g., new code, diffs) directly in the editor.
*   **Validation Results:** Show the results of the Gatekeeper's validation, including any errors or warnings.
*   **Notifications:** Use VSCode's notification system to alert the developer when a task is completed, blocked, or requires human review.
*   **Chat Interface:** A chat interface for interacting with the Gatekeeper Agent, allowing for more natural language commands and queries.

**Implementation Approach:**
*   The VSCode extension will communicate with the Gatekeeper Agent via a local server or a message queue.
*   The extension will use VSCode's API to create custom views, display notifications, and interact with the editor.
*   The project plan and task status will be synchronized between the Gatekeeper and the extension.

### 6.2. OpenWebUI Integration

OpenWebUI is a popular web-based interface for interacting with LLMs. Integrating the multi-agent system with OpenWebUI would provide a more accessible and platform-agnostic way to use the system.

**Features of the OpenWebUI Integration:**
*   **Custom Chat Interface:** A dedicated chat interface for interacting with the Gatekeeper Agent, similar to the VSCode extension's chat interface.
*   **Project Plan Display:** A web-based view of the project plan, showing task status and progress.
*   **File Browser:** A file browser to view the project's file system and the output of the Coding Agent.
*   **Code Editor:** A simple code editor for viewing and editing code generated by the Coding Agent.

**Implementation Approach:**
*   The OpenWebUI integration will be a custom backend that communicates with the Gatekeeper Agent.
*   The frontend will be a custom web application built with a modern JavaScript framework (e.g., React, Vue.js).
*   The backend will expose a REST API or a WebSocket connection for the frontend to interact with the Gatekeeper.

### 6.3. General Applicability to Long AI Assistant Tasks

The core concept of this multi-agent system—a Gatekeeper managing a long-term plan and a focused executor—is not limited to software development. It can be applied to any long-duration AI assistant task that requires adherence to a complex plan, such as:

*   **Research and Report Writing:** The Gatekeeper manages the research outline, and the executor gathers information, writes sections, and generates citations.
*   **Data Analysis and Visualization:** The Gatekeeper manages the analysis workflow, and the executor performs data cleaning, statistical analysis, and generates plots.
*   **Automated Marketing Campaigns:** The Gatekeeper manages the campaign strategy, and the executor creates ad copy, designs visuals, and schedules posts.

By abstracting the core logic of the Gatekeeper and the executor, the system can be adapted to different domains by simply providing a domain-specific plan and toolset for the executor.





## 7. Detailed Implementation Plan for VSCode Development

This section provides a very detailed, step-by-step implementation plan for developing the multi-agent system, with a focus on enabling the user to follow along in VSCode. This plan is designed to be comprehensive, breaking down the development process into small, actionable tasks suitable for someone new to coding.

### 7.1. Phase 1: Project Setup and Core Utilities

This phase focuses on setting up the project environment, establishing the basic directory structure, and implementing foundational utilities that will be used by both agents.

#### Task 7.1.1: Initialize the Project Repository

**Goal:** Create a new Git repository and set up the basic project directory structure.

**Actionable Steps:**
1.  **Open VSCode:** Launch Visual Studio Code.
2.  **Open Terminal:** In VSCode, open the integrated terminal (Terminal > New Terminal or `Ctrl+`` `).
3.  **Create Project Directory:** Choose a location for your project and create a new directory:
    ```bash
    mkdir llm-dev-agent
    cd llm-dev-agent
    ```
4.  **Initialize Git:** Initialize a new Git repository:
    ```bash
    git init
    ```
5.  **Create `.gitignore`:** Create a file named `.gitignore` in the root of your project and add common Python and environment-related entries:
    ```
    # Python
    __pycache__/
    *.pyc
    *.pyd
    *.pyo
    .Python/
    build/
    dist/
    *.egg-info/
    .env
    venv/

    # VSCode
    .vscode/

    # Data/Logs
    *.log
    *.db
    session_state.json
    work_logs/
    ```
6.  **Initial Commit:** Stage and commit your initial project setup:
    ```bash
    git add .
    git commit -m "Initial project setup: created directory and .gitignore"
    ```

#### Task 7.1.2: Set Up Python Virtual Environment

**Goal:** Create and activate a dedicated Python virtual environment for the project to manage dependencies cleanly.

**Actionable Steps:**
1.  **Create Virtual Environment:** In your project root directory (within the VSCode terminal), create a virtual environment named `venv`:
    ```bash
    python3 -m venv venv
    ```
2.  **Activate Virtual Environment:**
    *   **Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```
    *   **Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```bash
        venv\Scripts\Activate.ps1
        ```
    (You should see `(venv)` prefixing your terminal prompt, indicating the environment is active.)
3.  **Install `pip` and `setuptools` (if needed):** Ensure `pip` is up-to-date:
    ```bash
    pip install --upgrade pip setuptools
    ```
4.  **Install `pytest`:** Install `pytest` for testing, which will be used later:
    ```bash
    pip install pytest
    ```
5.  **Create `requirements.txt`:** Create a `requirements.txt` file to list your project's dependencies:
    ```bash
    pip freeze > requirements.txt
    ```
6.  **Commit Virtual Environment Setup:**
    ```bash
    git add requirements.txt
    git commit -m "Setup Python virtual environment and added pytest"
    ```

#### Task 7.1.3: Define Core Project Structure (`src` Layout)

**Goal:** Implement the recommended `src` layout for the Python source code.

**Actionable Steps:**
1.  **Create `src` Directory:** In the project root, create the main source directory:
    ```bash
    mkdir src
    ```
2.  **Create `supermanus` Package:** Inside `src`, create the top-level package for your system:
    ```bash
    mkdir src/supermanus
    ```
3.  **Add `__init__.py` Files:** Create empty `__init__.py` files to mark these directories as Python packages:
    ```bash
    touch src/__init__.py
    touch src/supermanus/__init__.py
    ```
4.  **Commit Directory Structure:**
    ```bash
    git add src/
    git commit -m "Implemented src layout with supermanus package"
    ```

#### Task 7.1.4: Implement `session_manager.py` (Basic Version)

**Goal:** Create a utility to handle loading and saving of the project's session state, starting with a basic JSON implementation.

**Actionable Steps:**
1.  **Create `session_manager.py`:** Create a new file `src/supermanus/session_manager.py`.
2.  **Add Basic JSON Logic:** Populate the file with Python code to load and save JSON data. This will be the foundation for the Gatekeeper's state management.
    ```python
    # src/supermanus/session_manager.py
    import json
    from pathlib import Path
    from typing import Dict, Any

    class SessionManager:
        def __init__(self, session_file_path: Path):
            self.session_file = session_file_path

        def load_state(self) -> Dict[str, Any]:
            if not self.session_file.exists():
                # Return a default empty state if file doesn't exist
                return {
                    "project_name": "LLM Dev Agent Project",
                    "current_phase": "",
                    "tasks": [],
                    "validation_history": []
                }
            with open(self.session_file, 'r') as f:
                return json.load(f)

        def save_state(self, state: Dict[str, Any]):
            with open(self.session_file, 'w') as f:
                json.dump(state, f, indent=2)

    # Example usage (for testing purposes, will be removed later)
    if __name__ == "__main__":
        test_file = Path("test_session.json")
        manager = SessionManager(test_file)

        # Load initial state (will be empty or default)
        current_state = manager.load_state()
        print(f"Loaded state: {current_state}")

        # Modify state
        current_state["project_name"] = "My First LLM Project"
        current_state["current_phase"] = "Planning"
        current_state["tasks"].append({"id": "T1", "title": "Initial Task"})

        # Save state
        manager.save_state(current_state)
        print(f"Saved state: {manager.load_state()}")

        # Clean up test file
        test_file.unlink()
    ```
3.  **Test `session_manager.py`:** Run the example usage directly from the terminal to verify it works:
    ```bash
    python src/supermanus/session_manager.py
    ```
    (You should see output indicating loading, modifying, and saving the state, and then the `test_session.json` file should be created and then deleted.)
4.  **Commit `session_manager.py`:**
    ```bash
    git add src/supermanus/session_manager.py
    git commit -m "Implemented basic session_manager for state persistence"
    ```

#### Task 7.1.5: Implement Basic Logging Configuration

**Goal:** Set up a centralized logging configuration for the entire application.

**Actionable Steps:**
1.  **Create `logging_config.py`:** Create a new file `src/supermanus/logging_config.py`.
2.  **Add Logging Setup:** Populate the file with code to configure logging, including file handlers and console handlers.
    ```python
    # src/supermanus/logging_config.py
    import logging
    from pathlib import Path

    def setup_logging(log_file: Path = Path("app.log"), level=logging.INFO):
        # Ensure log directory exists if log_file is in a subdirectory
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Basic configuration
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        # Set a higher level for some noisy libraries if needed
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)

    # Example usage (for testing purposes)
    if __name__ == "__main__":
        log_path = Path("logs/test_app.log")
        setup_logging(log_path, logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.debug("This is a debug message.")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        try:
            1 / 0
        except ZeroDivisionError:
            logger.exception("An exception occurred!")
    ```
3.  **Test Logging:** Run the example usage:
    ```bash
    python src/supermanus/logging_config.py
    ```
    (You should see log messages in the terminal and a new `logs/app.log` file created with the same messages.)
4.  **Commit Logging Configuration:**
    ```bash
    git add src/supermanus/logging_config.py
    git commit -m "Implemented basic logging configuration"
    ```

### 7.2. Phase 2: Gatekeeper Agent Core Development

This phase focuses on building the foundational components of the Gatekeeper Agent.

#### Task 7.2.1: Implement `task_enforcer.py` (Refactored)

**Goal:** Create the core `TaskSystemEnforcer` class, integrating it with the new `session_manager`.

**Actionable Steps:**
1.  **Create `task_enforcer.py`:** Create a new file `src/supermanus/task_enforcer.py`.
2.  **Refactor `TaskSystemEnforcer`:** Copy the relevant logic from the original `task_enforcer.py` but adapt it to use `SessionManager` for state persistence. Focus on the core logic for task management, risk assessment, and validation.
    ```python
    # src/supermanus/task_enforcer.py
    import json
    import logging
    from pathlib import Path
    from datetime import datetime
    from typing import Dict, Any, List, Optional, Tuple
    from enum import Enum
    from .session_manager import SessionManager # Import the new SessionManager

    logger = logging.getLogger(__name__)

    class TaskRiskLevel(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    class ValidationResult(Enum):
        APPROVED = "approved"
        REJECTED = "rejected"
        PENDING = "pending_human_review"
        BLOCKED = "blocked"

    class TaskSystemEnforcer:
        def __init__(self, project_root: Path = Path(".")):
            self.project_root = project_root.resolve()
            self.session_file = self.project_root / "session_state.json"
            self.work_log_dir = self.project_root / "work_logs"
            self.work_log_dir.mkdir(exist_ok=True)
            self.session_manager = SessionManager(self.session_file)
            self._load_state()

        def _load_state(self):
            state = self.session_manager.load_state()
            self.current_task: Optional[Dict[str, Any]] = state.get("current_task", None)
            self.work_log_active: bool = state.get("work_log_active", False)
            self.validation_history: List[Dict[str, Any]] = state.get("validation_history", [])
            self.project_tasks: List[Dict[str, Any]] = state.get("tasks", [])

        def _save_state(self):
            state = {
                "project_name": self.session_manager.load_state().get("project_name", "Unknown Project"),
                "current_phase": self.session_manager.load_state().get("current_phase", ""),
                "current_task": self.current_task,
                "work_log_active": self.work_log_active,
                "validation_history": self.validation_history,
                "tasks": self.project_tasks # Save the full task list
            }
            self.session_manager.save_state(state)

        def get_active_tasks(self) -> List[str]:
            # For now, assume all tasks in project_tasks are active until marked complete
            return [task["task_id"] for task in self.project_tasks if task["status"] != "completed"]

        def force_task_selection(self) -> str:
            active_tasks = self.get_active_tasks()
            if not active_tasks:
                return "❌ BLOCKED: No active tasks in project plan. Update plan first."

            task_list = "\n".join([f"  {i+1}. {task}" for i, task in enumerate(active_tasks)])

            return f"""
🚨 TASK SELECTION REQUIRED

You must select ONE active task before proceeding:

{task_list}

REQUIRED: Call set_current_task(task_id) with exact task string.
            """

        def set_current_task(self, task_id: str) -> ValidationResult:
            active_tasks = self.get_active_tasks()
            if task_id not in active_tasks:
                logger.error(f"Invalid task selection: {task_id}")
                return ValidationResult.BLOCKED

            # Find the task object in project_tasks
            selected_task_obj = next((task for task in self.project_tasks if task["task_id"] == task_id), None)
            if not selected_task_obj:
                logger.error(f"Task object not found for ID: {task_id}")
                return ValidationResult.BLOCKED

            self.current_task = {
                "id": task_id,
                "title": selected_task_obj.get("title", task_id),
                "start_time": datetime.now().isoformat(),
                "status": "active",
                "risk_level": self._assess_task_risk(task_id).value
            }
            self._save_state()
            logger.info(f"Task selected: {task_id}")
            return ValidationResult.APPROVED

        def _assess_task_risk(self, task_id: str) -> TaskRiskLevel:
            high_risk_keywords = ["deploy", "security", "auth", "database", "kubernetes", "production"]
            medium_risk_keywords = ["implement", "refactor", "api", "service", "docker"]

            task_lower = task_id.lower()

            if any(keyword in task_lower for keyword in high_risk_keywords):
                return TaskRiskLevel.HIGH
            elif any(keyword in task_lower for keyword in medium_risk_keywords):
                return TaskRiskLevel.MEDIUM
            else:
                return TaskRiskLevel.LOW

        def require_work_log(self) -> str:
            if not self.current_task:
                return self.force_task_selection()

            if self.work_log_active:
                return "✅ Work log active. Proceed with task."

            work_log_file = self.work_log_dir / f"task_{self.current_task['id'].replace(':', '_').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

            work_log_template = self._generate_work_log_template()

            return f"""
🚨 WORK LOG REQUIRED

Create work log file: {work_log_file}

Template content:
{work_log_template}

REQUIRED: Create the work log file, then call start_work_log().
            """

        def _generate_work_log_template(self) -> str:
            return f"""# Work Log: {self.current_task['id']}

## Task Information
- **Task ID:** {self.current_task['id']}
- **Start Time:** {self.current_task['start_time']}
- **Risk Level:** {self.current_task['risk_level']}
- **Status:** {self.current_task['status']}

## Success Criteria
- [ ] Define clear, measurable completion criteria
- [ ] Identify all deliverables
- [ ] List validation commands

## Work Steps
### Step 1: [Description]
- **Action:**
- **Expected Result:**
- **Actual Result:**
- **Validation Command:**
- **Success:** [ ]

## Completion Proof
- **Test Commands:**
- **Output Evidence:**
- **File Evidence:**
- **Functional Proof:**

## Validation
- [ ] All tests pass
- [ ] Files exist as expected
- [ ] Functionality verified
- [ ] Documentation updated
- [ ] Ready for review

---
*Auto-generated by SuperManUS Task Enforcer*
"""

        def start_work_log(self) -> ValidationResult:
            if not self.current_task:
                return ValidationResult.BLOCKED

            self.work_log_active = True
            self._save_state()
            logger.info(f"Work log activated for task: {self.current_task['id']}")
            return ValidationResult.APPROVED

        def validate_action(self, action_description: str, justification: str) -> Tuple[ValidationResult, str]:
            if not self.current_task:
                return ValidationResult.BLOCKED, self.force_task_selection()

            if not self.work_log_active:
                return ValidationResult.BLOCKED, self.require_work_log()

            action_log = {
                "timestamp": datetime.now().isoformat(),
                "task_id": self.current_task["id"],
                "action": action_description,
                "justification": justification,
                "status": "proposed"
            }

            self.validation_history.append(action_log)
            self._save_state()

            if len(justification.strip()) < 20:
                return ValidationResult.REJECTED, "❌ Insufficient justification. Explain how this action advances the current task."

            task_keywords = self._extract_task_keywords(self.current_task["title"])
            justification_lower = justification.lower()

            if not any(keyword in justification_lower for keyword in task_keywords):
                return ValidationResult.REJECTED, f"❌ Justification must explain connection to task: {self.current_task['title']}"

            return ValidationResult.APPROVED, "✅ Action approved. Proceed."

        def _extract_task_keywords(self, task_title: str) -> List[str]:
            words = task_title.lower().replace(":", " ").split()
            return [word for word in words if len(word) > 3]

        def require_completion_proof(self) -> Dict[str, Any]:
            if not self.current_task:
                return {"error": "No active task"}

            risk_level = TaskRiskLevel(self.current_task["risk_level"])

            base_requirements = {
                "file_evidence": "List all files created/modified with ls -la",
                "functional_test": "Provide command that demonstrates functionality",
                "error_check": "Show no errors in logs or output"
            }

            if risk_level == TaskRiskLevel.MEDIUM:
                base_requirements.update({
                    "integration_test": "Test integration with existing system",
                    "syntax_validation": "Validate syntax of all code changes"
                })

            if risk_level == TaskRiskLevel.HIGH:
                base_requirements.update({
                    "comprehensive_testing": "Full test suite execution",
                    "security_check": "Security implications reviewed",
                    "human_review_required": "Human approval needed for completion"
                })

            return {
                "task_id": self.current_task["id"],
                "risk_level": risk_level.value,
                "requirements": base_requirements,
                "validation_commands": self._generate_validation_commands()
            }

        def _generate_validation_commands(self) -> List[str]:
            commands = [
                "git status --porcelain  # Check file changes",
                "find . -name '*.py' -exec python -m py_compile {} \\;  # Syntax check",
            ]

            task_lower = self.current_task["title"].lower()

            if "docker" in task_lower:
                commands.append("docker-compose config --quiet  # Validate Docker config")

            if "test" in task_lower:
                commands.append("python -m pytest -v  # Run tests")

            if "kubernetes" in task_lower or "k8s" in task_lower:
                commands.append("kubectl apply --dry-run=client --validate=true -f k8s/  # Validate K8s")

            return commands

        def validate_completion(self, proof_data: Dict[str, Any]) -> Tuple[ValidationResult, str]:
            if not self.current_task:
                return ValidationResult.BLOCKED, "No active task to complete"

            requirements = self.require_completion_proof()["requirements"]

            missing_proof = []
            for req_key, req_desc in requirements.items():
                if req_key not in proof_data or not proof_data[req_key]:
                    missing_proof.append(req_desc)

            if missing_proof:
                return ValidationResult.REJECTED, f"❌ Missing proof for: {', '.join(missing_proof)}"

            risk_level = TaskRiskLevel(self.current_task["risk_level"])
            if risk_level == TaskRiskLevel.HIGH:
                return ValidationResult.PENDING, "⏳ High-risk task requires human approval"

            self._mark_task_complete()
            return ValidationResult.APPROVED, "✅ Task completion validated and approved"

        def _mark_task_complete(self):
            # Update the status of the completed task in project_tasks
            for task in self.project_tasks:
                if task.get("task_id") == self.current_task["id"]:
                    task["status"] = "completed"
                    task["end_time"] = datetime.now().isoformat()
                    break

            self.current_task = None
            self.work_log_active = False
            self._save_state()
            logger.info("Task completed and session state updated")

        def get_status(self) -> Dict[str, Any]:
            return {
                "current_task": self.current_task,
                "work_log_active": self.work_log_active,
                "active_tasks_available": len(self.get_active_tasks()),
                "validation_history_count": len(self.validation_history)
            }

        def update_project_plan(self, new_plan: List[Dict[str, Any]]):
            self.project_tasks = new_plan
            self._save_state()
            logger.info("Project plan updated.")

    # Global enforcer instance (for convenience, can be managed differently in a larger app)
    _enforcer_instance: Optional[TaskSystemEnforcer] = None

    def get_enforcer(project_root: Path = Path(".")) -> TaskSystemEnforcer:
        global _enforcer_instance
        if _enforcer_instance is None:
            _enforcer_instance = TaskSystemEnforcer(project_root)
        return _enforcer_instance

    # Convenience functions for LLM integration
    def enforce_task_discipline() -> str:
        enforcer = get_enforcer()
        if not enforcer.current_task:
            return enforcer.force_task_selection()
        if not enforcer.work_log_active:
            return enforcer.require_work_log()
        return "✅ Task discipline maintained. Proceed with work."

    def validate_llm_action(action: str, justification: str) -> Tuple[bool, str]:
        enforcer = get_enforcer()
        result, message = enforcer.validate_action(action, justification)
        return result == ValidationResult.APPROVED, message

    def require_completion_proof() -> Dict[str, Any]:
        enforcer = get_enforcer()
        return enforcer.require_completion_proof()
    ```
3.  **Update `pyproject.toml`:** If you are using `pyproject.toml` for project metadata, ensure your project is set up as a package. If not, create one.
    ```toml
    # pyproject.toml
    [project]
    name = "supermanus"
    version = "0.1.0"
    description = "A multi-agent system for LLM-driven development"
    authors = [
        { name = "Manus AI", email = "ai@example.com" }
    ]
    dependencies = [
        "pytest", # Add other dependencies as you install them
    ]
    readme = "README.md"
    requires-python = ">=3.8"

    [build-system]
    requires = ["setuptools>=61.0"]
    build-backend = "setuptools.build_meta"

    [tool.setuptools.packages.find]
    where = ["src"]
    ```
4.  **Commit `task_enforcer.py` and `pyproject.toml`:**
    ```bash
    git add src/supermanus/task_enforcer.py pyproject.toml
    git commit -m "Implemented refactored task_enforcer and updated pyproject.toml"
    ```

#### Task 7.2.2: Implement `llm_guard.py` (Refactored)

**Goal:** Create the core `LLMGuard` functionality, integrating it with the refactored `task_enforcer`.

**Actionable Steps:**
1.  **Create `llm_guard.py`:** Create a new file `src/supermanus/llm_guard.py`.
2.  **Refactor `LLMGuard`:** Copy the relevant logic from the original `llm_guard.py` but ensure it imports `get_enforcer` from the new `src.supermanus.task_enforcer`.
    ```python
    # src/supermanus/llm_guard.py
    import functools
    import logging
    from typing import Any, Callable, Dict, Tuple, Optional
    from .task_enforcer import get_enforcer, ValidationResult # Corrected import

    logger = logging.getLogger(__name__)

    class LLMGuardException(Exception):
        """Exception raised when LLM attempts unauthorized actions"""
        pass

    class TaskViolationException(LLMGuardException):
        """Exception raised when LLM deviates from assigned task"""
        pass

    class ProofRequiredException(LLMGuardException):
        """Exception raised when LLM claims completion without proof"""
        pass

    def require_active_task(func: Callable) -> Callable:
        """Decorator that blocks function execution without an active task"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            enforcer = get_enforcer()

            if not enforcer.current_task:
                raise TaskViolationException(
                    "❌ BLOCKED: No active task selected. "
                    "Call set_current_task() first with official task from project plan."
                )

            if not enforcer.work_log_active:
                raise TaskViolationException(
                    "❌ BLOCKED: Work log required. "
                    "Create work log using template and call start_work_log()"
                )

            return func(*args, **kwargs)

        return wrapper

    def require_task_justification(action_description: str):
        """Decorator that requires justification for how action advances current task"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                justification = kwargs.get('justification', '')

                if not justification:
                    raise TaskViolationException(
                        f"❌ BLOCKED: Action '{action_description}' requires justification. "
                        f"Add justification='...' parameter explaining how this advances current task."
                    )

                enforcer = get_enforcer()
                result, message = enforcer.validate_action(action_description, justification)

                if result != ValidationResult.APPROVED:
                    raise TaskViolationException(f"❌ Action blocked: {message}")

                kwargs.pop('justification', None)

                logger.info(f"Action approved: {action_description}")
                return func(*args, **kwargs)

            return wrapper
        return decorator

    def require_completion_proof(func: Callable) -> Callable:
        """Decorator that blocks completion claims without comprehensive proof"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            proof_data = kwargs.get('proof_data', {})

            if not proof_data:
                raise ProofRequiredException(
                    "❌ BLOCKED: Task completion requires proof_data parameter with comprehensive evidence"
                )

            enforcer = get_enforcer()
            result, message = enforcer.validate_completion(proof_data)

            if result == ValidationResult.REJECTED:
                raise ProofRequiredException(f"❌ Completion proof insufficient: {message}")

            if result == ValidationResult.PENDING:
                logger.warning(f"Completion pending human review: {message}")
                return {"status": "pending_human_review", "message": message}

            logger.info("Task completion validated")
            return func(*args, **kwargs)

        return wrapper

    class LLMActionGuard:
        """Context manager that enforces task discipline during LLM operations"""

        def __init__(self, action_description: str, justification: str):
            self.action_description = action_description
            self.justification = justification
            self.enforcer = get_enforcer()

        def __enter__(self):
            if not self.enforcer.current_task:
                raise TaskViolationException(self.enforcer.force_task_selection())

            if not self.enforcer.work_log_active:
                raise TaskViolationException(self.enforcer.require_work_log())

            result, message = self.enforcer.validate_action(
                self.action_description,
                self.justification
            )

            if result != ValidationResult.APPROVED:
                raise TaskViolationException(f"❌ {message}")

            logger.info(f"Guarded action started: {self.action_description}")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                logger.info(f"Guarded action completed: {self.action_description}")
            else:
                logger.error(f"Guarded action failed: {self.action_description} - {exc_val}")

            return False

    # Convenience functions for common LLM operations
    def guard_file_operation(operation: str, filepath: str, justification: str):
        return LLMActionGuard(
            f"File operation: {operation} on {filepath}",
            justification
        )

    def guard_code_change(module: str, change_description: str, justification: str):
        return LLMActionGuard(
            f"Code change: {change_description} in {module}",
            justification
        )

    def guard_tool_usage(tool_name: str, purpose: str, justification: str):
        return LLMActionGuard(
            f"Tool usage: {tool_name} for {purpose}",
            justification
        )

    # Pre-built validation functions for common scenarios
    def validate_file_creation(filepath: str, purpose: str, justification: str) -> bool:
        try:
            with guard_file_operation("create", filepath, justification):
                return True
        except TaskViolationException:
            return False

    def validate_code_modification(module: str, changes: str, justification: str) -> bool:
        try:
            with guard_code_change(module, changes, justification):
                return True
        except TaskViolationException:
            return False

    # Task enforcement utilities
    def check_task_discipline() -> Tuple[bool, str]:
        try:
            enforcer = get_enforcer()

            if not enforcer.current_task:
                return False, enforcer.force_task_selection()

            if not enforcer.work_log_active:
                return False, enforcer.require_work_log()

            return True, "✅ Task discipline maintained"

        except Exception as e:
            return False, f"❌ Task discipline check failed: {e}"

    def get_current_task_context() -> Dict[str, Any]:
        enforcer = get_enforcer()

        if not enforcer.current_task:
            return {"error": "No active task"}

        return {
            "current_task": enforcer.current_task,
            "completion_requirements": enforcer.require_completion_proof(),
            "validation_history_count": len(enforcer.validation_history),
            "work_log_active": enforcer.work_log_active
        }

    def enforce_completion_standards(proofhat specific task or question would you like assistance with? Let me know if you'd like help organizing your work or creating a to-do list for your current project._package: Dict[str, Any]) -> Dict[str, Any]:
        enforcer = get_enforcer()

        if not enforcer.current_task:
            return {"error": "No active task to complete"}

        result, message = enforcer.validate_completion(proof_package)

        return {
            "validation_result": result.value,
            "message": message,
            "requires_human_review": result == ValidationResult.PENDING,
            "approved": result == ValidationResult.APPROVED
        }

    # Integration hooks for external systems
    def hook_git_operations(justification: str = None):
        if not justification:
            raise TaskViolationException(
                "❌ Git operations require justification parameter: "
                "Explain how this git operation advances the current task"
            )

        return guard_tool_usage("git", "version control", justification)

    def hook_docker_operations(justification: str = None):
        if not justification:
            raise TaskViolationException(
                "❌ Docker operations require justification parameter: "
                "Explain how this Docker operation advances the current task"
            )

        return guard_tool_usage("docker", "containerization", justification)

    def hook_test_execution(justification: str = None):
        if not justification:
            raise TaskViolationException(
                "❌ Test execution requires justification parameter: "
                "Explain how running tests advances the current task"
            )

        return guard_tool_usage("pytest", "testing", justification)

    # Emergency controls
    def emergency_unlock() -> str:
        logger.warning("EMERGENCY UNLOCK ACTIVATED - Human intervention required")
        return """
🚨 EMERGENCY UNLOCK ACTIVATED

This bypasses normal task enforcement.
Use only for:
- Critical system recovery
- Emergency bug fixes
- Human-supervised operations

Normal task discipline will resume after human confirmation.
"""

    def reset_task_state() -> str:
        global _enforcer_instance
        _enforcer_instance = None
        logger.warning("Task enforcer state reset")
        return "⚠️ Task state reset. Must select new task before proceeding."
    ```
3.  **Commit `llm_guard.py`:**
    ```bash
    git add src/supermanus/llm_guard.py
    git commit -m "Implemented refactored llm_guard"
    ```

#### Task 7.2.3: Create `gatekeeper_agent.py` (Initial Version)

**Goal:** Implement the main logic for the Gatekeeper Agent, including plan loading, task selection, and dispatching.

**Actionable Steps:**
1.  **Create `gatekeeper_agent.py`:** Create a new file `src/supermanus/gatekeeper_agent.py`.
2.  **Implement Gatekeeper Logic:** This will be the orchestrator. It will use `TaskSystemEnforcer` to manage the plan and interact with the (soon-to-be-created) Coding Agent.
    ```python
    # src/supermanus/gatekeeper_agent.py
    import logging
    from pathlib import Path
    from typing import Dict, Any, List, Optional
    from .task_enforcer import get_enforcer, ValidationResult, TaskSystemEnforcer
    from .logging_config import setup_logging

    logger = logging.getLogger(__name__)

    class GatekeeperAgent:
        def __init__(self, project_root: Path = Path(".")):
            self.project_root = project_root
            self.enforcer = get_enforcer(project_root)
            setup_logging(log_file=self.project_root / "gatekeeper.log")
            logger.info("Gatekeeper Agent initialized.")

        def load_project_plan(self, plan_data: List[Dict[str, Any]]):
            """Loads a new project plan into the enforcer."""
            self.enforcer.update_project_plan(plan_data)
            logger.info(f"Loaded project plan with {len(plan_data)} tasks.")

        def get_next_task_for_coding_agent(self) -> Optional[Dict[str, Any]]:
            """Identifies and returns the next task for the Coding Agent."""
            for task in self.enforcer.project_tasks:
                if task["status"] == "pending":
                    # Check dependencies (simple check for now)
                    dependencies_met = True
                    for dep_id in task.get("dependencies", []):
                        dep_task = next((t for t in self.enforcer.project_tasks if t["task_id"] == dep_id), None)
                        if not dep_task or dep_task["status"] != "completed":
                            dependencies_met = False
                            break
                    if dependencies_met:
                        return task
            return None

        def dispatch_task_to_coding_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
            """Simulates dispatching a task to the Coding Agent and setting it as current."""
            logger.info(f"Dispatching task: {task['task_id']} - {task['title']}")
            # In a real system, this would send the task to a separate process/API
            # For now, we'll just set it as the current task in the enforcer
            result = self.enforcer.set_current_task(task["task_id"])
            if result == ValidationResult.APPROVED:
                # Update task status in the project plan
                for t in self.enforcer.project_tasks:
                    if t["task_id"] == task["task_id"]:
                        t["status"] = "in_progress"
                        break
                self.enforcer._save_state() # Save state after status update
                return {"status": "dispatched", "task": task}
            else:
                logger.error(f"Failed to set current task for dispatch: {task['task_id']}")
                return {"status": "failed_dispatch", "message": str(result)}

        def receive_coding_agent_report(self, task_id: str, status: str, output: Any = None, error: Any = None):
            """Receives report from Coding Agent and updates task status."""
            logger.info(f"Received report for task {task_id}: Status={status}")
            # In a real system, this would involve more complex validation and state updates
            for task in self.enforcer.project_tasks:
                if task["task_id"] == task_id:
                    if status == "completed":
                        # Simulate validation (real validation would be more complex)
                        validation_result, message = self.enforcer.validate_completion({"mock_proof": True})
                        if validation_result == ValidationResult.APPROVED:
                            task["status"] = "completed"
                            task["end_time"] = datetime.now().isoformat()
                            logger.info(f"Task {task_id} marked completed and validated.")
                        else:
                            task["status"] = "blocked"
                            logger.warning(f"Task {task_id} completed but validation failed: {message}")
                    elif status == "failed":
                        task["status"] = "blocked"
                        logger.error(f"Task {task_id} failed with error: {error}")
                    # Add other statuses like 'in_progress' if needed
                    break
            self.enforcer._save_state()

        def run_orchestration_loop(self):
            """Main orchestration loop for the Gatekeeper."""
            logger.info("Starting Gatekeeper orchestration loop.")
            while True:
                current_status = self.enforcer.get_status()
                logger.info(f"Gatekeeper Status: {current_status}")

                if current_status["current_task"] is None:
                    next_task = self.get_next_task_for_coding_agent()
                    if next_task:
                        self.dispatch_task_to_coding_agent(next_task)
                        # In a real system, wait for Coding Agent to pick up and report
                        # For this simulation, we'll just mark it as in_progress and break
                        # The actual Coding Agent will report back later
                        logger.info(f"Task {next_task['task_id']} dispatched. Waiting for Coding Agent...")
                        break # For initial test, dispatch one and stop
                    else:
                        logger.info("No pending tasks. Project might be complete or blocked.")
                        break # No more tasks to dispatch
                else:
                    logger.info(f"Current task {current_status['current_task']['id']} is in progress. Waiting for report...")
                    break # For initial test, if task is active, wait

    # Example Usage (for testing the Gatekeeper's basic flow)
    if __name__ == "__main__":
        # Ensure logging is set up for the main script
        setup_logging(log_file=Path("gatekeeper_main.log"), level=logging.DEBUG)

        # Define a simple project plan
        sample_plan = [
            {
                "task_id": "GK1.1",
                "title": "Gatekeeper: Initialize project",
                "description": "Set up the initial project structure.",
                "status": "pending",
                "dependencies": [],
                "risk_level": "low",
                "output_expected": "Project structure created",
                "validation_criteria": "Manual check",
                "agent_instructions": "Create basic project directories and files."
            },
            {
                "task_id": "CA1.1",
                "title": "Coding Agent: Implement basic file operations",
                "description": "Write a Python function to create and write to a file.",
                "status": "pending",
                "dependencies": ["GK1.1"],
                "risk_level": "medium",
                "output_expected": "file_utils.py with create_file function",
                "validation_criteria": "Unit tests",
                "agent_instructions": "Create src/supermanus/utils/file_utils.py and add a function `create_file(path, content)` that creates a file at `path` with `content`."
            },
            {
                "task_id": "CA1.2",
                "title": "Coding Agent: Implement basic read operations",
                "description": "Write a Python function to read from a file.",
                "status": "pending",
                "dependencies": ["CA1.1"],
                "risk_level": "medium",
                "output_expected": "file_utils.py with read_file function",
                "validation_criteria": "Unit tests",
                "agent_instructions": "Add a function `read_file(path)` to src/supermanus/utils/file_utils.py that reads and returns the content of a file at `path`."
            }
        ]

        gatekeeper = GatekeeperAgent()
        gatekeeper.load_project_plan(sample_plan)

        # First run: GK1.1 should be dispatched
        gatekeeper.run_orchestration_loop()

        # Simulate GK1.1 completion (manual for now)
        # In a real scenario, the Coding Agent would report this back
        print("\nSimulating GK1.1 completion...")
        gatekeeper.receive_coding_agent_report("GK1.1", "completed", output="Project structure created.")

        # Second run: CA1.1 should be dispatched
        gatekeeper.run_orchestration_loop()

        # Simulate CA1.1 failure
        print("\nSimulating CA1.1 failure...")
        gatekeeper.receive_coding_agent_report("CA1.1", "failed", error="Syntax error in file_utils.py")

        # Third run: GK should see CA1.1 as blocked and not dispatch CA1.2
        gatekeeper.run_orchestration_loop()

        # You can manually inspect session_state.json and gatekeeper.log
    ```
3.  **Commit `gatekeeper_agent.py`:**
    ```bash
    git add src/supermanus/gatekeeper_agent.py
    git commit -m "Implemented initial Gatekeeper Agent core logic"
    ```

#### Task 7.2.4: Create `project_plan_template.json`

**Goal:** Provide a structured template for the comprehensive project plan that the Gatekeeper will consume.

**Actionable Steps:**
1.  **Create `project_plan_template.json`:** Create a new file `project_plan_template.json` in the root of your project.
2.  **Populate with Example Plan:** Use the structure defined in the design document (Section 4.2.1) to create a sample project plan. This will be the input for your Gatekeeper.
    ```json
    [
        {
            "task_id": "P1.1",
            "title": "Understand and formalize the multi-agent system architecture",
            "description": "Outline the roles, responsibilities, and communication flow.",
            "status": "pending",
            "assigned_to": "Gatekeeper",
            "dependencies": [],
            "risk_level": "low",
            "output_expected": "Architectural overview document",
            "validation_criteria": "Manual review",
            "agent_instructions": "Review the existing design document and confirm understanding."
        },
        {
            "task_id": "P1.2",
            "title": "Design the 'Gatekeeper' agent's functionalities and data structures",
            "description": "Detail the internal components and data models for the Gatekeeper.",
            "status": "pending",
            "assigned_to": "Gatekeeper",
            "dependencies": ["P1.1"],
            "risk_level": "medium",
            "output_expected": "Gatekeeper design document section",
            "validation_criteria": "Internal consistency check, human review",
            "agent_instructions": "Elaborate on the Gatekeeper's core components: Plan Parser, Task Dispatcher, Progress Monitor, Human Interaction Layer, and their data structures."
        },
        {
            "task_id": "P1.3",
            "title": "Design the 'Coding Agent's' functionalities and interaction protocols",
            "description": "Detail the internal components and interaction patterns for the Coding Agent.",
            "status": "pending",
            "assigned_to": "Gatekeeper",
            "dependencies": ["P1.2"],
            "risk_level": "medium",
            "output_expected": "Coding Agent design document section",
            "validation_criteria": "Internal consistency check, human review",
            "agent_instructions": "Elaborate on the Coding Agent's core components: Task Interpreter, Toolset, Enforcement Layer, Status Reporter, and its interaction protocol with the Gatekeeper."
        },
        {
            "task_id": "P2.1",
            "title": "Implement basic file creation utility",
            "description": "Write a Python function to create and write content to a file.",
            "status": "pending",
            "assigned_to": "Coding Agent",
            "dependencies": ["P1.3"],
            "risk_level": "low",
            "output_expected": "src/supermanus/utils/file_utils.py with create_file function",
            "validation_criteria": "Unit tests",
            "agent_instructions": "Create a new file `src/supermanus/utils/file_utils.py`. Implement a function `create_file(path: Path, content: str)` that creates a file at the given `path` and writes the `content` to it. Ensure necessary parent directories are created. Use `pathlib` for path manipulation."
        },
        {
            "task_id": "P2.2",
            "title": "Implement basic file reading utility",
            "description": "Write a Python function to read content from a file.",
            "status": "pending",
            "assigned_to": "Coding Agent",
            "dependencies": ["P2.1"],
            "risk_level": "low",
            "output_expected": "src/supermanus/utils/file_utils.py with read_file function",
            "validation_criteria": "Unit tests",
            "agent_instructions": "Add a function `read_file(path: Path) -> str` to `src/supermanus/utils/file_utils.py` that reads and returns the entire content of the file at the given `path`. Handle `FileNotFoundError` gracefully by returning an empty string or raising a custom exception."
        }
        // ... more tasks for the full project
    ]
    ```
3.  **Commit `project_plan_template.json`:**
    ```bash
    git add project_plan_template.json
    git commit -m "Added project plan template for Gatekeeper"
    ```

### 7.3. Phase 3: Coding Agent Core Development

This phase focuses on building the foundational components of the Coding Agent.

#### Task 7.3.1: Implement `coding_agent.py` (Initial Version)

**Goal:** Create the main logic for the Coding Agent, capable of receiving a task and simulating execution.

**Actionable Steps:**
1.  **Create `coding_agent.py`:** Create a new file `src/supermanus/coding_agent.py`.
2.  **Implement Coding Agent Logic:** This agent will receive tasks from the Gatekeeper and simulate performing actions. Initially, it will just print the task and report completion.
    ```python
    # src/supermanus/coding_agent.py
    import logging
    from pathlib import Path
    from typing import Dict, Any
    import time

    from .logging_config import setup_logging
    from .task_enforcer import get_enforcer, LLMActionGuard, TaskViolationException

    logger = logging.getLogger(__name__)

    class CodingAgent:
        def __init__(self, project_root: Path = Path(".")):
            self.project_root = project_root
            self.enforcer = get_enforcer(project_root)
            setup_logging(log_file=self.project_root / "coding_agent.log")
            logger.info("Coding Agent initialized.")

        def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
            """Executes a given task and reports back to the Gatekeeper."""
            task_id = task["task_id"]
            instructions = task["agent_instructions"]
            title = task["title"]

            logger.info(f"Coding Agent received task: {task_id} - {title}")
            logger.info(f"Instructions: {instructions}")

            try:
                # Simulate task execution with enforcement
                # In a real scenario, this would involve actual tool calls
                with LLMActionGuard(f"Execute task {task_id}", justification=f"Working on {title}"):
                    logger.info(f"Simulating work for task {task_id}...")
                    time.sleep(2) # Simulate work
                    # Here, you would call actual tools based on instructions
                    # For now, just a placeholder
                    simulated_output = f"Successfully simulated execution of task {task_id}."
                    logger.info(simulated_output)

                # Simulate successful completion report
                return {"status": "completed", "task_id": task_id, "output": simulated_output}

            except TaskViolationException as e:
                logger.error(f"Task {task_id} blocked by enforcement: {e}")
                return {"status": "failed", "task_id": task_id, "error": str(e)}
            except Exception as e:
                logger.error(f"Task {task_id} failed unexpectedly: {e}", exc_info=True)
                return {"status": "failed", "task_id": task_id, "error": str(e)}

    # Example Usage (for testing the Coding Agent's basic flow)
    if __name__ == "__main__":
        # Ensure logging is set up for the main script
        setup_logging(log_file=Path("coding_agent_main.log"), level=logging.DEBUG)

        # This part would typically be called by the Gatekeeper
        # For standalone testing, we need to manually set up a current task
        enforcer = get_enforcer()
        # Manually load a dummy plan for testing purposes
        dummy_plan = [
            {
                "task_id": "TEST_CA_1",
                "title": "Test Coding Agent Task",
                "description": "This is a test task for the Coding Agent.",
                "status": "pending",
                "dependencies": [],
                "risk_level": "low",
                "output_expected": "Test output",
                "validation_criteria": "None",
                "agent_instructions": "Perform a simulated action."
            }
        ]
        enforcer.update_project_plan(dummy_plan)
        enforcer.set_current_task("TEST_CA_1")
        enforcer.start_work_log()

        coding_agent = CodingAgent()
        test_task = dummy_plan[0]

        report = coding_agent.execute_task(test_task)
        print(f"\nCoding Agent Report: {report}")

        # Simulate a task that would be blocked (e.g., no work log)
        enforcer.work_log_active = False # Temporarily disable work log
        report_blocked = coding_agent.execute_task(test_task)
        print(f"\nCoding Agent Report (Blocked): {report_blocked}")
    ```
3.  **Commit `coding_agent.py`:**
    ```bash
    git add src/supermanus/coding_agent.py
    git commit -m "Implemented initial Coding Agent core logic"
    ```

#### Task 7.3.2: Integrate Coding Agent into Gatekeeper Loop

**Goal:** Modify the Gatekeeper to actually call the Coding Agent and process its reports.

**Actionable Steps:**
1.  **Modify `gatekeeper_agent.py`:** Open `src/supermanus/gatekeeper_agent.py`.
2.  **Import `CodingAgent`:** Add the import statement:
    ```python
    from .coding_agent import CodingAgent
    ```
3.  **Instantiate `CodingAgent`:** In the `GatekeeperAgent.__init__` method, instantiate the Coding Agent:
    ```python
    class GatekeeperAgent:
        def __init__(self, project_root: Path = Path(".")):
            # ... existing code ...
            self.coding_agent = CodingAgent(project_root) # Add this line
            logger.info("Gatekeeper Agent initialized.")
    ```
4.  **Modify `dispatch_task_to_coding_agent`:** Instead of just setting the current task, actually call the Coding Agent and process its report.
    ```python
    class GatekeeperAgent:
        # ... existing code ...

        def dispatch_task_to_coding_agent(self, task: Dict[str, Any]) -> Dict[str, Any]:
            logger.info(f"Dispatching task: {task['task_id']} - {task['title']}")
            result = self.enforcer.set_current_task(task["task_id"])
            if result == ValidationResult.APPROVED:
                # Update task status in the project plan to in_progress
                for t in self.enforcer.project_tasks:
                    if t["task_id"] == task["task_id"]:
                        t["status"] = "in_progress"
                        break
                self.enforcer._save_state()

                # *** NEW: Call the Coding Agent and get its report ***
                coding_agent_report = self.coding_agent.execute_task(task)
                self.receive_coding_agent_report(
                    coding_agent_report["task_id"],
                    coding_agent_report["status"],
                    output=coding_agent_report.get("output"),
                    error=coding_agent_report.get("error")
                )
                return {"status": "dispatched_and_processed", "task": task, "coding_agent_report": coding_agent_report}
            else:
                logger.error(f"Failed to set current task for dispatch: {task['task_id']}")
                return {"status": "failed_dispatch", "message": str(result)}

        # ... existing code ...

        def run_orchestration_loop(self):
            logger.info("Starting Gatekeeper orchestration loop.")
            while True:
                current_status = self.enforcer.get_status()
                logger.info(f"Gatekeeper Status: {current_status}")

                if current_status["current_task"] is None:
                    next_task = self.get_next_task_for_coding_agent()
                    if next_task:
                        self.dispatch_task_to_coding_agent(next_task)
                        # After dispatching and processing, loop again to check for next task
                        # This makes the loop run until no more tasks are pending or a task is blocked
                        continue
                    else:
                        logger.info("No pending tasks. Project might be complete or blocked.")
                        break
                else:
                    logger.info(f"Current task {current_status['current_task']['id']} is in progress. Waiting for report (already processed in dispatch). Looping again to check next task.")
                    # If current_task is not None, it means it was just dispatched and processed
                    # We can immediately check for the next task in the next iteration
                    continue

    # Update the example usage in __main__ to reflect the new flow
    if __name__ == "__main__":
        setup_logging(log_file=Path("gatekeeper_main.log"), level=logging.DEBUG)

        sample_plan = [
            {
                "task_id": "GK1.1",
                "title": "Gatekeeper: Initialize project",
                "description": "Set up the initial project structure.",
                "status": "pending",
                "dependencies": [],
                "risk_level": "low",
                "output_expected": "Project structure created",
                "validation_criteria": "Manual check",
                "agent_instructions": "Simulate creating basic project directories and files."
            },
            {
                "task_id": "CA1.1",
                "title": "Coding Agent: Implement basic file operations",
                "description": "Write a Python function to create and write to a file.",
                "status": "pending",
                "dependencies": ["GK1.1"],
                "risk_level": "medium",
                "output_expected": "file_utils.py with create_file function",
                "validation_criteria": "Unit tests",
                "agent_instructions": "Simulate creating src/supermanus/utils/file_utils.py and adding a function `create_file(path, content)`."
            },
            {
                "task_id": "CA1.2",
                "title": "Coding Agent: Implement basic read operations",
                "description": "Write a Python function to read from a file.",
                "status": "pending",
                "dependencies": ["CA1.1"],
                "risk_level": "medium",
                "output_expected": "file_utils.py with read_file function",
                "validation_criteria": "Unit tests",
                "agent_instructions": "Simulate adding a function `read_file(path)` to src/supermanus/utils/file_utils.py."
            }
        ]

        gatekeeper = GatekeeperAgent()
        gatekeeper.load_project_plan(sample_plan)

        # Run the orchestration loop
        gatekeeper.run_orchestration_loop()

        print("\nFinal Gatekeeper Status after loop:")
        print(gatekeeper.enforcer.get_status())
        print("Full Project Tasks:")
        for task in gatekeeper.enforcer.project_tasks:
            print(f"  - {task['task_id']}: {task['status']}")

        # To test a blocked scenario, you could manually change a task status to 'blocked' in session_state.json
        # or modify the CodingAgent to sometimes fail.
    ```
5.  **Commit `gatekeeper_agent.py`:**
    ```bash
    git add src/supermanus/gatekeeper_agent.py
    git commit -m "Integrated Coding Agent into Gatekeeper orchestration loop"
    ```

### 7.4. Phase 4: Basic Tooling for Coding Agent

This phase focuses on giving the Coding Agent actual capabilities to interact with the file system.

#### Task 7.4.1: Implement `file_utils.py`

**Goal:** Create a utility module for file system operations that the Coding Agent can use.

**Actionable Steps:**
1.  **Create `utils` Directory:** Create a new directory `src/supermanus/utils`.
    ```bash
    mkdir src/supermanus/utils
    touch src/supermanus/utils/__init__.py
    ```
2.  **Create `file_utils.py`:** Create a new file `src/supermanus/utils/file_utils.py`.
3.  **Add File Operations:** Implement `create_file` and `read_file` functions.
    ```python
    # src/supermanus/utils/file_utils.py
    from pathlib import Path
    import logging

    logger = logging.getLogger(__name__)

    def create_file(path: Path, content: str):
        """Creates a file at the given path with the specified content."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            logger.info(f"Created/wrote file: {path}")
        except Exception as e:
            logger.error(f"Error creating/writing file {path}: {e}", exc_info=True)
            raise

    def read_file(path: Path) -> str:
        """Reads and returns the content of a file at the given path."""
        try:
            if not path.exists():
                logger.warning(f"File not found: {path}")
                return ""
            content = path.read_text()
            logger.info(f"Read file: {path}")
            return content
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}", exc_info=True)
            raise

    # Add more file utilities as needed (e.g., append_to_file, delete_file, list_directory)
    ```
4.  **Commit `file_utils.py`:**
    ```bash
    git add src/supermanus/utils/file_utils.py src/supermanus/utils/__init__.py
    git commit -m "Implemented basic file utilities for Coding Agent"
    ```

#### Task 7.4.2: Integrate `file_utils` into `coding_agent.py`

**Goal:** Enable the Coding Agent to use the new file utilities.

**Actionable Steps:**
1.  **Modify `coding_agent.py`:** Open `src/supermanus/coding_agent.py`.
2.  **Import `file_utils`:** Add the import statement:
    ```python
    from .utils import file_utils
    ```
3.  **Update `execute_task` to use `file_utils`:** Modify the `execute_task` method to conditionally call `file_utils` based on the `agent_instructions`. This will require some basic instruction parsing.
    ```python
    # src/supermanus/coding_agent.py (excerpt)
    # ... existing imports ...
    from .utils import file_utils # Add this import

    class CodingAgent:
        # ... existing __init__ ...

        def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
            task_id = task["task_id"]
            instructions = task["agent_instructions"]
            title = task["title"]

            logger.info(f"Coding Agent received task: {task_id} - {title}")
            logger.info(f"Instructions: {instructions}")

            try:
                with LLMActionGuard(f"Execute task {task_id}", justification=f"Working on {title}"):
                    logger.info(f"Starting work for task {task_id}...")
                    actual_output = ""

                    # --- Basic Instruction Parsing and Tool Usage --- #
                    if "create a new file" in instructions.lower() and "file_utils.py" in instructions.lower():
                        # This is a very simple parser. A real LLM would do this more intelligently.
                        file_path_str = "src/supermanus/utils/file_utils.py"
                        file_content = "# This is a placeholder for file_utils.py\n" \
                                       "from pathlib import Path\n" \
                                       "\n" \
                                       "def create_file(path: Path, content: str):\n" \
                                       "    path.parent.mkdir(parents=True, exist_ok=True)\n" \
                                       "    path.write_text(content)\n" \
                                       "\n" \
                                       "def read_file(path: Path) -> str:\n" \
                                       "    if not path.exists(): return \"\"\n" \
                                       "    return path.read_text()\n"
                        file_utils.create_file(self.project_root / file_path_str, file_content)
                        actual_output = f"Created {file_path_str}"

                    elif "add a function `read_file`" in instructions.lower() and "file_utils.py" in instructions.lower():
                        file_path_str = "src/supermanus/utils/file_utils.py"
                        current_content = file_utils.read_file(self.project_root / file_path_str)
                        # Simple append for demonstration. Real LLM would edit intelligently.
                        new_content = current_content + "\n# Added by Coding Agent\n" \
                                      "def read_file_new(path: Path) -> str:\n" \
                                      "    return path.read_text()\n"
                        file_utils.create_file(self.project_root / file_path_str, new_content)
                        actual_output = f"Added read_file_new to {file_path_str}"

                    else:
                        logger.warning(f"Coding Agent doesn't know how to handle instructions: {instructions}")
                        actual_output = f"Simulated execution of task {task_id}. No specific file operations performed."

                    logger.info(f"Work for task {task_id} completed.")

                return {"status": "completed", "task_id": task_id, "output": actual_output}

            # ... existing exception handling ...
    ```
4.  **Update `project_plan_template.json`:** Adjust the `agent_instructions` for tasks `P2.1` and `P2.2` to match the simple parsing logic implemented in `coding_agent.py`.
    ```json
    // ... (inside project_plan_template.json)
    {
        "task_id": "P2.1",
        "title": "Implement basic file creation utility",
        "description": "Write a Python function to create and write content to a file.",
        "status": "pending",
        "assigned_to": "Coding Agent",
        "dependencies": ["P1.3"],
        "risk_level": "low",
        "output_expected": "src/supermanus/utils/file_utils.py with create_file function",
        "validation_criteria": "Unit tests",
        "agent_instructions": "Coding Agent: create a new file `src/supermanus/utils/file_utils.py` and add a function `create_file(path, content)` that creates a file at `path` with `content`."
    },
    {
        "task_id": "P2.2",
        "title": "Implement basic file reading utility",
        "description": "Write a Python function to read content from a file.",
        "status": "pending",
        "assigned_to": "Coding Agent",
        "dependencies": ["P2.1"],
        "risk_level": "low",
        "output_expected": "src/supermanus/utils/file_utils.py with read_file function",
        "validation_criteria": "Unit tests",
        "agent_instructions": "Coding Agent: add a function `read_file(path)` to `src/supermanus/utils/file_utils.py` that reads and returns the content of a file at `path`."
    }
    // ...
    ```
5.  **Commit Changes:**
    ```bash
    git add src/supermanus/coding_agent.py project_plan_template.json
    git commit -m "Integrated file_utils into Coding Agent and updated plan instructions"
    ```

### 7.5. Phase 5: Testing Framework and Initial Tests

This phase focuses on setting up the testing infrastructure and writing initial tests for the core components.

#### Task 7.5.1: Set Up `tests` Directory and `conftest.py`

**Goal:** Create the test directory and a `conftest.py` for shared fixtures.

**Actionable Steps:**
1.  **Create `tests` Directory:** In the project root, create the `tests` directory:
    ```bash
    mkdir tests
    ```
2.  **Create `conftest.py`:** Create a new file `tests/conftest.py`. This file will hold fixtures that can be shared across multiple test files.
    ```python
    # tests/conftest.py
    import pytest
    from pathlib import Path
    import json
    import shutil

    # Define a temporary project root for tests
    @pytest.fixture
    def temp_project_root(tmp_path: Path) -> Path:
        # Create a dummy session_state.json for tests
        session_data = {
            "project_name": "Test Project",
            "current_phase": "",
            "tasks": [],
            "validation_history": []
        }
        (tmp_path / "session_state.json").write_text(json.dumps(session_data, indent=2))

        # Create work_logs directory
        (tmp_path / "work_logs").mkdir()

        # Create src/supermanus structure
        (tmp_path / "src" / "supermanus").mkdir(parents=True)
        (tmp_path / "src" / "supermanus" / "__init__.py").touch()
        (tmp_path / "src" / "supermanus" / "utils").mkdir()
        (tmp_path / "src" / "supermanus" / "utils" / "__init__.py").touch()

        # Ensure the current working directory is temporarily set to tmp_path
        # This is important for get_enforcer() which defaults to Path(".")
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(tmp_path)
            yield tmp_path
        finally:
            os.chdir(original_cwd)

    # Fixture to reset the global enforcer instance for each test
    @pytest.fixture(autouse=True)
    def reset_enforcer_instance():
        from src.supermanus.task_enforcer import _enforcer_instance
        _enforcer_instance = None
        yield
        _enforcer_instance = None

    # Fixture for a sample project plan
    @pytest.fixture
    def sample_project_plan() -> List[Dict[str, Any]]:
        return [
            {
                "task_id": "T1.1",
                "title": "Implement feature A",
                "description": "Description for A",
                "status": "pending",
                "dependencies": [],
                "risk_level": "low",
                "output_expected": "Code for A",
                "validation_criteria": "Unit tests",
                "agent_instructions": "Implement feature A."
            },
            {
                "task_id": "T1.2",
                "title": "Implement feature B",
                "description": "Description for B",
                "status": "pending",
                "dependencies": ["T1.1"],
                "risk_level": "medium",
                "output_expected": "Code for B",
                "validation_criteria": "Integration tests",
                "agent_instructions": "Implement feature B, depends on A."
            }
        ]
    ```
3.  **Commit Test Setup:**
    ```bash
    git add tests/ tests/conftest.py
    git commit -m "Setup tests directory and conftest.py for fixtures"
    ```

#### Task 7.5.2: Write Unit Tests for `session_manager.py`

**Goal:** Ensure the `SessionManager` correctly loads and saves state.

**Actionable Steps:**
1.  **Create `test_session_manager.py`:** Create a new file `tests/test_session_manager.py`.
2.  **Add Tests:** Write tests using `pytest` and the `tmp_path` fixture.
    ```python
    # tests/test_session_manager.py
    from pathlib import Path
    import json
    from src.supermanus.session_manager import SessionManager

    def test_session_manager_initial_load(tmp_path: Path):
        session_file = tmp_path / "test_session.json"
        manager = SessionManager(session_file)
        state = manager.load_state()
        assert state["project_name"] == "LLM Dev Agent Project"
        assert state["tasks"] == []
        assert not session_file.exists() # Should not create file on load if not exists

    def test_session_manager_save_and_load(tmp_path: Path):
        session_file = tmp_path / "test_session.json"
        manager = SessionManager(session_file)

        initial_state = manager.load_state()
        initial_state["project_name"] = "New Project"
        initial_state["tasks"].append({"id": "T1", "title": "Task 1"})
        manager.save_state(initial_state)

        assert session_file.exists()
        loaded_state = manager.load_state()
        assert loaded_state["project_name"] == "New Project"
        assert len(loaded_state["tasks"]) == 1
        assert loaded_state["tasks"][0]["id"] == "T1"

    def test_session_manager_existing_file(tmp_path: Path):
        session_file = tmp_path / "existing_session.json"
        existing_data = {"project_name": "Existing", "tasks": [{"id": "E1"}]}
        session_file.write_text(json.dumps(existing_data))

        manager = SessionManager(session_file)
        state = manager.load_state()
        assert state["project_name"] == "Existing"
        assert len(state["tasks"]) == 1
    ```
3.  **Run Tests:** In the terminal, run `pytest` from the project root:
    ```bash
    pytest tests/test_session_manager.py
    ```
    (You should see all tests pass.)
4.  **Commit Tests:**
    ```bash
    git add tests/test_session_manager.py
    git commit -m "Added unit tests for session_manager"
    ```

#### Task 7.5.3: Write Unit Tests for `task_enforcer.py` (Basic)

**Goal:** Ensure the core `TaskSystemEnforcer` functionalities work as expected.

**Actionable Steps:**
1.  **Create `test_task_enforcer.py`:** Create a new file `tests/test_task_enforcer.py`.
2.  **Add Tests:** Write tests for task selection, work log, and basic action validation.
    ```python
    # tests/test_task_enforcer.py
    import pytest
    from pathlib import Path
    from src.supermanus.task_enforcer import TaskSystemEnforcer, ValidationResult, TaskRiskLevel
    from src.supermanus.session_manager import SessionManager

    def test_enforcer_initialization(temp_project_root: Path):
        enforcer = TaskSystemEnforcer(temp_project_root)
        assert enforcer.project_root == temp_project_root
        assert enforcer.current_task is None
        assert not enforcer.work_log_active
        assert enforcer.validation_history == []

    def test_enforcer_load_and_save_state(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        enforcer.set_current_task("T1.1")
        enforcer.start_work_log()
        enforcer.validate_action("test action", "justification for test action")

        # Re-initialize enforcer to load saved state
        new_enforcer = TaskSystemEnforcer(temp_project_root)
        assert new_enforcer.current_task["id"] == "T1.1"
        assert new_enforcer.work_log_active
        assert len(new_enforcer.validation_history) == 1
        assert len(new_enforcer.project_tasks) == 2

    def test_get_active_tasks(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        active_tasks = enforcer.get_active_tasks()
        assert len(active_tasks) == 2
        assert "T1.1" in active_tasks
        assert "T1.2" in active_tasks

        # Mark one task complete and re-check
        enforcer.set_current_task("T1.1")
        enforcer.start_work_log()
        enforcer.validate_completion({"mock_proof": True})
        active_tasks_after_completion = enforcer.get_active_tasks()
        assert len(active_tasks_after_completion) == 1
        assert "T1.1" not in active_tasks_after_completion
        assert "T1.2" in active_tasks_after_completion

    def test_set_current_task(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)

        result = enforcer.set_current_task("T1.1")
        assert result == ValidationResult.APPROVED
        assert enforcer.current_task["id"] == "T1.1"

        # Test invalid task
        result_invalid = enforcer.set_current_task("INVALID_TASK")
        assert result_invalid == ValidationResult.BLOCKED

    def test_require_work_log(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        enforcer.set_current_task("T1.1")

        # Should require work log initially
        assert "WORK LOG REQUIRED" in enforcer.require_work_log()

        enforcer.start_work_log()
        assert "Work log active" in enforcer.require_work_log()

    def test_validate_action_success(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        enforcer.set_current_task("T1.1")
        enforcer.start_work_log()

        result, msg = enforcer.validate_action("Write code", "Implementing feature A as per task T1.1")
        assert result == ValidationResult.APPROVED
        assert "Action approved" in msg
        assert len(enforcer.validation_history) == 1

    def test_validate_action_no_justification(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        enforcer.set_current_task("T1.1")
        enforcer.start_work_log()

        result, msg = enforcer.validate_action("Write code", "")
        assert result == ValidationResult.REJECTED
        assert "Insufficient justification" in msg

    def test_validate_action_irrelevant_justification(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        enforcer.set_current_task("T1.1")
        enforcer.start_work_log()

        result, msg = enforcer.validate_action("Write code", "Just doing some random stuff unrelated to anything.")
        assert result == ValidationResult.REJECTED
        assert "Justification must explain connection to task" in msg

    def test_validate_completion_low_risk(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        enforcer.set_current_task("T1.1") # Low risk
        enforcer.start_work_log()

        proof = {
            "file_evidence": "mock_evidence",
            "functional_test": "mock_test_output",
            "error_check": "no errors"
        }
        result, msg = enforcer.validate_completion(proof)
        assert result == ValidationResult.APPROVED
        assert "Task completion validated and approved" in msg
        assert enforcer.current_task is None # Task should be marked complete

    def test_validate_completion_high_risk_pending(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        # Manually set a high-risk task
        high_risk_plan = [
            {
                "task_id": "T_HIGH",
                "title": "Deploy to Production",
                "description": "Deploy the application to production environment.",
                "status": "pending",
                "dependencies": [],
                "risk_level": "high",
                "output_expected": "Application live",
                "validation_criteria": "Human review"
            }
        ]
        enforcer.update_project_plan(high_risk_plan)
        enforcer.set_current_task("T_HIGH")
        enforcer.start_work_log()

        proof = {
            "file_evidence": "mock_evidence",
            "functional_test": "mock_test_output",
            "error_check": "no errors",
            "comprehensive_testing": "full suite passed",
            "security_check": "passed",
            "human_review_required": "pending"
        }
        result, msg = enforcer.validate_completion(proof)
        assert result == ValidationResult.PENDING
        assert "High-risk task requires human approval" in msg
        assert enforcer.current_task is not None # Task should still be active

    def test_validate_completion_missing_proof(temp_project_root: Path, sample_project_plan):
        enforcer = TaskSystemEnforcer(temp_project_root)
        enforcer.update_project_plan(sample_project_plan)
        enforcer.set_current_task("T1.1")
        enforcer.start_work_log()

        proof = {"file_evidence": "mock_evidence"} # Missing functional_test, error_check
        result, msg = enforcer.validate_completion(proof)
        assert result == ValidationResult.REJECTED
        assert "Missing proof for" in msg
    ```
3.  **Run Tests:**
    ```bash
    pytest tests/test_task_enforcer.py
    ```
    (You should see all tests pass.)
4.  **Commit Tests:**
    ```bash
    git add tests/test_task_enforcer.py
    git commit -m "Added basic unit tests for task_enforcer"
    ```

### 7.6. Phase 6: Human Interaction Layer (HIL) - Command Line Interface (CLI)

This phase focuses on building a basic command-line interface for the Gatekeeper Agent, allowing the user to interact with the system.

#### Task 7.6.1: Create `main.py` for CLI Interaction

**Goal:** Create a main entry point for the application that allows basic interaction with the Gatekeeper.

**Actionable Steps:**
1.  **Create `main.py`:** Create a new file `main.py` in the project root.
2.  **Implement CLI Logic:** Use `argparse` for command-line arguments to load a plan, get status, and potentially dispatch tasks.
    ```python
    # main.py
    import argparse
    import json
    from pathlib import Path
    from src.supermanus.gatekeeper_agent import GatekeeperAgent
    from src.supermanus.logging_config import setup_logging

    def main():
        parser = argparse.ArgumentParser(description="SuperManUS LLM Dev Agent CLI.")
        parser.add_argument("--project_root", type=str, default=".",
                            help="Root directory of the project. Defaults to current directory.")
        parser.add_argument("--log_level", type=str, default="INFO",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                            help="Set the logging level.")

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Command: init
        init_parser = subparsers.add_parser("init", help="Initialize a new project with a plan.")
        init_parser.add_argument("--plan_file", type=str, required=True,
                                 help="Path to the JSON file containing the project plan.")

        # Command: status
        status_parser = subparsers.add_parser("status", help="Get current project status.")

        # Command: run
        run_parser = subparsers.add_parser("run", help="Run the Gatekeeper orchestration loop.")

        # Command: complete_task (for human simulation)
        complete_parser = subparsers.add_parser("complete_task", help="Simulate completion of a task.")
        complete_parser.add_argument("--task_id", type=str, required=True,
                                     help="ID of the task to mark as completed.")
        complete_parser.add_argument("--status", type=str, default="completed",
                                     choices=["completed", "failed"],
                                     help="Status of the task completion (completed or failed).")
        complete_parser.add_argument("--output", type=str, default="",
                                     help="Output from the simulated task.")
        complete_parser.add_argument("--error", type=str, default="",
                                     help="Error message if task failed.")

        args = parser.parse_args()

        project_root_path = Path(args.project_root).resolve()
        setup_logging(log_file=project_root_path / "app.log", level=getattr(logging, args.log_level.upper()))

        gatekeeper = GatekeeperAgent(project_root=project_root_path)

        if args.command == "init":
            plan_file_path = Path(args.plan_file).resolve()
            if not plan_file_path.exists():
                print(f"Error: Plan file not found at {plan_file_path}")
                return
            with open(plan_file_path, 'r') as f:
                plan_data = json.load(f)
            gatekeeper.load_project_plan(plan_data)
            print(f"Project initialized with plan from {plan_file_path}")
            print("Run 'python main.py status' to see current state.")
            print("Run 'python main.py run' to start orchestration.")

        elif args.command == "status":
            status = gatekeeper.enforcer.get_status()
            print("\n--- Current Project Status ---")
            print(f"Project Root: {gatekeeper.project_root}")
            print(f"Current Task: {status['current_task']['id'] if status['current_task'] else 'None'}")
            print(f"Work Log Active: {status['work_log_active']}")
            print(f"Active Tasks Remaining: {status['active_tasks_available']}")
            print(f"Validation History Entries: {status['validation_history_count']}")
            print("\n--- Project Plan Tasks ---")
            for task in gatekeeper.enforcer.project_tasks:
                print(f"  - {task['task_id']}: {task['title']} (Status: {task['status']})")
            print("--------------------------")

        elif args.command == "run":
            print("Starting Gatekeeper orchestration loop...")
            gatekeeper.run_orchestration_loop()
            print("Gatekeeper orchestration loop finished.")
            print("Run 'python main.py status' to see updated state.")

        elif args.command == "complete_task":
            gatekeeper.receive_coding_agent_report(
                args.task_id,
                args.status,
                output=args.output if args.output else None,
                error=args.error if args.error else None
            )
            print(f"Simulated report for task {args.task_id} with status '{args.status}'.")
            print("Run 'python main.py status' to see updated state.")

        else:
            parser.print_help()

    if __name__ == "__main__":
        main()
    ```
3.  **Test CLI:**
    *   **Initialize a project:**
        ```bash
        python main.py init --plan_file project_plan_template.json
        ```
    *   **Check status:**
        ```bash
        python main.py status
        ```
    *   **Run orchestration (will dispatch GK1.1):**
        ```bash
        python main.py run
        ```
    *   **Check status again (GK1.1 should be in_progress):**
        ```bash
        python main.py status
        ```
    *   **Simulate GK1.1 completion:**
        ```bash
        python main.py complete_task --task_id GK1.1 --status completed --output "Project initialized."
        ```
    *   **Run orchestration again (CA1.1 should be dispatched and processed):**
        ```bash
        python main.py run
        ```
    *   **Check status (CA1.1 should be completed):**
        ```bash
        python main.py status
        ```
4.  **Commit `main.py`:**
    ```bash
    git add main.py
    git commit -m "Implemented basic CLI for Gatekeeper interaction"
    ```

### 7.7. Phase 7: Advanced Coding Agent Tooling and LLM Integration

This phase focuses on making the Coding Agent more capable by integrating actual LLM calls and a broader set of tools.

#### Task 7.7.1: Integrate OpenAI API for Code Generation

**Goal:** Enable the Coding Agent to use an LLM (e.g., OpenAI's GPT models) to generate code based on instructions.

**Actionable Steps:**
1.  **Install OpenAI Library:**
    ```bash
    pip install openai
    pip freeze > requirements.txt
    git add requirements.txt
    git commit -m "Added openai to dependencies"
    ```
2.  **Set Up OpenAI API Key:** Ensure your `OPENAI_API_KEY` is set as an environment variable. For local development, you can create a `.env` file in your project root and load it (e.g., using `python-dotenv`).
    ```
    # .env
    OPENAI_API_KEY="your_openai_api_key_here"
    ```
    (Remember to add `.env` to your `.gitignore` if you haven't already.)
3.  **Create `llm_tools.py`:** Create a new file `src/supermanus/llm_tools.py`.
4.  **Implement LLM Code Generation:**
    ```python
    # src/supermanus/llm_tools.py
    import os
    import logging
    from openai import OpenAI

    logger = logging.getLogger(__name__)

    class LLMTools:
        def __init__(self):
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            if not self.client.api_key:
                logger.error("OPENAI_API_KEY environment variable not set.")
                raise ValueError("OPENAI_API_KEY is required for LLMTools.")

        def generate_code(self, prompt: str, temperature: float = 0.7, model: str = "gpt-4") -> str:
            """Generates code based on a given prompt using an LLM."""
            try:
                logger.info(f"Generating code with model {model} for prompt: {prompt[:100]}...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful coding assistant. Provide only code unless explicitly asked for explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                )
                code = response.choices[0].message.content.strip()
                logger.info("Code generation successful.")
                return code
            except Exception as e:
                logger.error(f"Error generating code: {e}", exc_info=True)
                raise

        # Add other LLM-based tools here (e.g., generate_documentation, analyze_code, summarize_text)

    # Example usage (for testing)
    if __name__ == "__main__":
        from dotenv import load_dotenv
        load_dotenv() # Load .env file
        from .logging_config import setup_logging
        setup_logging()

        llm_tools = LLMTools()
        code_prompt = "Write a Python function `add(a, b)` that returns the sum of two numbers."
        generated_code = llm_tools.generate_code(code_prompt)
        print(f"\nGenerated Code:\n{generated_code}")
    ```
5.  **Modify `coding_agent.py` to use `llm_tools`:**
    ```python
    # src/supermanus/coding_agent.py (excerpt)
    # ... existing imports ...
    from .llm_tools import LLMTools # Add this import

    class CodingAgent:
        def __init__(self, project_root: Path = Path(".")):
            # ... existing code ...
            self.llm_tools = LLMTools() # Instantiate LLMTools
            logger.info("Coding Agent initialized.")

        def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
            # ... existing code ...

            try:
                with LLMActionGuard(f"Execute task {task_id}", justification=f"Working on {title}"):
                    logger.info(f"Starting work for task {task_id}...")
                    actual_output = ""

                    # --- Enhanced Instruction Parsing and Tool Usage --- #
                    if "create a new file" in instructions.lower() and "file_utils.py" in instructions.lower() and "create_file" in instructions.lower():
                        file_path_str = "src/supermanus/utils/file_utils.py"
                        # Use LLM to generate the initial content for file_utils.py
                        code_prompt = f"Write a Python module for file utilities. Include a function `create_file(path: Path, content: str)` that creates a file at the given `path` and writes the `content` to it. Ensure necessary parent directories are created. Use `pathlib` for path manipulation. Also include a function `read_file(path: Path) -> str` that reads and returns the entire content of the file at the given `path`. Handle `FileNotFoundError` gracefully by returning an empty string. Provide only the Python code, no explanations."
                        generated_code = self.llm_tools.generate_code(code_prompt)
                        file_utils.create_file(self.project_root / file_path_str, generated_code)
                        actual_output = f"Created {file_path_str} with LLM-generated code."

                    elif "add a function `read_file`" in instructions.lower() and "file_utils.py" in instructions.lower():
                        file_path_str = "src/supermanus/utils/file_utils.py"
                        current_content = file_utils.read_file(self.project_root / file_path_str)
                        # Use LLM to generate the read_file function and integrate it
                        code_prompt = f"Given the following Python code for file_utils.py:\n```python\n{current_content}\n```\nAdd or update a function `read_file(path: Path) -> str` that reads and returns the entire content of the file at the given `path`. Handle `FileNotFoundError` gracefully by returning an empty string. Ensure the module remains valid Python code. Provide only the updated Python code, no explanations."
                        updated_code = self.llm_tools.generate_code(code_prompt)
                        file_utils.create_file(self.project_root / file_path_str, updated_code)
                        actual_output = f"Updated {file_path_str} with LLM-generated read_file function."

                    else:
                        logger.warning(f"Coding Agent doesn't have specific tool for instructions: {instructions}. Simulating.")
                        time.sleep(1) # Simulate some thinking time
                        actual_output = f"Simulated execution of task {task_id}. No specific LLM operations performed."

                    logger.info(f"Work for task {task_id} completed.")

                return {"status": "completed", "task_id": task_id, "output": actual_output}

            # ... existing exception handling ...
    ```
6.  **Update `project_plan_template.json`:** Adjust `agent_instructions` for `P2.1` and `P2.2` to be more generic, allowing the LLM to interpret them.
    ```json
    // ... (inside project_plan_template.json)
    {
        "task_id": "P2.1",
        "title": "Implement basic file creation utility",
        "description": "Write a Python function to create and write content to a file.",
        "status": "pending",
        "assigned_to": "Coding Agent",
        "dependencies": ["P1.3"],
        "risk_level": "low",
        "output_expected": "src/supermanus/utils/file_utils.py with create_file function",
        "validation_criteria": "Unit tests",
        "agent_instructions": "Implement a Python module `src/supermanus/utils/file_utils.py` with a function `create_file(path: Path, content: str)` that creates a file at the given `path` and writes the `content` to it. Ensure necessary parent directories are created. Use `pathlib` for path manipulation."
    },
    {
        "task_id": "P2.2",
        "title": "Implement basic file reading utility",
        "description": "Write a Python function to read content from a file.",
        "status": "pending",
        "assigned_to": "Coding Agent",
        "dependencies": ["P2.1"],
        "risk_level": "low",
        "output_expected": "src/supermanus/utils/file_utils.py with read_file function",
        "validation_criteria": "Unit tests",
        "agent_instructions": "Add a function `read_file(path: Path) -> str` to `src/supermanus/utils/file_utils.py` that reads and returns the entire content of the file at the given `path`. Handle `FileNotFoundError` gracefully by returning an empty string."
    }
    // ...
    ```
7.  **Commit Changes:**
    ```bash
    git add src/supermanus/llm_tools.py src/supermanus/coding_agent.py project_plan_template.json
    git commit -m "Integrated OpenAI LLM for code generation into Coding Agent"
    ```

### 7.8. Phase 8: Advanced Features and Integrations

This phase covers more advanced aspects, including a more robust HIL and integration considerations.

#### Task 7.8.1: Implement a More Robust Human Interaction Layer (HIL) - Web UI (Flask)

**Goal:** Create a simple web-based UI for the Gatekeeper, allowing for easier interaction than the CLI.

**Actionable Steps:**
1.  **Install Flask:**
    ```bash
    pip install Flask
    pip freeze > requirements.txt
    git add requirements.txt
    git commit -m "Added Flask to dependencies"
    ```
2.  **Create `app.py`:** Create a new file `app.py` in the project root.
3.  **Implement Flask App:** This will expose API endpoints for the Gatekeeper and serve a simple frontend.
    ```python
    # app.py
    from flask import Flask, request, jsonify, render_template_string
    from pathlib import Path
    import logging
    import json

    from src.supermanus.gatekeeper_agent import GatekeeperAgent
    from src.supermanus.logging_config import setup_logging

    # Setup logging for the Flask app
    project_root = Path(".").resolve()
    setup_logging(log_file=project_root / "web_app.log", level=logging.INFO)
    logger = logging.getLogger(__name__)

    app = Flask(__name__)
    gatekeeper = GatekeeperAgent(project_root=project_root)

    # Simple HTML template for the UI
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SuperManUS Dev Agent</title>
        <style>
            body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
            .container { max-width: 900px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1, h2 { color: #0056b3; }
            pre { background: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
            button { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-right: 10px; }
            button:hover { background-color: #0056b3; }
            .task-list { list-style: none; padding: 0; }
            .task-item { background: #e9ecef; margin-bottom: 8px; padding: 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
            .task-item.completed { background: #d4edda; }
            .task-item.in_progress { background: #fff3cd; }
            .task-item.blocked { background: #f8d7da; }
            .task-status { font-weight: bold; }
            .log-entry { background: #f8f9fa; padding: 5px; margin-bottom: 3px; border-radius: 3px; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SuperManUS LLM Dev Agent</h1>
            <p>This is a simple web interface to interact with the Gatekeeper Agent.</p>

            <h2>Project Control</h2>
            <button onclick="initProject()">Initialize Project (from project_plan_template.json)</button>
            <button onclick="runOrchestration()">Run Orchestration Loop</button>
            <button onclick="getStatus()">Refresh Status</button>

            <h2>Current Status</h2>
            <pre id="status-display">Loading status...</pre>

            <h2>Project Tasks</h2>
            <ul id="tasks-list" class="task-list"></ul>

            <h2>Gatekeeper Log</h2>
            <div id="log-display" style="max-height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; background: #fdfdfd;"></div>

        </div>

        <script>
            const statusDisplay = document.getElementById('status-display');
            const tasksList = document.getElementById('tasks-list');
            const logDisplay = document.getElementById('log-display');

            async function fetchData(url, method = 'GET', body = null) {
                const options = {
                    method: method,
                    headers: { 'Content-Type': 'application/json' }
                };
                if (body) {
                    options.body = JSON.stringify(body);
                }
                const response = await fetch(url, options);
                return response.json();
            }

            async function getStatus() {
                const status = await fetchData('/api/status');
                statusDisplay.textContent = JSON.stringify(status, null, 2);

                tasksList.innerHTML = '';
                if (status.project_tasks) {
                    status.project_tasks.forEach(task => {
                        const li = document.createElement('li');
                        li.className = `task-item ${task.status}`;
                        li.innerHTML = `
                            <span><strong>${task.task_id}:</strong> ${task.title}</span>
                            <span class="task-status">Status: ${task.status}</span>
                        `;
                        tasksList.appendChild(li);
                    });
                }

                // Fetch and display logs (simple way, for real-time use websockets)
                const logContent = await fetchData('/api/logs');
                logDisplay.innerHTML = logContent.split('\n').map(line => `<div class="log-entry">${line}</div>`).join('');
                logDisplay.scrollTop = logDisplay.scrollHeight; // Scroll to bottom
            }

            async function initProject() {
                const planFile = 'project_plan_template.json'; // Assuming this file exists in root
                const result = await fetchData('/api/init_project', 'POST', { plan_file: planFile });
                alert(result.message);
                getStatus();
            }

            async function runOrchestration() {
                const result = await fetchData('/api/run_orchestration', 'POST');
                alert(result.message);
                getStatus();
            }

            // Initial status load
            getStatus();
            // Refresh status every 5 seconds
            setInterval(getStatus, 5000);

        </script>
    </body>
    </html>
    """

    @app.route('/')
    def index():
        return render_template_string(HTML_TEMPLATE)

    @app.route('/api/status', methods=['GET'])
    def get_current_status():
        status = gatekeeper.enforcer.get_status()
        # Include project tasks for display
        status["project_tasks"] = gatekeeper.enforcer.project_tasks
        return jsonify(status)

    @app.route('/api/init_project', methods=['POST'])
    def init_project():
        data = request.get_json()
        plan_file = data.get('plan_file')
        if not plan_file:
            return jsonify({"message": "plan_file is required"}), 400
        try:
            plan_file_path = project_root / plan_file
            if not plan_file_path.exists():
                return jsonify({"message": f"Plan file not found: {plan_file}"}), 404
            with open(plan_file_path, 'r') as f:
                plan_data = json.load(f)
            gatekeeper.load_project_plan(plan_data)
            return jsonify({"message": "Project initialized successfully."})
        except Exception as e:
            logger.error(f"Error initializing project: {e}", exc_info=True)
            return jsonify({"message": f"Error initializing project: {str(e)}"}), 500

    @app.route('/api/run_orchestration', methods=['POST'])
    def run_orchestration():
        try:
            gatekeeper.run_orchestration_loop()
            return jsonify({"message": "Orchestration loop initiated. Check logs for details."})
        except Exception as e:
            logger.error(f"Error running orchestration: {e}", exc_info=True)
            return jsonify({"message": f"Error running orchestration: {str(e)}"}), 500

    @app.route('/api/logs', methods=['GET'])
    def get_logs():
        log_file_path = project_root / "web_app.log"
        if log_file_path.exists():
            with open(log_file_path, 'r') as f:
                return f.read()
        return "No logs yet."

    if __name__ == '__main__':
        # To run this, use 'flask run' or 'python -m flask run'
        # For development, use 'flask --app app run --debug'
        app.run(debug=True)
    ```
4.  **Run Flask App:** In your terminal, make sure your virtual environment is active, then run:
    ```bash
    flask --app app run --debug
    ```
    (This will start the Flask development server, usually on `http://127.0.0.1:5000`. Open this URL in your browser.)
5.  **Test Web UI:** Interact with the buttons to initialize the project and run the orchestration loop. Observe the status and logs updating.
6.  **Commit `app.py`:**
    ```bash
    git add app.py
    git commit -m "Implemented basic Flask web UI for Gatekeeper HIL"
    ```

#### Task 7.8.2: VSCode Extension (Conceptual Outline)

**Goal:** Understand the conceptual steps for building a VSCode extension that interacts with your multi-agent system.

**Actionable Steps (Conceptual - not implemented in code in this plan):**
1.  **Learn VSCode Extension Development:** Familiarize yourself with TypeScript/JavaScript and the VSCode Extension API. The official VSCode documentation is the best resource.
2.  **Extension Project Setup:** Use the Yeoman generator for VSCode extensions (`yo code`) to scaffold a new extension project.
3.  **Communication Channel:** Decide on the communication method between the VSCode extension (frontend) and your Python Flask backend (Gatekeeper). Options include:
    *   **REST API Calls:** The extension makes HTTP requests to your Flask app.
    *   **WebSockets:** For real-time updates (e.g., live log streaming, task status changes).
    *   **VSCode Language Server Protocol (LSP):** If you want to provide rich language features (e.g., code completion, diagnostics) based on the agent's understanding.
4.  **Implement Custom Views:** Use VSCode's `webview` API to create custom HTML/CSS/JavaScript views within the sidebar or a custom editor to display the project plan, task status, and agent logs.
5.  **Command Palette Integration:** Register commands that trigger actions in your Python backend (e.g., 


triggering the orchestration loop, marking a task complete).
6.  **Contextual Information:** Display relevant files, code snippets, and diffs generated by the Coding Agent directly in the VSCode editor.

### 7.9. Phase 9: Advanced Error Handling and Robustness

This phase focuses on making the system more resilient to errors and providing better feedback mechanisms.

#### Task 7.9.1: Implement Centralized Error Handling and Reporting

**Goal:** Establish a consistent way to catch, log, and report errors across the entire system.

**Actionable Steps:**
1.  **Review Existing Error Handling:** Examine `llm_guard.py`, `task_enforcer.py`, `coding_agent.py`, and `gatekeeper_agent.py` for existing `try-except` blocks. Ensure they are logging errors appropriately.
2.  **Custom Exception Classes:** Define specific exception classes for different types of errors (e.g., `PlanParsingError`, `TaskExecutionError`, `ToolUsageError`). This makes error handling more granular.
    ```python
    # src/supermanus/exceptions.py
    class SuperManUSException(Exception):
        """Base exception for SuperManUS system."""
        pass

    class PlanParsingError(SuperManUSException):
        """Raised when there's an issue parsing the project plan."""
        pass

    class TaskExecutionError(SuperManUSException):
        """Raised when the Coding Agent fails to execute a task."""
        def __init__(self, message, task_id=None, original_exception=None):
            super().__init__(message)
            self.task_id = task_id
            self.original_exception = original_exception

    class ToolUsageError(SuperManUSException):
        """Raised when a tool used by the Coding Agent encounters an error."""
        def __init__(self, message, tool_name=None, original_exception=None):
            super().__init__(message)
            self.tool_name = tool_name
            self.original_exception = original_exception

    # Add more as needed, e.g., AgentCommunicationError, PersistenceError
    ```
3.  **Integrate Custom Exceptions:** Modify relevant parts of `gatekeeper_agent.py` and `coding_agent.py` to raise and catch these custom exceptions.
    *   **In `gatekeeper_agent.py`:** When `coding_agent.execute_task` returns a `failed` status, raise a `TaskExecutionError`.
    *   **In `coding_agent.py`:** When `LLMActionGuard` catches an exception or a tool fails, wrap it in a `ToolUsageError`.
4.  **Centralized Error Logging:** Ensure all exceptions are caught at a higher level (e.g., in `main.py` or `app.py`) and logged with `logger.exception()` for full stack traces.
5.  **Error Reporting to Gatekeeper:** When the Coding Agent encounters an error, ensure the `error` field in its report to the Gatekeeper is populated with a meaningful message and potentially the type of exception.
6.  **Gatekeeper Error Handling:** The Gatekeeper should use the error information to decide whether to retry the task, mark it as blocked, or flag it for human intervention.

#### Task 7.9.2: Implement Retries and Backoff for Transient Errors

**Goal:** Make the system more robust by automatically retrying operations that might fail due to transient issues (e.g., network glitches, API rate limits).

**Actionable Steps:**
1.  **Install `tenacity`:** A powerful library for retrying operations.
    ```bash
    pip install tenacity
    pip freeze > requirements.txt
    git add requirements.txt
    git commit -m "Added tenacity for retries"
    ```
2.  **Apply Retries to LLM Calls:** Modify `src/supermanus/llm_tools.py` to use `tenacity` for `generate_code` calls.
    ```python
    # src/supermanus/llm_tools.py (excerpt)
    # ... existing imports ...
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    from openai import OpenAI, OpenAIError # Import specific OpenAI errors
    from .exceptions import ToolUsageError # Import your custom exception

    class LLMTools:
        # ... existing __init__ ...

        @retry(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type(OpenAIError), # Retry on OpenAI specific errors
            reraise=True # Re-raise the last exception if all retries fail
        )
        def generate_code(self, prompt: str, temperature: float = 0.7, model: str = "gpt-4") -> str:
            """Generates code based on a given prompt using an LLM."""
            try:
                logger.info(f"Generating code with model {model} for prompt: {prompt[:100]}...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful coding assistant. Provide only code unless explicitly asked for explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                )
                code = response.choices[0].message.content.strip()
                logger.info("Code generation successful.")
                return code
            except OpenAIError as e:
                logger.error(f"OpenAI API error during code generation: {e}")
                raise # tenacity will catch and retry
            except Exception as e:
                logger.error(f"Unexpected error during code generation: {e}", exc_info=True)
                raise ToolUsageError(f"Failed to generate code: {e}", tool_name="OpenAI", original_exception=e)
    ```
3.  **Consider Retries for File Operations:** For very critical file operations, you might also consider adding retries, though typically file system operations are either immediately successful or fail definitively.

### 7.10. Phase 10: Monitoring and Observability

This phase focuses on providing better insights into the system's operation and performance.

#### Task 7.10.1: Enhance Logging with Structured Data

**Goal:** Make logs more parseable and useful for analysis by including structured data (e.g., JSON format).

**Actionable Steps:**
1.  **Install `python-json-logger`:**
    ```bash
    pip install python-json-logger
    pip freeze > requirements.txt
    git add requirements.txt
    git commit -m "Added python-json-logger"
    ```
2.  **Modify `logging_config.py`:** Update `setup_logging` to use `JsonFormatter`.
    ```python
    # src/supermanus/logging_config.py (excerpt)
    import logging
    from pathlib import Path
    from pythonjsonlogger import jsonlogger # Add this import

    def setup_logging(log_file: Path = Path("app.log"), level=logging.INFO, json_format: bool = False):
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Remove any existing handlers to prevent duplicate logs
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        handlers = [
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]

        if json_format:
            formatter = jsonlogger.JsonFormatter(
                '%(levelname)s %(asctime)s %(name)s %(message)s',
                json_ensure_ascii=False
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

        for handler in handlers:
            handler.setFormatter(formatter)
            logging.root.addHandler(handler)

        logging.root.setLevel(level)

        # Set a higher level for some noisy libraries if needed
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)

    # Example usage (for testing purposes)
    if __name__ == "__main__":
        log_path = Path("logs/test_app_json.log")
        setup_logging(log_path, logging.DEBUG, json_format=True)
        logger = logging.getLogger(__name__)
        logger.info("This is an info message with extra data", extra={"task_id": "T123", "agent": "Gatekeeper"})
        logger.error("An error occurred", extra={"error_code": 500, "component": "LLMTools"})

        log_path_text = Path("logs/test_app_text.log")
        setup_logging(log_path_text, logging.INFO, json_format=False)
        logger_text = logging.getLogger(__name__)
        logger_text.info("This is a regular text log.")
    ```
3.  **Update `main.py` and `app.py`:** Pass `json_format=True` to `setup_logging` when initializing.
    *   **In `main.py`:**
        ```python
        setup_logging(log_file=project_root_path / "app.log", level=getattr(logging, args.log_level.upper()), json_format=True)
        ```
    *   **In `app.py`:**
        ```python
        setup_logging(log_file=project_root / "web_app.log", level=logging.INFO, json_format=True)
        ```
4.  **Add `extra` to Log Calls:** Throughout your code, add `extra` dictionaries to log calls for relevant context (e.g., `task_id`, `agent_type`, `tool_used`).

#### Task 7.10.2: Implement Basic Metrics Collection

**Goal:** Collect simple metrics (e.g., task completion times, number of retries) to monitor system performance.

**Actionable Steps:**
1.  **Metrics Storage:** For simplicity, store metrics in the `session_state.json` or a separate metrics file. For production, consider a time-series database.
2.  **Modify `task_enforcer.py`:** Add fields to `current_task` and `validation_history` to store timing information.
    *   When `set_current_task` is called, record `start_time`.
    *   When `_mark_task_complete` is called, record `end_time` and calculate `duration`.
    *   In `validation_history`, record `validation_time`.
3.  **Modify `llm_tools.py`:** Record the number of retries for each LLM call.
    ```python
    # src/supermanus/llm_tools.py (excerpt)
    # ...
    @retry(
        # ... existing retry config ...
        after=lambda retry_state: logger.info(f"Retrying {retry_state.fn.__name__} (attempt {retry_state.attempt_number})...")
    )
    def generate_code(self, prompt: str, temperature: float = 0.7, model: str = "gpt-4") -> str:
        # ... existing code ...
        # You can access retry_state.attempt_number here if needed for metrics
        # For example, pass it back in a return value or log it explicitly
        # ...
    ```
4.  **Expose Metrics via CLI/Web UI:** Add commands/endpoints to `main.py` and `app.py` to display these metrics.

### 7.11. Phase 11: Deployment Considerations

This phase outlines how to deploy the multi-agent system for continuous operation.

#### Task 7.11.1: Containerization with Docker

**Goal:** Package the application into Docker containers for consistent deployment across environments.

**Actionable Steps:**
1.  **Install Docker:** Ensure Docker is installed on your development machine.
2.  **Create `Dockerfile`:** In the project root, create a `Dockerfile` for your application.
    ```dockerfile
    # Dockerfile
    # Use a lightweight Python base image
    FROM python:3.10-slim-buster

    # Set working directory in the container
    WORKDIR /app

    # Copy requirements file and install dependencies
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the rest of the application code
    COPY . .

    # Set environment variables (e.g., for OpenAI API Key)
    # It's better to pass these at runtime for security
    # ENV OPENAI_API_KEY="your_api_key_here"

    # Expose the Flask port if using the web UI
    EXPOSE 5000

    # Command to run the Flask app (for web UI)
    CMD ["flask", "--app", "app", "run", "--host=0.0.0.0"]

    # Or command to run the CLI (for background processing)
    # CMD ["python", "main.py", "run"]
    ```
3.  **Build Docker Image:**
    ```bash
    docker build -t supermanus-dev-agent .
    ```
4.  **Run Docker Container:**
    *   **For Web UI:**
        ```bash
        docker run -p 5000:5000 -e OPENAI_API_KEY="your_api_key" supermanus-dev-agent
        ```
    *   **For CLI (background orchestration):**
        ```bash
        docker run -e OPENAI_API_KEY="your_api_key" supermanus-dev-agent python main.py run
        ```
5.  **Commit `Dockerfile`:**
    ```bash
    git add Dockerfile
    git commit -m "Added Dockerfile for containerization"
    ```

#### Task 7.11.2: Orchestration with Docker Compose (Optional but Recommended)

**Goal:** Simplify the management of multiple services (e.g., Flask app, separate Gatekeeper/Coding Agent processes) using Docker Compose.

**Actionable Steps:**
1.  **Create `docker-compose.yml`:** In the project root, create a `docker-compose.yml` file.
    ```yaml
    # docker-compose.yml
    version: '3.8'

    services:
      gatekeeper-web:
        build: .
        container_name: supermanus_gatekeeper_web
        ports:
          - "5000:5000"
        environment:
          - OPENAI_API_KEY=${OPENAI_API_KEY}
        # Mount the project directory to persist session state and logs
        volumes:
          - .:/app
        command: flask --app app run --host=0.0.0.0

      # If you want to run the orchestration loop in a separate container
      # gatekeeper-orchestrator:
      #   build: .
      #   container_name: supermanus_gatekeeper_orchestrator
      #   environment:
      #     - OPENAI_API_KEY=${OPENAI_API_KEY}
      #   volumes:
      #     - .:/app
      #   command: python main.py run
      #   depends_on:
      #     - gatekeeper-web # Ensure web UI is up if needed
    ```
2.  **Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
3.  **Commit `docker-compose.yml`:**
    ```bash
    git add docker-compose.yml
    git commit -m "Added docker-compose for multi-service orchestration"
    ```

### 7.12. Phase 12: Future Enhancements and Considerations

This section outlines potential future work and advanced topics.

#### Task 7.12.1: Advanced Plan Management

**Goal:** Improve the flexibility and power of the project plan.

**Actionable Steps:**
*   **YAML Support:** Add support for YAML as a plan format, which is often more human-readable than JSON.
*   **Dynamic Plan Generation:** Allow the Gatekeeper (or another LLM) to dynamically generate or refine parts of the plan based on project progress or new requirements.
*   **Version Control for Plans:** Implement a system to version control the project plan itself, allowing for rollbacks and tracking changes.

#### Task 7.12.2: Enhanced Coding Agent Capabilities

**Goal:** Make the Coding Agent more autonomous and capable.

**Actionable Steps:**
*   **Tool Registry:** Implement a dynamic tool registry where the Coding Agent can discover and select tools based on task requirements.
*   **Self-Correction:** Enable the Coding Agent to identify and correct its own errors (e.g., failed tests, syntax errors) without immediate Gatekeeper intervention.
*   **Code Review:** Integrate static analysis tools (linters, formatters) and potentially LLM-based code review capabilities.

#### Task 7.12.3: Integration with Version Control Systems (VCS)

**Goal:** Deeply integrate the system with Git for automated commits, branching, and pull requests.

**Actionable Steps:**
*   **GitPython Integration:** Use the `GitPython` library to programmatically interact with Git.
*   **Automated Commits:** Configure the Coding Agent to make small, atomic commits after completing sub-tasks.
*   **Feature Branching:** Implement a strategy for the Gatekeeper to manage feature branches for each major task.
*   **Pull Request Generation:** Automatically generate pull requests for human review upon completion of a feature branch.

#### Task 7.12.4: Advanced Human Interaction Layers

**Goal:** Provide richer and more intuitive interfaces for human interaction.

**Actionable Steps:**
*   **Full VSCode Extension:** Develop the complete VSCode extension as outlined in Task 7.8.2.
*   **OpenWebUI Plugin:** Create a dedicated plugin for OpenWebUI to integrate the system seamlessly.
*   **Desktop Application:** Consider building a cross-platform desktop application using frameworks like Electron or PyQt for a standalone experience.

#### Task 7.12.5: Multi-Agent Collaboration

**Goal:** Explore scenarios where multiple Coding Agents or specialized agents collaborate under the Gatekeeper.

**Actionable Steps:**
*   **Parallel Task Execution:** Allow the Gatekeeper to dispatch multiple independent tasks to different Coding Agents in parallel.
*   **Specialized Agents:** Introduce agents specialized in specific domains (e.g., a Testing Agent, a Documentation Agent, a UI/UX Agent).
*   **Agent Communication Protocols:** Define clear communication protocols between specialized agents.

This comprehensive plan provides a roadmap for building a robust and intelligent multi-agent system for LLM-driven development. Each task is designed to be incremental, allowing for step-by-step development and testing. Remember to commit your changes frequently and refer back to this document as you progress. Good luck with your vibe coding!




## 8. Detailed Implementation Plan for VSCode Extension Development

This section provides a very detailed, step-by-step implementation plan for developing the VSCode extension for the SuperManUS LLM Dev Agent. This plan assumes you have completed the Python backend development and have a running Flask application serving the Gatekeeper Agent. It is designed to guide you through the process, even if you are new to VSCode extension development.

### 8.1. Phase 1: VSCode Extension Project Setup

This phase focuses on setting up your development environment and scaffolding the basic VSCode extension project.

#### Task 8.1.1: Install Node.js and npm

**Goal:** Ensure your system has Node.js and npm (Node Package Manager) installed, which are essential for VSCode extension development.

**Actionable Steps:**
1.  **Check for Existing Installation:** Open your terminal (outside of VSCode for now) and run:
    ```bash
    node -v
    npm -v
    ```
    If you see version numbers (e.g., `v18.17.1`, `9.6.7`), you likely have them installed. If not, proceed to step 2.
2.  **Install Node.js (with npm):**
    *   **Recommended (using `nvm` for Linux/macOS/WSL):** `nvm` allows you to manage multiple Node.js versions. Follow the installation instructions on the `nvm` GitHub page [1]. After installing `nvm`, install a stable Node.js version:
        ```bash
        nvm install --lts
        nvm use --lts
        ```
    *   **Recommended (using `nvm-windows` for Windows):** Similar to `nvm`, but for Windows. Follow instructions at [2].
    *   **Direct Download:** If you prefer a direct installer, download the LTS (Long Term Support) version from the official Node.js website [3]. The installer usually includes npm.
3.  **Verify Installation:** After installation, open a **new** terminal and re-run `node -v` and `npm -v` to confirm they are correctly installed and accessible in your PATH.

#### Task 8.1.2: Install Yeoman and VSCode Extension Generator

**Goal:** Install the tools necessary to scaffold a new VSCode extension project.

**Actionable Steps:**
1.  **Install Global Packages:** In your terminal, run the following command to install Yeoman (`yo`) and the VSCode Extension Generator (`generator-code`) globally:
    ```bash
    npm install -g yo generator-code
    ```
    *   `yo`: The scaffolding tool.
    *   `generator-code`: The specific generator for VSCode extensions.
2.  **Verify Installation:** You can test if `yo` is installed by running `yo` in the terminal. It should show a list of available generators.

#### Task 8.1.3: Scaffold a New VSCode Extension Project

**Goal:** Create the basic file structure for your VSCode extension.

**Actionable Steps:**
1.  **Create a Dedicated Directory:** Create a new directory where you will store your VSCode extension projects. This keeps your projects organized.
    ```bash
    mkdir ~/vscode-extensions
    cd ~/vscode-extensions
    ```
2.  **Run the Generator:** Execute the VSCode extension generator:
    ```bash
    yo code
    ```
3.  **Answer the Prompts:** The generator will ask you several questions. Here are suggested answers:
    *   `? What type of extension do you want to create?` Select `New Extension (TypeScript)`. TypeScript is highly recommended for VSCode extensions due to its type safety and better tooling support.
    *   `? What's the name of your extension?` Enter `SuperManUS Dev Agent`.
    *   `? What's the identifier of your extension? (e.g. publisher.extension-name)` Use a unique identifier, for example, `yourgithubusername.supermanus-dev-agent`. Replace `yourgithubusername` with your actual GitHub username or a unique string.
    *   `? What's the description of your extension?` Enter `VSCode integration for the SuperManUS LLM Development Agent.`
    *   `? Initialize a Git repository?` Select `Yes`. This will set up Git for your extension project.
    *   `? Bundle dependencies with webpack?` Select `Yes`. Webpack helps bundle your extension for better performance and smaller size.
    *   `? Which package manager to use?` Select `npm` (or `yarn` if you prefer).
4.  **Open the Project in VSCode:** Once the generator completes, navigate into your new extension directory and open it with VSCode:
    ```bash
    cd supermanus-dev-agent # Or whatever name you chose
    code .
    ```

#### Task 8.1.4: Understand the Basic Extension Structure

**Goal:** Familiarize yourself with the key files and directories of a VSCode extension project.

**Actionable Steps:**
1.  **Explore `package.json`:** This is the manifest file for your extension. It defines:
    *   `name`, `displayName`, `description`, `version`, `publisher`.
    *   `main`: The entry point of your extension (usually `out/extension.js` after TypeScript compilation).
    *   `contributes`: Where you declare commands, views, keybindings, etc.
    *   `activationEvents`: When your extension will be activated (e.g., when a specific command is run, or a file of a certain type is opened).
    *   `scripts`: npm scripts for building, testing, and running your extension.
    *   `dependencies`, `devDependencies`.
2.  **Examine `src/extension.ts`:** This is the main TypeScript file where your extension's logic resides. It contains:
    *   `activate()`: Called when your extension is activated. This is where you register commands and other contributions.
    *   `deactivate()`: Called when your extension is deactivated.
3.  **Review `.vscode/launch.json`:** This file configures how to debug your extension. The `Run Extension` configuration will launch a new VSCode window with your extension loaded.
4.  **Look at `tsconfig.json`:** TypeScript configuration file.
5.  **Explore `vsc-extension-quickstart.md`:** This file provides a quick guide to developing and debugging your extension.

#### Task 8.1.5: Run and Debug Your Extension

**Goal:** Verify that your newly scaffolded extension can run and debug successfully.

**Actionable Steps:**
1.  **Open Debug View:** In VSCode, go to the Run and Debug view (Ctrl+Shift+D or Cmd+Shift+D).
2.  **Select 


the `Run Extension` configuration from the dropdown at the top of the Debug view.
3.  **Start Debugging:** Click the green play button (Start Debugging) or press `F5`.
4.  **New VSCode Window:** A new VSCode window (Extension Development Host) will open. This is where your extension will run.
5.  **Test the Sample Command:** In the new window, open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P) and type `Hello World`. You should see the `Hello World` command provided by your extension. Select it, and a notification should appear in the bottom right corner.
6.  **Set Breakpoints:** Go back to your original VSCode window (where you are developing the extension). Open `src/extension.ts` and set a breakpoint inside the `activate` function or the `helloWorld` command function. Run the extension again (F5) and trigger the command. The debugger should hit your breakpoint, allowing you to inspect variables and step through your code.
7.  **Stop Debugging:** Close the Extension Development Host window to stop the debugging session.

#### Task 8.1.6: Initial Git Commit for Extension Project

**Goal:** Save your initial, working extension project to Git.

**Actionable Steps:**
1.  **Open Source Control View:** In VSCode, go to the Source Control view (Ctrl+Shift+G or Cmd+Shift+G).
2.  **Stage Changes:** You should see many new files. Stage all changes (click the `+` icon next to 


the `Changes` section, or use `git add .` in the terminal).
3.  **Commit Changes:** Enter a commit message like `Initial VSCode extension scaffold` and commit the changes.
    ```bash
    git commit -m "Initial VSCode extension scaffold"
    ```

### 8.2. Phase 2: Communication with Python Backend

This phase focuses on establishing the communication channel between your VSCode extension (written in TypeScript/JavaScript) and your Python Flask backend (the Gatekeeper Agent).

#### Task 8.2.1: Ensure Flask Backend is Running and Accessible

**Goal:** Verify that your Python Flask application (from `app.py`) is running and accessible from where your VSCode extension will operate.

**Actionable Steps:**
1.  **Start Flask App:** In a separate terminal window (outside of your VSCode extension project, in your Python project root), activate your Python virtual environment and start the Flask app:
    ```bash
    cd /path/to/your/python/project/llm-dev-agent # Navigate to your Python project
    source venv/bin/activate # Or venv\Scripts\activate.bat for Windows
    flask --app app run --debug --host=0.0.0.0
    ```
    *   Ensure it's running on `0.0.0.0` so it's accessible externally (even if just locally).
    *   Note the port it's running on (default is `5000`).
2.  **Test Accessibility:** Open your web browser and navigate to `http://localhost:5000/` (or whatever port Flask is using). You should see the basic web UI. Also, try `http://localhost:5000/api/status` to ensure the API endpoint is reachable and returns JSON.

#### Task 8.2.2: Install HTTP Client in VSCode Extension

**Goal:** Add a library to your VSCode extension project to make HTTP requests to your Flask backend.

**Actionable Steps:**
1.  **Open Extension Project in VSCode:** If not already open, open your `supermanus-dev-agent` (or chosen name) extension project in VSCode.
2.  **Open Terminal:** Open the integrated terminal in VSCode (Ctrl+`` `).
3.  **Install `axios`:** `axios` is a popular promise-based HTTP client for the browser and Node.js.
    ```bash
    npm install axios
    ```
    This will add `axios` to your `package.json` dependencies and install it into `node_modules`.
4.  **Commit Changes:**
    ```bash
    git add package.json package-lock.json
    git commit -m "Added axios for HTTP requests"
    ```

#### Task 8.2.3: Create a Backend API Client Module

**Goal:** Create a dedicated TypeScript module to encapsulate all API calls to your Python backend, making your `extension.ts` cleaner and more organized.

**Actionable Steps:**
1.  **Create `src/apiClient.ts`:** Create a new file `src/apiClient.ts`.
2.  **Implement API Client:** Add code to make requests to your Flask endpoints.
    ```typescript
    // src/apiClient.ts
    import axios from 'axios';
    import * as vscode from 'vscode';

    const BASE_URL = 'http://localhost:5000/api'; // Ensure this matches your Flask app URL

    export interface Task {
        task_id: string;
        title: string;
        description: string;
        status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'skipped';
        assigned_to: string;
        dependencies: string[];
        risk_level: 'low' | 'medium' | 'high';
        output_expected: string;
        validation_criteria: string;
        agent_instructions: string;
        start_time?: string;
        end_time?: string;
        // Add other fields as per your Python project_plan_template.json
    }

    export interface GatekeeperStatus {
        current_task: Task | null;
        work_log_active: boolean;
        active_tasks_available: number;
        validation_history_count: number;
        project_tasks: Task[];
        // Add other status fields as per your Python get_status() endpoint
    }

    export async function getGatekeeperStatus(): Promise<GatekeeperStatus> {
        try {
            const response = await axios.get<GatekeeperStatus>(`${BASE_URL}/status`);
            return response.data;
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to fetch Gatekeeper status: ${error}`);
            throw error;
        }
    }

    export async function initProject(planFile: string): Promise<any> {
        try {
            const response = await axios.post(`${BASE_URL}/init_project`, { plan_file: planFile });
            return response.data;
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to initialize project: ${error}`);
            throw error;
        }
    }

    export async function runOrchestration(): Promise<any> {
        try {
            const response = await axios.post(`${BASE_URL}/run_orchestration`);
            return response.data;
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to run orchestration: ${error}`);
            throw error;
        }
    }

    export async function getLogs(): Promise<string> {
        try {
            const response = await axios.get<string>(`${BASE_URL}/logs`);
            return response.data;
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to fetch logs: ${error}`);
            throw error;
        }
    }

    // Add more API calls as you implement new endpoints in your Flask app
    ```
3.  **Commit Changes:**
    ```bash
    git add src/apiClient.ts
    git commit -m "Created API client for Python backend communication"
    ```

#### Task 8.2.4: Test API Client in `extension.ts` (Temporary)

**Goal:** Quickly test if your API client can successfully communicate with the Flask backend.

**Actionable Steps:**
1.  **Modify `src/extension.ts`:** Open `src/extension.ts` and add a temporary command to fetch and display the Gatekeeper status.
    ```typescript
    // src/extension.ts
    import * as vscode from 'vscode';
    import { getGatekeeperStatus, initProject, runOrchestration, getLogs } from './apiClient'; // Import your API client

    export function activate(context: vscode.ExtensionContext) {

        console.log('Congratulations, your extension 


is now active!`
        console.log("Extension 'supermanus-dev-agent' is now active!");

        // Register a command to get and display Gatekeeper status
        let disposableStatus = vscode.commands.registerCommand(
            'supermanus-dev-agent.getGatekeeperStatus',
            async () => {
                try {
                    const status = await getGatekeeperStatus();
                    vscode.window.showInformationMessage(
                        `Gatekeeper Status: Current Task - ${status.current_task ? status.current_task.title : 'None'}`
                    );
                    console.log("Gatekeeper Status:", status);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error fetching status: ${error}`);
                }
            }
        );
        context.subscriptions.push(disposableStatus);

        // Register a command to initialize project
        let disposableInit = vscode.commands.registerCommand(
            'supermanus-dev-agent.initProject',
            async () => {
                const planFile = 'project_plan_template.json'; // Assuming this is in your Python project root
                try {
                    const result = await initProject(planFile);
                    vscode.window.showInformationMessage(result.message);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error initializing project: ${error}`);
                }
            }
        );
        context.subscriptions.push(disposableInit);

        // Register a command to run orchestration
        let disposableRun = vscode.commands.registerCommand(
            'supermanus-dev-agent.runOrchestration',
            async () => {
                try {
                    const result = await runOrchestration();
                    vscode.window.showInformationMessage(result.message);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error running orchestration: ${error}`);
                }
            }
        );
        context.subscriptions.push(disposableRun);

        // Register a command to get logs
        let disposableLogs = vscode.commands.registerCommand(
            'supermanus-dev-agent.getLogs',
            async () => {
                try {
                    const logs = await getLogs();
                    const panel = vscode.window.createWebviewPanel(
                        'supermanusLogs',
                        'SuperManUS Logs',
                        vscode.ViewColumn.Two,
                        {}
                    );
                    panel.webview.html = `<pre>${logs}</pre>`;
                } catch (error) {
                    vscode.window.showErrorMessage(`Error fetching logs: ${error}`);
                }
            }
        );
        context.subscriptions.push(disposableLogs);

    }

    export function deactivate() {}
    ```
2.  **Update `package.json`:** You need to declare these new commands in your `package.json` so VSCode knows about them.
    ```json
    // package.json (excerpt)
    {
        // ...
        "contributes": {
            "commands": [
                {
                    "command": "supermanus-dev-agent.helloWorld",
                    "title": "Hello World"
                },
                {
                    "command": "supermanus-dev-agent.getGatekeeperStatus",
                    "title": "SuperManUS: Get Gatekeeper Status"
                },
                {
                    "command": "supermanus-dev-agent.initProject",
                    "title": "SuperManUS: Initialize Project"
                },
                {
                    "command": "supermanus-dev-agent.runOrchestration",
                    "title": "SuperManUS: Run Orchestration Loop"
                },
                {
                    "command": "supermanus-dev-agent.getLogs",
                    "title": "SuperManUS: View Logs"
                }
            ]
        },
        // ...
    }
    ```
3.  **Run and Test:** Press `F5` to launch the Extension Development Host. Open the Command Palette (Ctrl+Shift+P) and try running your new `SuperManUS:` commands. You should see information messages or a new webview panel for logs.
4.  **Commit Changes:**
    ```bash
    git add src/extension.ts package.json
    git commit -m "Implemented basic commands for API interaction"
    ```

### 8.3. Phase 3: Custom Views and Tree View Integration

This phase focuses on creating more persistent and structured UI elements within VSCode, specifically a custom sidebar view to display project status and tasks.

#### Task 8.3.1: Create a Custom Tree View for Project Status

**Goal:** Display the Gatekeeper status and project tasks in a dedicated sidebar view.

**Actionable Steps:**
1.  **Define Data Providers:** You need to create classes that implement `vscode.TreeDataProvider` to tell VSCode how to render your data in a tree view.
    *   **Create `src/treeViewProviders.ts`:**
        ```typescript
        // src/treeViewProviders.ts
        import * as vscode from 'vscode';
        import { GatekeeperStatus, Task, getGatekeeperStatus } from './apiClient';

        // Represents a single item in our tree view
        export class StatusItem extends vscode.TreeItem {
            constructor(
                public readonly label: string,
                public readonly collapsibleState: vscode.TreeItemCollapsibleState,
                public readonly description?: string,
                public readonly command?: vscode.Command
            ) {
                super(label, collapsibleState);
                this.tooltip = this.label;
                this.description = description;
            }
        }

        // Tree Data Provider for the Gatekeeper Status
        export class GatekeeperStatusProvider implements vscode.TreeDataProvider<StatusItem> {
            private _onDidChangeTreeData: vscode.EventEmitter<StatusItem | undefined | void> = new vscode.EventEmitter<StatusItem | undefined | void>();
            readonly onDidChangeTreeData: vscode.Event<StatusItem | undefined | void> = this._onDidChangeTreeData.event;

            private status: GatekeeperStatus | undefined;

            constructor() {
                this.refresh();
            }

            async refresh(): Promise<void> {
                try {
                    this.status = await getGatekeeperStatus();
                    this._onDidChangeTreeData.fire(); // Notify VSCode to refresh the view
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to refresh status: ${error}`);
                    this.status = undefined;
                    this._onDidChangeTreeData.fire();
                }
            }

            getTreeItem(element: StatusItem): vscode.TreeItem {
                return element;
            }

            async getChildren(element?: StatusItem): Promise<StatusItem[]> {
                if (!this.status) {
                    return [new StatusItem('Loading Gatekeeper Status...', vscode.TreeItemCollapsibleState.None)];
                }

                if (element) {
                    // If an element is clicked, we can provide sub-items
                    // For now, we'll keep it simple and not have nested items beyond top-level
                    return [];
                } else {
                    // Top-level items
                    const items: StatusItem[] = [];

                    items.push(new StatusItem(
                        `Current Task: ${this.status.current_task ? this.status.current_task.title : 'None'}`,
                        vscode.TreeItemCollapsibleState.None
                    ));
                    items.push(new StatusItem(
                        `Work Log Active: ${this.status.work_log_active ? 'Yes' : 'No'}`,
                        vscode.TreeItemCollapsibleState.None
                    ));
                    items.push(new StatusItem(
                        `Active Tasks Remaining: ${this.status.active_tasks_available}`,
                        vscode.TreeItemCollapsibleState.None
                    ));
                    items.push(new StatusItem(
                        `Validation History Entries: ${this.status.validation_history_count}`,
                        vscode.TreeItemCollapsibleState.None
                    ));

                    // Add a section for all project tasks
                    if (this.status.project_tasks && this.status.project_tasks.length > 0) {
                        items.push(new StatusItem(
                            'Project Tasks',
                            vscode.TreeItemCollapsibleState.Expanded,
                            undefined,
                            { command: 'supermanus-dev-agent.refreshStatus', title: 'Refresh Status' } // Example command
                        ));
                        this.status.project_tasks.forEach(task => {
                            items.push(new StatusItem(
                                `${task.task_id}: ${task.title}`,
                                vscode.TreeItemCollapsibleState.None,
                                `Status: ${task.status}`
                            ));
                        });
                    }

                    return items;
                }
            }
        }
        ```
2.  **Register the Tree View in `extension.ts`:**
    ```typescript
    // src/extension.ts (excerpt)
    import * as vscode from 'vscode';
    import { getGatekeeperStatus, initProject, runOrchestration, getLogs } from './apiClient';
    import { GatekeeperStatusProvider, StatusItem } from './treeViewProviders'; // Import your new provider

    export function activate(context: vscode.ExtensionContext) {

        console.log('Congratulations, your extension is now active!');

        // Instantiate your tree view provider
        const gatekeeperStatusProvider = new GatekeeperStatusProvider();

        // Register the tree view
        vscode.window.registerTreeDataProvider(
            'supermanusGatekeeperStatus',
            gatekeeperStatusProvider
        );

        // Register a command to refresh the tree view
        context.subscriptions.push(vscode.commands.registerCommand(
            'supermanus-dev-agent.refreshStatus',
            () => gatekeeperStatusProvider.refresh()
        ));

        // ... existing command registrations ...

    }

    export function deactivate() {}
    ```
3.  **Declare the View in `package.json`:** You need to tell VSCode where to place your new tree view.
    ```json
    // package.json (excerpt)
    {
        // ...
        "contributes": {
            "commands": [
                // ... existing commands ...
            ],
            "viewsContainers": {
                "activitybar": [
                    {
                        "id": "supermanus-explorer",
                        "title": "SuperManUS Dev Agent",
                        "icon": "./resources/supermanus-icon.svg" // You'll need to create this icon
                    }
                ]
            },
            "views": {
                "supermanus-explorer": [
                    {
                        "id": "supermanusGatekeeperStatus",
                        "name": "Gatekeeper Status"
                    }
                ]
            }
        },
        // ...
    }
    ```
    *   **Create an Icon:** Create a simple SVG icon (e.g., `supermanus-icon.svg`) in a `resources` folder at your extension project root (e.g., `supermanus-dev-agent/resources/supermanus-icon.svg`). You can use a simple SVG like:
        ```svg
        <svg width="16" height="16" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="16" height="16" fill="#007ACC"/>
            <text x="50%" y="50%" font-family="Arial" font-size="10" fill="white" text-anchor="middle" dominant-baseline="middle">SM</text>
        </svg>
        ```
4.  **Run and Test:** Press `F5`. You should now see a new icon in the VSCode Activity Bar (left sidebar). Click it to open your 


new custom activity bar view and see the Gatekeeper Status tree view.
5.  **Commit Changes:**
    ```bash
    git add src/treeViewProviders.ts package.json resources/
    git commit -m "Implemented custom tree view for Gatekeeper Status"
    ```

#### Task 8.3.2: Implement a Custom Webview for Detailed Task View or Logs

**Goal:** Create a more flexible UI element using a Webview to display detailed information, such as comprehensive logs or a rich view of a selected task.

**Actionable Steps:**
1.  **Create `src/webviewManager.ts`:** This module will handle the creation and management of webview panels.
    ```typescript
    // src/webviewManager.ts
    import * as vscode from 'vscode';

    export class WebviewManager {
        private static currentPanel: vscode.WebviewPanel | undefined;

        public static createOrShow(extensionUri: vscode.Uri, viewType: string, title: string, content: string) {
            const column = vscode.window.activeTextEditor
                ? vscode.window.activeTextEditor.viewColumn
                : undefined;

            // If we already have a panel, show it.
            if (WebviewManager.currentPanel) {
                WebviewManager.currentPanel.reveal(column);
                WebviewManager.currentPanel.title = title;
                WebviewManager.currentPanel.webview.html = content;
                return;
            }

            // Otherwise, create a new panel.
            WebviewManager.currentPanel = vscode.window.createWebviewPanel(
                viewType, // Identifies the type of the webview. Used internally
                title, // Title of the panel displayed to the user
                column || vscode.ViewColumn.One, // Editor column to show the new webview panel in.
                {
                    // Enable scripts in the webview
                    enableScripts: true,
                    // And restrict the webview to only loading content from our extension's `media` directory.
                    localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
                }
            );

            WebviewManager.currentPanel.webview.html = content;

            WebviewManager.currentPanel.onDidDispose(
                () => {
                    WebviewManager.currentPanel = undefined;
                },
                null,
                [] // Disposables
            );
        }

        public static updateContent(content: string) {
            if (WebviewManager.currentPanel) {
                WebviewManager.currentPanel.webview.html = content;
            }
        }

        public static dispose() {
            WebviewManager.currentPanel?.dispose();
            WebviewManager.currentPanel = undefined;
        }
    }
    ```
2.  **Modify `src/extension.ts` to use `WebviewManager` for Logs:**
    ```typescript
    // src/extension.ts (excerpt)
    import * as vscode from 'vscode';
    import { getGatekeeperStatus, initProject, runOrchestration, getLogs } from './apiClient';
    import { GatekeeperStatusProvider, StatusItem } from './treeViewProviders';
    import { WebviewManager } from './webviewManager'; // Import your new manager

    export function activate(context: vscode.ExtensionContext) {

        console.log('Congratulations, your extension is now active!');

        const gatekeeperStatusProvider = new GatekeeperStatusProvider();
        vscode.window.registerTreeDataProvider(
            'supermanusGatekeeperStatus',
            gatekeeperStatusProvider
        );

        context.subscriptions.push(vscode.commands.registerCommand(
            'supermanus-dev-agent.refreshStatus',
            () => gatekeeperStatusProvider.refresh()
        ));

        // ... existing commands (helloWorld, initProject, runOrchestration) ...

        // Update the getLogs command to use WebviewManager
        let disposableLogs = vscode.commands.registerCommand(
            'supermanus-dev-agent.getLogs',
            async () => {
                try {
                    const logs = await getLogs();
                    const htmlContent = `
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>SuperManUS Logs</title>
                            <style>
                                body { font-family: monospace; white-space: pre-wrap; background-color: #1e1e1e; color: #d4d4d4; padding: 10px; }
                            </style>
                        </head>
                        <body>
                            <pre>${logs}</pre>
                        </body>
                        </html>
                    `;
                    WebviewManager.createOrShow(context.extensionUri, 'supermanusLogs', 'SuperManUS Logs', htmlContent);
                } catch (error) {
                    vscode.window.showErrorMessage(`Error fetching logs: ${error}`);
                }
            }
        );
        context.subscriptions.push(disposableLogs);

    }

    export function deactivate() {
        WebviewManager.dispose(); // Clean up webview on deactivate
    }
    ```
3.  **Run and Test:** Press `F5`. Run the `SuperManUS: View Logs` command. A new webview panel should open displaying the logs.
4.  **Commit Changes:**
    ```bash
    git add src/webviewManager.ts src/extension.ts
    git commit -m "Implemented custom webview for logs"
    ```

### 8.4. Phase 4: Advanced Commands and UI Integration

This phase focuses on adding more interactive commands and integrating them seamlessly into the VSCode UI.

#### Task 8.4.1: Add Commands for Task-Specific Actions

**Goal:** Allow users to interact with individual tasks (e.g., mark as complete, view details) directly from the tree view.

**Actionable Steps:**
1.  **Modify `src/treeViewProviders.ts` to include commands on `StatusItem`:**
    ```typescript
    // src/treeViewProviders.ts (excerpt)
    // ... existing imports ...

    export class StatusItem extends vscode.TreeItem {
        constructor(
            public readonly label: string,
            public readonly collapsibleState: vscode.TreeItemCollapsibleState,
            public readonly description?: string,
            public readonly command?: vscode.Command,
            public readonly contextValue?: string // Add contextValue
        ) {
            super(label, collapsibleState);
            this.tooltip = this.label;
            this.description = description;
            this.contextValue = contextValue; // Assign contextValue
        }
    }

    // ... GatekeeperStatusProvider class ...

            async getChildren(element?: StatusItem): Promise<StatusItem[]> {
                // ... existing code ...

                    // Add a section for all project tasks
                    if (this.status.project_tasks && this.status.project_tasks.length > 0) {
                        items.push(new StatusItem(
                            'Project Tasks',
                            vscode.TreeItemCollapsibleState.Expanded,
                            undefined,
                            { command: 'supermanus-dev-agent.refreshStatus', title: 'Refresh Status' } // Example command
                        ));
                        this.status.project_tasks.forEach(task => {
                            let contextValue = 'taskItem';
                            if (task.status === 'completed') {
                                contextValue = 'taskItemCompleted';
                            } else if (task.status === 'in_progress') {
                                contextValue = 'taskItemInProgress';
                            } else if (task.status === 'blocked') {
                                contextValue = 'taskItemBlocked';
                            }

                            items.push(new StatusItem(
                                `${task.task_id}: ${task.title}`,
                                vscode.TreeItemCollapsibleState.None,
                                `Status: ${task.status}`,
                                { command: 'supermanus-dev-agent.viewTaskDetails', title: 'View Details', arguments: [task] }, // Command to view details
                                contextValue // Assign contextValue
                            ));
                        });
                    }

                    return items;
                }
            }
        }
    ```
2.  **Define `viewTaskDetails` Command in `extension.ts`:**
    ```typescript
    // src/extension.ts (excerpt)
    // ... existing imports ...
    import { Task } from './apiClient'; // Import Task interface

    export function activate(context: vscode.ExtensionContext) {

        // ... existing code ...

        // Command to view task details in a webview
        let disposableViewTaskDetails = vscode.commands.registerCommand(
            'supermanus-dev-agent.viewTaskDetails',
            (task: Task) => {
                const htmlContent = `
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Task Details: ${task.task_id}</title>
                        <style>
                            body { font-family: sans-serif; background-color: #f4f4f4; color: #333; padding: 20px; }
                            h1 { color: #0056b3; }
                            pre { background: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
                            strong { color: #0056b3; }
                        </style>
                    </head>
                    <body>
                        <h1>Task: ${task.task_id} - ${task.title}</h1>
                        <p><strong>Description:</strong> ${task.description}</p>
                        <p><strong>Status:</strong> ${task.status}</p>
                        <p><strong>Assigned To:</strong> ${task.assigned_to}</p>
                        <p><strong>Risk Level:</strong> ${task.risk_level}</p>
                        <p><strong>Output Expected:</strong> ${task.output_expected}</p>
                        <p><strong>Validation Criteria:</strong> ${task.validation_criteria}</p>
                        <p><strong>Agent Instructions:</strong></p>
                        <pre>${task.agent_instructions}</pre>
                        ${task.start_time ? `<p><strong>Start Time:</strong> ${new Date(task.start_time).toLocaleString()}</p>` : ''}
                        ${task.end_time ? `<p><strong>End Time:</strong> ${new Date(task.end_time).toLocaleString()}</p>` : ''}
                    </body>
                    </html>
                `;
                WebviewManager.createOrShow(context.extensionUri, 'supermanusTaskDetails', `Task Details: ${task.task_id}`, htmlContent);
            }
        );
        context.subscriptions.push(disposableViewTaskDetails);

        // ... existing commands ...
    }
    ```
3.  **Define Context Menus in `package.json`:** Use `menus` contribution point to add context menu items to your tree view items based on their `contextValue`.
    ```json
    // package.json (excerpt)
    {
        // ...
        "contributes": {
            "commands": [
                // ... existing commands ...
            ],
            "viewsContainers": {
                // ...
            },
            "views": {
                // ...
            },
            "menus": {
                "view/item/context": [
                    {
                        "command": "supermanus-dev-agent.viewTaskDetails",
                        "when": "viewItem == taskItem || viewItem == taskItemInProgress || viewItem == taskItemBlocked || viewItem == taskItemCompleted",
                        "group": "inline"
                    },
                    {
                        "command": "supermanus-dev-agent.markTaskCompleted",
                        "when": "viewItem == taskItem || viewItem == taskItemInProgress",
                        "group": "inline"
                    },
                    {
                        "command": "supermanus-dev-agent.markTaskFailed",
                        "when": "viewItem == taskItem || viewItem == taskItemInProgress",
                        "group": "inline"
                    }
                ]
            }
        },
        // ...
    }
    ```
4.  **Implement `markTaskCompleted` and `markTaskFailed` Commands:** These commands will call your Python backend to simulate task completion/failure.
    ```typescript
    // src/extension.ts (excerpt)
    // ... existing imports ...

    export function activate(context: vscode.ExtensionContext) {

        // ... existing code ...

        // Command to mark a task as completed (simulated)
        let disposableMarkCompleted = vscode.commands.registerCommand(
            'supermanus-dev-agent.markTaskCompleted',
            async (task: Task) => {
                try {
                    // Call your Python backend API to mark task as completed
                    // This would typically be a new endpoint in your Flask app
                    // For now, we'll simulate by calling the CLI command via a shell exec or a dedicated API
                    // In a real scenario, you'd have an API like: await apiClient.completeTask(task.task_id, 'completed', 'Manual completion');
                    vscode.window.showInformationMessage(`Simulating completion for task: ${task.task_id}`);
                    // After successful API call, refresh the tree view
                    gatekeeperStatusProvider.refresh();
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to mark task completed: ${error}`);
                }
            }
        );
        context.subscriptions.push(disposableMarkCompleted);

        // Command to mark a task as failed (simulated)
        let disposableMarkFailed = vscode.commands.registerCommand(
            'supermanus-dev-agent.markTaskFailed',
            async (task: Task) => {
                try {
                    // Call your Python backend API to mark task as failed
                    vscode.window.showInformationMessage(`Simulating failure for task: ${task.task_id}`);
                    // After successful API call, refresh the tree view
                    gatekeeperStatusProvider.refresh();
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to mark task failed: ${error}`);
                }
            }
        );
        context.subscriptions.push(disposableMarkFailed);

        // ... existing commands ...
    }
    ```
5.  **Run and Test:** Press `F5`. Right-click on a task in the `Gatekeeper Status` tree view. You should see the new context menu items. Clicking `View Details` should open a webview with task information.
6.  **Commit Changes:**
    ```bash
    git add src/treeViewProviders.ts src/extension.ts package.json
    git commit -m "Added task-specific commands and context menus"
    ```

### 8.5. Phase 5: Debugging and Troubleshooting

This phase provides guidance on debugging your VSCode extension and troubleshooting common issues.

#### Task 8.5.1: Effective Debugging Techniques

**Goal:** Learn how to effectively use VSCode's debugging tools for extension development.

**Actionable Steps:**
1.  **`console.log` for Quick Checks:** Use `console.log()` statements in your `extension.ts` and other TypeScript files. The output appears in the `Debug Console` of your primary VSCode window (where you are developing the extension) when you run the Extension Development Host.
2.  **Breakpoints:** Set breakpoints by clicking in the gutter next to the line numbers in your TypeScript files. When your extension code executes that line, the debugger will pause, allowing you to inspect variables, step through code, and evaluate expressions.
3.  **Variables and Watch Windows:** In the Debug view, use the `Variables` pane to see the current state of local and global variables. Use the `Watch` pane to monitor specific expressions.
4.  **Call Stack:** The `Call Stack` pane shows you the sequence of function calls that led to the current execution point.
5.  **`launch.json` Configuration:** Understand your `.vscode/launch.json` file. The `Run Extension` configuration is crucial. You can modify it to pass environment variables or arguments if needed.
6.  **Debugging Webviews:** To debug the JavaScript running inside your webviews, open the Extension Development Host window, then open the Command Palette and search for `Developer: Open Webview Developer Tools`. This will open a Chromium DevTools instance for your webview.

#### Task 8.5.2: Troubleshooting Common Issues

**Goal:** Understand and resolve common problems encountered during VSCode extension development.

**Common Issues and Solutions:**
*   **Extension Not Activating:**
    *   **Check `activationEvents` in `package.json`:** Ensure your activation events are correctly defined. If you expect it to activate on a command, make sure the command ID matches.
    *   **Check `console.log`:** Look for errors in the `Debug Console` of your primary VSCode window.
*   **Commands Not Appearing/Working:**
    *   **Check `contributes.commands` in `package.json`:** Verify the command ID and title are correct.
    *   **Check `registerCommand` in `extension.ts`:** Ensure the command ID passed to `vscode.commands.registerCommand` matches the one in `package.json`.
*   **Tree View Not Appearing/Updating:**
    *   **Check `contributes.viewsContainers` and `contributes.views` in `package.json`:** Ensure the IDs and structure are correct.
    *   **Check `registerTreeDataProvider` in `extension.ts`:** Make sure you are registering your `TreeDataProvider` correctly.
    *   **Call `_onDidChangeTreeData.fire()`:** Remember to call `this._onDidChangeTreeData.fire()` in your `TreeDataProvider` whenever the underlying data changes and you want the view to refresh.
*   **API Calls Failing (to Python Backend):**
    *   **Check Python Flask App:** Ensure your Flask app is running and accessible at the `BASE_URL` specified in `src/apiClient.ts`.
    *   **Network Issues:** Check your firewall or network settings if you cannot connect to `localhost:5000`.
    *   **CORS Errors:** If you see CORS (Cross-Origin Resource Sharing) errors in your browser's developer console (for webviews) or in the VSCode Debug Console, you need to enable CORS in your Flask app. (The provided Flask `app.py` does not explicitly include CORS, you might need to add `flask-cors` library and enable it).
        ```bash
        pip install Flask-Cors
        ```
        Then in `app.py`:
        ```python
        from flask_cors import CORS
        # ...
        app = Flask(__name__)
        CORS(app) # Enable CORS for all routes
        # ...
        ```
    *   **API Endpoint Mismatches:** Double-check that the API paths (`/api/status`, `/api/init_project`, etc.) and HTTP methods (GET/POST) in `src/apiClient.ts` match your Flask `app.py`.
*   **TypeScript Compilation Errors:**
    *   **Check `tsconfig.json`:** Ensure your TypeScript configuration is correct.
    *   **Review Error Messages:** TypeScript error messages are usually very descriptive and point to the exact location of the problem.

### 8.6. Phase 6: Packaging and Publishing (Optional)

This phase covers how to package your extension for distribution and optionally publish it to the VSCode Marketplace.

#### Task 8.6.1: Package Your Extension

**Goal:** Create a `.vsix` file, which is the installable package for your VSCode extension.

**Actionable Steps:**
1.  **Install `vsce`:** The VS Code Extension Manager (`vsce`) is a command-line tool for packaging and publishing extensions.
    ```bash
    npm install -g vsce
    ```
2.  **Prepare `package.json`:** Ensure your `package.json` has all the required fields for publishing (e.g., `publisher`, `repository`, `bugs`, `homepage`).
3.  **Run `vsce package`:** Navigate to your extension project root in the terminal and run:
    ```bash
    vsce package
    ```
    This will create a `.vsix` file in your project directory (e.g., `yourpublisher.supermanus-dev-agent-0.0.1.vsix`).

#### Task 8.6.2: Install from VSIX

**Goal:** Test your packaged extension by installing it locally.

**Actionable Steps:**
1.  **Open VSCode:** Open your regular VSCode instance (not the Extension Development Host).
2.  **Install from VSIX:** Go to the Extensions view (Ctrl+Shift+X or Cmd+Shift+X), click the `...` (More Actions) menu at the top, and select `Install from VSIX...`.
3.  **Select VSIX File:** Browse to your `.vsix` file and select it. Your extension will be installed.

#### Task 8.6.3: Publish to VSCode Marketplace (Optional)

**Goal:** Make your extension publicly available on the VSCode Marketplace.

**Actionable Steps:**
1.  **Create an Azure DevOps Organization:** You need an Azure DevOps organization to publish extensions. Go to [https://azure.microsoft.com/en-us/services/devops/](https://azure.microsoft.com/en-us/services/devops/) and create one.
2.  **Create a Personal Access Token (PAT):** In your Azure DevOps organization, create a PAT with `All accessible organizations` and `Marketplace (Read/Write)` scopes.
3.  **Login with `vsce`:** In your terminal, run:
    ```bash
    vsce publish -p <your_personal_access_token>
    ```
    Replace `<your_personal_access_token>` with the PAT you generated.
4.  **Publish:** Follow the prompts. Your extension will be published to the Marketplace.

This comprehensive plan should provide you with a solid roadmap for developing the VSCode extension for your SuperManUS LLM Dev Agent. Remember to commit your changes frequently and test iteratively. Good luck!




## 9. Detailed Implementation Plan for Multi-Context Protocol (MCP) Server

This section outlines the design and implementation steps for a standalone Multi-Context Protocol (MCP) Server. This server will provide a generalized API for interacting with the SuperManUS LLM Dev Agent, allowing integration with various clients beyond VSCode, such as OpenWebUI, custom desktop applications, or even other AI agents. The MCP Server will act as a standardized communication layer, abstracting the internal complexities of the Gatekeeper and Coding Agents.

### 9.1. Phase 1: MCP Server Core Setup

This phase focuses on setting up the basic server infrastructure using FastAPI, a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.

#### Task 9.1.1: Initialize FastAPI Project

**Goal:** Create a new Python project for the MCP Server and set up a basic FastAPI application.

**Actionable Steps:**
1.  **Create Project Directory:** In your main `llm-dev-agent` project, create a new directory for the MCP Server. This could be `mcp_server/` at the root level, or `src/mcp_server/` if you prefer to keep it within the `src` structure.
    ```bash
    mkdir mcp_server
    cd mcp_server
    ```
2.  **Set Up Virtual Environment:** Create and activate a new Python virtual environment for this server, separate from the main `supermanus` core.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install FastAPI and Uvicorn:** Uvicorn is an ASGI server, necessary to run FastAPI applications.
    ```bash
    pip install fastapi uvicorn
    pip freeze > requirements.txt
    ```
4.  **Create `main.py`:** Create a file named `main.py` in the `mcp_server` directory.
5.  **Add Basic FastAPI App:** Populate `main.py` with a simple FastAPI application.
    ```python
    # mcp_server/main.py
    from fastapi import FastAPI
    import uvicorn

    app = FastAPI()

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "message": "MCP Server is running"}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
    ```
6.  **Run the Server:** From within the `mcp_server` directory with the virtual environment active, run:
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `main:app`: Refers to the `app` object in `main.py`.
    *   `--reload`: Automatically reloads the server on code changes (useful for development).
    *   `--host 0.0.0.0`: Makes the server accessible from outside `localhost`.
    *   `--port 8000`: Specifies the port.
7.  **Test in Browser:** Open your browser and navigate to `http://localhost:8000/health`. You should see `{"status":"ok","message":"MCP Server is running"}`. Also, visit `http://localhost:8000/docs` to see the auto-generated OpenAPI (Swagger UI) documentation.
8.  **Commit Changes:**
    ```bash
    git add mcp_server/
    git commit -m "Initial MCP Server setup with FastAPI"
    ```

#### Task 9.1.2: Integrate SuperManUS Core

**Goal:** Make the `supermanus` core components (Gatekeeper, TaskEnforcer, SessionManager) accessible within the MCP Server.

**Actionable Steps:**
1.  **Adjust Python Path (Temporary for Development):** For development purposes, you can temporarily add the parent directory of `src` to your Python path so the MCP Server can import `supermanus`. In a production deployment, `supermanus` would be installed as a package.
    *   Modify `mcp_server/main.py`:
        ```python
        # mcp_server/main.py
        import sys
        from pathlib import Path

        # Add the parent directory of 'src' to Python path
        # This assumes mcp_server is a sibling of src
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

        from fastapi import FastAPI
        import uvicorn
        from src.supermanus.gatekeeper_agent import GatekeeperAgent
        from src.supermanus.logging_config import setup_logging

        # Setup logging for the MCP Server
        project_root = Path(__file__).resolve().parent.parent # Points to the main llm-dev-agent root
        setup_logging(log_file=project_root / "mcp_server.log", level=logging.INFO)

        app = FastAPI()
        gatekeeper = GatekeeperAgent(project_root=project_root)

        @app.get("/health")
        async def health_check():
            return {"status": "ok", "message": "MCP Server is running"}

        # ... rest of your code ...
        ```
2.  **Test Integration:** Restart the `uvicorn` server. If there are no import errors, the integration is successful.
3.  **Commit Changes:**
    ```bash
    git add mcp_server/main.py
    git commit -m "Integrated SuperManUS core into MCP Server"
    ```

### 9.2. Phase 2: MCP Server API Endpoints

This phase focuses on exposing the core functionalities of the Gatekeeper Agent through RESTful API endpoints.

#### Task 9.2.1: Implement Project Initialization Endpoint

**Goal:** Allow clients to initialize a new project by providing a project plan.

**Actionable Steps:**
1.  **Define Request Body Model:** Use Pydantic models for request body validation.
    *   Modify `mcp_server/main.py`:
        ```python
        # mcp_server/main.py (excerpt)
        from pydantic import BaseModel
        from typing import List, Dict, Any

        # ... existing imports and app setup ...

        class InitProjectRequest(BaseModel):
            plan_file: str

        @app.post("/project/init")
        async def init_project(request: InitProjectRequest):
            try:
                plan_file_path = gatekeeper.project_root / request.plan_file
                if not plan_file_path.exists():
                    return {"message": f"Plan file not found: {request.plan_file}"}, 404
                with open(plan_file_path, 'r') as f:
                    plan_data = json.load(f)
                gatekeeper.load_project_plan(plan_data)
                return {"message": "Project initialized successfully."}
            except Exception as e:
                logger.error(f"Error initializing project: {e}", exc_info=True)
                return {"message": f"Error initializing project: {str(e)}"}, 500
        ```
2.  **Test Endpoint:** Use `curl` or a tool like Postman/Insomnia, or FastAPI's interactive docs (`/docs`).
    ```bash
    curl -X POST 


http://localhost:8000/project/init -H "Content-Type: application/json" -d '{"plan_file": "project_plan_template.json"}'
    ```
    (Ensure `project_plan_template.json` exists in your main project root directory.)

#### Task 9.2.2: Implement Project Status Endpoint

**Goal:** Provide an API endpoint to retrieve the current status of the project, including overall state and detailed task information.

**Actionable Steps:**
1.  **Add Status Endpoint:** Modify `mcp_server/main.py` to include a GET endpoint for status.
    ```python
    # mcp_server/main.py (excerpt)
    # ... existing imports and app setup ...

    @app.get("/project/status")
    async def get_project_status():
        try:
            status = gatekeeper.enforcer.get_status()
            # Include project tasks for display
            status["project_tasks"] = gatekeeper.enforcer.project_tasks
            return status
        except Exception as e:
            logger.error(f"Error getting project status: {e}", exc_info=True)
            return {"message": f"Error getting project status: {str(e)}"}, 500
    ```
2.  **Test Endpoint:** Navigate to `http://localhost:8000/project/status` in your browser or use `curl`.
    ```bash
    curl http://localhost:8000/project/status
    ```

#### Task 9.2.3: Implement Orchestration Run Endpoint

**Goal:** Provide an API endpoint to trigger the Gatekeeper Agent's orchestration loop.

**Actionable Steps:**
1.  **Add Run Orchestration Endpoint:** Modify `mcp_server/main.py`.
    ```python
    # mcp_server/main.py (excerpt)
    # ... existing imports and app setup ...

    @app.post("/orchestration/run")
    async def run_orchestration():
        try:
            gatekeeper.run_orchestration_loop()
            return {"message": "Orchestration loop initiated. Check logs for details."}
        except Exception as e:
            logger.error(f"Error running orchestration: {e}", exc_info=True)
            return {"message": f"Error running orchestration: {str(e)}"}, 500
    ```
2.  **Test Endpoint:** Use `curl` or FastAPI's interactive docs.
    ```bash
    curl -X POST http://localhost:8000/orchestration/run
    ```

#### Task 9.2.4: Implement Task Completion/Failure Simulation Endpoint

**Goal:** Allow external systems or human users to simulate the completion or failure of a task, which the Gatekeeper will then process.

**Actionable Steps:**
1.  **Define Request Body Model:**
    *   Modify `mcp_server/main.py`:
        ```python
        # mcp_server/main.py (excerpt)
        # ... existing imports and app setup ...

        class TaskReportRequest(BaseModel):
            task_id: str
            status: str # 


Literal["completed", "failed"]
            output: Optional[str] = None
            error: Optional[str] = None

        @app.post("/task/report")
        async def report_task_status(request: TaskReportRequest):
            try:
                gatekeeper.receive_coding_agent_report(
                    request.task_id,
                    request.status,
                    output=request.output,
                    error=request.error
                )
                return {"message": f"Report received for task {request.task_id} with status {request.status}."}
            except Exception as e:
                logger.error(f"Error processing task report: {e}", exc_info=True)
                return {"message": f"Error processing task report: {str(e)}"}, 500
        ```
2.  **Test Endpoint:** Use `curl` or FastAPI docs.
    *   **Simulate completion:**
        ```bash
        curl -X POST http://localhost:8000/task/report -H "Content-Type: application/json" -d '{"task_id": "GK1.1", "status": "completed", "output": "Simulated completion from MCP."}'
        ```
    *   **Simulate failure:**
        ```bash
        curl -X POST http://localhost:8000/task/report -H "Content-Type: application/json" -d '{"task_id": "CA1.1", "status": "failed", "error": "Simulated error from MCP."}'
        ```

#### Task 9.2.5: Implement Logs Endpoint

**Goal:** Provide an API endpoint to retrieve the server logs, useful for debugging and monitoring.

**Actionable Steps:**
1.  **Add Logs Endpoint:** Modify `mcp_server/main.py`.
    ```python
    # mcp_server/main.py (excerpt)
    # ... existing imports and app setup ...

    @app.get("/logs")
    async def get_logs():
        log_file_path = project_root / "mcp_server.log"
        if log_file_path.exists():
            with open(log_file_path, 'r') as f:
                return f.read()
        return "No logs yet."
    ```
2.  **Test Endpoint:** Navigate to `http://localhost:8000/logs` in your browser or use `curl`.
    ```bash
    curl http://localhost:8000/logs
    ```

#### Task 9.2.6: Implement CORS (Cross-Origin Resource Sharing)

**Goal:** Enable the MCP Server to accept requests from different origins (e.g., a web-based client running on a different port or domain).

**Actionable Steps:**
1.  **Install `python-multipart` and `fastapi-cors`:**
    ```bash
    pip install python-multipart fastapi-cors
    pip freeze > requirements.txt
    ```
2.  **Add CORS Middleware:** Modify `mcp_server/main.py` to include CORS middleware.
    ```python
    # mcp_server/main.py (excerpt)
    from fastapi.middleware.cors import CORSMiddleware

    # ... existing imports and app setup ...

    app = FastAPI()

    # Add CORS middleware
    origins = [
        "http://localhost",
        "http://localhost:3000", # Example for a React frontend
        "http://localhost:8080", # Example for a Vue frontend
        # Add other origins as needed
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ... rest of your app code ...
    ```
3.  **Commit Changes:**
    ```bash
    git add mcp_server/main.py requirements.txt
    git commit -m "Implemented CORS for MCP Server"
    ```

### 9.3. Phase 3: Deployment Considerations for MCP Server

This phase outlines how to deploy the MCP Server for continuous operation.

#### Task 9.3.1: Containerization with Docker

**Goal:** Package the MCP Server into a Docker container for consistent deployment.

**Actionable Steps:**
1.  **Create `Dockerfile`:** In the `mcp_server` directory, create a `Dockerfile`.
    ```dockerfile
    # mcp_server/Dockerfile
    FROM python:3.10-slim-buster

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the mcp_server application code
    COPY . .

    # Copy the main supermanus core (assuming it's a sibling directory)
    COPY ../src /app/src
    COPY ../project_plan_template.json /app/project_plan_template.json
    COPY ../session_state.json /app/session_state.json
    COPY ../work_logs /app/work_logs

    EXPOSE 8000

    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
2.  **Build Docker Image:** From the `mcp_server` directory:
    ```bash
    docker build -t supermanus-mcp-server .
    ```
3.  **Run Docker Container:**
    ```bash
    docker run -p 8000:8000 -e OPENAI_API_KEY="your_api_key" supermanus-mcp-server
    ```
4.  **Commit `Dockerfile`:**
    ```bash
    git add mcp_server/Dockerfile
    git commit -m "Added Dockerfile for MCP Server containerization"
    ```

#### Task 9.3.2: Orchestration with Docker Compose (for full system)

**Goal:** Manage both the `supermanus` core (if run as a separate service, e.g., for background orchestration) and the MCP Server using Docker Compose.

**Actionable Steps:**
1.  **Modify Root `docker-compose.yml`:** Update the `docker-compose.yml` in your main project root to include the MCP Server.
    ```yaml
    # docker-compose.yml (in project root)
    version: '3.8'

    services:
      # Main SuperManUS core (e.g., for background orchestration or CLI)
      supermanus-core:
        build:
          context: .
          dockerfile: Dockerfile # Refers to the Dockerfile in the root for the main app
        container_name: supermanus_core
        environment:
          - OPENAI_API_KEY=${OPENAI_API_KEY}
        volumes:
          - .:/app # Mount the entire project to persist state and logs
        # command: python main.py run # Uncomment if you want the core to run orchestration in background

      # Multi-Context Protocol Server
      mcp-server:
        build:
          context: ./mcp_server # Build context is the mcp_server directory
          dockerfile: Dockerfile # Refers to the Dockerfile inside mcp_server
        container_name: supermanus_mcp_server
        ports:
          - "8000:8000"
        environment:
          - OPENAI_API_KEY=${OPENAI_API_KEY}
        volumes:
          - .:/app # Mount the entire project to persist state and logs
        depends_on:
          - supermanus-core # MCP server depends on core components being available
        command: uvicorn main:app --host 0.0.0.0 --port 8000

    ```
2.  **Run with Docker Compose:** From the project root:
    ```bash
    docker-compose up --build
    ```
3.  **Commit `docker-compose.yml`:**
    ```bash
    git add docker-compose.yml
    git commit -m "Updated docker-compose to include MCP Server"
    ```

### 9.4. Phase 4: Client Integration Examples

This phase provides conceptual examples of how different clients would interact with the MCP Server.

#### Task 9.4.1: OpenWebUI Integration (Conceptual)

**Goal:** Understand how OpenWebUI could be configured to use the MCP Server.

**Actionable Steps (Conceptual):**
1.  **Custom Tool/Agent Definition:** In OpenWebUI, you would define a custom tool or agent that makes HTTP requests to your MCP Server endpoints.
2.  **Frontend Components:** Potentially develop custom frontend components within OpenWebUI (if its architecture allows) to display the project plan, task status, and logs from the MCP Server.
3.  **Example Interaction Flow:**
    *   User types a command like `/init_project my_new_app`.
    *   OpenWebUI sends a POST request to `http://mcp-server:8000/project/init` with the plan file.
    *   User types `/run_agent`.
    *   OpenWebUI sends a POST request to `http://mcp-server:8000/orchestration/run`.
    *   OpenWebUI periodically polls `http://mcp-server:8000/project/status` to update the UI.

#### Task 9.4.2: Generic Python Client Example

**Goal:** Provide a simple Python script demonstrating how to interact with the MCP Server.

**Actionable Steps:**
1.  **Create `client_example.py`:** Create a new file `client_example.py` in your project root.
2.  **Add Client Code:**
    ```python
    # client_example.py
    import requests
    import json
    import time

    MCP_SERVER_URL = "http://localhost:8000"

    def init_project(plan_file: str):
        url = f"{MCP_SERVER_URL}/project/init"
        payload = {"plan_file": plan_file}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Init Project Response: {response.json()}")

    def get_status():
        url = f"{MCP_SERVER_URL}/project/status"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def run_orchestration():
        url = f"{MCP_SERVER_URL}/orchestration/run"
        response = requests.post(url)
        response.raise_for_status()
        print(f"Run Orchestration Response: {response.json()}")

    def report_task(task_id: str, status: str, output: str = None, error: str = None):
        url = f"{MCP_SERVER_URL}/task/report"
        payload = {"task_id": task_id, "status": status}
        if output: payload["output"] = output
        if error: payload["error"] = error
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Report Task Response: {response.json()}")

    def get_logs():
        url = f"{MCP_SERVER_URL}/logs"
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    if __name__ == "__main__":
        print("--- MCP Client Example ---")

        # 1. Initialize Project
        print("\nInitializing project...")
        try:
            init_project("project_plan_template.json")
        except requests.exceptions.HTTPError as e:
            print(f"Error initializing project: {e.response.json()}")

        # 2. Get Status
        print("\nGetting initial status...")
        status = get_status()
        print(json.dumps(status, indent=2))

        # 3. Run Orchestration (this will dispatch GK1.1)
        print("\nRunning orchestration...")
        run_orchestration()
        time.sleep(2) # Give some time for the backend to process

        # 4. Get Status again to see GK1.1 in progress
        print("\nGetting status after first run...")
        status = get_status()
        print(json.dumps(status, indent=2))

        # 5. Simulate GK1.1 completion (if it was dispatched)
        if status["current_task"] and status["current_task"]["id"] == "GK1.1":
            print("\nSimulating GK1.1 completion...")
            report_task("GK1.1", "completed", output="GK1.1 completed via client.")
            time.sleep(2)

        # 6. Run Orchestration again (should dispatch CA1.1)
        print("\nRunning orchestration again...")
        run_orchestration()
        time.sleep(2)

        # 7. Get Status to see CA1.1 in progress
        print("\nGetting status after second run...")
        status = get_status()
        print(json.dumps(status, indent=2))

        # 8. Get Logs
        print("\nFetching logs...")
        logs = get_logs()
        print("--- MCP Server Logs ---")
        print(logs[-1000:]) # Print last 1000 characters of logs
        print("-----------------------")

        print("\n--- MCP Client Example Finished ---")
    ```
3.  **Run Client Example:** Ensure your MCP Server is running, then execute the client script:
    ```bash
    python client_example.py
    ```
4.  **Commit Changes:**
    ```bash
    git add client_example.py
    git commit -m "Added generic Python client example for MCP Server"
    ```

This detailed plan for the MCP Server provides a robust and flexible way to interact with your `Miss_TaskMaster` system from various applications. It complements the VSCode extension by offering a generalized API. The next step will be to craft the comprehensive LLM prompt for project execution.




## 10. Comprehensive LLM Prompt for Project Execution

This section provides a detailed, comprehensive prompt designed to be given to a powerful Large Language Model (LLM) to execute the development of the "Miss_TaskMaster" application. The prompt is structured to provide maximum context, clear instructions, and a defined operational framework to ensure the LLM stays on task and performs effectively. This prompt is intended to be used in conjunction with the detailed implementation plan outlined in the previous sections.

### 10.1. The "Miss_TaskMaster" Execution Prompt

**BEGIN PROMPT**

**SYSTEM:** You are **SuperManUS**, an elite AI software engineer. Your mission is to build a new application called **"Miss_TaskMaster"**. This application is a sophisticated multi-agent system designed to manage and execute complex, long-term software development projects with high fidelity. You will be working within a sandboxed environment with access to a file system, a code interpreter, and a set of specialized tools.

Your primary directive is to follow a detailed, multi-phase project plan. You must adhere to this plan strictly. Do not deviate, do not get creative with the overall architecture, and do not attempt to complete tasks out of order. Your goal is to be a focused, disciplined, and highly effective executor of the provided plan.

**PROJECT GOAL:** To build "Miss_TaskMaster," a multi-agent system featuring:
1.  A **Gatekeeper Agent** (the strategic planner) that manages a detailed project plan and dispenses tasks one by one.
2.  A **Coding Agent** (the tactical executor) that receives and executes individual tasks with a limited, focused context.
3.  A **VSCode Extension** for a rich, interactive user experience.
4.  A **Multi-Context Protocol (MCP) Server** for generalized, API-driven interaction with the system.

**CORE PRINCIPLE: THE MULTI-CONTEXT PROTOCOL (MCP)**
This entire project is an implementation of the Multi-Context Protocol. This means:
*   **The Gatekeeper holds the "multi-context" view:** It understands the entire project, all dependencies, and the long-term strategy.
*   **The Coding Agent operates in a "single-context" view:** It only knows about the current task it has been assigned. It is deliberately shielded from the complexity of the full plan.
*   **Your role is to build this system.** You will be acting as the initial, "meta" Coding Agent, bootstrapping the very system that will eventually replace your direct, full-context involvement. You must respect this principle in the code you write.

**YOUR OPERATIONAL FRAMEWORK:**
1.  **The Plan is Law:** You will be provided with a comprehensive, multi-phase implementation plan. This plan is your single source of truth. Each of your actions must directly correspond to a task in the current phase of this plan.
2.  **One Task at a Time:** Focus exclusively on the current, active task. Do not work on future tasks, and do not revisit completed tasks unless explicitly instructed to do so for a refactor or bug fix.
3.  **Justify Your Actions:** For every significant action you take (e.g., creating a file, writing code, running a command), you must provide a clear and concise justification that links your action directly to the current task.
4.  **Incremental Development and Commits:** After completing each small, logical piece of a task, you must commit your changes to Git with a clear, descriptive commit message. This creates a clean history and allows for easy rollbacks.
5.  **Testing is Mandatory:** For every piece of functionality you implement, you must also write corresponding unit tests. The plan will specify when to write these tests. Do not skip this step.
6.  **Think Step-by-Step:** Before writing any code, briefly outline your plan for the current task. For example: "To complete Task 7.1.4, I will first create the `session_manager.py` file. Then, I will add the `SessionManager` class with `load_state` and `save_state` methods. Finally, I will add a simple test case under `if __name__ == '__main__':` to verify its functionality before committing."

**AVAILABLE TOOLS AND LIBRARIES:**
*   **File System:** You have full access to read, write, and manage files and directories.
*   **Shell/Terminal:** You can execute shell commands, including `git`, `pip`, `npm`, `python`, `node`, `uvicorn`, `flask`, etc.
*   **Python Environment:** You will be working with Python 3.10+. You must manage your dependencies using `pip` and a `requirements.txt` file.
*   **Node.js Environment:** You will use Node.js and `npm` for the VSCode extension development.
*   **Pre-installed Libraries:** The environment will have standard libraries, but you are responsible for installing project-specific dependencies like `fastapi`, `uvicorn`, `openai`, `axios`, etc., as specified in the plan.

**THE IMPLEMENTATION PLAN:**
Here is the detailed, multi-phase implementation plan you must follow. I will provide you with the first task to begin.

**(The full, detailed implementation plan from Section 7, 8, and 9 of the `multi_agent_system_design.md` document would be inserted here. For the purpose of this prompt, we will assume it is available to the LLM.)**

**YOUR FIRST TASK:**

**Phase 7: Project Setup and Core Utilities**
**Task 7.1.1: Initialize the Project Repository**

**Goal:** Create a new Git repository and set up the basic project directory structure for "Miss_TaskMaster".

**Actionable Steps:**
1.  Create a new project directory named `miss_taskmaster`.
2.  Navigate into this directory.
3.  Initialize a new Git repository.
4.  Create a `.gitignore` file with standard Python, VSCode, and environment-related entries.
5.  Stage and commit your initial project setup with the message: "Initial project setup: created directory and .gitignore".

**Begin execution now. Provide your first action.**

**END PROMPT**

### 10.2. How to Use This Prompt

1.  **Initial Seeding:** This entire prompt, including the detailed implementation plan, should be provided to the LLM at the beginning of the session.
2.  **LLM as the "Meta" Coding Agent:** The LLM will act as the primary developer, following the plan step-by-step.
3.  **Human as the "Meta" Gatekeeper:** The user or a supervisory script will act as the initial Gatekeeper, verifying that the LLM has completed each task correctly before providing it with the next task from the plan.
4.  **Feedback Loop:** If the LLM deviates or makes a mistake, the user should intervene, referencing the "Operational Framework" section of the prompt to correct the LLM's behavior.
5.  **Progressive Task Delegation:** As the LLM builds the "Miss_TaskMaster" system, the user can progressively delegate more of the Gatekeeper's role to the running application itself, eventually bootstrapping the full multi-agent system.

This prompt is designed to be a "constitution" for the LLM, providing a clear set of rules, goals, and constraints to guide its development process and minimize unproductive "screwing around." It sets a professional, goal-oriented tone and gives the LLM all the information it needs to succeed.





## 11. Strategies for Project Success with LLMs (e.g., Claude Sonnet 4)

To maximize the likelihood of success when an LLM like Claude Sonnet 4 is tasked with implementing the "Miss_TaskMaster" project, it's crucial to go beyond just providing a detailed plan and a comprehensive prompt. We need to consider the nuances of how LLMs operate, their strengths, and their limitations within a development context. This section outlines additional strategies to ensure robust execution.

### 11.1. Environment and Tooling Optimization

#### 11.1.1. Robust and Consistent Execution Environment

Ensure the LLM operates within a highly stable and consistent sandboxed environment. This means:
*   **Pre-installed Dependencies:** Where possible, pre-install common system-level dependencies (e.g., `git`, `python3-venv`, `npm`) to reduce initial setup friction and potential errors during package installation. The current sandbox environment already provides a good foundation.
*   **Clear PATH:** Ensure all necessary executables (Python, Node.js, Git, etc.) are correctly configured in the system's `PATH` environment variable, so the LLM doesn't struggle with command discovery.
*   **Sufficient Resources:** Provide adequate CPU, memory, and disk space. LLM-driven development can be resource-intensive, especially during compilation, testing, or large file operations.

#### 11.1.2. Streamlined Tool Access and Feedback

The LLM's interaction with its tools (shell, file system, browser, etc.) should be as seamless as possible:
*   **Atomic Tool Calls:** Tools should be designed to perform specific, atomic actions and return clear, structured feedback. Avoid tools that require complex, multi-step interactive dialogues unless absolutely necessary.
*   **Error Parsing:** The LLM needs to be able to parse and understand error messages from tool outputs. If a tool's error messages are cryptic, consider wrapping the tool with a simpler interface that translates errors into more LLM-friendly language.
*   **Contextual Tool Selection:** The prompt should reinforce the importance of selecting the *right* tool for the *right* job, as outlined in the implementation plan (e.g., `file_write_text` for writing files, `shell_exec` for running commands).

### 11.2. Advanced Prompt Engineering and Guidance

While the initial prompt is comprehensive, ongoing guidance can be beneficial:

#### 11.2.1. Iterative Prompt Refinement

Observe the LLM's behavior during initial execution. If it consistently struggles with a particular type of task or makes recurring mistakes, refine the prompt or provide more specific examples for that scenario. This might involve:
*   **More Specific Constraints:** If the LLM tries to skip tests, add an explicit constraint like: 


 "You MUST write unit tests for every function you implement. Skipping tests will result in task failure." 
*   **Clarifying Ambiguity:** If the LLM misinterprets an instruction, rephrase it with more explicit language and provide a negative example (e.g., "Do NOT use `os.system` for file operations; use `pathlib` as specified.").
*   **Reinforcing Best Practices:** Remind the LLM of coding best practices (e.g., modularity, error handling, clear variable names) if its generated code consistently falls short.

#### 11.2.2. Contextual Reminders and Guardrails

Even with a comprehensive initial prompt, LLMs can sometimes lose track of specific instructions or constraints over long interactions. Implement mechanisms to provide contextual reminders:
*   **Pre-task Checklists:** Before each task, present the LLM with a mini-checklist derived from the main prompt (e.g., "Before starting this task, confirm: 1. I have selected the correct task. 2. I have a work log active. 3. I will justify all actions. 4. I will commit incrementally.").
*   **Automated Feedback Loops:** The `LLMGuard` and `TaskSystemEnforcer` components are designed for this. Ensure their feedback messages are clear, actionable, and directly reference the violated rule from the prompt. For example, instead of just "Action blocked," provide "Action blocked: Insufficient justification. Remember to explain how this action advances the current task as per your operational framework."
*   **Periodic Reinforcement:** For very long-running projects, consider periodically re-injecting key sections of the initial prompt (e.g., the "Operational Framework" or "Core Principle") to refresh the LLM's memory.

#### 11.2.3. Example-Driven Learning

LLMs learn effectively from examples. Provide concrete examples of desired behavior:
*   **Good Commit Messages:** Show examples of well-structured, atomic commit messages.
*   **Correct Tool Usage:** Demonstrate how to use specific tools correctly for a given task.
*   **Desired Code Style:** If you have a preferred coding style, provide examples of code that adheres to it.

### 11.3. Monitoring and Intervention Strategies

Even with the best prompts and environment, human oversight remains crucial, especially in the early stages of an LLM-driven project.

#### 11.3.1. Active Human Monitoring

*   **Real-time Log Analysis:** Monitor the LLM's output and tool usage logs in real-time. The structured logging (Phase 10.1) will be invaluable here.
*   **Progress Tracking:** Regularly check the `project/status` endpoint of the MCP Server or the VSCode extension's tree view to track task progression.
*   **Code Review:** Periodically review the code generated by the LLM. Focus on architectural adherence, code quality, and test coverage.

#### 11.3.2. Strategic Intervention

When the LLM deviates or gets stuck, intervene strategically:
*   **Corrective Feedback:** Instead of just restarting, provide specific, actionable feedback. "The `create_file` function should use `pathlib.Path` objects, not raw strings, for the `path` argument. Please refactor it to accept `Path` objects." 
*   **Re-prompting:** If the LLM is completely off track, consider stopping the current task, providing a refined prompt for that specific task, and then restarting it.
*   **Emergency Controls:** The `emergency_unlock()` and `reset_task_state()` functions in `task_enforcer.py` are designed for critical interventions. Use them judiciously when the system is in an unrecoverable state or requires immediate human override.

### 11.4. Leveraging LLM Strengths and Mitigating Weaknesses

#### 11.4.1. Strengths to Leverage:
*   **Rapid Prototyping:** LLMs can generate boilerplate code and initial implementations very quickly.
*   **Pattern Recognition:** They are good at recognizing and applying coding patterns.
*   **Documentation Generation:** Excellent for generating comments, docstrings, and basic documentation.
*   **Refactoring (with guidance):** Can perform refactoring tasks if given clear instructions and constraints.

#### 11.4.2. Weaknesses to Mitigate:
*   **Lack of True Understanding:** LLMs don't 


possess true understanding or common sense. They operate based on patterns learned from training data. This means they might generate syntactically correct but semantically incorrect code, or make logical errors.
    *   **Mitigation:** Rigorous testing (unit, integration, end-to-end), strong validation mechanisms (like `LLMGuard`), and human code review are essential. The Gatekeeper's role in validating outputs is critical here.
*   **Hallucinations/Confabulations:** LLMs can generate plausible-sounding but entirely false information, including non-existent functions, libraries, or APIs.
    *   **Mitigation:** The `LLMGuard`'s enforcement layer should prevent the use of non-existent tools or unauthorized file paths. The prompt should explicitly state that the LLM must only use tools and libraries that are either provided or explicitly installed within the environment. For code generation, emphasize using standard libraries or explicitly defined project modules.
*   **Context Window Limitations:** While modern LLMs have large context windows, for very large projects, they can still lose track of information that falls outside the current window. 
    *   **Mitigation:** The Gatekeeper's role in providing *only* the necessary context for the current task is key. For the LLM acting as the 

