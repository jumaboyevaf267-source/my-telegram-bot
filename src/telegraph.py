import aiohttp


async def upload_to_telegraph(file_bytes: bytes, filename: str):

    url = "https://telegra.ph/upload"

    if filename.endswith(".gif"):
        content_type = "image/gif"
    elif filename.endswith(".png"):
        content_type = "image/png"
    else:
        content_type = "image/jpeg"

    form = aiohttp.FormData()

    form.add_field(
        "file",
        file_bytes,
        filename=filename,
        content_type=content_type
    )

    async with aiohttp.ClientSession() as session:

        async with session.post(url, data=form) as response:

            if response.status != 200:
                return None

            data = await response.json()

            if isinstance(data, list):
                return "https://telegra.ph" + data[0]["src"]

            return None
