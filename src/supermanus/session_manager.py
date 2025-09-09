# src/supermanus/session_manager.py
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional


class SessionManager:
    """
    Manages the session state for the Miss_TaskMaster application.
    Handles loading and saving state to/from a JSON file.
    """

    def __init__(self, state_file: str = "session_state.json"):
        """
        Initializes the SessionManager.

        Args:
            state_file (str): Path to the state file.
        """
        self.state_file = Path(state_file)
        self.state: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def load_state(self) -> Dict[str, Any]:
        """
        Loads the state from the file.

        Returns:
            Dict[str, Any]: The loaded state.
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                self.logger.info(f"State loaded from {self.state_file}")
            except (json.JSONDecodeError, IOError) as e:
                self.logger.error(f"Error loading state: {e}")
                self.state = {}
        else:
            self.logger.info(f"State file {self.state_file} does not exist. Starting with empty state.")
            self.state = {}
        return self.state

    def save_state(self, state: Optional[Dict[str, Any]] = None) -> None:
        """
        Saves the state to the file.

        Args:
            state (Optional[Dict[str, Any]]): The state to save. If None, uses current state.
        """
        if state is not None:
            self.state = state
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            self.logger.info(f"State saved to {self.state_file}")
        except IOError as e:
            self.logger.error(f"Error saving state: {e}")

    def get_state(self) -> Dict[str, Any]:
        """
        Gets the current state.

        Returns:
            Dict[str, Any]: The current state.
        """
        return self.state

    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Updates the state with new values.

        Args:
            updates (Dict[str, Any]): The updates to apply.
        """
        self.state.update(updates)
        self.logger.debug(f"State updated: {updates}")


if __name__ == "__main__":
    # Simple test
    logging.basicConfig(level=logging.INFO)
    manager = SessionManager()
    manager.load_state()
    print("Loaded state:", manager.get_state())
    manager.update_state({"current_task": "test_task", "status": "in_progress"})
    manager.save_state()
    print("Updated and saved state:", manager.get_state())
