import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiohttp import web 

BOT_TOKEN = "8967874048:AAHIPcxEe736SozG0RFktU1iNce3tgy_rW8"
RENDER_URL = "https://my-telegram-bot-1-7jlg.onrender.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def upload_to_storage(file_bytes: bytes, filename: str = 'image.jpg') -> str:
    url = "https://teleg.ph/upload"
    form = aiohttp.FormData()
    form.add_field('file', file_bytes, filename=filename, content_type='image/jpeg' if not filename.endswith('.gif') else 'image/gif')
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=form) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0 and 'src' in result[0]:
                        image_path = result[0]['src']
                        return f"https://teleg.ph{image_path}"
                return None
        except Exception as e:
            logger.exception(f"Telegraph'ga yuklashda xato: {e}")
            return None

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga rasm yoki GIF yuboring (5 MB gacha). Men uni Telegraph silkasiga aylantirib beraman🤗.")

@dp.message(F.photo | F.animation)
async def handle_media(message: types.Message):
    wait_msg = await message.answer("Yuklanmoqda...")
    try:
        if message.photo:
            file_id = message.photo[-1].file_id
            filename = 'image.jpg'
        elif message.animation:
            file_id = message.animation.file_id
            filename = 'animation.gif'
        else:
            await wait_msg.edit_text("❌ Faqat rasm yoki GIF yuboring.")
            return

        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        
        direct_url = await upload_to_storage(file_bytes.read(), filename)
        if direct_url:
            await wait_msg.edit_text(f"✅ Havola: `{direct_url}`", parse_mode="Markdown")
        else:
            await wait_msg.edit_text("❌ Xatolik yuz berdi. Fayl hajmi 5 MB dan katta bo'lishi mumkin.")
    except Exception as e:
        logger.exception(f"Media qabul qilishda xato: {e}")
        await wait_msg.edit_text("❌ Xatolik.")

async def handle_web(request):
    return web.Response(text="Bot is running!")

async def self_ping():
    await asyncio.sleep(15)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as response:
                    logger.info(f"Self-ping yuborildi, status: {response.status}")
            except Exception as e:
                logger.error(f"Self-ping xatosi: {e}")
            await asyncio.sleep(600)

async def main():
    app = web.Application()
    app.router.add_get("/", handle_web)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    await asyncio.gather(
        site.start(),
        self_ping(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
        
