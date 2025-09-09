# src/supermanus/coding_agent.py
import logging
from typing import Dict, Any, Optional, Callable


class CodingAgent:
    """
    The Coding Agent executes individual tasks with limited context.
    """

    def __init__(self, report_callback: Optional[Callable[[str, str, Optional[str], Optional[str]], None]] = None):
        """
        Initializes the CodingAgent.

        Args:
            report_callback (Optional[Callable]): Callback to report to Gatekeeper.
        """
        self.report_callback = report_callback
        self.current_task: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger(__name__)

    def assign_task(self, task: Dict[str, Any]) -> None:
        """
        Assigns a task to the Coding Agent.

        Args:
            task (Dict[str, Any]): The task.
        """
        self.current_task = task
        self.logger.info(f"Task assigned: {task['id']}")

    def execute_task(self) -> None:
        """
        Executes the current task.
        """
        if not self.current_task:
            self.logger.warning("No task assigned.")
            return

        task_id = self.current_task["id"]
        self.logger.info(f"Executing task {task_id}")

        try:
            # Simulate task execution
            # In a real implementation, this would perform actual coding actions
            result = f"Task {task_id} executed successfully."
            self.report_completion(result)
        except Exception as e:
            self.report_failure(str(e))

    def report_completion(self, output: str) -> None:
        """
        Reports task completion.

        Args:
            output (str): The output.
        """
        if self.report_callback and self.current_task:
            self.report_callback(self.current_task["id"], "completed", output, None)
            self.logger.info(f"Reported completion for task {self.current_task['id']}")

    def report_failure(self, error: str) -> None:
        """
        Reports task failure.

        Args:
            error (str): The error message.
        """
        if self.report_callback and self.current_task:
            self.report_callback(self.current_task["id"], "failed", None, error)
            self.logger.error(f"Reported failure for task {self.current_task['id']}: {error}")


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)

    def mock_report(task_id, status, output, error):
        print(f"Report: {task_id} - {status} - {output or error}")

    agent = CodingAgent(mock_report)
    task = {"id": "CA1", "description": "Test coding task"}
    agent.assign_task(task)
    agent.execute_task()
