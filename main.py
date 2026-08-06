import logging
import asyncio
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiohttp import web 

BOT_TOKEN = "8967874048:AAHTC9TcuYLOpjAOVmBdATwyf7vj5puofO4"
RENDER_URL = "https://my-telegram-bot-1-id6z.onrender.com"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Catbox orqali rasmni xatosiz yuklash funksiyasi
async def upload_to_storage(file_bytes: bytes, filename: str = 'image.jpg') -> str:
    url = "https://catbox.moe/user/api.php"
    form = aiohttp.FormData()
    form.add_field('reqtype', 'fileupload')
    form.add_field('fileToUpload', file_bytes, filename=filename)
    
    # SSL xatolarini oldini olish uchun verify_ssl=False
    conn = aiohttp.TCPConnector(verify_ssl=False)
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
    
    # Eski webhooklarni tozalash
    await bot.delete_webhook(drop_pending_updates=True)
    
    await site.start()
    asyncio.create_task(self_ping())
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot to'xtatildi.")
                            
