import disnake

from bot import Bot, config
from bot.ext.views import Tweet


async def send_tweet(bot: Bot, message: disnake.Message) -> None:
    bot.logger.debug(
        f"{message.guild} ({message.guild.id}) "
        f"#{message.channel} ({message.channel.id}) "
        f"@{message.author} ({message.author.id}): "
        f"{message.content!r} ({message.id})"
    )
    async with Tweet(original_message=message) as tweet:
        tweet_message = await tweet.send()
        await tweet.update_reference()
    await tweet_message.add_reaction(config.EMOJI_RETWEET)
    await tweet_message.add_reaction(config.EMOJI_LIKE)
    await message.delete()


async def update_tweet(bot: Bot, message: disnake.Message) -> None:
    bot.logger.debug(
        f"{message.guild} ({message.guild.id}) "
        f"#{message.channel} ({message.channel.id}) "
        f"@{message.author} ({message.author.id}): "
        f"{message.embeds[0].image.url!r} ({message.id})"
    )
    async with Tweet(tweet_message=message) as tweet:
        await tweet.update()

    # text = tweet_message.embeds[0].description
    # if text is None or "https://discord.com/" not in text:
    #     return None
    # url = text[text.index("https://discord.com/"):].split(maxsplit=1)[0].strip()
    # message_id = url.rsplit("/", maxsplit=1)[-1]
    # message = await tweet_message.channel.fetch_message(message_id)
    # if message is None:
    #     return None
    # async with Tweet(tweet_message=message) as tweet:
    #     await tweet.update()
