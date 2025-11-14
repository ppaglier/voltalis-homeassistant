import asyncio
import json
from datetime import timedelta

from custom_components.voltalis.lib.infrastructure.date_provider_real import DateProviderReal
from custom_components.voltalis.lib.infrastructure.voltalis_client_aiohttp import VoltalisClientAiohttp


async def main() -> None:
    date_provider = DateProviderReal()
    async with VoltalisClientAiohttp(
        username="pierrelouis.pagliero@gmail.com",
        password="!s2XJ3@yq!oR65wvYm3*",
    ) as client:
        # Get the consumption of the previous hour (We can't get future or current consumption)
        target_datetime = date_provider.get_now() - timedelta(hours=1)

        # await client.get_devices()
        print(json.dumps(await client.get_devices_consumptions(target_datetime), indent=4))


if __name__ == "__main__":
    asyncio.run(main())
