# src/supermanus/task_enforcer.py
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from .session_manager import SessionManager


class TaskEnforcer:
    """
    Enforces task execution rules and manages project progress.
    """

    def __init__(self, session_manager: SessionManager):
        """
        Initializes the TaskEnforcer.

        Args:
            session_manager (SessionManager): The session manager instance.
        """
        self.session_manager = session_manager
        self.project_tasks: List[Dict[str, Any]] = []
        self.current_task: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger(__name__)

    def load_project_plan(self, plan: Dict[str, Any]) -> None:
        """
        Loads the project plan.

        Args:
            plan (Dict[str, Any]): The project plan.
        """
        self.project_tasks = plan.get("tasks", [])
        state = self.session_manager.load_state()
        state["project_tasks"] = self.project_tasks
        self.session_manager.save_state(state)
        self.logger.info("Project plan loaded.")

    def get_status(self) -> Dict[str, Any]:
        """
        Gets the current status of the project.

        Returns:
            Dict[str, Any]: The status.
        """
        state = self.session_manager.get_state()
        return {
            "current_task": self.current_task,
            "project_tasks": self.project_tasks,
            "overall_status": state.get("overall_status", "not_started"),
            "completed_tasks": [t for t in self.project_tasks if t.get("status") == "completed"],
            "pending_tasks": [t for t in self.project_tasks if t.get("status") != "completed"]
        }

    def assign_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Assigns the next pending task.

        Returns:
            Optional[Dict[str, Any]]: The next task.
        """
        for task in self.project_tasks:
            if task.get("status") != "completed":
                self.current_task = task
                state = self.session_manager.get_state()
                state["current_task"] = self.current_task
                self.session_manager.save_state(state)
                self.logger.info(f"Assigned task: {task['id']}")
                return task
        self.current_task = None
        self.logger.info("No more tasks to assign.")
        return None

    def mark_task_completed(self, task_id: str) -> None:
        """
        Marks a task as completed.

        Args:
            task_id (str): The task ID.
        """
        for task in self.project_tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                self.logger.info(f"Task {task_id} marked as completed.")
                break
        state = self.session_manager.get_state()
        state["project_tasks"] = self.project_tasks
        self.session_manager.save_state(state)

    def mark_task_failed(self, task_id: str, error: str) -> None:
        """
        Marks a task as failed.

        Args:
            task_id (str): The task ID.
            error (str): The error message.
        """
        for task in self.project_tasks:
            if task["id"] == task_id:
                task["status"] = "failed"
                task["error"] = error
                self.logger.error(f"Task {task_id} failed: {error}")
                break
        state = self.session_manager.get_state()
        state["project_tasks"] = self.project_tasks
        self.session_manager.save_state(state)


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    session_manager = SessionManager()
    enforcer = TaskEnforcer(session_manager)
    plan = {
        "tasks": [
            {"id": "1", "description": "Test task 1", "status": "pending"},
            {"id": "2", "description": "Test task 2", "status": "pending"}
        ]
    }
    enforcer.load_project_plan(plan)
    print("Status:", enforcer.get_status())
    task = enforcer.assign_next_task()
    print("Assigned task:", task)
    if task:
        enforcer.mark_task_completed(task["id"])
    print("Status after completion:", enforcer.get_status())
