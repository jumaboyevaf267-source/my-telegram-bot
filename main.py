# Botingiz tokenini bu yerga yozing
TOKEN = '8980326952:AAFo1jeKNcld1JMeyGZ9k3LYLUJpXTSRVyA'
bot = telebot.TeleBot(TOKEN)

# Kanal username'i (admin qilib qo'shgan kanal)
CHANNEL_ID = "@nj26k"

# Kanalga a'zolikni tekshirish funksiyasi
def check_sub(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id)
        if status.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

# Start buyrug'i va tekshiruv
@bot.message_handler(commands=['start'])
def start(message):
    if check_sub(message.chat.id):
        bot.reply_to(message, "✅ Xush kelibsiz! Botdan foydalanishingiz mumkin.")
    else:
        bot.reply_to(message, f"❌ Botdan foydalanish uchun oldin kanalimizga a'zo bo'ling:\n\n👉 {CHANNEL_ID}\n\nA'zo bo'lgach, yana /start tugmasini bosing.")

# Agar foydalanuvchi boshqa narsa yozsa ham tekshirish
@bot.message_handler(func=lambda message: True)
def all_messages(message):
    if not check_sub(message.chat.id):
        bot.reply_to(message, f"⚠️ Bot ishlashi uchun avval kanalimizga a'zo bo'ling: {CHANNEL_ID}")
    else:
        bot.reply_to(message, "Siz kanalimiz a'zosisiz! Buyruqlaringizni yuboring.")

# Botni ishga tushirish
print("Bot ishga tushdi...")
bot.polling(none_stop=True)
