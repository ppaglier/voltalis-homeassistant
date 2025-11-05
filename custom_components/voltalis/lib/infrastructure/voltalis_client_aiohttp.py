import logging
from typing import Any, TypedDict

from aiohttp import ClientConnectorError, ClientError, ClientResponseError, ClientSession, ClientTimeout

from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException


class VoltalisClientAiohttp(VoltalisClient):
    """Voltalis client integration using the Aiohttp lib"""

    BASE_URL = "https://api.myvoltalis.com"
    LOGIN_ROUTE = "/auth/login"
    TIMEOUT = 30  # Seconds

    class Storage(TypedDict):
        """Dict that represent the storage of the client"""

        auth_token: str | None
        default_site_id: str | None

    def __init__(
        self,
        *,
        username: str,
        password: str,
        base_url: str = BASE_URL,
        session: ClientSession | None = None,
    ) -> None:
        self.__username = username
        self.__password = password

        # Setup session if not provided & set the close_session var for later
        _session = session
        if _session is None:
            _session = ClientSession(
                base_url=base_url,
                timeout=ClientTimeout(VoltalisClientAiohttp.TIMEOUT),
            )
        self.__session = _session
        self.__close_session = session is None

        # Setup storage
        self.__storage = VoltalisClientAiohttp.Storage(
            auth_token=None,
            default_site_id=None,
        )

        # Configure logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        self.__logger = logger

    async def __aenter__(self) -> "VoltalisClientAiohttp":
        """Async enter."""

        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        """Logout and close the session if the session wasn't provided at init."""
        await self.logout()

        if self.__close_session:
            await self.__session.close()

    async def login(self) -> None:
        """Execute Voltalis login."""

        self.__logger.debug("Login start")
        payload = {
            "login": self.__username,
            "password": self.__password,
        }
        response = await self.__send_request(
            url=VoltalisClientAiohttp.LOGIN_ROUTE,
            method="POST",
            retry=False,
            json=payload,
        )
        self.__logger.debug("Login Response: %s", response)
        self.__storage["auth_token"] = response["token"]
        self.__logger.info("Login successful")

    async def logout(self) -> None:
        await self.__send_request(url="/auth/logout", retry=False, method="DELETE")
        self.__logger.info("Logout successful")
        self.__storage["auth_token"] = None

    async def get_me(self) -> None:
        self.__logger.debug("Get me start")
        response = await self.__send_request(
            url="/api/account/me",
            retry=False,
            method="GET",
        )
        self.__storage["default_site_id"] = response["defaultSite"]["id"]
        self.__logger.info(f"Default site id set = {self.__storage['default_site_id']}")

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        """Get all Voltalis devices."""

        self.__logger.debug("Get all Voltalis devices")
        devices_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
            retry=False,
        )

        self.__logger.debug("Get all Voltalis status")
        devices_health_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/autodiag",
            method="GET",
            retry=False,
        )

        devices_health: dict[int, bool] = {
            device_health_document["csApplianceId"]: device_health_document["status"] == "OK"
            for device_health_document in devices_health_response
        }

        devices = {
            device_document["id"]: VoltalisDevice(
                id=device_document["id"],
                status=devices_health.get(device_document["id"], False),
                name=device_document["name"],
                type=device_document["applianceType"],
                modulator_type=device_document["modulatorType"],
                available_modes=device_document["availableModes"],
                prog_type=device_document.get("programming", {})["progType"],
            )
            for device_document in devices_response
        }

        return devices

    async def get_consumption(self) -> list[dict]:
        """Get all Voltalis devices consumption."""

        self.__logger.debug("Get all Voltalis devices consumption")
        response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/consumption/realtime",
            params={
                "mode": "TEN_SECONDS",
                "numPoints": 1,
            },
            method="GET",
            retry=False,
        )

        return response

    async def __send_request(
        self,
        *,
        url: str,
        method: str,
        retry: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Send http requests to Voltalis."""

        if self.__storage["auth_token"] is None and url != VoltalisClientAiohttp.LOGIN_ROUTE:
            await self.login()

        headers = {
            "content-type": "application/json",
            "accept": "*/*",
        }
        if self.__storage["auth_token"] is not None:
            headers["Authorization"] = f"Bearer {self.__storage['auth_token']}"

        _url = url
        if self.__storage["default_site_id"] is not None:
            _url = url.format(site_id=self.__storage["default_site_id"])

        self.__logger.debug(f"Call Voltalis API to {url} using {method}")

        try:
            response = await self.__session.request(url=_url, method=method, headers=headers, **kwargs)
            if response.status == 401:
                raise VoltalisAuthenticationException(await response.text())
            if response.status == 404:
                self.__logger.exception(await response.text())
                return None
            response.raise_for_status()
        except (ClientConnectorError, ClientError, ClientResponseError) as ex:
            if retry:
                await self.login()
                return await self.__send_request(url=_url, method=method, retry=False, **kwargs)
            raise VoltalisException from ex

        self.__logger.debug("End call to Voltalis API")

        # Return response depends on the content type
        if response.content_type == "application/json":
            return await response.json()
        return await response.read()
