import os

import disnake
from disnake.ext import commands

from src import config
from src.bot import Bot
from src.components.tweet import Tweet
from src.utils.persistent_dict import PersistentDict


class Twitter(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.guilds = PersistentDict.from_file(config.PATH_DATA)
        os.makedirs(config.PATH_AVATAR, exist_ok=True)
        os.makedirs(config.PATH_ATTACHMENT, exist_ok=True)
        os.makedirs(config.PATH_TWEET, exist_ok=True)
        os.makedirs(config.PATH_STATISTICS, exist_ok=True)

    def _is_valid_channel(self, obj) -> bool:
        return obj.guild_id in self.guilds and obj.channel_id == self.guilds[obj.guild_id]["channel_id"]

    async def on_raw_reaction_update(
        self,
        payload: disnake.RawReactionActionEvent | disnake.RawReactionClearEvent | disnake.RawReactionClearEmojiEvent,
    ) -> None:
        if not self._is_valid_channel(payload):
            return None
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author.id != self.bot.user.id:
            return None
        async with Tweet(tweet_message=message) as tweet:
            await tweet.update()

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

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if not self._is_valid_channel(message):
            return None
        if message.author.id == self.bot.user.id:
            return None
        if message.is_system():
            return None
        async with Tweet(original_message=message) as tweet:
            tweet_message = await tweet.send()
            await tweet.update_reference()
        await tweet_message.add_reaction(config.EMOJI_RETWEET)
        await tweet_message.add_reaction(config.EMOJI_LIKE)
        await message.delete()

    @commands.has_permissions(administrator=True)
    @commands.slash_command()
    async def settings(
        self,
        inter: disnake.GuildCommandInteraction,
        channel: disnake.TextChannel,
    ) -> None:
        """Sets the specified text channel as the X in the server. {{ SETTINGS_COMMAND }}

        Parameters
        ----------
        channel: The text channel to set as the X. {{ SETTINGS_CHANNEL }}
        """
        self.guilds[inter.guild.id] = {
            "guild_id": inter.guild.id,
            "channel_id": channel.id,
            "created_by": inter.author.id,
            "created_at": inter.created_at.isoformat(),
        }
        await inter.send(f"{channel.mention} is now your 𝕏.")


def setup(bot: Bot) -> None:
    bot.add_cog(Twitter(bot))
