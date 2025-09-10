# src/supermanus/metrics_collector.py
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from .logging_config import get_logger

logger = get_logger("metrics_collector")


class TaskMetricsCollector:
    """Dedicated collector for task-related metrics"""

    def __init__(self):
        self._lock = threading.Lock()
        # Task completion times by status
        self.task_completion_times = defaultdict(list)
        # Active tasks count over time
        self.active_tasks_history = []
        # Task status transitions
        self.task_status_changes = defaultdict(int)
        # Agent performance by type
        self.agent_performance = defaultdict(lambda: {
            "tasks_assigned": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_completion_time": 0,
            "success_rate": 0
        })

    def record_task_start(self, task_id: str, agent_type: str, risk_level: str):
        """Record when a task starts execution"""
        with self._lock:
            logger.info(
                f"Task {task_id} started by {agent_type}",
                metric="task_started",
                task_id=task_id,
                agent_type=agent_type,
                risk_level=risk_level
            )

            agent_stats = self.agent_performance[agent_type]
            agent_stats["tasks_assigned"] += 1
            self._update_success_rate(agent_type)

    def record_task_completion(self, task_id: str, agent_type: str, start_time: datetime, end_time: datetime, status: str):
        """Record task completion with timing"""
        with self._lock:
            duration = (end_time - start_time).total_seconds()
            self.task_completion_times[status].append(duration)
            self.task_status_changes[status] += 1

            agent_stats = self.agent_performance[agent_type]
            if status == "completed":
                agent_stats["tasks_completed"] += 1
                self._update_avg_completion_time(agent_type, duration)
            elif status == "failed":
                agent_stats["tasks_failed"] += 1

            self._update_success_rate(agent_type)

            logger.info(
                f"Task {task_id} {status} by {agent_type}",
                metric="task_completed",
                task_id=task_id,
                agent_type=agent_type,
                duration_seconds=duration,
                status=status
            )

    def _update_avg_completion_time(self, agent_type: str, new_duration: float):
        """Update average completion time for an agent type"""
        agent_stats = self.agent_performance[agent_type]
        if agent_stats["tasks_completed"] == 1:
            agent_stats["avg_completion_time"] = new_duration
        else:
            # Calculate running average
            total_completed = agent_stats["tasks_completed"]
            current_avg = agent_stats["avg_completion_time"]
            agent_stats["avg_completion_time"] = (current_avg * (total_completed - 1) + new_duration) / total_completed

    def _update_success_rate(self, agent_type: str):
        """Update success rate for an agent type"""
        agent_stats = self.agent_performance[agent_type]
        total_tasks = agent_stats["tasks_assigned"]
        if total_tasks > 0:
            successful_tasks = agent_stats["tasks_completed"]
            agent_stats["success_rate"] = successful_tasks / total_tasks

    def get_task_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive task metrics summary"""
        with self._lock:
            summary = {
                "total_tasks_by_status": dict(self.task_status_changes),
                "task_completion_stats": {},
                "agent_performance": dict(self.agent_performance),
                "generated_at": datetime.utcnow().isoformat()
            }

            # Calculate stats for each task status
            for status, times in self.task_completion_times.items():
                if times:
                    summary["task_completion_stats"][status] = {
                        "count": len(times),
                        "avg_duration": sum(times) / len(times),
                        "max_duration": max(times),
                        "min_duration": min(times),
                        "total_duration": sum(times)
                    }

            # Overall system stats
            total_completed = sum(stats["tasks_completed"] for stats in self.agent_performance.values())
            total_failed = sum(stats["tasks_failed"] for stats in self.agent_performance.values())
            total_tasks = total_completed + total_failed

            if total_tasks > 0:
                summary["system_stats"] = {
                    "total_tasks_processed": total_tasks,
                    "overall_success_rate": total_completed / total_tasks,
                    "agent_types_count": len(self.agent_performance)
                }

            return summary


class SystemHealthCollector:
    """Collect system health and performance metrics"""

    def __init__(self):
        self._lock = threading.Lock()
        # API request metrics
        self.api_requests = defaultdict(lambda: {"count": 0, "errors": 0, "avg_duration": 0})
        # Memory usage approximations
        self.request_times = []
        # Error counts by type
        self.error_counts = defaultdict(int)

    def record_api_request(self, endpoint: str, method: str, duration: float, success: bool = True):
        """Record API request metrics"""
        with self._lock:
            api_key = f"{method}:{endpoint}"
            metrics = self.api_requests[api_key]

            metrics["count"] += 1
            if not success:
                metrics["errors"] += 1

            # Update average duration (running average)
            if metrics["avg_duration"] == 0:
                metrics["avg_duration"] = duration
            else:
                metrics["avg_duration"] = (metrics["avg_duration"] + duration) / 2

            logger.info(
                f"API request {method}:{endpoint}",
                metric="api_request",
                endpoint=endpoint,
                method=method,
                duration_seconds=duration,
                success=success
            )

    def record_error(self, error_type: str, error_message: str):
        """Record error occurrence"""
        with self._lock:
            self.error_counts[error_type] += 1

            logger.error(
                f"System error: {error_message}",
                metric="system_error",
                error_type=error_type,
                error_message=error_message,
                total_errors_for_type=self.error_counts[error_type]
            )

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics"""
        with self._lock:
            health_data = {
                "api_requests": dict(self.api_requests),
                "error_counts": dict(self.error_counts),
                "total_errors": sum(self.error_counts.values()),
                "timestamp": datetime.utcnow().isoformat()
            }

            # Calculate error rate
            total_requests = sum(metrics["count"] for metrics in self.api_requests.values())
            total_errors = sum(metrics["errors"] for metrics in self.api_requests.values())

            health_data["error_rate"] = total_errors / total_requests if total_requests > 0 else 0
            health_data["total_requests"] = total_requests

            return health_data


