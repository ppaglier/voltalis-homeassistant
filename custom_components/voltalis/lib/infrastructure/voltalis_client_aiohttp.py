import logging
from datetime import datetime
from typing import Any, TypedDict
from urllib.parse import urljoin

from aiohttp import ClientConnectorError, ClientError, ClientResponseError, ClientSession, ClientTimeout

from custom_components.voltalis.lib.application.voltalis_client import VoltalisClient
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.device import (
    VoltalisApplianceDiagnostic,
    VoltalisApplianceProgramming,
    VoltalisConsumptionObjective,
    VoltalisContract,
    VoltalisContractPeakHours,
    VoltalisDevice,
    VoltalisManagedAppliance,
    VoltalisProgram,
    VoltalisRealTimeConsumption,
    VoltalisSiteInfo,
)
from custom_components.voltalis.lib.domain.exceptions import VoltalisAuthenticationException, VoltalisException


class VoltalisClientAiohttp(VoltalisClient):
    """Voltalis client integration using the Aiohttp lib"""

    BASE_URL = "https://api.myvoltalis.com"
    LOGIN_ROUTE = "/auth/login"

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
        logger.setLevel(logging.DEBUG)
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

        self.__logger.debug("Login start")
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
        self.__logger.debug("Login Response: %s", response)
        return response["token"]

    async def __get_me(self) -> str:
        self.__logger.debug("Get me start")
        response = await self.__send_request(
            url="/api/account/me",
            retry=False,
            method="GET",
        )
        self.__logger.debug("Get me Response: %s", response)
        return response["defaultSite"]["id"]

    async def login(self) -> None:
        """Execute Voltalis login."""

        if self.__username is None or self.__password is None:
            raise VoltalisException("You must provide username & password")

        self.__logger.debug("Login start")
        token = await self.get_access_token(
            username=self.__username,
            password=self.__password,
        )
        self.__storage["auth_token"] = token

        self.__storage["default_site_id"] = await self.__get_me()
        self.__logger.info("Login successful")

    async def logout(self) -> None:
        if self.__storage["auth_token"] is None:
            return

        await self.__send_request(url="/auth/logout", retry=False, method="DELETE")
        self.__logger.info("Logout successful")
        self.__storage["auth_token"] = None

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        """Get all Voltalis devices."""

        self.__logger.debug("Get all Voltalis devices")
        devices_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
            retry=False,
        )

        devices = {
            device_document["id"]: VoltalisDevice(
                id=device_document["id"],
                name=device_document["name"],
                type=device_document["applianceType"],
                modulator_type=device_document["modulatorType"],
                available_modes=device_document["availableModes"],
                prog_type=device_document.get("programming", {})["progType"],
            )
            for device_document in devices_response
        }

        return devices

    async def get_devices_health(self) -> dict[int, bool]:
        """Get devices health"""

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

        self.__logger.debug("Get all Voltalis devices consumption")

        # Fetch the data from the voltalis API
        target_date_str = target_datetime.isoformat("T").split("T")[0]
        response: dict[str, dict[str, list[dict]]] = await self.__send_request(
            url="/api/site/{site_id}/consumption/day/" + target_date_str + "/full-data",
            method="GET",
            retry=False,
        )

        filtered_consumptions = __get_consumption_for_hour(
            devices_consumptions={
                int(device_id): [
                    RawDeviceConsumption(
                        date=device_consumption["stepTimestampOnSite"],
                        consumption=device_consumption["totalConsumptionInWh"],
                    )
                    for device_consumption in device_consumptions
                ]
                for device_id, device_consumptions in response["perAppliance"].items()
            },
            target_datetime=target_datetime,
        )

        return {
            device_id: filtered_consumption.consumption
            for device_id, filtered_consumption in filtered_consumptions.items()
        }

    async def get_consumption_objective(self) -> VoltalisConsumptionObjective | None:
        """Get consumption objective."""

        self.__logger.debug("Get consumption objective")
        response: dict | None = await self.__send_request(
            url="/api/site/{site_id}/objective",
            method="GET",
            retry=False,
        )

        if response is None:
            return None

        return VoltalisConsumptionObjective(
            yearly_objective_in_wh=response["yearlyObjectiveInWh"],
            yearly_objective_in_currency=response["yearlyObjectiveInCurrency"],
        )

    async def get_realtime_consumption(self, num_points: int = 10) -> list[VoltalisRealTimeConsumption]:
        """Get real-time consumption."""

        self.__logger.debug("Get real-time consumption")
        response: dict | None = await self.__send_request(
            url=f"/api/site/{{site_id}}/consumption/realtime?mode=TEN_MINUTES&numPoints={num_points}",
            method="GET",
            retry=False,
        )

        if response is None:
            return []

        return [
            VoltalisRealTimeConsumption(
                timestamp=consumption["stepTimestampInUtc"],
                total_consumption_in_wh=consumption["totalConsumptionInWh"],
                total_consumption_in_currency=consumption["totalConsumptionInCurrency"],
            )
            for consumption in response.get("consumptions", [])
        ]

    async def get_programs(self) -> list[VoltalisProgram]:
        """Get programs."""

        self.__logger.debug("Get programs")
        response: list[dict] | None = await self.__send_request(
            url="/api/site/{site_id}/programming/program",
            method="GET",
            retry=False,
        )

        if response is None:
            return []

        return [
            VoltalisProgram(
                id=program["id"],
                name=program["name"],
                enabled=program["enabled"],
                program_type=program.get("programType"),
                program_name=program.get("programName"),
                until_further_notice=program.get("untilFurtherNotice", False),
                end_date=program.get("endDate"),
                geoloc_currently_on=program.get("geolocCurrentlyOn", False),
            )
            for program in response
        ]

    async def get_site_info(self) -> VoltalisSiteInfo | None:
        """Get site information."""

        self.__logger.debug("Get site information")
        response: dict | None = await self.__send_request(
            url="/api/account/me",
            method="GET",
            retry=False,
        )

        if response is None or "defaultSite" not in response:
            return None

        site = response["defaultSite"]
        return VoltalisSiteInfo(
            id=site["id"],
            address=site["address"],
            name=site["name"],
            postal_code=site["postalCode"],
            city=site["city"],
            country=site["country"],
            timezone=site["timezone"],
            voltalis_version=site["voltalisVersion"],
            installation_date=site["installationDate"],
            has_global_consumption_measure=site["hasGlobalConsumptionMeasure"],
            has_dso_measure=site["hasDsoMeasure"],
        )

    async def get_subscriber_contracts(self) -> list[VoltalisContract]:
        """Get subscriber contracts."""

        self.__logger.debug("Get subscriber contracts")
        response: list[dict] | None = await self.__send_request(
            url="/api/site/{site_id}/subscriber-contract",
            method="GET",
            retry=False,
        )

        if response is None:
            return []

        return [
            VoltalisContract(
                id=contract["id"],
                name=contract["name"],
                is_default=contract["isDefault"],
                subscribed_power=contract["subscribedPower"],
                is_peak_off_peak_contract=contract["isPeakOffPeakContract"],
                subscription_base_price=contract.get("subscriptionBasePrice"),
                subscription_peak_and_off_peak_hour_base_price=contract["subscriptionPeakAndOffPeakHourBasePrice"],
                kwh_base_price=contract.get("kwhBasePrice"),
                kwh_peak_hour_price=contract["kwhPeakHourPrice"],
                kwh_offpeak_hour_price=contract["kwhOffpeakHourPrice"],
                company_name=contract["companyName"],
                peak_hours=[
                    VoltalisContractPeakHours(from_time=ph["from"], to_time=ph["to"]) for ph in contract["peakHours"]
                ],
                offpeak_hours=[
                    VoltalisContractPeakHours(from_time=ph["from"], to_time=ph["to"])
                    for ph in contract["offpeakHours"]
                ],
            )
            for contract in response
        ]

    async def get_managed_appliances(self) -> dict[int, VoltalisManagedAppliance]:
        """Get managed appliances with full details."""

        self.__logger.debug("Get managed appliances")
        appliances_response: list[dict] = await self.__send_request(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
            retry=False,
        )

        appliances = {
            appliance_doc["id"]: VoltalisManagedAppliance(
                id=appliance_doc["id"],
                name=appliance_doc["name"],
                type=appliance_doc["applianceType"],
                modulator_type=appliance_doc["modulatorType"],
                available_modes=appliance_doc["availableModes"],
                voltalis_version=appliance_doc["voltalisVersion"],
                programming=VoltalisApplianceProgramming(
                    prog_type=appliance_doc["programming"]["progType"],
                    prog_name=appliance_doc["programming"].get("progName"),
                    id_manual_setting=appliance_doc["programming"].get("idManualSetting"),
                    is_on=appliance_doc["programming"]["isOn"],
                    until_further_notice=appliance_doc["programming"].get("untilFurtherNotice"),
                    mode=appliance_doc["programming"]["mode"],
                    id_planning=appliance_doc["programming"].get("idPlanning"),
                    end_date=appliance_doc["programming"].get("endDate"),
                    temperature_target=appliance_doc["programming"]["temperatureTarget"],
                    default_temperature=appliance_doc["programming"]["defaultTemperature"],
                ),
                heating_level=appliance_doc["heatingLevel"],
            )
            for appliance_doc in appliances_response
        }

        return appliances

    async def get_appliance_diagnostics(self) -> dict[int, VoltalisApplianceDiagnostic]:
        """Get appliance diagnostics."""

        self.__logger.debug("Get appliance diagnostics")
        diagnostics_response: list[dict] | None = await self.__send_request(
            url="/api/site/{site_id}/autodiag",
            method="GET",
            retry=False,
        )

        if diagnostics_response is None:
            return {}

        diagnostics: dict[int, VoltalisApplianceDiagnostic] = {
            diag_doc["csApplianceId"]: VoltalisApplianceDiagnostic(
                name=diag_doc["name"],
                cs_modulator_id=diag_doc["csModulatorId"],
                cs_appliance_id=diag_doc["csApplianceId"],
                status=diag_doc["status"],
                diag_test_enabled=diag_doc["diagTestEnabled"],
            )
            for diag_doc in diagnostics_response
        }

        return diagnostics

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

        self.__logger.debug(f"Call Voltalis API to {_url} using {method}")

        full_url = urljoin(self.__base_url, _url)

        try:
            response = await self.__session.request(url=full_url, method=method, headers=headers, **kwargs)
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
