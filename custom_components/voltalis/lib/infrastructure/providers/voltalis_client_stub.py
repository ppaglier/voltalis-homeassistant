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
        payload = {
            "login": username,
            "password": password,
        }
        try:
            response: HttpClientResponse[dict] = await self.send_request(
                url="some_url",
                method="POST",
                body=payload,
            )
            return response.data["token"]
        except HttpClientException as err:
            if err.response and err.response.status == 401:
                raise VoltalisAuthenticationException("Invalid username or password") from err
            raise err

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
        if self.__should_fail_auth:
            raise HttpClientException(
                "Authentication failed",
                response=HttpClientResponse(
                    data=None,
                    status=401,
                    url=url,
                    header={},
                ),
            )
        if self.__should_fail_connection:
            raise HttpClientException(
                "Connection failed",
                response=HttpClientResponse(
                    data=None,
                    status=503,
                    url=url,
                    header={},
                ),
            )
        if self.__should_fail_unexpected:
            raise RuntimeError("Unexpected error")
        return HttpClientResponse[TData](data={"token": None}, status=200, url=url)
