import telebot
import os

# TOKEN'ni Environment Variable'dan o'qib oladi (Render sozlamalarida kiritganingizdek)
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

# /start buyrug'i uchun javob
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Assalomu alaykum! Bot ishga tushdi. Sizga qanday yordam bera olaman?")

# Har qanday boshqa matnli xabarga javob
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Siz yozgan xabar: " + message.text)

# Botni uzluksiz ishlash rejimi
print("Bot ishga tushdi...")
bot.polling(none_stop=True)
