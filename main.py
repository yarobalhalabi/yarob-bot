
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

def clear_user_data(user_id):
    user_data.pop(user_id, None)

@bot.message_handler(commands=['on'])
def activate_bot(message):
    global BOT_ACTIVE
    if message.from_user.id == ADMIN_ID:
        BOT_ACTIVE = True
        bot.send_message(message.chat.id, "✅ تم تفعيل البوت.")
    else:
        bot.send_message(message.chat.id, "🚫 هذا الأمر مخصص للإدارة فقط.")

@bot.message_handler(commands=['off'])
def deactivate_bot(message):
    global BOT_ACTIVE
    if message.from_user.id == ADMIN_ID:
        BOT_ACTIVE = False
        bot.send_message(message.chat.id, "⛔ تم إيقاف البوت.")
    else:
        bot.send_message(message.chat.id, "🚫 هذا الأمر مخصص للإدارة فقط.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "🚫 البوت متوقف حالياً، شكراً لتفهمكم ❤️")
        return

    clear_user_data(user_id)
    user_data[user_id] = {"step": "start"}
    welcome_text = "👋 أهلاً بك في متجر YAROB لشحن الألعاب 💳
🔽 اختر اللعبة التي ترغب بشحنها:"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📱 PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("🎮 Free Fire", callback_data="freefire")
    )
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    user_id = call.from_user.id
    user_data[user_id] = {'game': call.data, "step": "choose_game"}

    if call.data == "pubg":
        prices = prices_pubg
        game_name = "Pubg"
        price_label = "UC"
    else:
        prices = prices_freefire
        game_name = "Free"
        price_label = "💎"

    welcome_text = f"🎁 عروض {game_name} المتوفّرة:
اختر باقتك:"
    markup = types.InlineKeyboardMarkup()
    for amount, price in prices.items():
        markup.add(types.InlineKeyboardButton(f"{game_name} {amount}{price_label} - {price} ل.س", callback_data=amount))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="go_back"))

    bot.edit_message_text(welcome_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in prices_pubg or call.data in prices_freefire)
def handle_selection(call):
    user_id = call.from_user.id
    game = user_data[user_id]['game']
    amount = call.data
    prices = prices_pubg if game == "pubg" else prices_freefire
    user_data[user_id].update({'amount': amount, "step": "choose_amount"})

    payment_text = (
        f"💰 السعر: {prices[amount]} ل.س

"
        f"📱 يرجى التحويل عبر سيرياتيل كاش (تحويل يدوي) إلى أحد الأرقام التالية:
"
        f"• `16954304`
"
        f"• `81827789`

"
        f"بعد التحويل، أرسل رقم العملية:"
    )
    bot.edit_message_text(payment_text, chat_id=user_id, message_id=call.message.message_id)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

def get_transaction_number(message):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ الرجاء إدخال رقم العملية بشكل رقمي فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)
    user_data[user_id]['transaction_number'] = message.text
    user_data[user_id]["step"] = "transaction_number"
    bot.send_message(user_id, "📞 الرجاء إدخال الرقم الذي قمت بالتحويل عليه (`16954304` أو `81827789`):")
    bot.register_next_step_handler_by_chat_id(user_id, get_target_number)

def get_target_number(message):
    user_id = message.from_user.id
    if message.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "⚠️ الرقم غير صحيح، الرجاء إدخال أحد الرقمين فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_target_number)
    user_data[user_id]['target_number'] = message.text
    user_data[user_id]["step"] = "target_number"
    bot.send_message(user_id, "🎮 أرسل الآن ID حسابك داخل اللعبة:")
    bot.register_next_step_handler_by_chat_id(user_id, get_game_id)

def get_game_id(message):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ الرجاء إدخال ID اللعبة بشكل رقمي فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_game_id)

    data = user_data[user_id]
    data['game_id'] = message.text
    data["step"] = "game_id"

    final_message = (
        f"🆕 طلب شحن جديد:
"
        f"👤 المستخدم: @{message.from_user.username or 'بدون يوزر'}
"
        f"🆔 تيليجرام: {user_id}
"
        f"🎮 ID اللعبة: {data['game_id']}
"
        f"🎯 الكمية: {data['amount']} {data['game']}
"
        f"📞 الرقم المحوّل عليه: {data['target_number']}
"
        f"🔢 رقم العملية: {data['transaction_number']}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تمت العملية", callback_data=f"confirm_{user_id}_{data['transaction_number']}"),
        types.InlineKeyboardButton("❌ فشلت العملية", callback_data=f"fail_{user_id}")
    )

    bot.send_message(ADMIN_ID, final_message, reply_markup=markup)
    bot.send_message(user_id, "✅ تم استلام معلوماتك بنجاح! سيتم تنفيذ طلبك قريبًا 💚")

@bot.callback_query_handler(func=lambda call: call.data == "go_back")
def go_back(call):
    user_id = call.from_user.id
    step = user_data.get(user_id, {}).get("step", "start")

    if step == "choose_amount":
        user_data[user_id]["step"] = "choose_game"
        prices = prices_pubg if user_data[user_id]["game"] == "pubg" else prices_freefire
        game_name = "Pubg" if user_data[user_id]["game"] == "pubg" else "Free"
        price_label = "UC" if user_data[user_id]["game"] == "pubg" else "💎"

        welcome_text = f"🎁 عروض {game_name} المتوفّرة:
اختر باقتك:"
        markup = types.InlineKeyboardMarkup()
        for amount, price in prices.items():
            markup.add(types.InlineKeyboardButton(f"{game_name} {amount}{price_label} - {price} ل.س", callback_data=amount))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="go_back"))

        bot.edit_message_text(welcome_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    else:
        clear_user_data(user_id)
        send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_delivery(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ هذا الزر مخصص للإدارة فقط.")
        return
    parts = call.data.split("_")
    user_id = int(parts[1])
    transaction_number = parts[2]

    game = user_data.get(user_id, {}).get("game", "unknown")
    amount = user_data.get(user_id, {}).get("amount", "?")
    game_id = user_data.get(user_id, {}).get("game_id", "غير معروف")
    unit = "UC" if game == "pubg" else "💎"
    confirm_msg = f"تم شحن حسابك بـ {amount} {unit} على الـ ID التالي: 📱{game_id} بنجاح ✅شكرا لتعاملك معنا🌟"
    bot.send_message(user_id, confirm_msg)

    bot.send_message(ADMIN_ID, f"📦 تم الشحن إلى رقم العملية: {transaction_number}")
    bot.answer_callback_query(call.id, "تم إعلام العميل.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail_"))
def fail_delivery(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ هذا الزر مخصص للإدارة فقط.")
        return

    user_id = int(call.data.split("_")[1])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("▶️ لإعادة المحاولة اضغط start", callback_data='retry'))
    fail_text = "❌ فشلت العملية
يرجى التأكد من صحة المعلومات، ثم اضغط /start لإعادة المحاولة."
    bot.send_message(user_id, fail_text, reply_markup=markup)
    bot.answer_callback_query(call.id, "تم إعلام العميل بفشل العملية.")

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    clear_user_data(call.from_user.id)
    send_welcome(call.message)

bot.infinity_polling()
