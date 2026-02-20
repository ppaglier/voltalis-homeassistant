from typing import AsyncGenerator

import pytest
from aiohttp import ClientSession

from custom_components.voltalis.lib.domain.shared.exceptions import VoltalisAuthenticationException
from custom_components.voltalis.lib.domain.shared.providers.http_client import HttpClientException, HttpClientResponse
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import (
    VoltalisClientAiohttp,
)
from custom_components.voltalis.tests.base_fixture import BaseFixture
from custom_components.voltalis.tests.utils.mock_http_server import MockHttpServer


@pytest.mark.integration
async def test_login_stores_token_and_site_id(fixture: "VoltalisClientFixture") -> None:
    """Test login stores token, site id, and credentials."""

    # Arrange
    fixture.given_login_ok(token="token-123", default_site_id="42")

    # Act
    await fixture.client.login(username="user", password="pass")

    # Assert
    assert fixture.client.storage["username"] == "user"
    assert fixture.client.storage["password"] == "pass"
    assert fixture.client.storage["auth_token"] == "token-123"
    assert fixture.client.storage["default_site_id"] == "42"
    assert fixture.state["login_calls"] == 1
    assert fixture.state["me_calls"] == 1


@pytest.mark.integration
async def test_get_access_token_unauthorized(fixture: "VoltalisClientFixture") -> None:
    """Test get_access_token raises on invalid credentials."""

    # Arrange
    fixture.given_login_unauthorized()

    # Act / Assert
    with pytest.raises(VoltalisAuthenticationException):
        await fixture.client.get_access_token(username="user", password="bad")


@pytest.mark.integration
async def test_send_request_triggers_login_and_formats_site_id(fixture: "VoltalisClientFixture") -> None:
    """Test send_request triggers login and injects site_id into URLs."""

    # Arrange
    fixture.given_login_ok()
    fixture.client.storage["username"] = "user"
    fixture.client.storage["password"] = "pass"

    def ping_handler(body: object, config: dict) -> MockHttpServer.StubResponse[dict]:
        assert fixture.state["login_calls"] == 1
        assert fixture.state["me_calls"] == 1
        assert config["path_params"]["site_id"] == "1"
        return MockHttpServer.StubResponse(status_code=200, data={"ok": True})

    fixture.server.set_request_handler(
        url="/api/site/{site_id}/ping",
        method="GET",
        new_request_handler=MockHttpServer.RequestHandler(handle=ping_handler),
    )

    # Act
    response: HttpClientResponse[dict] = await fixture.client.send_request(url="/api/site/{site_id}/ping", method="GET")

    # Assert
    assert response.data == {"ok": True}


@pytest.mark.integration
async def test_send_request_retries_on_401(fixture: "VoltalisClientFixture") -> None:
    """Test send_request retries once after a 401 response."""

    # Arrange
    fixture.given_login_ok(token="new-token", default_site_id="1")
    fixture.client.storage["username"] = "user"
    fixture.client.storage["password"] = "pass"
    fixture.client.storage["auth_token"] = "stale-token"
    fixture.client.storage["default_site_id"] = "1"

    calls = {"count": 0}

    def retry_handler(body: object, config: dict) -> MockHttpServer.StubResponse[dict]:
        calls["count"] += 1
        if calls["count"] == 1:
            return MockHttpServer.StubResponse(status_code=401, data={"error": "unauthorized"})
        return MockHttpServer.StubResponse(status_code=200, data={"ok": True})

    fixture.server.set_request_handler(
        url="/api/site/{site_id}/retry",
        method="GET",
        new_request_handler=MockHttpServer.RequestHandler(handle=retry_handler),
    )

    # Act
    response: HttpClientResponse[dict] = await fixture.client.send_request(
        url="/api/site/{site_id}/retry", method="GET"
    )

    # Assert
    assert response.data == {"ok": True}
    assert calls["count"] == 2
    assert fixture.state["login_calls"] == 1
    assert fixture.state["me_calls"] == 1


@pytest.mark.integration
async def test_logout_clears_storage(fixture: "VoltalisClientFixture") -> None:
    """Test logout clears the storage when a token is present."""

    # Arrange
    fixture.client.storage["username"] = "user"
    fixture.client.storage["password"] = "pass"
    fixture.client.storage["auth_token"] = "token"
    fixture.client.storage["default_site_id"] = "1"
    fixture.server.set_request_handler(
        url="/auth/logout",
        method="DELETE",
        new_request_handler=MockHttpServer.RequestHandler(
            handle=lambda body, config: MockHttpServer.StubResponse(status_code=200)
        ),
    )

    # Act
    await fixture.client.logout()

    # Assert
    assert fixture.client.storage["username"] is None
    assert fixture.client.storage["password"] is None
    assert fixture.client.storage["auth_token"] is None
    assert fixture.client.storage["default_site_id"] is None


