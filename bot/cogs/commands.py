import disnake
from disnake.ext import commands

from bot import Bot
from bot.db import save_data


class Commands(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

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
        for timeline in self.bot.timelines:
            if timeline["guild_id"] == str(inter.guild.id):
                self.bot.timelines.remove(timeline)
                break
        self.bot.timelines.append(
            {
                "guild_id": str(inter.guild.id),
                "channel_id": str(channel.id),
                "created_by": str(inter.author.id),
                "created_at": inter.created_at.isoformat(),
            }
        )
        await save_data({"timelines": self.bot.timelines})
        await inter.send(f"{channel.mention} is now your 𝕏.", delete_after=60.0)


def setup(bot: Bot) -> None:
    bot.add_cog(Commands(bot))
