import asyncio
import json

from custom_components.voltalis.lib.infrastructure.voltalis_client_aiohttp import VoltalisClientAiohttp


async def main() -> None:
    async with VoltalisClientAiohttp(
        username="pierrelouis.pagliero@gmail.com",
        password="!s2XJ3@yq!oR65wvYm3*",
    ) as client:
        await client.get_me()
        # await client.get_devices()
        print(json.dumps(await client.get_consumption(), indent=4))


if __name__ == "__main__":
    asyncio.run(main())
