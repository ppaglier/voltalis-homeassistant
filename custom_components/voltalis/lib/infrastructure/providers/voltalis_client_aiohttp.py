import logging
from typing import Any, TypedDict

from aiohttp import ClientSession

from custom_components.voltalis.const import VOLTALIS_API_BASE_URL, VOLTALIS_API_LOGIN_ROUTE
from custom_components.voltalis.lib.application.providers.http_client import (
    HttpClientException,
    HttpClientResponse,
    TData,
)
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException
from custom_components.voltalis.lib.infrastructure.providers.http_client_aiohttp import HttpClientAioHttp


class VoltalisClientAiohttp(HttpClientAioHttp):
    """
    Aiohttp client for Voltalis API.
    It implements authentication and token management.
    """

    BASE_URL = VOLTALIS_API_BASE_URL
    LOGIN_ROUTE = VOLTALIS_API_LOGIN_ROUTE

    class Storage(TypedDict):
        """Dict that represent the storage of the client"""

        username: str | None
        password: str | None
        auth_token: str | None
        default_site_id: str | None

    def __init__(
        self,
        *,
        session: ClientSession,
        base_url: str = BASE_URL,
    ) -> None:
        super().__init__(session=session, base_url=base_url)

        # Setup storage
        self.__storage = VoltalisClientAiohttp.Storage(
            username=None,
            password=None,
            auth_token=None,
            default_site_id=None,
        )

        # Configure logger
        logger = logging.getLogger(__name__)
        self.__logger = logger

    @property
    def storage(self) -> "VoltalisClientAiohttp.Storage":
        """Get the aiohttp storage."""
        return self.__storage

    async def get_access_token(
        self,
        *,
        username: str,
        password: str,
    ) -> str:
        """Get Voltalis access token."""

        payload = {
            "login": username,
            "password": password,
        }
        try:
            response: HttpClientResponse[dict] = await self.send_request(
                url=VoltalisClientAiohttp.LOGIN_ROUTE,
                method="POST",
                body=payload,
                can_retry=False,
            )
            return response.data["token"]
        except HttpClientException as err:
            self.__logger.error("Error while getting access token: %s", err)
            if err.response and err.response.status == 401:
                raise VoltalisAuthenticationException("Invalid username or password") from err
            raise err

    async def __get_me(self) -> str:
        response: HttpClientResponse[dict] = await self.send_request(
            url="/api/account/me",
            method="GET",
        )
        return response.data["defaultSite"]["id"]

    async def login(self, *, username: str, password: str) -> None:
        """Execute Voltalis login."""

        self.__logger.info("Voltalis login in progress...")
        token = await self.get_access_token(
            username=username,
            password=password,
        )
        # Store login data for refreshing token later (maybe hash credentials?)
        self.__storage["username"] = username
        self.__storage["password"] = password

        self.__storage["auth_token"] = token
        self.__storage["default_site_id"] = await self.__get_me()

        self.__logger.info("Voltalis login successful")

    async def logout(self) -> None:
        if self.__storage["auth_token"] is None:
            return

        self.__logger.info("Voltalis logout in progress...")
        await self.send_request(url="/auth/logout", method="DELETE")
        self.__logger.info("Logout successful")

        self.__storage["username"] = None
        self.__storage["password"] = None

        self.__storage["auth_token"] = None
        self.__storage["default_site_id"] = None

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
        """Send http requests to Voltalis."""

        can_retry = kwargs.pop("can_retry", True)

        if self.__storage["auth_token"] is None and url != VoltalisClientAiohttp.LOGIN_ROUTE:
            await self.login(
                username=self.__storage["username"] or "",
                password=self.__storage["password"] or "",
            )

        headers = {
            **{
                "content-type": "application/json",
                "accept": "*/*",
            },
            **(headers or {}),
        }
        if self.__storage["auth_token"] is not None:
            headers["Authorization"] = f"Bearer {self.__storage['auth_token']}"

        _url = url
        if self.__storage["default_site_id"] is not None:
            _url = url.format(site_id=self.__storage["default_site_id"])

        try:
            response: HttpClientResponse[TData] = await super().send_request(
                url=_url,
                method=method,
                body=body,
                query_params=query_params,
                headers=headers,
                **kwargs,
            )
        except HttpClientException as ex:
            if ex.response is None or ex.response.status != 401 or not can_retry:
                raise ex

            self.__logger.warning("Authentication failed (401), retrying with new login...")
            try:
                await self.login(
                    username=self.__storage["username"] or "",
                    password=self.__storage["password"] or "",
                )
            except Exception as login_ex:
                self.__logger.error("Re-login failed during retry after 401: %s", login_ex)
            response = await super().send_request(
                url=_url,
                method=method,
                body=body,
                query_params=query_params,
                headers=headers,
                can_retry=False,
                **kwargs,
            )

        return response
