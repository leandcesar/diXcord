import os

import disnake
from disnake.ext import commands

from src import log

logger = log.get_logger(__name__)


class Bot(commands.InteractionBot):
    def __init__(
        self,
        intents: disnake.Intents,
        allowed_mentions: disnake.AllowedMentions | None = None,
        *,
        reload: bool | None = None,
        owner_ids: set[int] | None = None,
        test_guilds: set[int] | None = None,
    ) -> None:
        super().__init__(
            intents=intents,
            allowed_mentions=allowed_mentions,
            owner_ids=owner_ids,
            reload=reload,
            test_guilds=test_guilds,
        )

    def load_extensions(self, path: str) -> None:
        for item in os.listdir(path):
            if "__" in item or not item.endswith(".py"):
                continue
            try:
                ext = f"src.extensions.{item[:-3]}"
                super().load_extension(ext)
            except commands.errors.NoEntryPointError as e:
                logger.critical(f"{e.name} has no setup function.")

    async def on_slash_command(self, inter: disnake.ApplicationCommandInteraction) -> None:
        logger.info(f"/{inter.application_command.qualified_name} {inter.options}")

    async def on_slash_command_error(self, inter: disnake.ApplicationCommandInteraction, e: Exception) -> None:
        if isinstance(e, commands.errors.MissingRequiredArgument):
            logger.warning(f"/{inter.application_command.qualified_name} {inter.options} = {e}")
        else:
            logger.error(f"/{inter.application_command.qualified_name} {inter.options} = {e}", exc_info=e)
