import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart

# Bot tokeningizni shu yerga aniq kiritib keting
BOT_TOKEN = "8967874048:AAEbexXemCOrLnQm66_GxQGN4GWW2SeZW_I"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def upload_to_storage(file_bytes: bytes) -> str:
    url = "https://catbox.moe/user/api.php"
    form = aiohttp.FormData()
    form.add_field('reqtype', 'fileupload')
    form.add_field('fileToUpload', file_bytes, filename='file.jpg')
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
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
    await message.answer(
        "👋 **Salom! Men rasmlar va GIF-larni doimiy havolaya aylantirib beruvchi botman.**\n\n"
        "Menga rasm yoki GIF yuboring, men sizga uning linkini taqdim etaman."
    )

@dp.message(F.photo | F.animation | F.document.mime_type.startswith("image/"))
async def handle_media(message: types.Message):
    wait_msg = await message.answer("🔄 Fayl xavfsiz serverga yuklanmoqda...")
    
    try:
        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.animation:
            file_id = message.animation.file_id
        else:
            file_id = message.document.file_id

        file = await bot.get_file(file_id)
        file_bytes = await bot.download_file(file.file_path)
        direct_url = await upload_to_storage(file_bytes.read())
        
        if direct_url:
            await wait_msg.edit_text(
                f"✅ **Muvaffaqiyatli yuklandi!**\n\n"
                f"🔗 **Havola:** `{direct_url}`",
                parse_mode="Markdown"
            )
        else:
            await wait_msg.edit_text("❌ Serverga yuklashda xatolik yuz berdi. Qayta urinib ko'ring.")
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await wait_msg.edit_text("❌ Faylni qayta ishlashda xatolik yuz berdi.")

if __name__ == "__main__":
    import asyncio
    async def main():
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    asyncio.run(main())
    
