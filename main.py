#!/usr/bin/env python3
# main.py
import argparse
import json
import logging
from pathlib import Path
from src.supermanus.gatekeeper_agent import GatekeeperAgent
from src.supermanus.coding_agent import CodingAgent
from src.supermanus.logging_config import setup_logging


def main():
    parser = argparse.ArgumentParser(description="Miss_TaskMaster CLI")
    parser.add_argument("command", choices=["load_plan", "run", "status", "execute_task"], help="Command to run")
    parser.add_argument("--plan_file", help="Path to project plan JSON file")
    parser.add_argument("--task_id", help="Task ID for execution")
    parser.add_argument("--log_file", default="miss_taskmaster.log", help="Log file path")
    parser.add_argument("--log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Log level")

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_file, getattr(logging, args.log_level))

    # Initialize components
    project_root = Path(".")
    gatekeeper = GatekeeperAgent(project_root)
    coding_agent = CodingAgent(gatekeeper.receive_coding_agent_report)

    if args.command == "load_plan":
        if not args.plan_file:
            print("Error: --plan_file required for load_plan")
            return
        with open(args.plan_file, 'r') as f:
            plan = json.load(f)
        gatekeeper.load_project_plan(plan)
        print("Project plan loaded.")

    elif args.command == "run":
        gatekeeper.run_orchestration_loop()
        print("Orchestration loop run.")

    elif args.command == "status":
        status = gatekeeper.get_status()
        print(json.dumps(status, indent=2))

    elif args.command == "execute_task":
        if not args.task_id:
            print("Error: --task_id required for execute_task")
            return
        # For simplicity, assign a dummy task
        task = {"id": args.task_id, "description": f"Execute task {args.task_id}"}
        coding_agent.assign_task(task)
        coding_agent.execute_task()
        print(f"Task {args.task_id} executed.")


if __name__ == "__main__":
    main()
