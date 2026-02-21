import logging
from datetime import date, datetime
from typing import Any, Callable

from aiohttp import ClientSession

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import (
    ManualSetting,
    ManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.providers.http_client import HttpClient
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_device import (
    VOLTALIS_DEVICE_MODE_MAPPING,
    VoltalisDeviceDto,
    VoltalisDeviceDtoModeEnum,
)
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_device_consumption import (
    VoltalisConsumptionDto,
    VoltalisConsumptionDtoDevice,
)
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_device_health import (
    VoltalisDeviceHealthDto,
)
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_manual_setting import (
    VoltalisManualSettingDto,
    VoltalisManualSettingUpdateDto,
)
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_program import VoltalisProgramDto
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_realtime_consumption import (
    VoltalisRealtimeConsumptionDto,
    VoltalisRealtimeConsumptionDtoConsumption,
)
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_subscriber_contract import (
    VoltalisSubscriberContractDto,
)
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import VoltalisProviderStub
from custom_components.voltalis.tests.utils.mock_http_server import MockHttpServer


class MockVoltalisServer:
    """Mock Voltalis API"""

    def __init__(self) -> None:
        self.__voltalis_provider = VoltalisProviderStub()
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.WARNING)
        self.__voltalis_api = MockHttpServer(logger=self.__logger)

    # --------------------------
    # Server management methods
    # --------------------------

    async def start_server(self) -> None:
        """Starts the mocked server"""

        self.__voltalis_api.start_server()
        self.__client_session = ClientSession()

    async def stop_server(self) -> None:
        """Stops the mocked server"""

        self.__voltalis_api.stop_server()
        await self.__client_session.close()

    def get_client(self) -> HttpClient:
        """Returns the HTTP client of the mocked server"""

        if not self.__voltalis_api.is_server_running():
            raise RuntimeError("Server is not started. Please start the server before getting the client.")

        return VoltalisClientAiohttp(
            session=self.__client_session,
            base_url=self.__voltalis_api.get_full_url(),
        )

    # --------------------------
    # Storage management methods
    # --------------------------

    def get_storage(self) -> dict:
        """Returns the storage of the mocked server"""

        return {
            "devices": self.__voltalis_provider._devices,
            "devices_health": self.__voltalis_provider._devices_health,
            "live_consumption": self.__voltalis_provider._live_consumption,
            "devices_consumptions": self.__voltalis_provider._devices_consumptions,
            "manual_settings": self.__voltalis_provider._manual_settings,
            "energy_contracts": self.__voltalis_provider._energy_contracts,
            "programs": self.__voltalis_provider._programs,
        }

    def reset_storage(self) -> None:
        """Resets the storage of the mocked server"""

        if not self.__voltalis_api.is_server_running():
            raise RuntimeError("Server is not started. Please start the server before resetting the storage.")

        self.__voltalis_api.reset_request_handlers()

    def given_login_ok(self) -> None:
        self.__voltalis_api.set_request_handler(
            url="/auth/login",
            method="POST",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=lambda body, config: MockHttpServer.StubResponse(
                    status_code=200,
                    data={"token": "fake_token"},
                ),
            ),
        )

        self.__voltalis_api.set_request_handler(
            url="/api/account/me",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=lambda body, config: MockHttpServer.StubResponse(
                    status_code=200,
                    data={"defaultSite": {"id": "1"}},
                ),
            ),
        )

        self.__voltalis_api.set_request_handler(
            url="/auth/logout",
            method="DELETE",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=lambda body, config: MockHttpServer.StubResponse(status_code=200)
            ),
        )

    def given_login_failure(self, error_type: str = "invalid_auth") -> None:
        """Configure the mock server to fail login with the specified error type.

        Args:
            error_type: One of:
                - "invalid_auth" (401),
                - "cannot_connect" (no handler)
                - "unknown" (no handler, same as cannot_connect)

                Note: "unknown" error responses (like 500) from an HTTP server are typically treated as "cannot_connect"
                by the client since they become HttpClientException. To get a true "unknown" error in the config_flow,
                you would need to raise an exception that isn't HttpClientException, which is not possible with a real HTTP server.
        """  # noqa: E501
        if error_type == "cannot_connect" or error_type == "unknown":
            # Reset all handlers to simulate connection failure
            self.__voltalis_api.reset_request_handlers()
        elif error_type == "invalid_auth":
            # Set up login to return 401 Unauthorized
            self.__voltalis_api.set_request_handler(
                url="/auth/login",
                method="POST",
                new_request_handler=MockHttpServer.RequestHandler(
                    handle=lambda body, config: MockHttpServer.StubResponse(status_code=401),
                    with_body=True,
                ),
            )

    def given_devices(self, devices: list[Device]) -> None:
        self.__voltalis_provider.set_devices(devices)

        async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
            devices_dict = await self.__voltalis_provider.get_devices()
            manual_settings = await self.__voltalis_provider.get_manual_settings()

            # Sync device programming.is_on and prog_type with manual setting
            synced_devices = []
            for device_id, device in devices_dict.items():
                # manual_settings is keyed by id_appliance (device_id)
                manual_setting = manual_settings.get(device_id)
                if manual_setting:
                    # Update the device programming to match manual setting
                    updated_programming = device.programming.model_copy(
                        update={
                            "prog_type": ProgramTypeEnum.MANUAL if manual_setting.enabled else ProgramTypeEnum.DEFAULT,
                            "is_on": manual_setting.is_on,
                            "mode": manual_setting.mode if manual_setting.enabled else device.programming.mode,
                        }
                    )
                    device = device.model_copy(update={"programming": updated_programming})
                synced_devices.append(device)

            voltalis_devices = [VoltalisDeviceDto.from_device(device) for device in synced_devices]

            return MockHttpServer.StubResponse(
                status_code=200,
                data=voltalis_devices,
            )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=request_handler,
            ),
        )

    def given_devices_health(self, devices_health: list[DeviceHealth]) -> None:
        self.__voltalis_provider.set_devices_health(devices_health)

        async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
            devices_health = await self.__voltalis_provider.get_devices_health()
            voltalis_devices_health = [
                VoltalisDeviceHealthDto.from_device_health(device_health) for device_health in devices_health.values()
            ]

            return MockHttpServer.StubResponse(
                status_code=200,
                data=voltalis_devices_health,
            )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/autodiag",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=request_handler,
            ),
        )

    def given_live_consumption(self, consumption: LiveConsumption) -> None:
        self.__voltalis_provider.set_live_consumption(consumption)

        async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
            live_consumption = await self.__voltalis_provider.get_live_consumption()
            voltalis_live_consumption = VoltalisRealtimeConsumptionDto(
                consumptions=[
                    VoltalisRealtimeConsumptionDtoConsumption(
                        total_consumption_in_wh=live_consumption.consumption,
                    ),
                ]
            )

            return MockHttpServer.StubResponse(
                status_code=200,
                data=voltalis_live_consumption,
            )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/consumption/realtime",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=request_handler,
            ),
        )

    def given_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        self.__voltalis_provider.set_devices_consumptions(devices_consumptions)

        async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
            target_date_str = date.fromisoformat(config["path_params"]["target_date_str"])
            devices_consumptions = await self.__voltalis_provider.get_devices_daily_consumptions(target_date_str)

            voltalis_devices_consumptions = VoltalisConsumptionDto(
                per_appliance={
                    device_id: [
                        VoltalisConsumptionDtoDevice(
                            step_timestamp_on_site=date,
                            total_consumption_in_wh=consumption,
                        )
                        for (date, consumption) in consumptions
                    ]
                    for device_id, consumptions in devices_consumptions.items()
                }
            )

            return MockHttpServer.StubResponse(
                status_code=200,
                data=voltalis_devices_consumptions,
            )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/consumption/day/{target_date_str}/full-data",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=request_handler,
            ),
        )

    def given_manual_settings(self, manual_settings: list[ManualSetting]) -> None:
        self.__voltalis_provider.set_manual_settings(manual_settings)

        async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
            manual_settings = await self.__voltalis_provider.get_manual_settings()
            voltalis_manual_settings = [
                VoltalisManualSettingDto.from_manual_setting(manual_setting)
                for manual_setting in manual_settings.values()
            ]

            return MockHttpServer.StubResponse(
                status_code=200,
                data=voltalis_manual_settings,
            )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/manualsetting",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=request_handler,
            ),
        )

        async def request_handler_2(body: Any, config: dict) -> MockHttpServer.StubResponse:
            manual_setting_id = int(config["path_params"]["manual_setting_id"])

            voltalis_manual_setting_update = VoltalisManualSettingUpdateDto(**body)

            has_ecov = voltalis_manual_setting_update.mode == VoltalisDeviceDtoModeEnum.ECOV
            if has_ecov:
                current_mode = DeviceModeEnum.ECO
            else:
                current_mode = VOLTALIS_DEVICE_MODE_MAPPING[voltalis_manual_setting_update.mode]

            manual_setting_update = ManualSettingUpdate(
                enabled=voltalis_manual_setting_update.enabled,
                id_appliance=voltalis_manual_setting_update.id_appliance,
                until_further_notice=voltalis_manual_setting_update.until_further_notice,
                is_on=voltalis_manual_setting_update.is_on,
                has_ecov=has_ecov,
                mode=current_mode,
                end_date=voltalis_manual_setting_update.end_date,
                temperature_target=voltalis_manual_setting_update.temperature_target,
            )

            await self.__voltalis_provider.set_manual_setting(manual_setting_id, manual_setting_update)

            return MockHttpServer.StubResponse(
                status_code=200,
            )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/manualsetting/{manual_setting_id}",
            method="PUT",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=request_handler_2,
                with_body=True,
            ),
        )

    def given_energy_contracts(self, energy_contracts: list[EnergyContract]) -> None:
        self.__voltalis_provider.set_energy_contracts(energy_contracts)

        async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
            energy_contracts = await self.__voltalis_provider.get_energy_contracts()
            voltalis_energy_contracts = [
                VoltalisSubscriberContractDto.from_energy_contract(energy_contract)
                for energy_contract in energy_contracts.values()
            ]

            return MockHttpServer.StubResponse(
                status_code=200,
                data=voltalis_energy_contracts,
            )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/subscriber-contract",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=request_handler,
            ),
        )

    def given_programs(self, programs: list[Program]) -> None:
        self.__voltalis_provider.set_programs(programs)

        def get_handler_from_endpoint(quick_setting: bool) -> Callable:
            async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
                programs = await self.__voltalis_provider.get_programs()
                voltalis_programs = [
                    VoltalisProgramDto.from_program(program)
                    for program in programs.values()
                    if (program.type is ProgramTypeEnum.QUICK and quick_setting)
                    or (program.type is ProgramTypeEnum.USER and not quick_setting)
                ]

                return MockHttpServer.StubResponse(
                    status_code=200,
                    data=voltalis_programs,
                )

            return request_handler

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/programming/program",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=get_handler_from_endpoint(quick_setting=False),
            ),
        )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/quicksettings",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=get_handler_from_endpoint(quick_setting=True),
            ),
        )

        def put_handler_from_endpoint(quick_setting: bool) -> Callable:
            async def request_handler(body: Any, config: dict) -> MockHttpServer.StubResponse:
                program_id = int(config["path_params"]["program_id"])
                name = body.pop("name", None)
                if quick_setting and name is None:
                    quick_settings_mapping = ["longleave", "shortleave", "athome"]
                    name = (
                        f"quicksettings.{quick_settings_mapping[program_id]}"
                        if program_id < len(quick_settings_mapping)
                        else f"quicksettings.unknown{program_id}"
                    )
                voltalis_program_update = VoltalisProgramDto(id=program_id, name=name, **body)
                program_update = voltalis_program_update.to_program(
                    ProgramTypeEnum.QUICK if quick_setting else ProgramTypeEnum.USER
                )

                await self.__voltalis_provider.toggle_program(program_update)

                return MockHttpServer.StubResponse(
                    status_code=200,
                )

            return request_handler

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/programming/program/{program_id}",
            method="PUT",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=put_handler_from_endpoint(quick_setting=False),
                with_body=True,
            ),
        )

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/quicksettings/{program_id}/enable",
            method="PUT",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=put_handler_from_endpoint(quick_setting=True),
                with_body=True,
            ),
        )
