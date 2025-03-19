import json
from typing import Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)

def create_callback_data(module: str, action: str, data: Dict[str, Any] = None) -> str:
    """
    Create a standardized callback data string.

    Args:
        module: Feature module identifier (e.g., "release", "squad")
        action: Specific action within the module
        data: Optional additional data

    Returns:
        Serialized callback data string
    """
    # Use short module IDs and action names for space efficiency
    callback_data = {
        "module": module,  # Full module name for clarity
        "action": action,  # Full action name for clarity
    }

    # Add data if provided
    if data:
        callback_data["data"] = data

    result = json.dumps(callback_data)

    # Warn if approaching Telegram's 64-byte limit
    if len(result) > 60:
        logger.warning(f"Callback data is approaching size limit: {len(result)}/64 bytes")
    
    # Enforce size limit if needed
    if len(result) > 64:
        logger.error(f"Callback data exceeds 64-byte limit: {len(result)} bytes")
        # Truncate keys to save space
        callback_data = {
            "m": module[:3],  # Abbreviated module
            "a": action[:3],  # Abbreviated action
        }
        
        # Abbreviate data keys too
        if data:
            compact_data = {}
            for k, v in data.items():
                compact_data[k[:1]] = v  # First character of key
            callback_data["d"] = compact_data
            
        result = json.dumps(callback_data)
        
        if len(result) > 64:
            logger.error(f"Even abbreviated callback data exceeds limit: {len(result)} bytes")
            # Further truncation if needed
            if "d" in callback_data and isinstance(callback_data["d"], dict):
                # Only keep numeric values to save space
                callback_data["d"] = {k: v for k, v in callback_data["d"].items() 
                                     if isinstance(v, (int, bool))}
                result = json.dumps(callback_data)

    return result

def parse_callback_data(callback_string: str) -> Optional[Dict[str, Any]]:
    """
    Parse a callback data string into a structured format.
    
    Handles both full and abbreviated callback formats.
    
    Returns:
        Parsed callback data or None if invalid
    """
    try:
        data = json.loads(callback_string)
        if not isinstance(data, dict):
            return None
            
        # Handle abbreviated format
        if "m" in data and "module" not in data:
            data["module"] = data.pop("m")
        if "a" in data and "action" not in data:
            data["action"] = data.pop("a")
        if "d" in data and "data" not in data:
            data["data"] = data.pop("d")
            
        # Check for required fields
        if "module" not in data or "action" not in data:
            return None
            
        return data
    except json.JSONDecodeError:
        return None

def create_callback_pattern(module: str) -> Callable[[str], bool]:
    """
    Create a pattern function for matching callbacks for a specific module.
    
    Args:
        module: The module identifier to match against
        
    Returns:
        A function that can be used as a pattern in CallbackQueryHandler
    """
    def pattern(callback_data: str) -> bool:
        if not callback_data:
            return False
            
        try:
            data = json.loads(callback_data)
            # Check both full and abbreviated formats
            return (data.get("module") == module or data.get("m") == module)
        except:
            return False
            
    return pattern
