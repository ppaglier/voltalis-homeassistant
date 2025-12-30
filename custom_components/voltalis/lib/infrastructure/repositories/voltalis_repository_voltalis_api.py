import logging
from datetime import datetime

from pydantic import TypeAdapter, ValidationError

from custom_components.voltalis.lib.application.providers.http_client import (
    HttpClient,
    HttpClientException,
    HttpClientResponse,
)
from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.exceptions import VoltalisConnectionException, VoltalisValidationException
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceProgramming
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth
from custom_components.voltalis.lib.domain.models.energy_contract import (
    VoltalisEnergyContract,
    VoltalisEnergyContractPrices,
    VoltalisEnergyContractTypeEnum,
)
from custom_components.voltalis.lib.domain.models.manual_setting import (
    VoltalisManualSetting,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.range_model import RangeModel
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_device import VoltalisDeviceDto
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_device_consumption import VoltalisConsumptionDto
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_device_health import VoltalisDeviceHealthDto
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_manual_setting import (
    VoltalisManualSettingDto,
    VoltalisManualSettingUpdateDto,
)
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_subscriber_contract import (
    VoltalisSubscriberContractDto,
)
from custom_components.voltalis.lib.infrastructure.helpers.get_consumption_for_hour import get_consumption_for_hour


class VoltalisRepositoryVoltalisApi(VoltalisRepository):
    """Repository for Voltalis data access using the Voltalis API client."""

    def __init__(self, *, http_client: HttpClient) -> None:
        self._client = http_client
        self.__logger = logging.getLogger(__name__)

    async def get_devices(self) -> dict[int, VoltalisDevice]:
        response: HttpClientResponse[list[dict]]
        try:
            response = await self._client.send_request(
                url="/api/site/{site_id}/managed-appliance",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

        parsed_devices: list[VoltalisDeviceDto]
        try:
            parsed_devices = TypeAdapter(list[VoltalisDeviceDto]).validate_python(response.data)
        except ValidationError as err:
            self.__logger.error("Error parsing health: %s", err)
            raise VoltalisValidationException(*err.args) from err

        devices = {
            device.id: VoltalisDevice(
                id=device.id,
                name=device.name,
                type=device.id,
                modulator_type=device.modulator_type.value.lower(),
                available_modes=[mode.value.lower() for mode in device.available_modes],
                programming=VoltalisDeviceProgramming(
                    prog_type=device.programming.prog_type.value.lower(),
                    id_manual_setting=device.programming.id_manual_setting,
                    is_on=device.programming.is_on,
                    mode=device.programming.mode.value.lower() if device.programming.mode else None,
                    temperature_target=device.programming.temperature_target,
                    default_temperature=device.programming.default_temperature,
                ),
            )
            for device in parsed_devices
        }

        return devices

    async def get_devices_health(self) -> dict[int, VoltalisDeviceHealth]:
        response: HttpClientResponse[list[dict]]
        try:
            response = await self._client.send_request(
                url="/api/site/{site_id}/autodiag",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

        parsed_devices_health: list[VoltalisDeviceHealthDto]
        try:
            parsed_devices_health = TypeAdapter(list[VoltalisDeviceHealthDto]).validate_python(response.data)
        except ValidationError as err:
            self.__logger.error("Error parsing health: %s", err)
            raise VoltalisValidationException(*err.args) from err

        devices_health = {
            device_health.cs_appliance_id: VoltalisDeviceHealth(
                status=device_health.status.value.lower(),
            )
            for device_health in parsed_devices_health
        }

        return devices_health

    async def get_devices_daily_consumptions(self, target_datetime: datetime) -> dict[int, float]:
        # Fetch the data from the voltalis API
        target_date_str = target_datetime.isoformat("T").split("T")[0]

        response: HttpClientResponse[dict]
        try:
            response = await self._client.send_request(
                url=f"/api/site/{{site_id}}/consumption/day/{target_date_str}/full-data",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

        parsed_consumption: VoltalisConsumptionDto
        try:
            parsed_consumption = TypeAdapter(VoltalisConsumptionDto).validate_python(response.data)
        except ValidationError as err:
            self.__logger.error("Error parsing consumptions: %s", err)
            raise VoltalisValidationException(*err.args) from err

        devices_consumptions = {
            device_id: get_consumption_for_hour(
                consumptions=[
                    (consumption_record.step_timestamp_on_site, consumption_record.total_consumption_in_wh)
                    for consumption_record in sorted(device_consumptions, key=lambda x: x.step_timestamp_on_site)
                ],
                target_datetime=target_datetime,
            )
            for device_id, device_consumptions in parsed_consumption.per_appliance.items()
        }

        return devices_consumptions

    async def get_manual_settings(self) -> dict[int, VoltalisManualSetting]:
        response: HttpClientResponse[list[dict]]
        try:
            response = await self._client.send_request(
                url="/api/site/{site_id}/manualsetting",
                method="GET",
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

        parsed_manual_settings: list[VoltalisManualSettingDto]
        try:
            parsed_manual_settings = TypeAdapter(list[VoltalisManualSettingDto]).validate_python(response.data)
        except ValidationError as err:
            self.__logger.error("Error parsing manual settings: %s", err)
            raise VoltalisValidationException(*err.args) from err

        manual_settings = {
            manual_setting.id_appliance: VoltalisManualSetting(
                id=manual_setting.id,
                enabled=manual_setting.enabled,
                id_appliance=manual_setting.id_appliance,
                until_further_notice=manual_setting.until_further_notice,
                is_on=manual_setting.is_on,
                mode=manual_setting.mode.value.lower(),
                end_date=manual_setting.end_date,
                temperature_target=manual_setting.temperature_target,
            )
            for manual_setting in parsed_manual_settings
        }

        return manual_settings

    async def set_manual_setting(self, manual_setting_id: int, setting: VoltalisManualSettingUpdate) -> None:
        payload = VoltalisManualSettingUpdateDto(
            id=manual_setting_id,
            enabled=setting.enabled,
            id_appliance=setting.id_appliance,
            until_further_notice=setting.until_further_notice,
            is_on=setting.is_on,
            mode=setting.mode.value.upper(),
            end_date=setting.end_date,
            temperature_target=setting.temperature_target,
        ).model_dump(by_alias=True)

        try:
            await self._client.send_request(
                url=f"/api/site/{{site_id}}/manualsetting/{manual_setting_id}",
                method="PUT",
                body=payload,
            )
        except HttpClientException as err:
            raise VoltalisConnectionException("Error connecting to Voltalis API") from err

        self.__logger.info("Manual setting %s updated for appliance %s", manual_setting_id, setting.id_appliance)

    async def get_energy_contracts(self) -> dict[int, VoltalisEnergyContract]:
        response: HttpClientResponse[list[dict]] = await self._client.send_request(
            url="/api/site/{site_id}/subscriber-contract",
            method="GET",
        )

        if not response.data or len(response.data) == 0:
            raise VoltalisValidationException("No subscriber contracts found")

        parsed_contracts: list[VoltalisSubscriberContractDto]
        try:
            parsed_contracts = TypeAdapter(list[VoltalisSubscriberContractDto]).validate_python(response.data)
        except ValidationError as err:
            self.__logger.exception("Failed to parse subscriber contracts")
            raise VoltalisValidationException("Failed to parse subscriber contracts") from err

        contracts = {
            contract.id: VoltalisEnergyContract(
                id=contract.id,
                company_name=contract.company_name,
                name=contract.name,
                subscribed_power=contract.subscribed_power,
                type=(
                    VoltalisEnergyContractTypeEnum.BASE
                    if not contract.is_peak_off_peak_contract
                    else VoltalisEnergyContractTypeEnum.PEAK_OFFPEAK
                ),
                prices=VoltalisEnergyContractPrices(
                    subscription=(
                        (contract.subscription_base_price or 0.0)
                        if not contract.is_peak_off_peak_contract
                        else (contract.subscription_peak_off_peak_base_price or 0.0)
                    ),
                    kwh_base=contract.kwh_base_price,
                    kwh_peak=contract.kwh_peak_hour_price,
                    kwh_offpeak=contract.kwh_offpeak_hour_price,
                ),
                peak_hours=[
                    RangeModel(
                        start=datetime.strptime(time_range.from_time, "%H:%M").time(),
                        end=datetime.strptime(time_range.to_time, "%H:%M").time(),
                    )
                    for time_range in contract.peak_hours
                ],
                offpeak_hours=[
                    RangeModel(
                        start=datetime.strptime(time_range.from_time, "%H:%M").time(),
                        end=datetime.strptime(time_range.to_time, "%H:%M").time(),
                    )
                    for time_range in contract.offpeak_hours
                ],
            )
            for contract in parsed_contracts
        }
        return contracts
