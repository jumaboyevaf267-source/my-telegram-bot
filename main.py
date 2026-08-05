import asyncio
import logging
import os

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher()


# ===================== Telegraph =====================

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


# ===================== Handlers =====================

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "👋 Salom!\n\n"
        "Menga rasm yoki GIF yuboring.\n"
        "Men uni Telegraph havolasiga aylantirib beraman."
    )


@dp.message(F.photo | F.animation)
async def media(message: Message):

    wait = await message.answer("⏳ Yuklanmoqda...")

    try:

        if message.photo:
            file_id = message.photo[-1].file_id
            filename = "image.jpg"

        else:
            file_id = message.animation.file_id
            filename = "animation.gif"

        telegram_file = await bot.get_file(file_id)

        file = await bot.download_file(telegram_file.file_path)

        url = await upload_to_telegraph(
            file.read(),
            filename
        )

        if url:
            await wait.edit_text(f"✅ Havola:\n`{url}`")
        else:
            await wait.edit_text("❌ Yuklashda xatolik.")

    except Exception as e:

        logging.exception(e)

        await wait.edit_text("❌ Xatolik yuz berdi.")


# ===================== Health Check =====================

async def health(request):
    return web.Response(text="Bot is running!")


async def start_web():

    app = web.Application()

    app.router.add_get("/", health)

    runner = web.AppRunner(app)

    await runner.setup()

    port = int(os.getenv("PORT", 10000))

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    logging.info(f"Web server started: {port}")


# ===================== Main =====================

async def main():

    await start_web()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
