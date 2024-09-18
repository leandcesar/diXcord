import json
import os

import aiofiles

from bot import config


async def save_data(data: dict) -> None:
    async with aiofiles.open(config.PATH_DATA, "w") as f:
        await f.write(json.dumps(data, indent=4))


async def load_data() -> dict:
    if os.path.exists(config.PATH_DATA):
        async with aiofiles.open(config.PATH_DATA) as f:
            content = await f.read()
            return json.loads(content)
    return {}
