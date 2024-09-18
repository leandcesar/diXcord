import disnake
from disnake.ext import commands

from bot import Bot
from bot.ext.message import send_tweet, update_tweet


class Events(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def on_raw_reaction_update(
        self,
        payload: disnake.RawReactionActionEvent | disnake.RawReactionClearEvent | disnake.RawReactionClearEmojiEvent,
    ) -> None:
        if payload.channel_id not in self.bot.timelines_ids:
            return None
        if payload.user_id == self.bot.user.id:
            return None
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id == self.bot.user.id:
            return await update_tweet(self.bot, message)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.channel.id not in self.bot.timelines_ids:
            return None
        if message.author.id == self.bot.user.id:
            return None
        if message.is_system():
            return None
        return await send_tweet(self.bot, message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: disnake.RawReactionActionEvent) -> None:
        await self.on_raw_reaction_update(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: disnake.RawReactionActionEvent) -> None:
        await self.on_raw_reaction_update(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_clear(self, payload: list[disnake.RawReactionClearEvent]) -> None:
        await self.on_raw_reaction_update(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_clear_emoji(self, payload: disnake.RawReactionClearEmojiEvent) -> None:
        await self.on_raw_reaction_update(payload)


def setup(bot: Bot) -> None:
    bot.add_cog(Events(bot))
