from datetime import datetime
from json import JSONEncoder
from typing import Any


class CustomJsonEncoder(JSONEncoder):
    """Class to customize JSON serialization."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        try:
            return super().default(obj)
        except Exception as e:
            # This is a catch-all for any other exceptions that might occur
            print(f"Error: {e}", flush=True)
            raise e
