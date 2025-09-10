# src/supermanus/logging_config.py
import logging
import sys
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class StructuredLogger:
    """Enhanced logger with structured logging capabilities"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        # Store structured data for current context
        self._context_data: Dict[str, Any] = {}
        self._local = threading.local()

    def with_context(self, **kwargs) -> 'StructuredLogger':
        """Add contextual information to all log messages"""
        self._context_data.update(kwargs)
        return self

    def clear_context(self) -> None:
        """Clear all contextual information"""
        self._context_data.clear()

    def _get_full_context(self, **extra) -> Dict[str, Any]:
        """Get the full context including both stored context and provided extra data"""
        full_context = dict(self._context_data)
        full_context.update(extra)
        return full_context

    def debug(self, message: str, **extra):
        self.logger.debug(message, extra=self._get_full_context(**extra))

    def info(self, message: str, **extra):
        self.logger.info(message, extra=self._get_full_context(**extra))

    def warning(self, message: str, **extra):
        self.logger.warning(message, extra=self._get_full_context(**extra))

    def error(self, message: str, exc_info: bool = None, **extra):
        self.logger.error(message, exc_info=exc_info, extra=self._get_full_context(**extra))

    def critical(self, message: str, **extra):
        self.logger.critical(message, extra=self._get_full_context(**extra))

    def exception(self, message: str, **extra):
        self.logger.exception(message, extra=self._get_full_context(**extra))


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        # Base log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra structured data if enabled and present
        if self.include_extra and hasattr(record, 'extra') and record.extra:
            # Ensure extra data is JSON serializable
            sanitized_extra = self._sanitize_for_json(record.extra)
            log_data["extra"] = sanitized_extra

        # Add task and agent context if available
        if hasattr(record, 'task_id'):
            log_data["task_id"] = record.task_id

        return json.dumps(log_data, default=str, separators=(',', ':'))

    def _sanitize_for_json(self, data: Any) -> Any:
        """Ensure data is JSON serializable"""
        if isinstance(data, dict):
            return {k: self._sanitize_for_json(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._sanitize_for_json(item) for item in data]
        elif isinstance(data, (str, int, float, bool)) or data is None:
            return data
        else:
            return str(data)


class MetricsCollector:
    """Collect basic metrics for system monitoring"""

    def __init__(self):
        self._metrics = {}
        self._lock = threading.Lock()

    def increment_counter(self, name: str, amount: int = 1, **labels):
        """Increment a counter metric"""
        with self._lock:
            key = self._make_key(name, labels)
            if key not in self._metrics:
                self._metrics[key] = {
                    "name": name,
                    "type": "counter",
                    "value": 0,
                    "labels": labels,
                    "created_at": datetime.utcnow().isoformat()
                }
            self._metrics[key]["value"] += amount
            self._metrics[key]["last_updated"] = datetime.utcnow().isoformat()

    def record_timing(self, name: str, duration_seconds: float, **labels):
        """Record timing metric"""
        with self._lock:
            key = self._make_key(name, labels)
            if key not in self._metrics:
                self._metrics[key] = {
                    "name": name,
                    "type": "timing",
                    "samples": [],
                    "count": 0,
                    "avg_duration": 0,
                    "max_duration": 0,
                    "min_duration": float('inf'),
                    "labels": labels,
                    "created_at": datetime.utcnow().isoformat()
                }

            metric = self._metrics[key]
            metric["samples"].append(duration_seconds)
            metric["count"] += 1
            metric["avg_duration"] = sum(metric["samples"]) / len(metric["samples"])
            metric["max_duration"] = max(metric["max_duration"], duration_seconds)
            metric["min_duration"] = min(metric["min_duration"], duration_seconds)
            metric["last_updated"] = datetime.utcnow().isoformat()

    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        with self._lock:
            return dict(self._metrics)

    def get_metric_summary(self) -> Dict[str, Any]:
        """Get summary of key metrics"""
        with self._lock:
            summary = {
                "total_metrics": len(self._metrics),
                "counters": {},
                "timings": {},
                "timestamp": datetime.utcnow().isoformat()
            }

            for key, metric in self._metrics.items():
                if metric["type"] == "counter":
                    summary["counters"][metric["name"]] = metric["value"]
                elif metric["type"] == "timing":
                    summary["timings"][metric["name"]] = {
                        "count": metric["count"],
                        "avg_duration": metric["avg_duration"],
                        "max_duration": metric["max_duration"],
                        "min_duration": metric["min_duration"]
                    }

            return summary

    def _make_key(self, name: str, labels: Dict[str, Any]) -> str:
        """Create unique key from metric name and labels"""
        if labels:
            label_parts = [f"{k}={v}" for k, v in sorted(labels.items())]
            return f"{name}#{','.join(label_parts)}"
        return name


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance"""
    return _metrics_collector


def setup_logging(
    log_file: str = "app.log",
    level: int = logging.INFO,
    json_format: bool = True,
    include_structured_logs: bool = True
) -> StructuredLogger:
    """
    Sets up advanced logging configuration with structured logging and metrics support.

    Args:
        log_file (str): Path to the log file.
        level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
        json_format (bool): Whether to use JSON format for logs.
        include_structured_logs (bool): Whether to include structured logging capabilities.
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create appropriate formatter
    if json_format:
        formatter = JsonFormatter(include_extra=include_structured_logs)
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    # File handler
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        "%(levelname)s - %(name)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    root_logger.addHandler(console_handler)

    # Create structured logger instance
    structured_logger = StructuredLogger("supermanus.app")
    structured_logger.info(
        f"Enhanced logging configured. JSON: {json_format}, Structured: {include_structured_logs}",
        log_file=str(log_path),
        level=logging.getLevelName(level),
        timestamp_setup=datetime.utcnow().isoformat()
    )

    return structured_logger


# Convenience functions for backward compatibility
def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance (backward compatibility)"""
    return StructuredLogger(name)


def log_performance(func_name: str, duration: float, result_success: bool = True):
    """ Convenience function to log performance metrics """
    collector = get_metrics_collector()
    collector.record_timing(
        "function_duration",
        duration,
        function=func_name,
        success=result_success
    )

    logger = get_logger("performance")
    logger.info(
        f"Function {func_name} completed",
        duration_seconds=duration,
        success=result_success,
        metric="performance"
    )


# Performance timing decorator
def timed(func):
    """Decorator to automatically time and log function performance"""
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            log_performance(func.__name__, duration, success)

        return result

    return wrapper
