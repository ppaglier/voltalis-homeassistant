from typing import Any

from custom_components.voltalis.lib.application.providers.http_client import (
    HttpClient,
    HttpClientException,
    HttpClientResponse,
    TData,
)
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException


class VoltalisClientStub(HttpClient):
    """
    Stub implementation of the Voltalis client.
    When the MockVoltalisServer is ready, this class should be deleted and replaced by a VoltalisClientAiohttp
    pointing to the MockVoltalisServer.
    """

    def __init__(self) -> None:
        self.__should_fail_auth = False
        self.__should_fail_connection = False
        self.__should_fail_unexpected = False

    def set_auth_failure(self, should_fail: bool = True) -> None:
        """Configure the client to fail authentication."""
        self.__should_fail_auth = should_fail

    def set_connection_failure(self, should_fail: bool = True) -> None:
        """Configure the client to fail connection."""
        self.__should_fail_connection = should_fail

    def set_unexpected_failure(self, should_fail: bool = True) -> None:
        """Configure the client to fail with unexpected error."""
        self.__should_fail_unexpected = should_fail

    async def get_access_token(
        self,
        *,
        username: str,
        password: str,
    ) -> str:
        if self.__should_fail_auth:
            raise VoltalisAuthenticationException("Invalid credentials")
        if self.__should_fail_connection:
            raise HttpClientException("Connection failed")
        if self.__should_fail_unexpected:
            raise RuntimeError("Unexpected error")
        return "valid_access_token"

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
        raise NotImplementedError("This is a stub method.")
