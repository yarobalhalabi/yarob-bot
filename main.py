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

# اشتراكات ببجي مع الأسعار (مرتبة وبنفس تنسيق الشدات)
subscriptions_pubg = {
    "برايم": "14,000",
    "برايم بلس": "140,000",
    "حزمة الشراء الأول": "14,000",
    "حزمة الشعار الخرافي": "62,000"
}

# اشتراكات فري فاير مع الأسعار
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
        bot.send_message(user_id, "🚫 البوت متوقف حالياً، نشكر تفهمكم ❤️")
        return

    clear_user_data(user_id)
    user_data[user_id] = {"step": "start"}
    welcome_text = "👋 أهلاً بك في متجر YAROB لشحن الألعاب 💳\n🔽 اختر اللعبة التي ترغب بشحنها:"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📱 PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("🎮 Free Fire", callback_data="freefire")
    )
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "back")
def go_back(call):
    user_id = call.from_user.id
    if not BOT_ACTIVE:
        bot.answer_callback_query(call.id, "🚫 البوت متوقف حالياً.")
        return
    step = user_data.get(user_id, {}).get("step", "start")

    # الرجوع خطوة واحدة حسب الخطوة الحالية
    if step.startswith("pubg_"):
        # من أقسام شدات أو اشتراكات ببجي للعبة
        send_game_options(call.message, "pubg")
        user_data[user_id]["step"] = "choose_game"
    elif step.startswith("freefire_"):
        # من أقسام شدات أو اشتراكات فري فاير للعبة
        send_game_options(call.message, "freefire")
        user_data[user_id]["step"] = "choose_game"
    elif step == "choose_game":
        send_welcome(call.message)
    else:
        send_welcome(call.message)

def send_game_options(message, game):
    user_id = message.chat.id
    if game == "pubg":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🪙 شدات", callback_data="pubg_shd"))
        markup.add(types.InlineKeyboardButton("🎫 اشتراكات", callback_data="pubg_sub"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("🎮 اختر القسم في PUBG:", chat_id=user_id, message_id=message.message_id, reply_markup=markup)
        user_data[user_id]["step"] = "choose_game"
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💎 جواهر", callback_data="freefire_shd"))
        markup.add(types.InlineKeyboardButton("🎫 اشتراكات", callback_data="freefire_sub"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("🎮 اختر القسم في Free Fire:", chat_id=user_id, message_id=message.message_id, reply_markup=markup)
        user_data[user_id]["step"] = "choose_game"

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("❌ البوت متوقف حالياً، لا يمكن إتمام الطلب الآن. يرجى المحاولة لاحقاً.",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        return

    user_id = call.from_user.id
    user_data[user_id] = {'game': call.data, "step": "choose_game"}
    send_game_options(call.message, call.data)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg_shd", "pubg_sub", "freefire_shd", "freefire_sub"])
def choose_section(call):
    if not BOT_ACTIVE:
        bot.answer_callback_query(call.id, "❌ البوت متوقف حالياً.")
        return

    user_id = call.from_user.id
    game = user_data[user_id]['game']

    if call.data == "pubg_shd":
        prices = prices_pubg
        unit = "UC"
        user_data[user_id]["step"] = "pubg_shd"
        text = "🪙 اختر كمية الشدات التي تريد شحنها:"
        markup = types.InlineKeyboardMarkup()
        for amount, price in prices.items():
            markup.add(types.InlineKeyboardButton(f"{amount} {unit} - {price} ل.س", callback_data=f"pubg_shd_{amount}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=markup)

    elif call.data == "pubg_sub":
        subs = subscriptions_pubg
        user_data[user_id]["step"] = "pubg_sub"
        text = "🎫 اختر الاشتراك الذي تريده:"
        markup = types.InlineKeyboardMarkup()
        for name, price in subs.items():
            markup.add(types.InlineKeyboardButton(f"{name} - {price} ل.س", callback_data=f"pubg_sub_{name}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=markup)

    elif call.data == "freefire_shd":
        prices = prices_freefire
        unit = "💎"
        user_data[user_id]["step"] = "freefire_shd"
        text = "💎 اختر كمية الجواهر التي تريد شحنها:"
        markup = types.InlineKeyboardMarkup()
        for amount, price in prices.items():
            markup.add(types.InlineKeyboardButton(f"{amount} {unit} - {price} ل.س", callback_data=f"freefire_shd_{amount}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=markup)

    elif call.data == "freefire_sub":
        subs = subscriptions_freefire
        user_data[user_id]["step"] = "freefire_sub"
        text = "🎫 اختر الاشتراك الذي تريده:"
        markup = types.InlineKeyboardMarkup()
        for name, price in subs.items():
            markup.add(types.InlineKeyboardButton(f"{name} - {price} ل.س", callback_data=f"freefire_sub_{name}"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text(text, user_id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pubg_shd_") or call.data.startswith("freefire_shd_"))
def handle_shd_selection(call):
    if not BOT_ACTIVE:
        bot.answer_callback_query(call.id, "❌ البوت متوقف حالياً.")
        return

    user_id = call.from_user.id
    data = call.data.split("_")
    game = user_data[user_id]['game']
    amount = data[2]
    if game == "pubg":
        price = prices_pubg.get(amount)
        unit = "UC"
    else:
        price = prices_freefire.get(amount)
        unit = "💎"

    user_data[user_id].update({'amount': amount, "step": "choose_amount", "type": "shd"})
    payment_text = (
        f"💰 السعر: {price} ل.س\n\n"
        f"📱 يرجى التحويل عبر سيرياتيل كاش (تحويل يدوي) إلى أحد الأرقام التالية:\n"
        f"• `16954304`\n"
        f"• `81827789`\n\n"
        f"بعد التحويل، أرسل رقم العملية:"
    )
    bot.edit_message_text(payment_text, user_id, call.message.message_id)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pubg_sub_") or call.data.startswith("freefire_sub_"))
def handle_sub_selection(call):
    if not BOT_ACTIVE:
        bot.answer_callback_query(call.id, "❌ البوت متوقف حالياً.")
        return

    user_id = call.from_user.id
    data = call.data.split("_", 2)
    sub_name = data[2]
    if data[0] == "pubg":
        price = subscriptions_pubg.get(sub_name)
        unit = "اشتراك"
        user_data[user_id]['game'] = "pubg"
    else:
        price = subscriptions_freefire.get(sub_name)
        unit = "اشتراك"
        user_data[user_id]['game'] = "freefire"

    user_data[user_id].update({'amount': price, "step": "choose_amount", "type": "sub", "subscription_name": sub_name})
    payment_text = (
        f"💰 السعر: {price} ل.س\n\n"
        f"📱 يرجى التحويل عبر سيرياتيل كاش (تحويل يدوي) إلى أحد الأرقام التالية:\n"
        f"• `16954304`\n"
        f"• `81827789`\n\n"
        f"بعد التحويل، أرسل رقم العملية:"
    )
    bot.edit_message_text(payment_text, user_id, call.message.message_id)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

def get_transaction_number(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "🚫 البوت متوقف حالياً.")
        return

    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ الرجاء إدخال رقم العملية بشكل رقمي فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)
    user_data[user_id]['transaction_number'] = message.text
    user_data[user_id]["step"] = "transaction_number"
    bot.send_message(user_id, "📞 الرجاء إدخال الرقم الذي قمت بالتحويل عليه (`16954304` أو `81827789`):")
    bot.register_next_step_handler_by_chat_id(user_id, get_target_number)

def get_target_number(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "🚫 البوت متوقف حالياً.")
        return

    if message.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "⚠️ الرقم غير صحيح، الرجاء إدخال أحد الرقمين فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_target_number)
    user_data[user_id]['target_number'] = message.text
    user_data[user_id]["step"] = "target_number"
    bot.send_message(user_id, "🎮 أرسل الآن ID حسابك داخل اللعبة:")
    bot.register_next_step_handler_by_chat_id(user_id, get_game_id)

def get_game_id(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "🚫 البوت متوقف حالياً.")
        return

    if user_data[user_id]['type'] == 'sub':
        # اشتراكات ما بتحتاج ID اللعبة
        data = user_data[user_id]
        data["step"] = "game_id"

        final_message = (
            f"🆕 طلب شحن جديد:\n"
            f"👤 المستخدم: @{message.from_user.username or 'بدون يوزر'}\n"
            f"🆔 تيليجرام: {user_id}\n"
            f"🎮 نوع الطلب: اشتراك\n"
            f"🎯 الاشتراك: {data['subscription_name']}\n"
            f"💰 السعر: {data['amount']} ل.س\n"
            f"📞 الرقم المحوّل عليه: {data['target_number']}\n"
            f"🔢 رقم العملية: {data['transaction_number']}"
        )
    else:
        # شدات تحتاج ID اللعبة
        if not message.text.isdigit():
            bot.send_message(user_id, "⚠️ الرجاء إدخال ID اللعبة بشكل رقمي فقط.")
            return bot.register_next_step_handler_by_chat_id(user_id, get_game_id)

        data = user_data[user_id]
        data['game_id'] = message.text
        data["step"] = "game_id"

        final_message = (
            f"🆕 طلب شحن جديد:\n"
            f"👤 المستخدم: @{message.from_user.username or 'بدون يوزر'}\n"
            f"🆔 تيليجرام: {user_id}\n"
            f"🎮 ID اللعبة: {data['game_id']}\n"
            f"🎯 الكمية: {data['amount']} {('UC' if data['game'] == 'pubg' else '💎') if data['type'] == 'shd' else ''}\n"
            f"📞 الرقم المحوّل عليه: {data['target_number']}\n"
            f"🔢 رقم العملية: {data['transaction_number']}"
        )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تمت العملية", callback_data=f"confirm_{user_id}_{data['transaction_number']}"),
        types.InlineKeyboardButton("❌ فشلت العملية", callback_data=f"fail_{user_id}")
    )

    bot.send_message(ADMIN_ID, final_message, reply_markup=markup)
    bot.send_message(user_id, "✅ تم استلام معلوماتك بنجاح! سيتم تنفيذ طلبك قريبًا 💚")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return
    parts = call.data.split("_")
    user_id = int(parts[1])
    transaction_number = parts[2]

    data = user_data.get(user_id, {})
    game = data.get("game", "unknown")
    amount = data.get("amount", "?")
    game_id = data.get("game_id", "غير معروف")
    type_ = data.get("type", "shd")
    unit = "UC" if game == "pubg" else "💎"

    # رسالة تأكيد خاصة حسب نوع الطلب
    if type_ == "sub":
        sub_name = data.get("subscription_name", "اشتراك")
        confirm_msg = f"تم تفعيل اشتراكك **{sub_name}** بنجاح ✅ شكراً لتعاملك معنا 🌟"
    else:
        confirm_msg = f"تم شحن حسابك بـ {amount} {unit} على الـ ID التالي: 📱{game_id} بنجاح ✅  شكراً لتعاملك معنا 🌟"

    bot.send_message(user_id, confirm_msg)
    bot.send_message(ADMIN_ID, f"📦 تم الشحن إلى رقم العملية: {transaction_number}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail_"))
def fail_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("▶️ لإعادة المحاولة اضغط /start", callback_data='retry'))
    fail_text = "❌ فشلت العملية\nيرجى التأكد من صحة المعلومات، ثم اضغط /start لإعادة المحاولة."
    bot.send_message(user_id, fail_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("❌ البوت متوقف حالياً، لا يمكن إتمام الطلب الآن. يرجى المحاولة لاحقاً.",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        return
    clear_user_data(call.from_user.id)
    send_welcome(call.message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter_spam_messages(message):
    if not BOT_ACTIVE:
        return
    spam_keywords = ["http", "https", "www", "t.me", ".com", ".me", "₹", "free", "click", "promo", "join", "channel", "offer", "mil jayga"]
    if any(word in message.text.lower() for word in spam_keywords):
        bot.reply_to