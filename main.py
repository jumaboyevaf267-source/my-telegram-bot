import telebot
import os
import threading
import requests
import uuid
import datetime
from flask import Flask

# Token va API kalitlari
TOKEN = "8980326952:AAH4uZO46pidoOdaMjeOL5Zw2cEMUVqkCrg"
IMGBB_API_KEY = "43078f794ef49efa6a8e7ea57a00a0b5"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Render uchun oddiy veb-server
@app.route('/')
def home():
    return "Bot 24/7 ishlamoqda!"

# Start buyrug'i (Kanal tekshiruvisiz)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga biror rasm yuboring, men uni linkka aylantirib beraman.")

# Rasm qabul qilish va yuklash
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status_msg = bot.reply_to(message, "Rasm yuklanmoqda...")
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY}
        files = {"image": downloaded_file}

        response = requests.post(url, data=payload, files=files)
        res_data = response.json()

        if res_data.get("success"):
            img_url = res_data["data"]["url"]
            img_id = str(uuid.uuid4())[:8]
            img_name = f"image_{img_id}.jpg"
            formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            caption_text = (
                f"✅ Rasm yuklandi!\n\n"
                f"🔗 Link: {img_url}\n"
                f"📅 Sana: {formatted_time}"
            )
            bot.edit_message_text(caption_text, chat_id=message.chat.id, message_id=status_msg.message_id)
        else:
            bot.edit_message_text("Xatolik: Rasm yuklanmadi.", chat_id=message.chat.id, message_id=status_msg.message_id)
    except Exception as e:
        bot.edit_message_text("Xatolik yuz berdi.", chat_id=message.chat.id, message_id=status_msg.message_id)

def run_bot():
    # Eski webhooklarni tozalash va pollingni boshlash
    bot.remove_webhook()
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    
