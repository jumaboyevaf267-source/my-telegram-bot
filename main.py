import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiohttp import web 

BOT_TOKEN = "8967874048:AAHIPcxEe736SozG0RFktU1iNce3tgy_rW8"  # Tokeningizni shu yerga yozing
RENDER_URL = "https://my-telegram-bot-1-7jlg.onrender.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.exception(f"Kutilmagan xatolik yuz berdi: {e}")
            return None

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga rasm yuboring. Men uni silkaga aylantirib beraman🤗.")

@dp.message(F.photo | F.animation)
async def handle_media(message: types.Message):
    wait_msg = await message.answer("Yuklanmoqda...")
    try:
        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.animation:
            file_id = message.animation.file_id
        else:
            await wait_msg.edit_text("❌ Faqat rasm yoki animatsiya yuboring.")
            return

        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        
        direct_url = await upload_to_storage(file_bytes.read())
        if direct_url:
            await wait_msg.edit_text(f"✅ Marhamat havola: `{direct_url}`", parse_mode="Markdown")
        else:
            await wait_msg.edit_text("❌ Xatolik yuz berdi.")
    except Exception as e:
        logger.exception(f"Media qabul qilishda xato: {e}")
        await wait_msg.edit_text("❌ Xatolik.")

async def handle_web(request):
    return web.Response(text="Bot is running!")

# Har 10 daqiqada o'ziga so'rov yuborib turuvchi funksiya
async def self_ping():
    await asyncio.sleep(15)  # Server to'liq ishga tushishi uchun biroz kutaiz
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as response:
                    logger.info(f"Self-ping yuborildi,status: {response.status}")
            except Exception as e:
                logger.error(f"Self-ping xatosi: {e}")
            await asyncio.sleep(600)  # 600 soniya = 10 daqiqa

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
        self_ping(),  # O'zini o'zi ping qilishni ishga tushiramiz
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
        
