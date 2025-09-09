"""Enhanced logging and monitoring for the Library Management System."""

import logging
import json
import os
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import queue
import sys


class LogLevel(Enum):
    """Log levels."""
    
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class EventType(Enum):
    """Types of events to monitor."""
    
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ERROR = "error"
    AUDIT = "audit"


@dataclass
class LogEvent:
    """Structured log event."""
    
    timestamp: str
    level: str
    event_type: str
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None
    duration_ms: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class PerformanceMetrics:
    """Performance monitoring metrics."""
    
    def __init__(self):
        """Initialize performance metrics."""
        self.request_count = 0
        self.total_response_time = 0.0
        self.error_count = 0
        self.start_time = time.time()
        
        # Operation-specific metrics
        self.operation_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Resource usage tracking
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
    
    def record_request(self, duration_ms: float, operation: str, success: bool = True) -> None:
        """Record a request metric.
        
        Args:
            duration_ms: Request duration in milliseconds
            operation: Operation name
            success: Whether the operation was successful
        """
        self.request_count += 1
        self.total_response_time += duration_ms
        
        if not success:
            self.error_count += 1
        
        # Track operation-specific metrics
        if operation not in self.operation_metrics:
            self.operation_metrics[operation] = {
                "count": 0,
                "total_time": 0.0,
                "errors": 0,
                "min_time": float('inf'),
                "max_time": 0.0
            }
        
        op_metrics = self.operation_metrics[operation]
        op_metrics["count"] += 1
        op_metrics["total_time"] += duration_ms
        op_metrics["min_time"] = min(op_metrics["min_time"], duration_ms)
        op_metrics["max_time"] = max(op_metrics["max_time"], duration_ms)
        
        if not success:
            op_metrics["errors"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics.
        
        Returns:
            Dictionary with performance statistics
        """
        uptime = time.time() - self.start_time
        avg_response_time = self.total_response_time / max(self.request_count, 1)
        error_rate = (self.error_count / max(self.request_count, 1)) * 100
        
        stats = {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "average_response_time_ms": avg_response_time,
            "error_count": self.error_count,
            "error_rate_percent": error_rate,
            "requests_per_second": self.request_count / max(uptime, 1),
            "operations": {}
        }
        
        # Add operation-specific stats
        for operation, metrics in self.operation_metrics.items():
            stats["operations"][operation] = {
                "count": metrics["count"],
                "average_time_ms": metrics["total_time"] / max(metrics["count"], 1),
                "min_time_ms": metrics["min_time"] if metrics["min_time"] != float('inf') else 0,
                "max_time_ms": metrics["max_time"],
                "error_count": metrics["errors"],
                "error_rate_percent": (metrics["errors"] / max(metrics["count"], 1)) * 100
            }
        
        return stats


class SecurityMonitor:
    """Security event monitoring."""
    
    def __init__(self):
        """Initialize security monitor."""
        self.failed_login_attempts: Dict[str, List[datetime]] = {}
        self.suspicious_activities: List[Dict[str, Any]] = []
        self.blocked_ips: Set[str] = set()
        
        # Thresholds
        self.max_failed_logins = 5
        self.failed_login_window_minutes = 15
        self.rate_limit_window_minutes = 1
        self.max_requests_per_minute = 100
    
    def record_failed_login(self, username: str, ip_address: str) -> bool:
        """Record a failed login attempt.
        
        Args:
            username: Username that failed to log in
            ip_address: IP address of the attempt
            
        Returns:
            True if account should be temporarily locked, False otherwise
        """
        now = datetime.now()
        
        # Clean old attempts
        if username in self.failed_login_attempts:
            cutoff = now - timedelta(minutes=self.failed_login_window_minutes)
            self.failed_login_attempts[username] = [
                attempt for attempt in self.failed_login_attempts[username]
                if attempt > cutoff
            ]
        else:
            self.failed_login_attempts[username] = []
        
        # Record this attempt
        self.failed_login_attempts[username].append(now)
        
        # Check if threshold exceeded
        if len(self.failed_login_attempts[username]) >= self.max_failed_logins:
            self.record_suspicious_activity(
                "excessive_failed_logins",
                f"User {username} exceeded failed login threshold",
                {"username": username, "ip_address": ip_address, "attempts": len(self.failed_login_attempts[username])}
            )
            return True
        
        return False
    
    def record_suspicious_activity(
        self,
        activity_type: str,
        description: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record suspicious activity.
        
        Args:
            activity_type: Type of suspicious activity
            description: Description of the activity
            details: Additional details
        """
        activity = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "description": description,
            "details": details or {}
        }
        
        self.suspicious_activities.append(activity)
        
        # Keep only recent activities (last 30 days)
        cutoff = datetime.now() - timedelta(days=30)
        self.suspicious_activities = [
            activity for activity in self.suspicious_activities
            if datetime.fromisoformat(activity["timestamp"]) > cutoff
        ]
    
    def check_rate_limit(self, identifier: str, current_time: Optional[datetime] = None) -> bool:
        """Check if an identifier (IP, user) is rate limited.
        
        Args:
            identifier: Identifier to check
            current_time: Current time (for testing)
            
        Returns:
            True if rate limited, False otherwise
        """
        # This is a simplified rate limiting implementation
        # In production, you might want to use Redis or similar
        
        if not hasattr(self, 'rate_limit_tracking'):
            self.rate_limit_tracking: Dict[str, List[datetime]] = {}
        
        now = current_time or datetime.now()
        
        if identifier not in self.rate_limit_tracking:
            self.rate_limit_tracking[identifier] = []
        
        # Clean old requests
        cutoff = now - timedelta(minutes=self.rate_limit_window_minutes)
        self.rate_limit_tracking[identifier] = [
            request_time for request_time in self.rate_limit_tracking[identifier]
            if request_time > cutoff
        ]
        
        # Check if over limit
        if len(self.rate_limit_tracking[identifier]) >= self.max_requests_per_minute:
            return True
        
        # Record this request
        self.rate_limit_tracking[identifier].append(now)
        return False
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security monitoring summary.
        
        Returns:
            Dictionary with security statistics
        """
        recent_activities = [
            activity for activity in self.suspicious_activities
            if datetime.fromisoformat(activity["timestamp"]) > datetime.now() - timedelta(days=7)
        ]
        
        return {
            "failed_login_accounts": len(self.failed_login_attempts),
            "suspicious_activities_last_7_days": len(recent_activities),
            "blocked_ips": len(self.blocked_ips),
            "recent_suspicious_activities": recent_activities[-10:],  # Last 10 activities
        }


class StructuredLogger:
    """Structured logging with JSON output."""
    
    def __init__(
        self,
        name: str = "library_management",
        log_file: str = "logs/library.log",
        log_level: LogLevel = LogLevel.INFO,
        enable_console: bool = True,
        max_file_size_mb: int = 10,
        backup_count: int = 5,
    ):
        """Initialize structured logger.
        
        Args:
            name: Logger name
            log_file: Log file path
            log_level: Minimum log level
            enable_console: Whether to log to console
            max_file_size_mb: Maximum log file size in MB
            backup_count: Number of backup log files to keep
        """
        self.name = name
        self.log_file = Path(log_file)
        self.log_level = log_level
        self.enable_console = enable_console
        
        # Create log directory
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Setup Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.value))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count
        )
        file_handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(file_handler)
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(console_handler)
        
        # Async logging queue
        self.log_queue = queue.Queue()
        self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.log_thread.start()
    
    def _log_worker(self) -> None:
        """Background worker for async logging."""
        while True:
            try:
                event = self.log_queue.get(timeout=1)
                if event is None:  # Shutdown signal
                    break
                
                # Log the event
                log_level = getattr(logging, event.level)
                self.logger.log(log_level, event.to_json())
                
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Logging error: {e}")
    
    def log(
        self,
        level: LogLevel,
        message: str,
        event_type: EventType = EventType.SYSTEM_EVENT,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        duration_ms: Optional[float] = None,
        **kwargs
    ) -> None:
        """Log a structured event.
        
        Args:
            level: Log level
            message: Log message
            event_type: Type of event
            user_id: User ID (if applicable)
            session_id: Session ID (if applicable)
            ip_address: IP address
            user_agent: User agent string
            action: Action performed
            resource: Resource accessed
            duration_ms: Duration in milliseconds
            **kwargs: Additional data
        """
        event = LogEvent(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            event_type=event_type.value,
            message=message,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action=action,
            resource=resource,
            duration_ms=duration_ms,
            additional_data=kwargs if kwargs else None
        )
        
        # Add to queue for async processing
        self.log_queue.put(event)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.log(LogLevel.CRITICAL, message, **kwargs)
    
    def shutdown(self) -> None:
        """Shutdown the logger."""
        self.log_queue.put(None)  # Shutdown signal
        self.log_thread.join(timeout=5)


class MonitoringSystem:
    """Complete monitoring system for the library."""
    
    def __init__(
        self,
        logger: Optional[StructuredLogger] = None,
        enable_performance_monitoring: bool = True,
        enable_security_monitoring: bool = True,
    ):
        """Initialize monitoring system.
        
        Args:
            logger: Structured logger instance
            enable_performance_monitoring: Whether to enable performance monitoring
            enable_security_monitoring: Whether to enable security monitoring
        """
        self.logger = logger or StructuredLogger()
        self.performance_metrics = PerformanceMetrics() if enable_performance_monitoring else None
        self.security_monitor = SecurityMonitor() if enable_security_monitoring else None
        
        # Alert thresholds
        self.error_rate_threshold = 10.0  # %
        self.response_time_threshold = 5000.0  # ms
        self.memory_threshold = 80.0  # %
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
    
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add a callback for alerts.
        
        Args:
            callback: Function to call when alerts are triggered
        """
        self.alert_callbacks.append(callback)
    
    def _trigger_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Trigger an alert.
        
        Args:
            alert_type: Type of alert
            data: Alert data
        """
        self.logger.critical(
            f"Alert triggered: {alert_type}",
            event_type=EventType.SYSTEM_EVENT,
            action="alert_triggered",
            alert_type=alert_type,
            alert_data=data
        )
        
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, data)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def record_user_action(
        self,
        user_id: str,
        action: str,
        resource: str,
        success: bool = True,
        duration_ms: Optional[float] = None,
        ip_address: Optional[str] = None,
        **kwargs
    ) -> None:
        """Record a user action.
        
        Args:
            user_id: User ID
            action: Action performed
            resource: Resource accessed
            success: Whether the action was successful
            duration_ms: Duration in milliseconds
            ip_address: IP address
            **kwargs: Additional data
        """
        level = LogLevel.INFO if success else LogLevel.WARNING
        message = f"User action: {action} on {resource}"
        
        self.logger.log(
            level=level,
            message=message,
            event_type=EventType.USER_ACTION,
            user_id=user_id,
            action=action,
            resource=resource,
            duration_ms=duration_ms,
            ip_address=ip_address,
            success=success,
            **kwargs
        )
        
        # Record performance metrics
        if self.performance_metrics and duration_ms is not None:
            self.performance_metrics.record_request(duration_ms, action, success)
    
    def record_system_event(
        self,
        event: str,
        description: str,
        level: LogLevel = LogLevel.INFO,
        **kwargs
    ) -> None:
        """Record a system event.
        
        Args:
            event: Event name
            description: Event description
            level: Log level
            **kwargs: Additional data
        """
        self.logger.log(
            level=level,
            message=description,
            event_type=EventType.SYSTEM_EVENT,
            action=event,
            **kwargs
        )
    
    def record_security_event(
        self,
        event_type: str,
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        severity: str = "medium",
        **kwargs
    ) -> None:
        """Record a security event.
        
        Args:
            event_type: Type of security event
            description: Event description
            user_id: User ID (if applicable)
            ip_address: IP address
            severity: Severity level
            **kwargs: Additional data
        """
        level = LogLevel.WARNING if severity == "medium" else LogLevel.ERROR
        
        self.logger.log(
            level=level,
            message=description,
            event_type=EventType.SECURITY,
            user_id=user_id,
            ip_address=ip_address,
            action=event_type,
            severity=severity,
            **kwargs
        )
        
        # Record in security monitor
        if self.security_monitor:
            self.security_monitor.record_suspicious_activity(
                event_type, description, {"user_id": user_id, "ip_address": ip_address, **kwargs}
            )
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health and trigger alerts if needed.
        
        Returns:
            Health status dictionary
        """
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "issues": []
        }
        
        # Check performance metrics
        if self.performance_metrics:
            stats = self.performance_metrics.get_stats()
            
            # Check error rate
            if stats["error_rate_percent"] > self.error_rate_threshold:
                issue = f"High error rate: {stats['error_rate_percent']:.1f}%"
                health_status["issues"].append(issue)
                self._trigger_alert("high_error_rate", {"error_rate": stats["error_rate_percent"]})
            
            # Check response time
            if stats["average_response_time_ms"] > self.response_time_threshold:
                issue = f"High response time: {stats['average_response_time_ms']:.1f}ms"
                health_status["issues"].append(issue)
                self._trigger_alert("high_response_time", {"response_time": stats["average_response_time_ms"]})
            
            health_status["performance"] = stats
        
        # Check security status
        if self.security_monitor:
            security_summary = self.security_monitor.get_security_summary()
            health_status["security"] = security_summary
            
            # Check for recent suspicious activities
            if security_summary["suspicious_activities_last_7_days"] > 10:
                issue = f"High number of suspicious activities: {security_summary['suspicious_activities_last_7_days']}"
                health_status["issues"].append(issue)
                self._trigger_alert("high_suspicious_activity", security_summary)
        
        # Set overall status
        if health_status["issues"]:
            health_status["status"] = "degraded" if len(health_status["issues"]) < 3 else "unhealthy"
        
        return health_status
    
    def get_log_analysis(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze recent logs for patterns and issues.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Log analysis results
        """
        # This is a simplified implementation
        # In production, you might want to use log analysis tools like ELK stack
        
        analysis = {
            "time_range_hours": hours,
            "analysis_timestamp": datetime.now().isoformat(),
            "top_errors": [],
            "user_activity_summary": {},
            "system_events_summary": {},
        }
        
        try:
            # Read recent log entries
            log_entries = []
            if self.logger.log_file.exists():
                with open(self.logger.log_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry_time = datetime.fromisoformat(entry["timestamp"])
                            if entry_time > datetime.now() - timedelta(hours=hours):
                                log_entries.append(entry)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
            
            # Analyze entries
            error_counts = {}
            user_actions = {}
            system_events = {}
            
            for entry in log_entries:
                # Count errors
                if entry["level"] in ["ERROR", "CRITICAL"]:
                    error_key = entry.get("action", "unknown_error")
                    error_counts[error_key] = error_counts.get(error_key, 0) + 1
                
                # Count user actions
                if entry["event_type"] == "user_action" and entry.get("user_id"):
                    user_id = entry["user_id"]
                    action = entry.get("action", "unknown")
                    if user_id not in user_actions:
                        user_actions[user_id] = {}
                    user_actions[user_id][action] = user_actions[user_id].get(action, 0) + 1
                
                # Count system events
                if entry["event_type"] == "system_event":
                    event = entry.get("action", "unknown")
                    system_events[event] = system_events.get(event, 0) + 1
            
            # Format results
            analysis["top_errors"] = sorted(
                error_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]
            
            analysis["user_activity_summary"] = {
                user_id: sum(actions.values())
                for user_id, actions in user_actions.items()
            }
            
            analysis["system_events_summary"] = dict(
                sorted(system_events.items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
        except Exception as e:
            analysis["error"] = f"Failed to analyze logs: {e}"
        
        return analysis
    
    def shutdown(self) -> None:
        """Shutdown the monitoring system."""
        self.logger.shutdown()


# Performance monitoring decorator
def monitor_performance(operation_name: str, monitoring_system: Optional[MonitoringSystem] = None):
    """Decorator to monitor function performance.
    
    Args:
        operation_name: Name of the operation being monitored
        monitoring_system: MonitoringSystem instance to use
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                if monitoring_system:
                    # Try to extract user info from args/kwargs
                    user_id = None
                    if hasattr(args[0], 'current_user') and args[0].current_user:
                        user_id = getattr(args[0].current_user, 'username', None)
                    
                    monitoring_system.record_user_action(
                        user_id=user_id or "system",
                        action=operation_name,
                        resource=func.__name__,
                        success=success,
                        duration_ms=duration_ms,
                        error=error
                    )
        
        return wrapper
    return decorator