import logging
from datetime import datetime
from typing import Any, TypedDict
from urllib.parse import urljoin

from aiohttp import ClientConnectorError, ClientError, ClientResponseError, ClientSession, ClientTimeout
from pydantic import ValidationError

from custom_components.voltalis.const import VOLTALIS_API_BASE_URL, VOLTALIS_API_LOGIN_ROUTE
from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.exceptions import (
    VoltalisAuthenticationException,
    VoltalisException,
    VoltalisValidationException,
)
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceProgrammingStatus
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.models.subscriber_contract import (
    VoltalisSubscriberContract,
    VoltalisTimeRange,
)


class VoltalisClientAiohttp(VoltalisClient):
    """Voltalis client integration using the Aiohttp lib"""

    BASE_URL = VOLTALIS_API_BASE_URL
    LOGIN_ROUTE = VOLTALIS_API_LOGIN_ROUTE

    class Storage(TypedDict):
        """Dict that represent the storage of the client"""

        auth_token: str | None
        default_site_id: str | None

    def __init__(
        self,
        *,
        username: str | None = None,
        password: str | None = None,
        base_url: str = BASE_URL,
        session: ClientSession | None = None,
    ) -> None:
        self.__username = username
        self.__password = password
        self.__base_url = base_url

        # Setup session if not provided & set the close_session var for later
        _session = session
        if _session is None:
            _session = ClientSession(
                timeout=ClientTimeout(30),
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
        self.__logger = logger

    async def __aenter__(self) -> "VoltalisClientAiohttp":
        """Async enter."""

        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        """Logout and close the session if the session wasn't provided at init."""
        await super().__aexit__()

        if self.__close_session:
            await self.__session.close()

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
        response = await self.__send_request(
            url=VoltalisClientAiohttp.LOGIN_ROUTE,
            method="POST",
            retry=False,
            json=payload,
        )
        return response["token"]

    async def __get_me(self) -> str:
        response = await self.__send_request(
            url="/api/account/me",
            retry=False,
            method="GET",
        )
        return response["defaultSite"]["id"]

    async def login(self) -> None:
        """Execute Voltalis login."""

        if self.__username is None or self.__password is None:
            raise VoltalisException("You must provide username & password")

        self.__logger.info("Voltalis login in progress...")
        token = await self.get_access_token(
            username=self.__username,
            password=self.__password,
        )
        self.__storage["auth_token"] = token

        self.__storage["default_site_id"] = await self.__get_me()
        self.__logger.info("Voltalis login successful")

    async def logout(self) -> None:
        if self.__storage["auth_token"] is None:
            return

        self.__logger.info("Voltalis logout in progress...")
        await self.__send_request(url="/auth/logout", retry=False, method="DELETE")
        self.__logger.info("Logout successful")
        self.__storage["auth_token"] = None

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        """Get all Voltalis devices."""

        devices_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
            retry=False,
        )

        devices: dict[int, VoltalisDevice] = {}

        try:
            for device_document in devices_response:
                device = VoltalisDevice(
                    id=device_document["id"],
                    name=device_document["name"],
                    type=device_document["applianceType"],
                    modulator_type=device_document["modulatorType"],
                    available_modes=[mode.lower() for mode in device_document["availableModes"]],
                    programming=VoltalisDeviceProgrammingStatus(
                        prog_type=device_document.get("programming", {}).get("progType", "").lower() or None,
                        id_manual_setting=device_document.get("programming", {}).get("idManualSetting"),
                        is_on=device_document.get("programming", {}).get("isOn"),
                        mode=device_document.get("programming", {}).get("mode", "").lower() or None,
                        temperature_target=device_document.get("programming", {}).get("temperatureTarget"),
                        default_temperature=device_document.get("programming", {}).get("defaultTemperature"),
                    ),
                )
                devices[device_document["id"]] = device
        except ValidationError as err:
            self.__logger.error("Error parsing devices: %s", err)
            raise VoltalisValidationException(*err.args) from err

        return devices

    async def get_devices_health(self) -> dict[int, VoltalisDeviceHealth]:
        """Get devices health"""

        devices_health_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/autodiag",
            method="GET",
            retry=False,
        )

        devices_health: dict[int, VoltalisDeviceHealth] = {}
        try:
            for device_health_document in devices_health_response:
                devices_health[device_health_document["csApplianceId"]] = VoltalisDeviceHealth(
                    status=device_health_document["status"].lower(),
                )
        except ValidationError as err:
            self.__logger.error("Error parsing health: %s", err)
            raise VoltalisValidationException(*err.args) from err

        return devices_health

    async def get_devices_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        """Get all Voltalis devices consumption."""

        class RawDeviceConsumption(CustomModel):
            date: datetime
            consumption: float

        def __get_consumption_for_hour(
            devices_consumptions: dict[int, list[RawDeviceConsumption]],
            target_datetime: datetime,
        ) -> dict[int, RawDeviceConsumption]:
            target_hour = target_datetime.replace(minute=0, second=0, microsecond=0)
            result: dict[int, RawDeviceConsumption] = {}

            for device_id, consumptions in devices_consumptions.items():
                match = next(
                    (c for c in consumptions if c.date.replace(minute=0, second=0, microsecond=0) == target_hour), None
                )
                if match:
                    result[device_id] = match

            return result

        # Fetch the data from the voltalis API
        target_date_str = target_datetime.isoformat("T").split("T")[0]
        response: dict[str, dict[str, list[dict]]] = await self.__send_request(
            url=f"/api/site/{{site_id}}/consumption/day/{target_date_str}/full-data",
            method="GET",
            retry=False,
        )

        devices_consumptions: dict[int, list[RawDeviceConsumption]] = {}

        try:
            for device_id, device_consumptions in response["perAppliance"].items():
                devices_consumptions[int(device_id)] = [
                    RawDeviceConsumption(
                        date=device_consumption["stepTimestampOnSite"],
                        consumption=device_consumption["totalConsumptionInWh"],
                    )
                    for device_consumption in device_consumptions
                ]
        except ValidationError as err:
            self.__logger.error("Error parsing consumptions: %s", err)
            raise VoltalisValidationException(*err.args) from err

        filtered_consumptions = __get_consumption_for_hour(
            devices_consumptions=devices_consumptions,
            target_datetime=target_datetime,
        )

        return {
            device_id: filtered_consumption.consumption
            for device_id, filtered_consumption in filtered_consumptions.items()
        }

    async def get_manual_settings(self) -> dict[int, VoltalisManualSetting]:
        """Get manual settings for all devices."""

        manual_settings_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/manualsetting",
            method="GET",
            retry=True,
        )

        manual_settings: dict[int, VoltalisManualSetting] = {}
        try:
            for setting_document in manual_settings_response:
                new_settings = VoltalisManualSetting(
                    id=setting_document["id"],
                    enabled=setting_document["enabled"],
                    id_appliance=setting_document["idAppliance"],
                    appliance_name=setting_document["applianceName"],
                    appliance_type=setting_document["applianceType"],
                    until_further_notice=setting_document["untilFurtherNotice"],
                    is_on=setting_document["isOn"],
                    mode=setting_document["mode"].lower(),
                    end_date=setting_document["endDate"],
                    temperature_target=setting_document["temperatureTarget"],
                )
                manual_settings[setting_document["idAppliance"]] = new_settings
        except ValidationError as err:
            self.__logger.error("Error parsing manual settings: %s", err)
            raise VoltalisValidationException(*err.args) from err

        return manual_settings

    async def set_manual_setting(self, manual_setting_id: int, setting: VoltalisManualSettingUpdate) -> None:
        """Set manual setting for a device."""

        payload = {
            "enabled": setting.enabled,
            "idAppliance": setting.id_appliance,
            "untilFurtherNotice": setting.until_further_notice,
            "isOn": setting.is_on,
            "mode": setting.mode.upper(),
            "endDate": setting.end_date,
            "temperatureTarget": setting.temperature_target,
        }

        await self.__send_request(
            url=f"/api/site/{{site_id}}/manualsetting/{manual_setting_id}",
            method="PUT",
            retry=False,
            json=payload,
        )

        self.__logger.info("Manual setting %s updated for appliance %s", manual_setting_id, setting.id_appliance)

    async def get_subscriber_contracts(self) -> list[VoltalisSubscriberContract]:
        """Get subscriber contracts."""

        contracts_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/subscriber-contract",
            method="GET",
            retry=False,
        )

        contracts: list[VoltalisSubscriberContract] = []

        try:
            for contract_data in contracts_response:
                # Parse peak hours
                peak_hours = [
                    VoltalisTimeRange(from_time=hour["from"], to_time=hour["to"])
                    for hour in contract_data.get("peakHours", [])
                ]
                # Parse offpeak hours
                offpeak_hours = [
                    VoltalisTimeRange(from_time=hour["from"], to_time=hour["to"])
                    for hour in contract_data.get("offpeakHours", [])
                ]

                contract = VoltalisSubscriberContract(
                    id=contract_data["id"],
                    site_id=contract_data["siteId"],
                    subscriber_id=contract_data["subscriberId"],
                    name=contract_data["name"],
                    is_default=contract_data["isDefault"],
                    subscribed_power=contract_data["subscribedPower"],
                    is_peak_offpeak_contract=contract_data["isPeakOffPeakContract"],
                    subscription_base_price=contract_data.get("subscriptionBasePrice"),
                    subscription_peak_offpeak_base_price=contract_data.get("subscriptionPeakAndOffPeakHourBasePrice"),
                    kwh_base_price=contract_data.get("kwhBasePrice"),
                    kwh_peak_hour_price=contract_data.get("kwhPeakHourPrice"),
                    kwh_offpeak_hour_price=contract_data.get("kwhOffpeakHourPrice"),
                    creation_date_time=contract_data["creationDateTime"],
                    start_date=contract_data.get("startDate"),
                    end_date=contract_data.get("endDate"),
                    company_name=contract_data["companyName"],
                    api_contract_id=contract_data["apiContractId"],
                    company_id=contract_data["companyId"],
                    peak_hours=peak_hours,
                    offpeak_hours=offpeak_hours,
                )
                contracts.append(contract)
        except ValidationError as err:
            self.__logger.exception("Failed to parse subscriber contracts")
            raise VoltalisValidationException("Failed to parse subscriber contracts") from err

        return contracts

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

        full_url = urljoin(self.__base_url, _url)

        try:
            response = await self.__session.request(url=full_url, method=method, headers=headers, **kwargs)
            if response.status == 401:
                if retry:
                    self.__logger.warning("Authentication failed (401), retrying with new login...")
                    await self.login()
                    return await self.__send_request(url=url, method=method, retry=False, **kwargs)
                raise VoltalisAuthenticationException(await response.text())
            if response.status == 404:
                self.__logger.exception(await response.text())
                return None
            response.raise_for_status()
        except (ClientConnectorError, ClientError, ClientResponseError) as ex:
            if retry:
                self.__logger.warning("Connection error, retrying with new login...")
                await self.login()
                return await self.__send_request(url=url, method=method, retry=False, **kwargs)
            raise VoltalisException from ex

        # Return response depends on the content type
        if response.content_type == "application/json":
            return await response.json()
        return await response.read()
