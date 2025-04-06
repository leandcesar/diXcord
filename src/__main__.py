from __future__ import annotations

import asyncio
import os
import signal
import sys

import disnake

from src import config, log
from src.bot import Bot

logger = log.get_logger(__name__)
_intents = disnake.Intents.all()


async def main() -> None:
    bot = Bot(
        intents=_intents,
        test_guilds=config.BOT_TEST_DISCORD_GUILD_IDS,
    )
    bot.i18n.load("src/locale/")  # type: ignore[reportUnknownMemberType]

    try:
        bot.load_extensions("src/extensions")
    except Exception as e:
        await bot.close()
        raise e

    try:
        logger.info("Bot is starting.")
        if os.name != "nt":
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(bot.start(config.BOT_TOKEN or ""), loop=loop)
            loop.add_signal_handler(signal.SIGINT, lambda: future.cancel())
            loop.add_signal_handler(signal.SIGTERM, lambda: future.cancel())
            await future
        else:
            await bot.start(config.BOT_TOKEN or "")
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.warning("Kill command received. Bot is closed.")
        if not bot.is_closed():
            await bot.close()
    except disnake.errors.PrivilegedIntentsRequired:
        logger.critical(
            "Missing Privileged Intents. "
            "Fix this by adding the required privileged intents for your bot inside of: "
            f"https://discord.com/developers/applications/{bot.user.id}/bot"
        )
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
