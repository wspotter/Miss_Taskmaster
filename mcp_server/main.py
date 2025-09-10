# mcp_server/main.py
import sys
from pathlib import Path
import logging
import json
from typing import Dict, Any, List, Optional

# Adjust path for development to access supermanus core
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.supermanus.gatekeeper_agent import GatekeeperAgent
from src.supermanus.logging_config import setup_logging

# Setup logging with JSON format for server logs
mcp_log_file = project_root / "mcp_server.log"
setup_logging(log_file=mcp_log_file, level=logging.INFO, json_format=True)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Context Protocol Server",
    description="FastAPI server providing standardized API access to Miss_TaskMaster's multi-agent system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gatekeeper Agent
gatekeeper_project_root = project_root
gatekeeper = GatekeeperAgent(project_root=gatekeeper_project_root)

# Pydantic models for request/response
class InitProjectRequest(BaseModel):
    plan_file: str

class TaskReportRequest(BaseModel):
    task_id: str
    status: str  # "completed", "failed"
    output: Optional[str] = None
    error: Optional[str] = None

class ProjectStatusResponse(BaseModel):
    current_task: Optional[Dict[str, Any]] = None
    work_log_active: bool = False
    active_tasks_available: int = 0
    validation_history_count: int = 0
    project_tasks: List[Dict[str, Any]] = []

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "ok",
        "message": "MCP Server is running",
        "gatekeeper_status": "initialized"
    }

@app.post("/project/init")
async def init_project(request: InitProjectRequest):
    """Initialize a new project with a plan file"""
    try:
        plan_file_path = project_root / request.plan_file
        if not plan_file_path.exists():
            raise HTTPException(status_code=404, detail=f"Plan file not found: {request.plan_file}")

        with open(plan_file_path, 'r') as f:
            plan_data = json.load(f)

        gatekeeper.load_project_plan(plan_data)

        logger.info(f"Project initialized with plan file: {request.plan_file}")
        return {"message": "Project initialized successfully."}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing project: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error initializing project: {str(e)}")

@app.get("/project/status", response_model=ProjectStatusResponse)
async def get_project_status():
    """Get current project status including tasks and active work"""
    try:
        status = gatekeeper.enforcer.get_status()
        # Include project tasks for comprehensive status
        status["project_tasks"] = gatekeeper.enforcer.project_tasks
        return ProjectStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting project status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting project status: {str(e)}")

@app.post("/orchestration/run")
async def run_orchestration():
    """Trigger the Gatekeeper Agent's orchestration loop"""
    try:
        gatekeeper.run_orchestration_loop()
        logger.info("Orchestration loop initiated")
        return {"message": "Orchestration loop initiated. Check logs for details."}
    except Exception as e:
        logger.error(f"Error running orchestration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error running orchestration: {str(e)}")

@app.post("/task/report")
async def report_task_status(request: TaskReportRequest):
    """Receive task completion/failure reports from Coding Agent"""
    try:
        gatekeeper.receive_coding_agent_report(
            request.task_id,
            request.status,
            output=request.output,
            error=request.error
        )

        logger.info(f"Task report received for {request.task_id} with status: {request.status}")
        return {"message": f"Report received for task {request.task_id} with status {request.status}."}

    except Exception as e:
        logger.error(f"Error processing task report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing task report: {str(e)}")

@app.get("/logs")
async def get_logs():
    """Get server logs for debugging and monitoring"""
    try:
        log_file_path = project_root / "mcp_server.log"
        if log_file_path.exists():
            with open(log_file_path, 'r') as f:
                return f.read()
        return "No logs yet."
    except Exception as e:
        logger.error(f"Error reading logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error reading logs: {str(e)}")

@app.get("/tasks")
async def get_task_list():
    """Get list of all project tasks"""
    try:
        tasks = gatekeeper.enforcer.project_tasks
        return {"tasks": tasks, "total_count": len(tasks)}
    except Exception as e:
        logger.error(f"Error getting task list: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting task list: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )