"""
Decorators for the GullyGuru bot.
"""

import functools
import logging
import time
import traceback
from typing import Callable, Any

# Create a logger for this module
logger = logging.getLogger(__name__)

def log_function_call(func: Callable) -> Callable:
    """
    Decorator to log function calls, arguments, and execution time.
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Get logger for the function's module
        func_logger = logging.getLogger(func.__module__)
        
        # Log function call with arguments
        # Skip 'self' or 'update' for cleaner logs
        args_repr = []
        for i, arg in enumerate(args):
            if i == 0 and hasattr(arg, '__class__') and 'self' in str(arg.__class__):
                args_repr.append("self")
            elif i == 0 and hasattr(arg, 'update_id'):
                args_repr.append("update")
            else:
                args_repr.append(repr(arg))
                
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        
        func_logger.debug(f"Calling {func.__name__}({signature})")
        
        # Measure execution time
        start_time = time.time()
        
        try:
            # Call the function
            result = await func(*args, **kwargs)
            
            # Log execution time
            execution_time = time.time() - start_time
            func_logger.debug(f"{func.__name__} completed in {execution_time:.4f} seconds")
            
            return result
        except Exception as e:
            # Log error with traceback
            execution_time = time.time() - start_time
            func_logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            func_logger.debug(f"Traceback: {traceback.format_exc()}")
            raise
    
    return wrapper