# Global instances
_task_collector = TaskMetricsCollector()
_health_collector = SystemHealthCollector()


def get_task_metrics_collector() -> TaskMetricsCollector:
    """Get the global task metrics collector"""
    return _task_collector


def get_health_metrics_collector() -> SystemHealthCollector:
    """Get the global health metrics collector"""
    return _health_collector


def get_all_metrics() -> Dict[str, Any]:
    """Get all collected metrics"""
    return {
        "task_metrics": _task_collector.get_task_metrics_summary(),
        "health_metrics": _health_collector.get_health_metrics(),
        "combined_summary": {
            "collected_at": datetime.utcnow().isoformat(),
            "total_metrics_types": 2
        }
    }


# Performance monitoring decorators
def monitor_task(func):
    """Decorator to monitor task execution"""
    def wrapper(*args, **kwargs):
        start_time = datetime.utcnow()
        success = False

        try:
            # Extract task info if available
            task_info = {}
            for arg in args:
                if isinstance(arg, dict) and "task_id" in arg:
                    task_info.update(arg)
                    break

            func(*args, **kwargs)
            success = True

        except Exception as e:
            success = False
            raise
        finally:
            end_time = datetime.utcnow()
            if task_info:
                agent_type = task_info.get("assigned_to", "unknown")
                risk_level = task_info.get("risk_level", "unknown")
                task_id = task_info.get("task_id", "unknown")

                status = "completed" if success else "failed"
                _task_collector.record_task_completion(task_id, agent_type, start_time, end_time, status)

                # Record task start as well (in a real system this would be recorded separately)
                _task_collector.record_task_start(task_id, agent_type, risk_level)

    return wrapper


def monitor_api_call(func):
    """Decorator to monitor API call performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = False

        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            _health_collector.record_error("api_error", str(e))
            raise
        finally:
            duration = time.time() - start_time
            # In a real system, you'd extract the endpoint and method from the request
            _health_collector.record_api_request("/api/unknown", "POST", duration, success)

    return wrapper


# Example usage and testing
if __name__ == "__main__":
    # Test the collectors
    logger = get_logger("test_metrics")

    # Test task metrics
    task_collector = get_task_metrics_collector()

    # Simulate some task completions
    task_collector.record_task_start("TASK_001", "Coding Agent", "medium")
    start = datetime.utcnow()
    time.sleep(0.1)  # Simulate work
    end = datetime.utcnow()
    task_collector.record_task_completion("TASK_001", "Coding Agent", start, end, "completed")

    task_collector.record_task_start("TASK_002", "Gatekeeper", "low")
    start2 = datetime.utcnow()
    time.sleep(0.05)
    end2 = datetime.utcnow()
    task_collector.record_task_completion("TASK_002", "Gatekeeper", start2, end2, "failed")

    # Test health metrics
    health_collector = get_health_metrics_collector()
    health_collector.record_api_request("/api/tasks", "GET", 0.0023, True)
    health_collector.record_api_request("/api/project", "POST", 0.0018, False)
    health_collector.record_error("validation_error", "Invalid project plan format")

    # Get all metrics
    all_metrics = get_all_metrics()

    logger.info("Metrics collection test completed", all_metrics=all_metrics)
    print(f"Collected metrics: {len(all_metrics)} categories")

    # Print summary
    summary = task_collector.get_task_metrics_summary()
    print(f"Tasks processed: {sum(summary['total_tasks_by_status'].values())}")
    print(f"Success rate: {summary.get('system_stats', {}).get('overall_success_rate', 0):.2%}")

    health_summary = health_collector.get_health_metrics()
    print(f"Total API requests: {health_summary['total_requests']}")
    print(f"Error rate: {health_summary['error_rate']:.2%}")