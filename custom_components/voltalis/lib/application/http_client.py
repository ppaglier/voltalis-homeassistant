from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from custom_components.voltalis.lib.domain.custom_model import CustomModel

T = TypeVar("T")
TData = TypeVar("TData")


class HttpClientResponse(CustomModel, Generic[T]):
    """Schema for the response of the HttpClient."""

    data: T
    status: int
    url: str
    headers: dict[str, str | list[str] | int | bool | None] = {}


class HttpClientException(Exception, Generic[T]):
    """Raised when an error occurs while sending an alert."""

    request: dict | None
    response: HttpClientResponse[T] | None

    def __init__(
        self,
        message: str,
        request: dict | None = None,
        response: HttpClientResponse[T] | None = None,
    ) -> None:
        super().__init__(message)
        self.request = request
        self.response = response


class HttpClient(ABC):
    """Create a Http client that will be used to communicate with http servers."""

    @abstractmethod
    async def send_request(
        self,
        *,
        url: str,
        method: str,
        body: Any | None = None,
        query_params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> HttpClientResponse[TData]:
        """Send an HTTP request to the server."""
        ...
