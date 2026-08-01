import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web 

BOT_TOKEN = "8967874048:AAHIPcxEe736SozG0RFktU1iNce3tgy_rW8"
RENDER_URL = "https://my-telegram-bot-1-id6z.onrender.com"

# Webhook sozlamalari
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def upload_to_storage(file_bytes: bytes, filename: str = 'image.jpg') -> str:
    url = "https://teleg.ph/upload"
    
    if filename.endswith('.gif'):
        content_type = 'image/gif'
    elif filename.endswith('.png'):
        content_type = 'image/png'
    else:
        content_type = 'image/jpeg'

    form = aiohttp.FormData()
    form.add_field('file', file_bytes, filename=filename, content_type=content_type)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, data=form) as response:
                if response.status == 200:
                    result = await response.json()
                    if isinstance(result, list) and len(result) > 0 and 'src' in result[0]:
                        return f"https://teleg.ph{result[0]['src']}"
                logger.error(f"Telegraph xatosi status kodi: {response.status}")
                return None
        except Exception as e:
            logger.exception(f"Yuklashda xatolik yuz berdi: {e}")
            return None

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga rasm yoki GIF yuboring. Men uni darhol Telegraph silkasiga aylantirib beraman🤗.")

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
            await wait_msg.edit_text("❌ Faqat rasm yoki GIF formatidagi fayl yuboring.")
            return

        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        
        direct_url = await upload_to_storage(file_bytes.read(), filename)
        if direct_url:
            await wait_msg.edit_text(f"✅ Havola: `{direct_url}`", parse_mode="Markdown")
        else:
            await wait_msg.edit_text("❌ Faylni yuklashda xatolik. Hajmi 5 MB dan katta bo'lishi mumkin.")
    except Exception as e:
        logger.exception(f"Media qabul qilishda xato: {e}")
        await wait_msg.edit_text("❌ Xatolik yuz berdi.")

async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook o'rnatildi: {WEBHOOK_URL}")

def main():
    app = web.Application()
    
    # Webhook handler'ni aiohttp ilovasiga ulaymiz
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
        
