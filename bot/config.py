import json
import os

DEBUG: bool = bool(os.getenv("DEBUG"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
BOT_TOKEN: str | None = os.getenv("BOT_TOKEN")
BOT_TEST_DISCORD_GUILD_IDS: list[int] = json.loads(os.getenv("BOT_TEST_DISCORD_GUILD_IDS", "[]"))

PATH_LOCALE = "bot/locale"
PATH_COGS = "bot/cogs"
PATH_AVATAR = "tmp/avatar"  # noqa: S108
PATH_ATTACHMENT = "tmp/attachment"  # noqa: S108
PATH_TWEET = "tmp/tweet"  # noqa: S108
PATH_STATISTICS = "tmp/statistics"  # noqa: S108
PATH_DATA = "data/data.json"

EMOJI_RETWEET = "🔁"
EMOJI_LIKE = "❤️"

IMAGE_FORMAT = "png"
