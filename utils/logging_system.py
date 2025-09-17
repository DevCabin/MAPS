"""
Comprehensive Logging System for Multi-Agent Product Listing System

This module provides structured logging, error tracking, and monitoring
capabilities for the entire system.
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs with contextual information.
    Suitable for production environments and log aggregation systems.
    """

    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize structured logger.

        Args:
            name: Logger name
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatters
        json_formatter = JsonFormatter()
        console_formatter = ConsoleFormatter()

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File handler (if specified)
        if log_file:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)

        # Error file handler
        error_file = log_file.replace('.log', '_errors.log') if log_file else 'errors.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        self.logger.addHandler(error_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        """Format log record as JSON."""

        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'pipeline_id'):
            log_entry["pipeline_id"] = record.pipeline_id
        if hasattr(record, 'agent_type'):
            log_entry["agent_type"] = record.agent_type
        if hasattr(record, 'stage'):
            log_entry["stage"] = record.stage

        return json.dumps(log_entry)

class ConsoleFormatter(logging.Formatter):
    """Human-readable console formatter with colors."""

    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m'   # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        """Format log record for console output."""

        color = self.COLORS.get(record.levelname, '')
        reset = self.RESET

        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')

        # Base format
        message = f"{color}[{timestamp}] {record.levelname:8} {record.name:20} {record.getMessage()}{reset}"

        # Add context if available
        context_parts = []
        if hasattr(record, 'pipeline_id'):
            context_parts.append(f"pipeline={record.pipeline_id[:8]}")
        if hasattr(record, 'agent_type'):
            context_parts.append(f"agent={record.agent_type}")
        if hasattr(record, 'stage'):
            context_parts.append(f"stage={record.stage}")

        if context_parts:
            message += f" [{', '.join(context_parts)}]"

        return message

class LoggerAdapter:
    """
    Adapter to add contextual information to log records.
    Useful for adding pipeline_id, agent_type, etc. to all log messages.
    """

    def __init__(self, logger: logging.Logger, extra: Dict[str, Any]):
        """
        Initialize logger adapter.

        Args:
            logger: Base logger instance
            extra: Extra fields to add to log records
        """
        self.logger = logger
        self.extra = extra

    def _log(self, level, message, *args, **kwargs):
        """Log message with extra context."""
        if self.logger.isEnabledFor(level):
            record = self.logger.makeRecord(
                self.logger.name, level, "", 0, message, args, None, 
                extra=self.extra, **kwargs
            )
            self.logger.handle(record)

    def debug(self, message, *args, **kwargs):
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log(logging.INFO, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log(logging.WARNING, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log(logging.ERROR, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log(logging.CRITICAL, message, *args, **kwargs)

class ErrorTracker:
    """
    Error tracking and metrics collection system.
    Tracks error patterns, frequencies, and provides debugging insights.
    """

    def __init__(self):
        """Initialize error tracker."""
        self.error_counts: Dict[str, int] = {}
        self.error_details: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def track_error(self, error_type: str, error_message: str, context: Dict[str, Any] = None):
        """
        Track an error occurrence.

        Args:
            error_type: Type/category of error
            error_message: Error message
            context: Additional context information
        """

        # Increment counter
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # Store details
        if error_type not in self.error_details:
            self.error_details[error_type] = {
                "first_seen": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "count": 0,
                "sample_messages": [],
                "contexts": []
            }

        details = self.error_details[error_type]
        details["last_seen"] = datetime.utcnow().isoformat()
        details["count"] = self.error_counts[error_type]

        # Store sample messages (keep last 5)
        if error_message not in details["sample_messages"]:
            details["sample_messages"].append(error_message)
            if len(details["sample_messages"]) > 5:
                details["sample_messages"].pop(0)

        # Store contexts (keep last 3)
        if context:
            details["contexts"].append(context)
            if len(details["contexts"]) > 3:
                details["contexts"].pop(0)

        self.logger.error(f"Error tracked: {error_type} - {error_message}", extra=context or {})

    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all tracked errors."""

        return {
            "total_error_types": len(self.error_counts),
            "total_error_count": sum(self.error_counts.values()),
            "error_breakdown": dict(self.error_counts),
            "top_errors": sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10],
            "generated_at": datetime.utcnow().isoformat()
        }

    def get_error_details(self, error_type: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific error type."""
        return self.error_details.get(error_type)

def setup_system_logging(log_level: str = "INFO", log_dir: str = "logs") -> Dict[str, logging.Logger]:
    """
    Set up system-wide logging configuration.

    Args:
        log_level: Global log level
        log_dir: Directory for log files

    Returns:
        Dict of configured loggers by component name
    """

    # Create log directory
    Path(log_dir).mkdir(exist_ok=True)

    # Configure loggers for each component
    loggers = {}

    components = [
        "orchestrator",
        "description_agent", 
        "image_agent",
        "ecommerce_agent",
        "base_agent",
        "pipeline"
    ]

    for component in components:
        log_file = Path(log_dir) / f"{component}.log"
        structured_logger = StructuredLogger(
            name=component,
            log_level=log_level,
            log_file=str(log_file)
        )
        loggers[component] = structured_logger.get_logger()

    return loggers
