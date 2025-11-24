from typing import Any, TypeVar

from aiohttp import ClientConnectorError, ClientError, ClientResponse, ClientResponseError, ClientSession

from custom_components.voltalis.lib.application.providers.http_client import (
    HttpClient,
    HttpClientException,
    HttpClientResponse,
)

T = TypeVar("T")
TData = TypeVar("TData")


class HttpClientAioHttp(HttpClient):
    """Concrete implementation of the HttpClient using the aiohttp library."""

    def __init__(
        self,
        *,
        session: ClientSession,
        base_url: str | None = None,
    ) -> None:
        self._session = session
        self._base_url = base_url

    @staticmethod
    async def _from_response(*, response: ClientResponse) -> HttpClientResponse[T]:
        """Convert a aiohttp Response to a HttpClientResponse."""

        data: Any = None
        if response.content_type == "application/json":
            data = await response.json()
        else:
            data = await response.read()

        return HttpClientResponse(
            data=data,
            status=response.status,
            url=str(response.url),
            headers=dict(response.headers),
        )

    @staticmethod
    def _from_exception(
        *, exception: ClientConnectorError | ClientError | ClientResponseError
    ) -> HttpClientException[T]:
        """
        Convert an aiohttp exception (ClientConnectorError, ClientError, or ClientResponseError)
        to a HttpClientException.
        """

        response: HttpClientResponse[T] | None = None
        if isinstance(exception, ClientResponseError):
            response = HttpClientResponse(
                data=None,
                status=exception.status,
                url=str(exception.request_info.url),
                headers=dict(exception.headers) if exception.headers else {},
            )

        return HttpClientException(
            message=str(exception),
            request={
                "url": str(exception.request_info.url),
                "method": exception.request_info.method,
                "headers": dict(exception.request_info.headers),
            }
            if hasattr(exception, "request_info")
            else {},
            response=response,
        )

    def _get_full_url(self, url: str) -> str:
        """Get the full url. If the url is relative, it will be appended to the base url."""

        return "/".join(s.strip("/") for s in [self._base_url, url] if isinstance(s, str))

    async def send_request(
        self,
        *,
        url: str,
        method: str,
        body: Any | None = None,
        query_params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> HttpClientResponse[TData]:
        """Send an HTTP request to the server."""

        full_url = self._get_full_url(url)
        full_headers = headers or {}
        try:
            response = await self._session.request(
                method=method,
                url=full_url,
                params=query_params,
                json=body,
                headers=full_headers,
                **kwargs,
            )
            response.raise_for_status()
            return await self._from_response(response=response)
        except (ClientConnectorError, ClientError, ClientResponseError) as e:
            raise self._from_exception(exception=e) from e
