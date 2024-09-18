from __future__ import annotations

import os

import disnake

from bot import config
from bot.components.image import crop_image, download_image, overlay_images
from bot.components.tweet import fake_tweet_generator


class Tweet:
    def __init__(
        self,
        *,
        original_message: disnake.Message | None = None,
        tweet_message: disnake.Message | None = None,
    ) -> None:
        if original_message is None and tweet_message is None:
            raise ValueError("Either 'original_message' or 'tweet_message' must be provided.")
        self.original_message: disnake.Message | None = original_message
        self.tweet_message: disnake.Message | None = tweet_message
        self.message_id: int = original_message.id if original_message else tweet_message.id
        self._total_retweets: int = None
        self._total_likes: int = None
        self._total_replies: int = None

    async def __aenter__(self) -> Tweet:
        if self.tweet_message is not None:
            await self.download_tweet()
            return self
        if self.original_message is not None:
            await self.download_avatar()
            await self.download_attachments()
            text = self.original_message.content
            for mention in self.original_message.mentions:
                text = text.replace(mention.mention, f"@{mention.name}")
            for channel_mention in self.original_message.channel_mentions:
                text = text.replace(channel_mention.mention, f"#{channel_mention.name}")
            await fake_tweet_generator(
                text=text,
                name=self.original_message.author.display_name,
                username=self.original_message.author.name,
                avatar_path=self.avatar_path,
                attachments_path=self.attachments_paths,
                timestamp=self.original_message.created_at,
                output_path=self.tweet_path,
            )
            return self
        raise ValueError("Either 'original_message' or 'tweet_message' must be provided.")

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        ...

    @property
    def avatar_path(self) -> str | None:
        return f"{config.PATH_AVATAR}/{self.original_message.author.id}.{config.IMAGE_FORMAT}"

    @property
    def tweet_path(self) -> str:
        return f"{config.PATH_TWEET}/{self.message_id}.{config.IMAGE_FORMAT}"

    @property
    def statistics_path(self) -> str:
        statistics = f"{self._total_replies}_{self.total_retweets}_{self.total_likes}"
        return f"{config.PATH_STATISTICS}/{statistics}.{config.IMAGE_FORMAT}"

    @property
    def attachments_paths(self) -> list[str]:
        return [
            f"{config.PATH_ATTACHMENT}/{attachment.id}.{config.IMAGE_FORMAT}"
            for attachment in self.original_message.attachments[:4]
        ]

    @property
    def total_retweets(self) -> int:
        if self._total_retweets is not None:
            return self._total_retweets
        for reaction in self.tweet_message.reactions:
            if reaction.emoji == config.EMOJI_RETWEET:
                return reaction.count - 1
        return 0

    @property
    def total_likes(self) -> int:
        if self._total_likes is not None:
            return self._total_likes
        for reaction in self.tweet_message.reactions:
            if reaction.emoji == config.EMOJI_LIKE:
                return reaction.count - 1
        return 0

    async def total_replies(self) -> int:
        if self._total_replies is not None:
            return self._total_replies
        total_replies = 0
        async for message in self.tweet_message.channel.history(after=self.tweet_message.created_at):
            if (
                message.embeds
                and message.embeds[0]
                and message.embeds[0].description
                and self.tweet_message.jump_url in message.embeds[0].description
            ):
                total_replies += 1
        self._total_replies = total_replies
        return total_replies

    async def download_avatar(self) -> None:
        if os.path.exists(self.avatar_path):
            return None
        await (
            self.original_message.author.display_avatar
            .with_size(128)
            .with_static_format("png")
            .save(self.avatar_path)
        )

    async def download_attachments(self) -> None:
        for i, attachment_path in enumerate(self.attachments_paths):
            if os.path.exists(attachment_path):
                continue
            await self.original_message.attachments[i].save(attachment_path)

    async def download_tweet(self) -> None:
        if os.path.exists(self.tweet_path):
            return None
        if not self.tweet_message.embeds:
            raise ValueError(f"Cannot download: {self.tweet_message} does not contain embeds.")
        await download_image(
            self.tweet_message.embeds[0].image.url,
            output_path=self.tweet_path,
        )

    async def send(self) -> disnake.Message:
        if self.original_message is None and self.tweet_message is not None:
            raise ValueError("Cannot send: 'original_message' must be provided.")
        tweet = disnake.File(self.tweet_path)
        embed = disnake.Embed()
        if self.original_message.reference:
            embed.description = f"Replying to {self.original_message.reference.jump_url}"
        embed.set_image(file=tweet)
        self.tweet_message = await self.original_message.channel.send(embed=embed)
        return self.tweet_message

    async def update(self) -> None:
        if self.tweet_message is None:
            raise ValueError("Cannot update: 'original_message' must be provided.")
        if not self.tweet_message.embeds:
            raise ValueError(f"Cannot update: {self.tweet_message} does not contain embeds.")
        total_replies = await self.total_replies()
        interactions = total_replies + self.total_retweets + self.total_likes
        if interactions <= 0:
            return None
        if not os.path.exists(self.statistics_path):
            await fake_tweet_generator(
                text=" ",
                name=" ",
                username=" ",
                output_path=self.statistics_path,
                replies=total_replies,
                retweets=self.total_retweets,
                likes=self.total_likes,
                views=interactions,
            )
            crop_image(self.statistics_path, top=-50)
        overlay_images(
            base_image_path=self.tweet_path,
            overlay_image_path=self.statistics_path,
            output_path=self.tweet_path,
        )
        tweet = disnake.File(self.tweet_path)
        embed = self.tweet_message.embeds[0]
        embed.set_image(file=tweet)
        await self.tweet_message.edit(embed=embed)

    async def update_reference(self) -> None:
        if self.original_message.reference is None:
            return None
        message = await self.tweet_message.channel.fetch_message(self.original_message.reference.message_id)
        async with Tweet(tweet_message=message) as tweet:
            await tweet.update()
