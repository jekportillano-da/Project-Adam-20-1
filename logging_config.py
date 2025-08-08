# Enhanced Logging System with Structured Logging
import json
import logging
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request
import uuid

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry)

class RequestLogger:
    """Request logging with correlation IDs"""
    
    def __init__(self):
        self.logger = logging.getLogger("request")
    
    def log_request(
        self,
        request: Request,
        response_status: int,
        response_time: float,
        correlation_id: Optional[str] = None
    ):
        """Log HTTP request with structured data"""
        correlation_id = correlation_id or str(uuid.uuid4())
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        self.logger.info(
            "HTTP Request",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": client_ip,
                "user_agent": request.headers.get("user-agent", ""),
                "response_status": response_status,
                "response_time_ms": round(response_time * 1000, 2),
                "request_size": request.headers.get("content-length", 0)
            }
        )

class SecurityLogger:
    """Security event logging"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def log_auth_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str = ""
    ):
        """Log authentication attempts"""
        self.logger.info(
            "Authentication attempt",
            extra={
                "event_type": "auth_attempt",
                "email": email,
                "success": success,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_suspicious_activity(
        self,
        event_type: str,
        details: Dict[str, Any],
        ip_address: str,
        severity: str = "medium"
    ):
        """Log suspicious security events"""
        self.logger.warning(
            f"Suspicious activity: {event_type}",
            extra={
                "event_type": "suspicious_activity",
                "activity_type": event_type,
                "severity": severity,
                "ip_address": ip_address,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

class PerformanceLogger:
    """Performance monitoring logger"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_operation(
        self,
        operation: str,
        duration: float,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log operation performance"""
        self.logger.info(
            f"Operation: {operation}",
            extra={
                "event_type": "operation",
                "operation": operation,
                "duration_ms": round(duration * 1000, 2),
                "success": success,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_slow_query(
        self,
        query_type: str,
        duration: float,
        threshold: float = 1.0
    ):
        """Log slow database queries"""
        if duration > threshold:
            self.logger.warning(
                f"Slow query detected: {query_type}",
                extra={
                    "event_type": "slow_query",
                    "query_type": query_type,
                    "duration_ms": round(duration * 1000, 2),
                    "threshold_ms": round(threshold * 1000, 2),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

def setup_logging(level: str = "INFO", format_type: str = "json"):
    """Setup application logging"""
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter
    if format_type == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Set specific logger levels
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    return root_logger

# Global logger instances
request_logger = RequestLogger()
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()

# Context manager for timing operations
class timer:
    """Context manager for timing operations"""
    
    def __init__(self, operation: str, logger: Optional[logging.Logger] = None):
        self.operation = operation
        self.logger = logger or performance_logger.logger
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            success = exc_type is None
            performance_logger.log_operation(
                self.operation,
                duration,
                success,
                {"exception": str(exc_val) if exc_val else None}
            )
