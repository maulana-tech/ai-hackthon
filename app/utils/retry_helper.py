"""
Retry Helper - Exponential backoff untuk API calls
"""
import asyncio
import logging
from typing import Callable, Any, Type, Tuple
from functools import wraps
import random

logger = logging.getLogger(__name__)

async def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    **kwargs
) -> Any:
    """
    Retry async function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to delays
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Function result if successful
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(f"Retry succeeded on attempt {attempt + 1}")
            
            return result
            
        except exceptions as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(f"All {max_retries} retries failed: {str(e)}")
                raise
            
            # Calculate delay with exponential backoff
            delay = min(
                initial_delay * (exponential_base ** attempt),
                max_delay
            )
            
            # Add jitter to prevent thundering herd
            if jitter:
                delay = delay * (0.5 + random.random())
            
            logger.warning(
                f"Attempt {attempt + 1} failed: {str(e)}. "
                f"Retrying in {delay:.2f}s..."
            )
            
            await asyncio.sleep(delay)
    
    raise last_exception


def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator to add retry logic to async functions
    
    Usage:
        @with_retry(max_retries=3, initial_delay=2.0)
        async def api_call():
            # ... API call that might fail
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                func,
                *args,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
                exceptions=exceptions,
                **kwargs
            )
        return wrapper
    return decorator


class RateLimiter:
    """
    Simple rate limiter to prevent API overload
    """
    
    def __init__(self, max_calls: int = 10, time_window: float = 60.0):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        
    async def wait_if_needed(self):
        """Wait if rate limit is exceeded"""
        import time
        
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [
            call_time for call_time in self.calls
            if now - call_time < self.time_window
        ]
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            # Calculate wait time
            oldest_call = min(self.calls)
            wait_time = self.time_window - (now - oldest_call) + 0.1
            
            if wait_time > 0:
                logger.warning(
                    f"Rate limit reached ({self.max_calls} calls in "
                    f"{self.time_window}s). Waiting {wait_time:.2f}s..."
                )
                await asyncio.sleep(wait_time)
                
                # Refresh timestamp
                now = time.time()
        
        # Record this call
        self.calls.append(now)
    
    def with_rate_limit(self, func: Callable):
        """
        Decorator to add rate limiting to async functions
        
        Usage:
            limiter = RateLimiter(max_calls=10, time_window=60.0)
            
            @limiter.with_rate_limit
            async def api_call():
                # ... API call
                pass
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            await self.wait_if_needed()
            return await func(*args, **kwargs)
        return wrapper


# Global rate limiters for different services
firecrawl_limiter = RateLimiter(max_calls=10, time_window=60.0)
google_trends_limiter = RateLimiter(max_calls=5, time_window=60.0)
apify_limiter = RateLimiter(max_calls=20, time_window=60.0)