@pytest.mark.integration
async def test_logout_no_token_does_nothing(fixture: "VoltalisClientFixture") -> None:
    """Test logout does nothing when no token is present."""

    # Arrange
    fixture.client.storage["username"] = None
    fixture.client.storage["password"] = None
    fixture.client.storage["auth_token"] = None
    fixture.client.storage["default_site_id"] = None

    # Act
    await fixture.client.logout()

    # Assert
    assert fixture.client.storage["username"] is None
    assert fixture.client.storage["password"] is None
    assert fixture.client.storage["auth_token"] is None
    assert fixture.client.storage["default_site_id"] is None


@pytest.mark.integration
async def test_send_request_non_retryable_401(fixture: "VoltalisClientFixture") -> None:
    """Test send_request does not retry on 401 if can_retry is False."""

    # Arrange
    fixture.given_login_ok()
    fixture.client.storage["username"] = "user"
    fixture.client.storage["password"] = "pass"
    fixture.client.storage["auth_token"] = "stale-token"
    fixture.client.storage["default_site_id"] = "1"

    def unauthorized_handler(body: object, config: dict) -> MockHttpServer.StubResponse[dict]:
        return MockHttpServer.StubResponse(status_code=401, data={"error": "unauthorized"})

    fixture.server.set_request_handler(
        url="/api/site/{site_id}/no-retry",
        method="GET",
        new_request_handler=MockHttpServer.RequestHandler(handle=unauthorized_handler),
    )

    # Act / Assert
    with pytest.raises(HttpClientException):
        await fixture.client.send_request(url="/api/site/{site_id}/no-retry", method="GET", can_retry=False)


class VoltalisClientFixture(BaseFixture):
    """VoltalisClientAiohttp fixture."""

    def __init__(self) -> None:
        super().__init__()
        self.server = MockHttpServer()
        self.state: dict[str, int] = {}

    async def async_before_all(self) -> None:
        self.server.start_server()
        self.client_session = ClientSession()
        self.client = VoltalisClientAiohttp(
            session=self.client_session,
            base_url=self.server.get_full_url(),
        )

    async def async_after_all(self) -> None:
        if self.client_session is not None:
            await self.client_session.close()
        self.server.stop_server()

    def before_each(self) -> None:
        self.server.reset_request_handlers()
        self.state = {"login_calls": 0, "me_calls": 0}

        assert self.client is not None
        self.client.storage["username"] = None
        self.client.storage["password"] = None
        self.client.storage["auth_token"] = None
        self.client.storage["default_site_id"] = None

    # --------------------------------------
    # Arrange
    # --------------------------------------
    def given_login_ok(self, *, token: str = "fake-token", default_site_id: str = "1") -> None:
        def login_handler(body: object, config: dict) -> MockHttpServer.StubResponse[dict]:
            self.state["login_calls"] += 1
            return MockHttpServer.StubResponse(status_code=200, data={"token": token})

        def me_handler(body: object, config: dict) -> MockHttpServer.StubResponse[dict]:
            self.state["me_calls"] += 1
            return MockHttpServer.StubResponse(status_code=200, data={"defaultSite": {"id": default_site_id}})

        self.server.set_request_handler(
            url="/auth/login",
            method="POST",
            new_request_handler=MockHttpServer.RequestHandler(handle=login_handler, with_body=True),
        )
        self.server.set_request_handler(
            url="/api/account/me",
            method="GET",
            new_request_handler=MockHttpServer.RequestHandler(handle=me_handler),
        )

    def given_login_unauthorized(self) -> None:
        self.server.set_request_handler(
            url="/auth/login",
            method="POST",
            new_request_handler=MockHttpServer.RequestHandler(
                handle=lambda body, config: MockHttpServer.StubResponse(status_code=401, data={"error": "invalid"}),
                with_body=True,
            ),
        )


pytestmark = [pytest.mark.asyncio(loop_scope="module"), pytest.mark.enable_socket]


@pytest.fixture(scope="module")
async def fixture_all() -> AsyncGenerator[VoltalisClientFixture, None]:
    """Before all tests, start the server. Then after all tests, stop the server."""
    fixture = VoltalisClientFixture()
    await fixture.async_before_all()
    yield fixture
    await fixture.async_after_all()


@pytest.fixture(scope="function")
async def fixture(fixture_all: VoltalisClientFixture) -> AsyncGenerator[VoltalisClientFixture, None]:
    """Before each test, reset server handlers and client storage."""
    fixture_all.before_each()
    yield fixture_all
