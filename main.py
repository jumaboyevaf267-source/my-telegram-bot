import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
# web qismini o'zgartirdik:
from aiohttp import web 

BOT_TOKEN = "8967874048:AAGu5Fh45tVOYNkEbT4ZRdFvZAyXG1Z57nE"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def upload_to_storage(file_bytes: bytes) -> str:
    url = "https://catbox.moe/user/api.php"
    form = aiohttp.FormData()
    form.add_field('reqtype', 'fileupload')
    form.add_field('fileToUpload', file_bytes, filename='file.jpg')
    headers = {"User-Agent": "Mozilla/5.0"}
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.post(url, data=form) as response:
                if response.status == 200:
                    text_res = await response.text()
                    if text_res.startswith("http"):
                        return text_res.strip()
                return None
        except Exception as e:
            logging.error(f"Tarmoq xatoligi: {e}")
            return None

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga rasm yuboring.")

@dp.message(F.photo | F.animation | F.document.mime_type.startswith("image/"))
async def handle_media(message: types.Message):
    wait_msg = await message.answer("Yuklanmoqda...")
    try:
        file_id = message.photo[-1].file_id if message.photo else (message.animation.file_id if message.animation else message.document.file_id)
        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        direct_url = await upload_to_storage(file_bytes.read())
        if direct_url:
            await wait_msg.edit_text(f"✅ Havola: `{direct_url}`", parse_mode="Markdown")
        else:
            await wait_msg.edit_text("❌ Xatolik.")
    except Exception as e:
        await wait_msg.edit_text("❌ Xatolik.")

async def handle_web(request):
    return web.Response(text="Bot is running!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle_web)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    await asyncio.gather(
        site.start(),
        bot.delete_webhook(drop_pending_updates=True),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
