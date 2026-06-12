import telebot
import requests
import datetime
import uuid
import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot 24/7 rejimda muvaffaqiyatli ishlamoqda!"

TOKEN = "8980326952:AAGlXNx2dcCV_KRW2AtYsJYyptbXz8ShbGQ"
IMGBB_API_KEY = "43078f794ef49efa6a8e7ea57a00a0b5"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga biror rasm yuboring, men uni havola (link) qilib beraman. 📸✨")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    status_msg = None
    try:
        status_msg = bot.reply_to(message, "Rasm yuklanmoqda, iltimos kuting...")
        
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": IMGBB_API_KEY}
        files = {"image": downloaded_file}
        
        response = requests.post(url, data=payload, files=files, timeout=15)
        res_data = response.json()
        
        if res_data.get("success"):
            img_url = res_data["data"]["url"]
            img_id = str(uuid.uuid4())[:8]
            img_name = f"image_{img_id}.jpg"
            now = datetime.datetime.now()
            formatted_time = now.strftime("%Y-%m-%dT%H:%M:%S")
            
            caption_text = (
                f"🆔 ID: {res_data['data']['id']}\n"
                f"📝 Имя: {img_name}\n"
                f"🔗 Ссылка: {img_url}\n"
                f"⏰ Дата: {formatted_time}"
            )
            try:
                bot.delete_message(message.chat.id, status_msg.message_id)
            except:
                pass
            bot.reply_to(message, caption_text)
        else:
            if status_msg:
                bot.edit_message_text("Xatolik: ImgBB serveri rasmni rad etdi.", message.chat.id, status_msg.message_id)
    except Exception as e:
        if status_msg:
            bot.edit_message_text("Xatolik yuz berdi. Qayta urinib ko'ring.", message.chat.id, status_msg.message_id)

if __name__ == "__main__":
    bot.skip_pending = True
    bot.remove_webhook()
    
    bot_thread = threading.Thread(target=bot.infinity_polling, kwargs={"skip_pending": True}, daemon=True)
    bot_thread.start()
    
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
      
