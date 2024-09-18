import disnake

from bot import config
from bot.ext.views import Tweet


async def send_tweet(message: disnake.Message, /) -> None:
    async with Tweet(original_message=message) as tweet:
        tweet_message = await tweet.send()
        await tweet.update_reference()
    await tweet_message.add_reaction(config.EMOJI_RETWEET)
    await tweet_message.add_reaction(config.EMOJI_LIKE)
    await message.delete()


async def update_tweet(message: disnake.Message, /) -> None:
    async with Tweet(tweet_message=message) as tweet:
        await tweet.update()
