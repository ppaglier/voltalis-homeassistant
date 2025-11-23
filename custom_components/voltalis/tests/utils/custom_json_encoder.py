from datetime import datetime
from json import JSONEncoder
from typing import Any
from uuid import UUID

from pydantic import HttpUrl, SecretStr
from pydantic_core import PydanticUndefinedType, Url
from typing_extensions import _AnnotatedAlias


class CustomJsonEncoder(JSONEncoder):
    """Class to customize JSON serialization."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        # if isinstance(obj, ValidationError):
        #     return [super().default(o) for o in obj.errors()]
        if isinstance(obj, (UUID, HttpUrl, Url, SecretStr, Exception, type, PydanticUndefinedType, _AnnotatedAlias)):
            return str(obj)
        try:
            return super().default(obj)
        except Exception as e:
            # This is a catch-all for any other exceptions that might occur
            print(f"Error: {e}", flush=True)
            raise e
