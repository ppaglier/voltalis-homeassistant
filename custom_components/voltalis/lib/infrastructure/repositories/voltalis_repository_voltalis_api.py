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
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceProgrammingStatus
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
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_device_consumption import VoltalisDeviceConsumptionDto
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

    async def get_devices_daily_consumptions(self, target_datetime: datetime) -> dict[int, float]:
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

        devices_consumptions: dict[int, list[VoltalisDeviceConsumptionDto]] = {}
        try:
            for device_id, device_consumptions in response.data["perAppliance"].items():
                devices_consumptions[int(device_id)] = sorted(
                    [VoltalisDeviceConsumptionDto(**device_consumption) for device_consumption in device_consumptions],
                    key=lambda x: x.step_timestamp_on_site,
                )
        except ValidationError as err:
            self.__logger.error("Error parsing consumptions: %s", err)
            raise VoltalisValidationException(*err.args) from err

        consumptions = {
            device_id: get_consumption_for_hour(
                consumptions=[
                    (consumption_record.step_timestamp_on_site, consumption_record.total_consumption_in_wh)
                    for consumption_record in consumption_records
                ],
                target_datetime=target_datetime,
            )
            for device_id, consumption_records in devices_consumptions.items()
        }

        return consumptions

    async def get_manual_settings(self) -> dict[int, VoltalisManualSetting]:
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

    async def get_energy_contracts(self) -> dict[int, VoltalisEnergyContract]:
        response: HttpClientResponse[list[dict]] = await self._client.send_request(
            url="/api/site/{site_id}/subscriber-contract",
            method="GET",
        )

        if not response.data or len(response.data) == 0:
            raise VoltalisValidationException("No subscriber contracts found")

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
