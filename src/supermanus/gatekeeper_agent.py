# src/supermanus/gatekeeper_agent.py
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .session_manager import SessionManager
from .task_enforcer import TaskEnforcer
from .llm_guard import LLMGuard


class GatekeeperAgent:
    """
    The Gatekeeper Agent manages the overall project orchestration.
    """

    def __init__(self, project_root: Path):
        """
        Initializes the GatekeeperAgent.

        Args:
            project_root (Path): The project root directory.
        """
        self.project_root = project_root
        self.session_manager = SessionManager(str(project_root / "session_state.json"))
        self.task_enforcer = TaskEnforcer(self.session_manager)
        self.llm_guard = LLMGuard()
        self.logger = logging.getLogger(__name__)

    def load_project_plan(self, plan: Dict[str, Any]) -> None:
        """
        Loads the project plan.

        Args:
            plan (Dict[str, Any]): The project plan.
        """
        self.task_enforcer.load_project_plan(plan)
        self.logger.info("Project plan loaded by Gatekeeper.")

    def run_orchestration_loop(self) -> None:
        """
        Runs the orchestration loop to assign tasks.
        """
        task = self.task_enforcer.assign_next_task()
        if task:
            self.logger.info(f"Orchestration: Assigned task {task['id']}")
            # In a real system, this would dispatch to Coding Agent
        else:
            self.logger.info("Orchestration: No tasks to assign.")

    def receive_coding_agent_report(self, task_id: str, status: str, output: Optional[str] = None, error: Optional[str] = None) -> None:
        """
        Receives a report from the Coding Agent.

        Args:
            task_id (str): The task ID.
            status (str): The status ('completed' or 'failed').
            output (Optional[str]): The output.
            error (Optional[str]): The error message.
        """
        if status == "completed":
            self.task_enforcer.mark_task_completed(task_id)
            self.logger.info(f"Task {task_id} completed.")
        elif status == "failed":
            self.task_enforcer.mark_task_failed(task_id, error or "Unknown error")
            self.logger.error(f"Task {task_id} failed: {error}")
        else:
            self.logger.warning(f"Unknown status for task {task_id}: {status}")

    def get_status(self) -> Dict[str, Any]:
        """
        Gets the project status.

        Returns:
            Dict[str, Any]: The status.
        """
        return self.task_enforcer.get_status()


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    project_root = Path(".")
    gatekeeper = GatekeeperAgent(project_root)
    plan = {
        "tasks": [
            {"id": "GK1", "description": "Gatekeeper test task", "status": "pending"}
        ]
    }
    gatekeeper.load_project_plan(plan)
    print("Status:", gatekeeper.get_status())
    gatekeeper.run_orchestration_loop()
    print("Status after orchestration:", gatekeeper.get_status())
    gatekeeper.receive_coding_agent_report("GK1", "completed", "Test output")
    print("Status after report:", gatekeeper.get_status())
