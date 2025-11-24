import logging
from datetime import datetime

from pydantic import ValidationError

from custom_components.voltalis.lib.application.providers.http_client import HttpClient, HttpClientResponse
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.exceptions import VoltalisValidationException
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceProgrammingStatus
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)


class VoltalisRepositoryVoltalisApi(VoltalisRepository):
    """Repository for Voltalis data access using the Voltalis API client."""

    def __init__(self, *, http_client: HttpClient) -> None:
        self._client = http_client
        self.__logger = logging.getLogger(__name__)

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        devices_response: HttpClientResponse[list[dict]] = await self._client.send_request(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
        )

        devices: dict[int, VoltalisDevice] = {}

        try:
            for device_document in devices_response.data:
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
        devices_health_response: HttpClientResponse[list[dict]] = await self._client.send_request(
            url="/api/site/{site_id}/autodiag",
            method="GET",
        )

        devices_health: dict[int, VoltalisDeviceHealth] = {}
        try:
            for device_health_document in devices_health_response.data:
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
        response: HttpClientResponse[dict[str, dict[str, list[dict]]]] = await self._client.send_request(
            url=f"/api/site/{{site_id}}/consumption/day/{target_date_str}/full-data",
            method="GET",
        )

        devices_consumptions: dict[int, list[RawDeviceConsumption]] = {}

        try:
            for device_id, device_consumptions in response.data["perAppliance"].items():
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

        manual_settings_response: HttpClientResponse[list[dict]] = await self._client.send_request(
            url="/api/site/{site_id}/manualsetting",
            method="GET",
        )

        manual_settings: dict[int, VoltalisManualSetting] = {}
        try:
            for setting_document in manual_settings_response.data:
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

        await self._client.send_request(
            url=f"/api/site/{{site_id}}/manualsetting/{manual_setting_id}",
            method="PUT",
            body=payload,
        )

        self.__logger.info("Manual setting %s updated for appliance %s", manual_setting_id, setting.id_appliance)
