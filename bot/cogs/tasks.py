import os
import time
from datetime import datetime, timedelta, timezone

from disnake.ext import commands, tasks

from bot import Bot, config
from bot.ext.message import send_tweet


class Tasks(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.recover_tweets.start()
        self.clean_tmp.start()

    @tasks.loop(seconds=10)
    async def recover_tweets(self):
        for timeline in self.bot.timelines:
            created_at = datetime.fromisoformat(timeline["created_at"])
            channel_id = int(timeline["channel_id"])
            channel = await self.bot.fetch_channel(channel_id)
            messages = await channel.history(limit=30, after=created_at, oldest_first=False).flatten()
            for message in messages[::-1]:
                if message.author.id == self.bot.user.id:
                    continue
                if datetime.now(tz=timezone.utc) - message.created_at < timedelta(seconds=20):
                    break
                return await send_tweet(self.bot, message)

    @recover_tweets.before_loop
    async def before_recover_tweets(self):
        await self.bot.wait_until_ready()

    @tasks.loop(seconds=60)
    async def clean_tmp(self):
        now = time.time()
        for path in [config.PATH_ATTACHMENT, config.PATH_AVATAR, config.PATH_TWEET]:
            for filename in os.listdir(path):
                file = os.path.join(path, filename)
                if (
                    os.path.isfile(file)
                    and file.endswith(config.IMAGE_FORMAT)
                    and now - os.path.getmtime(file) > 300
                ):
                    os.remove(file)


def setup(bot: Bot) -> None:
    bot.add_cog(Tasks(bot))
