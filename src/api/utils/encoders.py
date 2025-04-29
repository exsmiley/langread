"""
Custom JSON encoders for MongoDB ObjectId and other non-serializable types.
"""

import json
from bson import ObjectId
from datetime import datetime, date
from typing import Any

class MongoJSONEncoder(json.JSONEncoder):
    """JSON encoder that can handle MongoDB ObjectIds and other special types."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def jsonable_encoder_with_objectid(obj: Any) -> Any:
    """Custom encoder for FastAPI that handles ObjectIds and other MongoDB types."""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: jsonable_encoder_with_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [jsonable_encoder_with_objectid(i) for i in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj
