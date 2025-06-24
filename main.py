from keep_alive import keep_alive
keep_alive()

import telebot
from telebot import types
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7188219652

BOT_ACTIVE = True

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}
pending_requests = {}

# أسعار شدات ببجي
prices_pubg = {
    "60": "9,500",
    "120": "20,000",
    "180": "29,000",
    "325": "47,000",
    "385": "56,500",
    "660": "95,000",
    "985": "142,000",
    "1320": "190,000",
    "1800": "235,000",
    "3850": "460,000"
}

# أسعار شدات فري فاير
prices_freefire = {
    "110": "11,000",
    "210": "22,000",
    "341": "33,000",
    "570": "55,000",
    "1160": "110,000",
    "2200": "200,000"
}

# اشتراكات ببجي
subscriptions_pubg = {
    "برايم": "14,000",
    "برايم بلس": "140,000",
    "حزمة الشراء الأول": "14,000",
    "حزمة الشعار الخرافي": "62,000"
}

# اشتراكات فري فاير
subscriptions_freefire = {
    "عضوية أسبوعية": "26,000",
    "عضوية شهرية": "77,000",
    "تصريح المستوى": "25,000"
}

def clear_user_data(user_id):
    user_data.pop(user_id, None)

def back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    return markup

@bot.message_handler(commands=['on'])
def activate_bot(message):
    global BOT_ACTIVE
    if message.from_user.id == ADMIN_ID:
        BOT_ACTIVE = True
        bot.send_message(message.chat.id, "✅ تم تفعيل البوت.")

@bot.message_handler(commands=['off'])
def deactivate_bot(message):
    global BOT_ACTIVE
    if message.from_user.id == ADMIN_ID:
        BOT_ACTIVE = False
        bot.send_message(message.chat.id, "⛔ تم إيقاف البوت.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "🚫 البوت متوقف حالياً، نشكر تفهمكم ❤️")
        return

    clear_user_data(user_id)
    user_data[user_id] = {"step": "start"}
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📱 PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("🎮 Free Fire", callback_data="freefire")
    )
    bot.send_message(user_id, "👋 أهلاً بك في متجر YAROB لشحن الألعاب 💳\n🔽 اختر اللعبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back")
def go_back(call):
    user_id = call.from_user.id
    step = user_data.get(user_id, {}).get("step", "start")
    if step in ["choose_game", "pubg_menu", "freefire_menu", "pubg_shd", "pubg_sub", "freefire_shd", "freefire_sub", "transaction_number"]:
        send_welcome(call.message)
    else:
        send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    user_id = call.from_user.id
    game = call.data
    user_data[user_id] = {"game": game, "step": f"{game}_menu"}
    markup = types.InlineKeyboardMarkup()
    if game == "pubg":
        markup.add(types.InlineKeyboardButton("🪙 شدات", callback_data="pubg_shd"))
        markup.add(types.InlineKeyboardButton("🎫 اشتراكات", callback_data="pubg_sub"))
    else:
        markup.add(types.InlineKeyboardButton("💎 جواهر", callback_data="freefire_shd"))
        markup.add(types.InlineKeyboardButton("🎫 اشتراكات", callback_data="freefire_sub"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.edit_message_text("🎮 اختر القسم:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg_shd", "pubg_sub", "freefire_shd", "freefire_sub"])
def choose_section(call):
    user_id = call.from_user.id
    game = user_data[user_id]["game"]
    markup = types.InlineKeyboardMarkup()
    user_data[user_id]["step"] = call.data
    if call.data.endswith("_shd"):
        prices = prices_pubg if game == "pubg" else prices_freefire
        unit = "UC" if game == "pubg" else "💎"
        for amount, price in prices.items():
            markup.add(types.InlineKeyboardButton(f"{amount} {unit} - {price} ل.س", callback_data=f"{game}_shd_{amount}"))
    else:
        subs = subscriptions_pubg if game == "pubg" else subscriptions_freefire
        for name, price in subs.items():
            markup.add(types.InlineKeyboardButton(f"{name} - {price} ل.س", callback_data=f"{game}_sub_{name}"))
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.edit_message_text("✅ اختر:", call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: "shd_" in call.data or "sub_" in call.data)
def handle_selection(call):
    user_id = call.from_user.id
    data = call.data.split("_", 2)
    game, type_, val = data[0], data[1], data[2]
    price = prices_pubg[val] if game == "pubg" and type_ == "shd" else \
            prices_freefire[val] if game == "freefire" and type_ == "shd" else \
            subscriptions_pubg[val] if game == "pubg" else subscriptions_freefire[val]

    transaction_id = str(call.id)
    pending_requests.setdefault(user_id, {})[transaction_id] = {
        "game": game, "type": type_, "value": val, "price": price
    }
    user_data[user_id]["step"] = "transaction_number"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.edit_message_text(
        f"💰 السعر: {price} ل.س\n"
        "📱 حول على أحد الرقمين:\n• `16954304`\n• `81827789`\n\nأرسل رقم العملية:",
        call.message.chat.id, call.message.message_id, reply_markup=markup
    )
    bot.register_next_step_handler_by_chat_id(user_id, lambda m: get_transaction_number(m, transaction_id))

def get_transaction_number(message, transaction_id):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ أدخل رقم العملية بشكل رقمي فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda m: get_transaction_number(m, transaction_id))
    pending_requests[user_id][transaction_id]["transaction_number"] = message.text
    bot.send_message(user_id, "📞 أدخل الرقم الذي حولت عليه:", reply_markup=back_button())
    bot.register_next_step_handler_by_chat_id(user_id, lambda m: get_target_number(m, transaction_id))

def get_target_number(message, transaction_id):
    user_id = message.from_user.id
    if message.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "⚠️ الرقم غير صحيح.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda m: get_target_number(m, transaction_id))
    pending_requests[user_id][transaction_id]["target_number"] = message.text
    request = pending_requests[user_id][transaction_id]
    if request["type"] == "sub":
        final_msg = (
            f"🆕 طلب اشتراك:\n👤 @{message.from_user.username or 'بدون يوزر'}\n🆔 {user_id}\n"
            f"🎯 {request['value']} - {request['price']} ل.س\n"
            f"📞 الرقم: {request['target_number']}\n🔢 العملية: {request['transaction_number']}"
        )
        send_admin_confirmation(user_id, transaction_id, final_msg)
    else:
        bot.send_message(user_id, "🎮 أرسل ID حسابك داخل اللعبة:")
        bot.register_next_step_handler_by_chat_id(user_id, lambda m: get_game_id(m, transaction_id))

def get_game_id(message, transaction_id):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ أدخل ID رقمي فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda m: get_game_id(m, transaction_id))
    pending_requests[user_id][transaction_id]["game_id"] = message.text
    r = pending_requests[user_id][transaction_id]
    unit = "UC" if r["game"] == "pubg" else "💎"
    final_msg = (
        f"🆕 طلب شدات:\n👤 @{message.from_user.username or 'بدون يوزر'}\n🆔 {user_id}\n"
        f"🎯 {r['value']} {unit} - {r['price']} ل.س\n🎮 ID: {r['game_id']}\n"
        f"📞 الرقم: {r['target_number']}\n🔢 العملية: {r['transaction_number']}"
    )
    send_admin_confirmation(user_id, transaction_id, final_msg)

def send_admin_confirmation(user_id, transaction_id, text):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تمت العملية", callback_data=f"confirm_{user_id}_{transaction_id}"),
        types.InlineKeyboardButton("❌ فشلت العملية", callback_data=f"fail_{user_id}_{transaction_id}")
    )
    bot.send_message(ADMIN_ID, text, reply_markup=markup)
    bot.send_message(user_id, "✅ تم استلام معلوماتك، سيتم تنفيذ الطلب قريباً.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_") or call.data.startswith("fail_"))
def handle_admin_response(call):
    parts = call.data.split("_")
    action, user_id, transaction_id = parts[0], int(parts[1]), parts[2]
    req = pending_requests.get(user_id, {}).get(transaction_id)
    if not req:
        return
    if action == "confirm":
        if req["type"] == "sub":
            msg = f"✅ تم تفعيل اشتراكك **{req['value']}** بنجاح، شكراً لتعاملك معنا 🌟"
        else:
            unit = "UC" if req["game"] == "pubg" else "💎"
            msg = f"✅ تم شحن {req['value']} {unit} على ID {req['game_id']}، شكراً لتعاملك معنا 🌟"
        bot.send_message(user_id, msg)
        bot.send_message(ADMIN_ID, f"📦 تم الشحن لرقم العملية: {req['transaction_number']}")
    else:
        bot.send_message(user_id, "❌ فشلت العملية، تأكد من معلوماتك واضغط /start لإعادة المحاولة.")
    pending_requests[user_id].pop(transaction_id, None)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def spam_filter(message):
    if not BOT_ACTIVE:
        return
    keywords = ["http", "https", "t.me", ".com"]
    if any(k in message.text.lower() for k in keywords):
        bot.reply_to(message, "🚫 ممنوع إرسال روابط.")

keep_alive()
bot.infinity_polling()