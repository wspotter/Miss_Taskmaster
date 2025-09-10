#!/usr/bin/env python3
"""
Client Integration Example for Miss_TaskMaster MCP Server

This script demonstrates how external applications can interact with
the Miss_TaskMaster MCP Server using its REST APIs.
"""

import requests
import json
import time
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServerClient:
    """Client for interacting with the Miss_TaskMaster MCP Server"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def health_check(self) -> Dict[str, Any]:
        """Check if MCP server is healthy"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def init_project(self, plan_file: str) -> Dict[str, Any]:
        """Initialize a project with a plan file"""
        payload = {"plan_file": plan_file}
        response = requests.post(f"{self.base_url}/project/init", json=payload)
        response.raise_for_status()
        return response.json()

    def get_project_status(self) -> Dict[str, Any]:
        """Get current project status"""
        response = requests.get(f"{self.base_url}/project/status")
        response.raise_for_status()
        return response.json()

    def run_orchestration(self) -> Dict[str, Any]:
        """Trigger the Gatekeeper agent's orchestration loop"""
        response = requests.post(f"{self.base_url}/orchestration/run")
        response.raise_for_status()
        return response.json()

    def report_task(self, task_id: str, status: str, output: Optional[str] = None, error: Optional[str] = None) -> Dict[str, Any]:
        """Report a task completion or failure"""
        payload = {
            "task_id": task_id,
            "status": status,
        }
        if output:
            payload["output"] = output
        if error:
            payload["error"] = error

        response = requests.post(f"{self.base_url}/task/report", json=payload)
        response.raise_for_status()
        return response.json()

    def get_logs(self) -> str:
        """Get MCP server logs"""
        response = requests.get(f"{self.base_url}/logs")
        response.raise_for_status()
        return response.text

    def get_task_list(self) -> Dict[str, Any]:
        """Get list of all project tasks"""
        response = requests.get(f"{self.base_url}/tasks")
        response.raise_for_status()
        return response.json()


def main():
    """Example usage of MCP Server Client"""
    logger.info("Miss_TaskMaster MCP Server Client Example")
    logger.info("=" * 50)

    # Initialize client
    client = MCPServerClient()

    try:
        # 1. Health check
        logger.info("1. Checking MCP server health...")
        health = client.health_check()
        logger.info(f"Health status: {health}")

        # 2. Initialize project
        logger.info("\n2. Initializing project...")
        init_response = client.init_project("project_plan_template.json")
        logger.info(f"Init response: {init_response}")

        # 3. Get initial status
        logger.info("\n3. Getting project status...")
        status = client.get_project_status()
        logger.info(f"Project has {status.get('active_tasks_available', 0)} active tasks")

        # 4. Run orchestration (this will dispatch the first task)
        logger.info("\n4. Starting orchestration...")
        orch_response = client.run_orchestration()
        logger.info(f"Orchestration: {orch_response}")

        # 5. Wait a moment for processing
        time.sleep(2)

        # 6. Check status after orchestration
        logger.info("\n5. Getting updated status...")
        updated_status = client.get_project_status()
        current_task = updated_status.get('current_task', {})
        if current_task:
            logger.info(f"Current active task: {current_task.get('id')} - {current_task.get('title')}")
        else:
            logger.info("No active tasks currently")

        # 7. Get task list
        logger.info("\n6. Getting task list...")
        tasks = client.get_task_list()
        logger.info(f"Total tasks in project: {tasks.get('total_count', 0)}")

        # 8. Get logs (last 200 characters to avoid spam)
        logger.info("\n7. Getting recent logs...")
        logs = client.get_logs()
        recent_logs = logs[-200:] if len(logs) > 200 else logs
        logger.info(f"Recent logs: {recent_logs}")

        # Example: Simulate task completion (if a task was dispatched)
        if current_task:
            task_id = current_task.get('id')
            logger.info(f"\n8. Simulating completion of task {task_id}...")
            report_response = client.report_task(
                task_id=task_id,
                status="completed",
                output=f"Successfully completed {task_id} via client integration"
            )
            logger.info(f"Task completion report: {report_response}")

        logger.info("\n" + "=" * 50)
        logger.info("MCP Client example completed successfully!")

    except requests.exceptions.ConnectionError:
        logger.error("❌ Could not connect to MCP server. Make sure it's running on http://localhost:8000")
        logger.info("Run: cd mcp_server && python main.py")
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP error: {e}")
        logger.error(f"Response: {e.response.text if hasattr(e.response, 'text') else 'No response'}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()