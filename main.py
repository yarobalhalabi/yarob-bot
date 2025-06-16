from keep_alive import keep_alive
keep_alive()

import telebot
from telebot import types
import json
import os

BOT_TOKEN = '8083535737:AAGqZ44PUyl5egPU-OVyl4_AngOZHwN7ZaA'
ADMIN_ID = 7188219652

STATE_FILE = "bot_state.json"

def load_bot_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("active", False)
    return False

def save_bot_state(active):
    with open(STATE_FILE, "w") as f:
        json.dump({"active": active}, f)

BOT_ACTIVE = load_bot_state()
bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

prices_pubg = {
    "60": "10,000 S.P",
    "120": "20,000 S.P",
    "325": "50,000 S.P",
    "660": "97,000 S.P",
    "1800": "250,000 S.P",
    "3850": "500,000 S.P"
}

prices_freefire = {
    "110": "11,000 S.P",
    "220": "22,000 S.P",
    "572": "55,000 S.P",
    "1266": "110,000 S.P"
}

@bot.message_handler(commands=['on'])
def activate_bot(message):
    if message.from_user.id == ADMIN_ID:
        save_bot_state(True)
        bot.send_message(message.chat.id, "✅ تم تفعيل البوت.")
    else:
        bot.send_message(message.chat.id, "🚫 هذا الأمر مخصص للإدارة فقط.")

@bot.message_handler(commands=['off'])
def deactivate_bot(message):
    if message.from_user.id == ADMIN_ID:
        save_bot_state(False)
        bot.send_message(message.chat.id, "⛔ تم إيقاف البوت.")
    else:
        bot.send_message(message.chat.id, "🚫 هذا الأمر مخصص للإدارة فقط.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "🚫 البوت متوقف حالياً، شكراً لتفهمكم ❤️")
        return

    user_data[user_id] = {}
    welcome_text = "👋 أهلاً بك في متجر YAROB لشحن الألعاب 💳\n🔽 اختر اللعبة التي ترغب بشحنها:"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📱 PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("🎮 Free Fire", callback_data="freefire")
    )
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    user_id = call.from_user.id
    user_data[user_id]['game'] = call.data

    if call.data == "pubg":
        prices = prices_pubg
        game_name = "PUBG"
        price_label = "شدة"
    else:
        prices = prices_freefire
        game_name = "Free Fire"
        price_label = "جوهره"

    welcome_text = f"🔽 اختر كمية {price_label} التي ترغب بشرائها ل {game_name}:"
    markup = types.InlineKeyboardMarkup()
    for amount, price in prices.items():
        markup.add(
            types.InlineKeyboardButton(f"{amount} {price_label} - {price}", callback_data=amount)
        )
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in prices_pubg or call.data in prices_freefire)
def handle_selection(call):
    user_id = call.from_user.id
    game = user_data[user_id]['game']
    amount = call.data

    if game == "pubg":
        prices = prices_pubg
        price_label = "شدة"
    else:
        prices = prices_freefire
        price_label = "جوهره"

    user_data[user_id] = {'amount': amount, 'game': game}

    payment_text = (
        f"💰 السعر: {prices[amount]}\n\n"
        f"📱 يرجى التحويل عبر سيرياتيل كاش (تحويل يدوي) إلى أحد الأرقام التالية:\n"
        f"• 0999999999\n"
        f"• 0988888888\n\n"
        f"بعد التحويل، أرسل رقم العملية:"
    )
    bot.send_message(user_id, payment_text)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

def get_transaction_number(message):
    user_id = message.from_user.id
    user_data[user_id]['transaction_number'] = message.text
    bot.send_message(user_id, "💸 أرسل الآن المبلغ الذي قمت بتحويله:")
    bot.register_next_step_handler_by_chat_id(user_id, get_amount)

def get_amount(message):
    user_id = message.from_user.id
    user_data[user_id]['transferred_amount'] = message.text
    bot.send_message(user_id, "🎮 أرسل الآن ID حسابك داخل اللعبة:")
    bot.register_next_step_handler_by_chat_id(user_id, get_game_id)

def get_game_id(message):
    user_id = message.from_user.id
    data = user_data[user_id]
    data['game_id'] = message.text

    final_message = (
        f"🆕 طلب شحن جديد:\n"
        f"👤 المستخدم: @{message.from_user.username or 'بدون يوزر'}\n"
        f"🆔 تيليجرام: {user_id}\n"
        f"🎮 ID اللعبة: {data['game_id']}\n"
        f"🎯 الكمية: {data['amount']} {data['game']}\n"
        f"💵 المبلغ: {data['transferred_amount']}\n"
        f"🔢 رقم العملية: {data['transaction_number']}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تمت العملية", callback_data=f"confirm_{user_id}"),
        types.InlineKeyboardButton("❌ فشلت العملية", callback_data=f"fail_{user_id}")
    )

    bot.send_message(ADMIN_ID, final_message, reply_markup=markup)
    bot.send_message(user_id, "✅ تم استلام معلوماتك بنجاح! سيتم تنفيذ طلبك قريبًا 💚")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_delivery(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ هذا الزر مخصص للإدارة فقط.")
        return

    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "✅ تم تنفيذ عملية الشحن بنجاح! شكراً لتعاملك معنا 🌟")
    bot.answer_callback_query(call.id, "تم إعلام العميل.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail_"))
def fail_delivery(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ هذا الزر مخصص للإدارة فقط.")
        return

    user_id = int(call.data.split("_")[1])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 إعادة المحاولة", callback_data='retry'))
    fail_text = "❌ فشلت العملية\nيرجى التأكد من صحة المعلومات وإعادة المحاولة."
    bot.send_message(user_id, fail_text, reply_markup=markup)
    bot.answer_callback_query(call.id, "تم إعلام العميل بفشل العملية.")

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    send_welcome(call.message)

bot.infinity_polling()
