import logging
from datetime import datetime

import disnake
from disnake.ext import commands

from bot.db import load_data


class Bot(commands.InteractionBot):
    def __init__(
        self,
        *,
        debug: bool = False,
        logger_cls: logging.Logger = logging.getLogger(),
        logger_level: str | int = "INFO",
        **kwargs,
    ) -> None:
        command_sync_flags = commands.CommandSyncFlags.default()
        command_sync_flags.sync_commands_debug = debug
        intents = disnake.Intents.all()
        super().__init__(
            intents=intents,
            command_sync_flags=command_sync_flags,
            reload=debug,
            asyncio_debug=debug,
            enable_debug_events=debug,
            strict_localization=True,
            **kwargs,
        )
        self.logger = logger_cls
        self.logger.setLevel(logger_level)
        self.started_at = datetime.utcnow()
        self.timelines: list[dict[str, str]] = []

    @property
    def timelines_ids(self) -> list[int]:
        return [int(timeline["channel_id"]) for timeline in self.timelines]

    async def on_ready(self) -> None:
        self.logger.info(f"Logged in as @{self.user} ({self.user.id})")
        if not self.timelines:
            data = await load_data()
            self.timelines = data["timelines"]
