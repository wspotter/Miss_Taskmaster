# src/supermanus/llm_guard.py
import logging
from typing import Dict, Any, List, Optional


class LLMGuard:
    """
    Guards LLM actions to ensure they comply with rules and constraints.
    """

    def __init__(self, rules: Optional[List[str]] = None):
        """
        Initializes the LLMGuard.

        Args:
            rules (Optional[List[str]]): List of rules to enforce.
        """
        self.rules = rules or [
            "Do not deviate from the assigned task.",
            "Always justify actions with reference to the current task.",
            "Do not perform unauthorized file operations.",
            "Validate inputs and outputs.",
        ]
        self.logger = logging.getLogger(__name__)

    def validate_action(self, action: str, context: Dict[str, Any]) -> bool:
        """
        Validates an action against the rules.

        Args:
            action (str): The action to validate.
            context (Dict[str, Any]): The context.

        Returns:
            bool: True if valid, False otherwise.
        """
        # Simple validation logic
        current_task = context.get("current_task")
        if not current_task:
            self.logger.warning("No current task assigned.")
            return False

        if "justification" not in context:
            self.logger.warning("Action lacks justification.")
            return False

        # Check if action is related to current task
        if current_task not in action and current_task not in context.get("justification", ""):
            self.logger.warning("Action not related to current task.")
            return False

        self.logger.info("Action validated.")
        return True

    def check_constraints(self, data: Dict[str, Any]) -> bool:
        """
        Checks constraints on data.

        Args:
            data (Dict[str, Any]): The data to check.

        Returns:
            bool: True if constraints met, False otherwise.
        """
        # Example constraints
        if "file_path" in data:
            path = data["file_path"]
            if ".." in path or path.startswith("/"):
                self.logger.warning("Potentially unsafe file path.")
                return False

        self.logger.info("Constraints checked.")
        return True

    def enforce_rules(self, action: str, context: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        Enforces all rules and constraints.

        Args:
            action (str): The action.
            context (Dict[str, Any]): The context.
            data (Dict[str, Any]): The data.

        Returns:
            bool: True if all checks pass, False otherwise.
        """
        if not self.validate_action(action, context):
            return False
        if not self.check_constraints(data):
            return False
        return True


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    guard = LLMGuard()
    context = {"current_task": "test_task", "justification": "Testing the guard."}
    data = {"file_path": "safe/path"}
    result = guard.enforce_rules("test_action", context, data)
    print("Guard result:", result)
