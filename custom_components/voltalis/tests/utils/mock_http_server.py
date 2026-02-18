import asyncio
import inspect
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import (
    Any,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    cast,
)
from urllib.parse import parse_qs, urlparse

from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.tests.utils.custom_json_encoder import CustomJsonEncoder

T = TypeVar("T")
TData = TypeVar("TData")
TModel = TypeVar("TModel", bound=CustomModel)


class MockHttpServer:
    """Mock Http Server"""

    class StubResponse(CustomModel, Generic[T]):
        """StubResponse type."""

        status_code: int | None = None
        headers: dict[str, str] = {}
        data: T | None = None

    class RequestHandler(CustomModel, Generic[T]):
        """Request handler type."""

        handle: (
            Callable[[Any, dict], Awaitable["MockHttpServer.StubResponse[T]"]]
            | Callable[[Any, dict], "MockHttpServer.StubResponse[T]"]
        )
        with_body: bool = False
        with_query_params: bool = False

    def __init__(self) -> None:
        self.__request_handlers: dict[str, dict[str, tuple[MockHttpServer.RequestHandler, dict]]] = {}
        self.__http_server = HTTPServer(("127.0.0.1", 0), self.server_request_handler_factory())
        self.__thread = Thread(target=self.__http_server.serve_forever, daemon=True)

    # --------------------------
    # Server management methods
    # --------------------------

    def start_server(self) -> None:
        """Starts the mocked server"""

        self.__thread.start()

    def is_server_running(self) -> bool:
        """Returns True if the server is running"""

        return self.__thread.is_alive()

    def stop_server(self) -> None:
        """Stops the mocked server"""

        self.__http_server.shutdown()
        self.__http_server.server_close()
        self.__thread.join()

    def get_server_address(self) -> tuple[str, int]:
        """Returns the address of the mocked server"""

        address, port = self.__http_server.server_address[:2]
        return (cast(str, address), port)

    def get_full_url(self, url: str = "") -> str:
        """Returns the full URL of the mocked server"""

        address, port = self.get_server_address()
        return f"http://{address}:{port}{url}"

    # --------------------------
    # Request handler methods
    # --------------------------

    def reset_request_handlers(self) -> None:
        """Reset all request handlers."""
        self.__request_handlers.clear()

    def set_request_handler(
        self,
        *,
        url: str,
        method: str,
        new_request_handler: RequestHandler[T],
        config: dict = {},
    ) -> None:
        """
        Set a request handler.
        When a request is made to the given url and method, the new_request_handler will be called.
        If a config is provided, the request will only be handled if the config params match the handler config params.
        The params in the config must match the handler config params in key and type.
        """
        if url not in self.__request_handlers:
            self.__request_handlers[url] = {}
        self.__request_handlers[url][method] = (new_request_handler, config)

    # --------------------------
    # Utils methods
    # --------------------------

    def server_request_handler_factory(self) -> type[BaseHTTPRequestHandler]:
        request_handlers = self.__request_handlers

        class ServerRequestHandler(BaseHTTPRequestHandler):
            """Server request handler for the mocked server"""

            def do_GET(self) -> None:
                self.__handle_request()

            def do_POST(self) -> None:
                self.__handle_request()

            def do_PUT(self) -> None:
                self.__handle_request()

            def do_DELETE(self) -> None:
                self.__handle_request()

            def do_PATCH(self) -> None:
                self.__handle_request()

            def do_HEAD(self) -> None:
                self.__handle_request()

            def do_OPTIONS(self) -> None:
                self.__handle_request()

            def __find_request_handler(self, url: str, method: str) -> tuple[MockHttpServer.RequestHandler, dict]:
                """Find the request handler for the given url and method."""

                # Handle path parameters in the URL
                for handler_url in request_handlers:
                    # Split URLs into parts
                    handler_parts = handler_url.strip("/").split("/")
                    url_parts = url.strip("/").split("/")

                    if len(handler_parts) != len(url_parts):
                        continue

                    path_params = {}
                    matched = True
                    for hp, up in zip(handler_parts, url_parts):
                        if hp.startswith("{") and hp.endswith("}"):
                            param_name = hp[1:-1]
                            path_params[param_name] = up
                        elif hp != up:
                            matched = False
                            break

                    if matched and method in request_handlers[handler_url]:
                        # Inject path params into config
                        config = request_handlers[handler_url][method][1].copy()
                        config["path_params"] = path_params
                        return request_handlers[handler_url][method][0], config

                if url not in request_handlers or method not in request_handlers[url]:
                    raise Exception(f"No request handler found for {method} {url}")

                return request_handlers[url][method]

            def __get_body(self) -> Any:
                """Get the body of the request."""

                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length) if content_length > 0 else b""
                if body is None:
                    return None

                # Try to parse the body as JSON if the content type is application/json
                content_type = self.headers.get("Content-Type", "")
                if content_type.startswith("multipart/form-data"):
                    raise Exception("Unsupported content type for body parsing: multipart/form-data")

                try:
                    body_str = body.decode()
                    body_data = json.loads(body_str)
                except json.JSONDecodeError:
                    return body_str
                except UnicodeDecodeError:
                    return None
                return body_data

            def __handle_request(self) -> None:
                url = urlparse(self.path)
                path = url.path
                method = self.command
                config: dict = {}

                # Find the handler for the requested path and method
                try:
                    request_handler, handler_config = self.__find_request_handler(path, method)
                except Exception as error:
                    self.send_error(404, str(error))
                    return

                if "path_params" in handler_config:
                    config["path_params"] = handler_config["path_params"]

                body_data: Any = None
                if request_handler.with_body:
                    try:
                        body_data = self.__get_body()
                    except Exception as error:
                        print("Error while parsing body", error)
                        self.send_error(400, str(error))
                        return

                if request_handler.with_query_params:
                    try:
                        query_params = {
                            k: v[0] if len(v) == 1 else v for k, v in parse_qs(url.query).items() if len(v) > 0
                        }
                        config["params"] = query_params
                    except Exception as error:
                        print("Error while parsing query params", error)
                        self.send_error(500, str(error))
                        return

                try:
                    # Handle both sync and async response callables
                    if inspect.iscoroutinefunction(request_handler.handle):
                        # Async callable
                        response = asyncio.run(request_handler.handle(body_data, config))
                    else:
                        # Sync callable
                        response = request_handler.handle(body_data, config)
                except Exception as error:
                    print("Error while handling request", error)
                    self.send_error(500, str(error))
                    return

                try:
                    status_code = response.status_code or 200
                    self.send_response(status_code)
                    self.send_header("Content-Type", "application/json")
                    for k, v in response.headers.items():
                        self.send_header(k, v)
                    self.end_headers()
                    if response.data is not None:
                        self.wfile.write(
                            json.dumps(MockHttpServer.serialize_data(response.data), cls=CustomJsonEncoder).encode()
                        )
                    else:
                        self.wfile.write(b"")
                except Exception as error:
                    print("Error while sending response", error)
                    self.send_error(500, str(error))

        return ServerRequestHandler

    @staticmethod
    def serialize_data(data: Any) -> Any:
        if data is None:
            return data

        if isinstance(data, list):
            return [MockHttpServer.serialize_data(d) for d in data]

        if isinstance(data, CustomModel):
            return data.model_dump(mode="json", by_alias=True)

        return data
