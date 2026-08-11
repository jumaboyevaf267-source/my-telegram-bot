import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.exceptions import TelegramRetryAfter
from aiohttp import web 

BOT_TOKEN = "8967874048:AAHyvBGewqXjANLm6gTtlXLI32XSjmHQ2uI"
RENDER_URL = "https://my-telegram-bot-1-oeq1.onrender.com"

WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- RASM YUKLASH FUNKSIYASI ---
async def upload_to_storage(file_bytes: bytes, filename: str = 'image.jpg') -> str:
    url = "https://catbox.moe/user/api.php"
    form = aiohttp.FormData()
    form.add_field('reqtype', 'fileupload')
    form.add_field('fileToUpload', file_bytes, filename=filename)
    
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            async with session.post(url, data=form) as response:
                if response.status == 200:
                    text_res = await response.text()
                    if text_res.startswith("http"):
                        return text_res.strip()
                return None
        except Exception as e:
            logger.exception(f"Catbox yuklashda xato: {e}")
            return None

# --- BOT HANDLERLARI ---

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga rasm yoki GIF yuboring. Men uni darhol silkaga aylantirib beraman🤗.")

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
            await wait_msg.edit_text("❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
    except Exception as e:
        logger.exception(f"Media qabul qilishda xato: {e}")
        await wait_msg.edit_text("❌ Xatolik yuz berdi.")

async def handle_web(request):
    return web.Response(text="Bot is running!")

async def self_ping():
    await asyncio.sleep(20)
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(RENDER_URL) as response:
                    logger.info(f"Self-ping status: {response.status}")
            except Exception as e:
                logger.error(f"Self-ping xatosi: {e}")
            await asyncio.sleep(600)

async def on_startup(bot: Bot):
    while True:
        try:
            await bot.set_webhook(WEBHOOK_URL)
            logger.info(f"Webhook o'rnatildi: {WEBHOOK_URL}")
            break
        except TelegramRetryAfter as e:
            logger.warning(f"Telegram Limit keldi: {e.retry_after} soniya kutilmoqda...")
            await asyncio.sleep(e.retry_after + 1)
        except Exception as e:
            logger.error(f"Webhook o'rnatishda kutilmagan xato: {e}")
            break

    asyncio.create_task(self_ping())

def main():
    app = web.Application()
    app.router.add_get("/", handle_web)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    dp.startup.register(on_startup)
    
    port = int(os.environ.get("PORT", 10000))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
