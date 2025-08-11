# Enhanced Error Handling and Resilience Patterns
import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Type
import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class CircuitBreakerError(Exception):
    """Circuit breaker is open"""
    pass

class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self.last_failure_time and time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info(f"Circuit breaker half-open for {func.__name__}")
                else:
                    logger.warning(f"Circuit breaker open for {func.__name__}")
                    raise CircuitBreakerError(f"Circuit breaker is open for {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    logger.info(f"Circuit breaker closed for {func.__name__}")
                return result
            except self.expected_exception as e:
                self.failure_count += 1
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    self.last_failure_time = time.time()
                    logger.error(f"Circuit breaker opened for {func.__name__}")
                raise e
        
        return wrapper

class RetryConfig:
    """Retry configuration"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def retry_with_exponential_backoff(config: RetryConfig):
    """Decorator for retry logic with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts - 1:
                        logger.error(f"Max retry attempts ({config.max_attempts}) reached for {func.__name__}")
                        raise e
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        import random
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    await asyncio.sleep(delay)
            
            # This should never be reached due to the raise in the loop
            if last_exception:
                raise last_exception
            raise Exception("Unexpected error in retry logic")
        
        return wrapper
    
    return decorator

class ServiceClient:
    """Enhanced HTTP client with resilience patterns"""
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        circuit_breaker: Optional[CircuitBreaker] = None,
        retry_config: Optional[RetryConfig] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.retry_config = retry_config or RetryConfig()
        
        # HTTP client configuration
        self.client_config = {
            "timeout": httpx.Timeout(timeout),
            "limits": httpx.Limits(max_keepalive_connections=20, max_connections=100),
            "follow_redirects": False
        }
    
    @retry_with_exponential_backoff(RetryConfig())
    async def _make_request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> httpx.Response:
        """Make HTTP request with timeout and error handling"""
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        try:
            async with httpx.AsyncClient(**self.client_config) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {method} {url}")
            raise HTTPException(status_code=504, detail=f"Service timeout: {self.base_url}")
        except httpx.ConnectError:
            logger.error(f"Connection error calling {method} {url}")
            raise HTTPException(status_code=503, detail=f"Service unavailable: {self.base_url}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {method} {url}: {e.response.status_code}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Service error: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error calling {method} {url}: {e}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    async def get(self, path: str, **kwargs) -> httpx.Response:
        """GET request"""
        return await self._make_request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> httpx.Response:
        """POST request"""
        return await self._make_request("POST", path, **kwargs)
    
    async def put(self, path: str, **kwargs) -> httpx.Response:
        """PUT request"""
        return await self._make_request("PUT", path, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> httpx.Response:
        """DELETE request"""
        return await self._make_request("DELETE", path, **kwargs)
    
    async def health_check(self) -> bool:
        """Check service health"""
        try:
            response = await self.get("/health")
            return response.status_code == 200
        except Exception:
            return False

# Rate limiting
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, requests_per_window: int, window_seconds: int):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests = {}  # client_id -> list of timestamps
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if now - req_time < self.window_seconds
            ]
        else:
            self.requests[client_id] = []
        
        # Check if under limit
        if len(self.requests[client_id]) < self.requests_per_window:
            self.requests[client_id].append(now)
            return True
        
        return False

# Global instances
default_rate_limiter = RateLimiter(100, 3600)  # 100 requests per hour
