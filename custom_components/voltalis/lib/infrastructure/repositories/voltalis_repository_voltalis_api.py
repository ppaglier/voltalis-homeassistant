import logging
from datetime import datetime

from pydantic import ValidationError

from custom_components.voltalis.lib.application.providers.http_client import (
    HttpClient,
    HttpClientException,
    HttpClientResponse,
)
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.exceptions import VoltalisConnectionException, VoltalisValidationException
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceProgrammingStatus
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram, VoltalisProgramTypeEnum


class VoltalisRepositoryVoltalisApi(VoltalisRepository):
    """Repository for Voltalis data access using the Voltalis API client."""

    def __init__(self, *, http_client: HttpClient) -> None:
        self._client = http_client
        self.__logger = logging.getLogger(__name__)

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        devices_response: HttpClientResponse[list[dict]]
        try:
            devices_response = await self._client.send_request(
                url="/api/site/{site_id}/managed-appliance",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

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
        devices_health_response: HttpClientResponse[list[dict]]
        try:
            devices_health_response = await self._client.send_request(
                url="/api/site/{site_id}/autodiag",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

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

        response: HttpClientResponse[dict[str, dict[str, list[dict]]]]
        try:
            response = await self._client.send_request(
                url=f"/api/site/{{site_id}}/consumption/day/{target_date_str}/full-data",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

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
        manual_settings_response: HttpClientResponse[list[dict]]
        try:
            manual_settings_response = await self._client.send_request(
                url="/api/site/{site_id}/manualsetting",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

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

        try:
            await self._client.send_request(
                url=f"/api/site/{{site_id}}/manualsetting/{manual_setting_id}",
                method="PUT",
                body=payload,
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

        self.__logger.info("Manual setting %s updated for appliance %s", manual_setting_id, setting.id_appliance)

    # -------------------------------------------------------------------------
    # Programs
    # -------------------------------------------------------------------------

    async def get_programs(self) -> dict[int, VoltalisProgram]:
        """Get all programs (USER + DEFAULT) from the Voltalis servers."""
        programs: dict[int, VoltalisProgram] = {}

        # Fetch USER programs from /programming/program
        user_programs_response: HttpClientResponse[list[dict]]
        try:
            user_programs_response = await self._client.send_request(
                url="/api/site/{site_id}/programming/program",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API for user programs") from err

        try:
            for program_json in user_programs_response.data:
                program = VoltalisProgram(
                    id=program_json["id"],
                    name=program_json["name"],
                    enabled=program_json["enabled"],
                    program_type=VoltalisProgramTypeEnum.USER,
                )
                programs[program.id] = program
        except (ValidationError, KeyError) as err:
            self.__logger.error("Error parsing user programs: %s", err)
            raise VoltalisValidationException(f"Error parsing user programs: {err}") from err

        # Fetch DEFAULT programs from /quicksettings
        default_programs_response: HttpClientResponse[list[dict]]
        try:
            default_programs_response = await self._client.send_request(
                url="/api/site/{site_id}/quicksettings",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API for default programs") from err

        try:
            for program_json in default_programs_response.data:
                program = VoltalisProgram(
                    id=program_json["id"],
                    name=program_json["name"],
                    enabled=program_json["enabled"],
                    program_type=VoltalisProgramTypeEnum.DEFAULT,
                )
                programs[program.id] = program
        except (ValidationError, KeyError) as err:
            self.__logger.error("Error parsing default programs: %s", err)
            raise VoltalisValidationException(f"Error parsing default programs: {err}") from err

        return programs

    async def get_user_program(self, program_id: int) -> VoltalisProgram:
        """Get a single user program by ID."""
        program_response: HttpClientResponse[dict]
        try:
            program_response = await self._client.send_request(
                url=f"/api/site/{{site_id}}/programming/program/{program_id}",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException(f"Error fetching user program {program_id}") from err

        try:
            return VoltalisProgram(
                id=program_response.data["id"],
                name=program_response.data["name"],
                enabled=program_response.data["enabled"],
                program_type=VoltalisProgramTypeEnum.USER,
            )
        except (ValidationError, KeyError) as err:
            self.__logger.error("Error parsing user program %s: %s", program_id, err)
            raise VoltalisValidationException(f"Error parsing user program {program_id}: {err}") from err

    async def get_default_programs(self) -> dict[int, VoltalisProgram]:
        """Get all default programs (quicksettings) from the Voltalis servers."""
        default_programs_response: HttpClientResponse[list[dict]]
        try:
            default_programs_response = await self._client.send_request(
                url="/api/site/{site_id}/quicksettings",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API for default programs") from err

        programs: dict[int, VoltalisProgram] = {}
        try:
            for program_json in default_programs_response.data:
                program = VoltalisProgram(
                    id=program_json["id"],
                    name=program_json["name"],
                    enabled=program_json["enabled"],
                    program_type=VoltalisProgramTypeEnum.DEFAULT,
                )
                programs[program.id] = program
        except (ValidationError, KeyError) as err:
            self.__logger.error("Error parsing default programs: %s", err)
            raise VoltalisValidationException(f"Error parsing default programs: {err}") from err

        return programs

    async def set_user_program_state(self, program_id: int, name: str, enabled: bool) -> None:
        """Set the enabled state of a user program."""
        payload = {
            "name": name,
            "enabled": enabled,
        }

        try:
            await self._client.send_request(
                url=f"/api/site/{{site_id}}/programming/program/{program_id}",
                method="PUT",
                body=payload,
            )
        except HttpClientException as err:
            raise VoltalisConnectionException(f"Error updating user program {program_id}") from err

        self.__logger.info("User program %s updated: enabled=%s", program_id, enabled)

    async def set_default_program_state(self, program_id: int, enabled: bool) -> None:
        """Set the enabled state of a default program."""
        payload = {
            "enabled": enabled,
        }

        try:
            await self._client.send_request(
                url=f"/api/site/{{site_id}}/quicksettings/{program_id}/enable",
                method="PUT",
                body=payload,
            )
        except HttpClientException as err:
            raise VoltalisConnectionException(f"Error updating default program {program_id}") from err

        self.__logger.info("Default program %s updated: enabled=%s", program_id, enabled)
