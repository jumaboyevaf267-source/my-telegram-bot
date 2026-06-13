import telebot
import os
import threading
from flask import Flask

TOKEN = "8980326952:AAG9PbC08liS9h67I_OMAtgTxFwOURVLYFk"
IMGBB_API_KEY = "43078f794ef49efa6a8e7ea57a00a0b5"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlamoqda!"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga rasm yuboring, men uni linkka aylantirib beraman.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # Bu yerda rasm yuklash kodingiz bo'lishi kerak
    bot.reply_to(message, "Rasm qabul qilindi...")

def run_bot():
    bot.infinity_polling(none_stop=True)

if __name__ == "__main__":
    # Botni alohida thread'da ishga tushiramiz
    threading.Thread(target=run_bot).start()
    # Flask serverini ishga tushiramiz
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
    
