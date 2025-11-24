import asyncio

from aiohttp import ClientSession

from custom_components.voltalis.lib.application.providers.http_client import HttpClient
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
from custom_components.voltalis.lib.infrastructure.providers.http_client_aiohttp import HttpClientAioHttp
from custom_components.voltalis.lib.infrastructure.repositories.voltalis_repository_in_memory import (
    VoltalisRepositoryInMemory,
)
from custom_components.voltalis.tests.utils.mock_http_server import MockHttpServer


class MockVoltalisServer:
    """Mock Voltalis API"""

    def __init__(self) -> None:
        self.__voltalis_repository = VoltalisRepositoryInMemory()
        self.__voltalis_api = MockHttpServer()

        self.__session = ClientSession()

    # --------------------------
    # Server management methods
    # --------------------------

    def start_server(self) -> None:
        """Starts the mocked server"""

        self.__voltalis_api.start_server()

    def stop_server(self) -> None:
        """Stops the mocked server"""

        self.__voltalis_api.stop_server()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.__session.close())

    def get_client(self) -> HttpClient:
        """Returns the HTTP client of the mocked server"""

        if not self.__voltalis_api.is_server_running():
            raise RuntimeError("Server is not started. Please start the server before getting the client.")

        return HttpClientAioHttp(session=self.__session, base_url=self.__voltalis_api.get_full_url())

    # --------------------------
    # Storage management methods
    # --------------------------

    def get_storage(self) -> dict:
        """Returns the storage of the mocked server"""

        return {"devices": self.__voltalis_repository.__devices}

    def reset_storage(self) -> None:
        """Resets the storage of the mocked server"""

        if not self.__voltalis_api.is_server_running():
            raise RuntimeError("Server is not started. Please start the server before resetting the storage.")

        self.__voltalis_api.reset_request_handlers()
        self.set_devices({})

    def set_devices(self, devices: dict[int, VoltalisDevice]) -> None:
        """Sets the devices in the mocked server storage"""

        self.__voltalis_repository.set_devices(devices)

        site_id: int | None = None

        def request_interceptor(request: dict, config: dict) -> None:
            """Intercepts the request to add additional checks"""
            nonlocal site_id

            _path_params = config.get("path_params", {})
            site_id = _path_params.get("site_id")

        async def get_response(request: dict) -> MockHttpServer.StubResponse:
            """Handles the GET /api/site/{site_id}/managed-appliance request"""
            if site_id is None:
                return MockHttpServer.StubResponse(status_code=404)

            devices = await self.__voltalis_repository.get_devices()
            devices_list = []
            for device in devices.values():
                devices_list.append(
                    {
                        "id": device.id,
                        "name": device.name,
                        "applianceType": device.type,
                        "modulatorType": device.modulator_type,
                        "availableModes": device.available_modes,
                        "programming": {
                            "progType": device.programming.prog_type,
                            "idManualSetting": device.programming.id_manual_setting,
                            "isOn": device.programming.is_on,
                            "mode": device.programming.mode,
                            "temperatureTarget": device.programming.temperature_target,
                            "defaultTemperature": device.programming.default_temperature,
                        },
                    }
                )

            return MockHttpServer.StubResponse(data=devices_list)

        self.__voltalis_api.set_request_handler(
            url="/api/site/{site_id}/managed-appliance",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(
                response=get_response,
                request_interceptor=request_interceptor,
            ),
        )
