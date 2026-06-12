import telebot

# Tokeningizni shu yerga qo'ying
TOKEN = '8980326952:AAFo1jeKNcld1JMeyGZ9k3LYLUJpXTSRVyA'
bot = telebot.TeleBot(TOKEN)

# Kanal username'i
CHANNEL_ID = "@nj26k"

def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id)
        if status.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.chat.id):
        bot.reply_to(message, "✅ Xush kelibsiz! Botdan foydalanishingiz mumkin.")
    else:
        bot.reply_to(message, f"❌ Botdan foydalanish uchun oldin kanalimizga a'zo bo'ling: {CHANNEL_ID}")

@bot.message_handler(func=lambda message: True)
def all_messages(message):
    if not check_sub(message.chat.id):
        bot.reply_to(message, f"⚠️ Bot ishlashi uchun avval kanalimizga a'zo bo'ling: {CHANNEL_ID}")
    else:
        bot.reply_to(message, "Siz kanalimiz a'zosisiz! Buyruqlaringizni yuboring.")

print("Bot ishga tushdi...")
bot.polling(none_stop=True)
