import json
from typing import Dict, Any


def create_feature_callback_data(
    feature: str, action: str, data: Dict[str, Any] = None
) -> str:
    """Create a callback data string for a specific feature."""
    callback_data = {"a": action, "feature": feature}
    if data:
        callback_data.update(data)
    return json.dumps(callback_data)


def belongs_to_feature(callback_data: str, feature: str) -> bool:
    """Check if a callback belongs to a specific feature."""
    try:
        data = json.loads(callback_data)
        return data.get("feature") == feature
    except:
        return False
