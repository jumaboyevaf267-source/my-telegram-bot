import logging

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from .telegraph import upload_to_telegraph


def register_handlers(dp: Dispatcher, bot):

    @dp.message(CommandStart())
    async def start(message: Message):

        await message.answer(
            "👋 Salom!\n\n"
            "Menga rasm yoki GIF yuboring."
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

            file = await bot.download_file(
                telegram_file.file_path
            )

            url = await upload_to_telegraph(
                file.read(),
                filename
            )

            if url:
                await wait.edit_text(
                    f"✅ Havola:\n`{url}`",
                    parse_mode="Markdown"
                )
            else:
                await wait.edit_text(
                    "❌ Yuklashda xatolik."
                )

        except Exception as e:

            logging.exception(e)

            await wait.edit_text(
                "❌ Xatolik yuz berdi."
            )
