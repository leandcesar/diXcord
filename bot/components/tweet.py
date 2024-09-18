from datetime import datetime, timedelta

from playwright.async_api import async_playwright

from bot.components.image import trim_image

__all__ = ("fake_tweet_generator", )


async def fake_tweet_generator(
    text: str,
    *,
    name: str,
    username: str,
    avatar_path: str | None = None,
    attachments_path: list[str] | None = None,
    replies: int = 0,
    retweets: int = 0,
    likes: int = 0,
    views: int = 0,
    timestamp: datetime = datetime.utcnow(),
    source: str = "Twitter for Discord",
    theme: str = "Default",
    output_path: str = "tweet.png",
    timeout_ms: float = 60000.0,
) -> None:
    timestamp = timestamp - timedelta(hours=3)  # TODO: don't set the timezone hardcoded
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(timeout=timeout_ms, headless=True)
        page = await browser.new_page()
        await page.goto("https://codebeautify.org/fake-tweet-generator#")
        await page.fill("#inputName", name)
        await page.fill("#inputUsername", username)
        await page.fill("#inputText", text[:280] or " ")
        await page.fill("#inputReplies", str(replies))
        await page.fill("#inputRetweets", str(retweets))
        await page.fill("#inputLikes", str(likes))
        await page.fill("#inputViews", str(views))
        await page.fill("#inputTime", timestamp.time().isoformat(timespec="minutes"))
        await page.fill("#inputDate", timestamp.date().isoformat())
        await page.fill("#inputSource", source)
        await page.get_by_title(theme, exact=True).click()
        await page.click("#verifiedButtonNone")
        if avatar_path:
            await page.set_input_files("#profile-picture", files=avatar_path, timeout=timeout_ms)
        if attachments_path:
            await page.set_input_files("#tweet-images", files=attachments_path, timeout=timeout_ms)
        async with page.expect_download(timeout=timeout_ms) as data:
            await page.get_by_title("Download Beautified Tweet Image").click()
        download = await data.value
        await download.save_as(output_path)
        await browser.close()
    trim_image(output_path)
