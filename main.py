
from keep_alive import keep_alive
keep_alive()

import telebot
from telebot import types

BOT_TOKEN = '8083003172:AAFAkfpg9D6ZgqjtEsKCM5khqCYK2QHeTGM'
ADMIN_ID = 7188219652

BOT_ACTIVE = True
bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

prices_pubg = {
    "60": "9,500",
    "120": "19,000",
    "180": "28,500",
    "325": "47,000",
    "660": "92,000",
    "1800": "240,000",
    "3850": "480,000"
}

prices_freefire = {
    "110": "11,000",
    "341": "33,000",
    "570": "55,000",
    "1160": "110,000",
    "2200": "200,000"
}

def clear_user(user_id):
    if user_id in user_data:
        user_data.pop(user_id)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    clear_user(user_id)
    user_data[user_id] = {"step": "game"}
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📱 PUBG", callback_data="game_pubg"))
    markup.add(types.InlineKeyboardButton("🎮 Free Fire", callback_data="game_freefire"))
    bot.send_message(user_id, "👋 أهلاً بك في متجر YAROB لشحن الألعاب!
اختر اللعبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("game_"))
def game_selection(call):
    user_id = call.message.chat.id
    game = call.data.split("_")[1]
    user_data[user_id] = {"game": game, "step": "amount"}
    prices = prices_pubg if game == "pubg" else prices_freefire
    label = "UC" if game == "pubg" else "💎"
    markup = types.InlineKeyboardMarkup()
    for k, v in prices.items():
        markup.add(types.InlineKeyboardButton(f"{k} {label} - {v} ل.س", callback_data=f"amount_{k}"))
    markup.add(types.InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel"))
    bot.edit_message_text("🎁 اختر الباقة:", user_id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("amount_"))
def amount_selection(call):
    user_id = call.message.chat.id
    amount = call.data.split("_")[1]
    user_data[user_id]["amount"] = amount
    user_data[user_id]["step"] = "transaction"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_amount"))
    markup.add(types.InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel"))
    bot.edit_message_text("💰 أرسل رقم العملية (أرقام فقط):", user_id, call.message.message_id, reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction)

def get_transaction(msg):
    user_id = msg.chat.id
    if not msg.text.isdigit():
        bot.send_message(user_id, "❗ أرسل رقم العملية أرقام فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_transaction)
    user_data[user_id]["transaction"] = msg.text
    user_data[user_id]["step"] = "target"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_transaction"))
    markup.add(types.InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel"))
    bot.send_message(user_id, "📞 أدخل الرقم الذي حوّلت عليه (16954304 أو 81827789):", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(user_id, get_target)

def get_target(msg):
    user_id = msg.chat.id
    if msg.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "⚠️ الرقم غير صحيح، حاول مرة أخرى.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_target)
    user_data[user_id]["target"] = msg.text
    user_data[user_id]["step"] = "id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_target"))
    markup.add(types.InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel"))
    bot.send_message(user_id, "🎮 أرسل ID اللعبة:", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(user_id, get_gameid)

def get_gameid(msg):
    user_id = msg.chat.id
    if not msg.text.isdigit():
        bot.send_message(user_id, "❗ ID اللعبة يجب أن يكون رقماً.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_gameid)
    data = user_data[user_id]
    text = f"🆕 طلب شحن:
User: @{msg.from_user.username or 'لا يوجد'}
Game: {data['game']}
Amount: {data['amount']}
رقم العملية: {data['transaction']}
حوّل على: {data['target']}
ID اللعبة: {msg.text}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ تمت", callback_data=f"confirm_{user_id}"))
    markup.add(types.InlineKeyboardButton("❌ فشلت", callback_data=f"fail_{user_id}"))
    bot.send_message(ADMIN_ID, text, reply_markup=markup)
    bot.send_message(user_id, "✅ تم استلام الطلب، سيتم التنفيذ قريباً 💚")

@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel(call):
    user_id = call.message.chat.id
    clear_user(user_id)
    bot.send_message(user_id, "❌ تم إلغاء الطلب.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("back_"))
def go_back(call):
    user_id = call.message.chat.id
    step = call.data.split("_")[1]
    if step == "amount":
        game_selection(call)
    elif step == "transaction":
        amount_selection(call)
    elif step == "target":
        bot.send_message(user_id, "💰 أرسل رقم العملية من جديد:")
        bot.register_next_step_handler_by_chat_id(user_id, get_transaction)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "✅ تم تنفيذ الشحن بنجاح، شكرًا لك 🌟")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail_"))
def fail(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "❌ فشلت العملية. تحقق من البيانات وأعد المحاولة بإرسال /start")

bot.infinity_polling()
