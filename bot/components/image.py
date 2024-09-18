from io import BytesIO

import aiohttp
from PIL import Image, ImageChops, ImageOps

__all__ = (
    "download_image",
    "crop_image",
    "trim_image",
    "overlay_images",
)


async def download_image(url: str, /, *, output_path: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            image_data = await response.read()
    image = Image.open(BytesIO(image_data))
    image.save(output_path)


def crop_image(
    input_path: str,
    /,
    *,
    output_path: str | None = None,
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
) -> None:
    if output_path is None:
        output_path = input_path
    image = Image.open(input_path)
    left = 0 if left is None else left if left >= 0 else image.width + left
    top = 0 if top is None else top if top >= 0 else image.height + top
    right = image.width if right is None else right if right >= 0 else image.width + right
    bottom = image.height if bottom is None else bottom if bottom >= 0 else image.height + bottom
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(output_path)


def trim_image(
    input_path: str,
    /,
    *,
    output_path: str | None = None,
    border_size: int = 25,
    trim_color: tuple[int, int, int] = (255, 255, 255),
) -> None:
    if output_path is None:
        output_path = input_path
    image = Image.open(input_path)
    if image.mode != "RGB":
        image = image.convert("RGB")
    bg = Image.new(image.mode, image.size, trim_color)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        trimmed_image = image.crop(bbox)
        bordered_image = ImageOps.expand(trimmed_image, border=border_size, fill=trim_color)
        bordered_image.save(output_path)


def overlay_images(
    *,
    base_image_path: str,
    overlay_image_path: str,
    output_path: str,
) -> None:
    base_image = Image.open(base_image_path)
    overlay_image = Image.open(overlay_image_path)
    x_offset = (base_image.width - overlay_image.width) // 2
    y_offset = (base_image.height - overlay_image.height)
    base_image.paste(overlay_image, (x_offset, y_offset))
    base_image.save(output_path)
