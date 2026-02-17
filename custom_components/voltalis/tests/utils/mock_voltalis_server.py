from datetime import datetime

from aiohttp import ClientSession

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import ManualSetting
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import LiveConsumption
from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.shared.providers.http_client import HttpClient
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_device import VoltalisDeviceDto
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_stub import VoltalisProviderStub
from custom_components.voltalis.tests.utils.mock_http_server import MockHttpServer


class MockVoltalisServer:
    """Mock Voltalis API"""

    def __init__(self) -> None:
        self.__voltalis_provider = VoltalisProviderStub()
        self.__voltalis_api = MockHttpServer()

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
                response=lambda: MockHttpServer.StubResponse(
                    status_code=200,
                    data={"token": "fake_token"},
                ),
            ),
        )

        self.__voltalis_api.set_request_handler(
            url="/api/account/me",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                response=lambda: MockHttpServer.StubResponse(
                    status_code=200,
                    data={"defaultSite": {"id": "1"}},
                ),
            ),
        )

    def given_devices(self, devices: dict[int, Device]) -> None:
        self.__voltalis_provider.set_devices(devices)

        voltalis_devices = [VoltalisDeviceDto.from_device(device) for device in devices.values()]

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                response=lambda: MockHttpServer.StubResponse(
                    status_code=200,
                    data=voltalis_devices,
                ),
            ),
        )

    def given_devices_health(self, devices_health: dict[int, DeviceHealth]) -> None:
        self.__voltalis_provider.set_devices_health(devices_health)

    def given_live_consumption(self, consumption: LiveConsumption) -> None:
        self.__voltalis_provider.set_live_consumption(consumption)

    def given_devices_consumptions(self, devices_consumptions: dict[int, list[tuple[datetime, float]]]) -> None:
        self.__voltalis_provider.set_devices_consumptions(devices_consumptions)

    def given_manual_settings(self, manual_settings: dict[int, ManualSetting]) -> None:
        self.__voltalis_provider.set_manual_settings(manual_settings)

    def given_current_energy_contract(self, energy_contracts: dict[int, EnergyContract]) -> None:
        self.__voltalis_provider.set_energy_contracts(energy_contracts)

    def given_programs(self, programs: dict[int, Program]) -> None:
        self.__voltalis_provider.set_programs(programs)
