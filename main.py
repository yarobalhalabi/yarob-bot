
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

prices_freefire = {
    "110": "11,000",
    "210": "22,000",
    "341": "33,000",
    "570": "55,000",
    "1160": "110,000",
    "2200": "200,000"
}

subscriptions_pubg = [
    "⭐ برايم",
    "🌟 برايم بلس",
    "🌸 حزم الازدهار"
]

subscriptions_freefire = [
    "🛡️ تصريح مستوى",
    "🗓️ عضوية أسبوعية",
    "📅 عضوية شهرية"
]

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
        bot.send_message(user_id, "🚫 البوت متوقف حالياً، نشكر تفهمكم ❤️")
        return

    clear_user_data(user_id)
    user_data[user_id] = {"step": "start"}
    welcome_text = "👋 أهلاً بك في متجر YAROB لشحن الألعاب 💳
🔽 اختر اللعبة:"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📱 PUBG", callback_data="game_pubg"),
        types.InlineKeyboardButton("🎮 Free Fire", callback_data="game_freefire")
    )
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("game_"))
def choose_game(call):
    game = call.data.split("_")[1]
    user_id = call.from_user.id
    user_data[user_id] = {"game": game, "step": "choose_type"}

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💰 الأسعار", callback_data="type_prices"),
        types.InlineKeyboardButton("🧾 الاشتراكات", callback_data="type_subscriptions"),
        types.InlineKeyboardButton("🔙 رجوع", callback_data="restart")
    )
    bot.edit_message_text(f"📍 اختر نوع الخدمة للعبة {'PUBG' if game == 'pubg' else 'Free Fire'}:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["type_prices", "type_subscriptions"])
def show_options(call):
    user_id = call.from_user.id
    game = user_data[user_id]["game"]
    choice = call.data

    markup = types.InlineKeyboardMarkup()
    if choice == "type_prices":
        items = prices_pubg if game == "pubg" else prices_freefire
        unit = "UC" if game == "pubg" else "💎"
        for amount, price in items.items():
            markup.add(types.InlineKeyboardButton(f"{amount} {unit} - {price} ل.س", callback_data=f"price_{amount}"))
        bot.edit_message_text("💵 الأسعار المتوفرة:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)
    else:
        items = subscriptions_pubg if game == "pubg" else subscriptions_freefire
        for i, sub in enumerate(items):
            markup.add(types.InlineKeyboardButton(sub, callback_data=f"sub_{i}"))
        bot.edit_message_text("🧾 الاشتراكات المتوفرة:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "restart")
def restart(call):
    send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("price_") or call.data.startswith("sub_"))
def handle_selection(call):
    user_id = call.from_user.id
    game = user_data[user_id]["game"]
    data_type = "price" if call.data.startswith("price_") else "sub"
    selected = call.data.split("_")[1]
    user_data[user_id]["step"] = "ordering"

    # Save the selection in user_data
    if data_type == "price":
        user_data[user_id]["amount"] = selected
        user_data[user_id]["selection_type"] = "price"
    else:
        sub_list = subscriptions_pubg if game == "pubg" else subscriptions_freefire
        user_data[user_id]["subscription"] = sub_list[int(selected)]
        user_data[user_id]["selection_type"] = "subscription"

    payment_text = ""
    if data_type == "price":
        price_val = prices_pubg[selected] if game == "pubg" else prices_freefire[selected]
        unit = "UC" if game == "pubg" else "💎"
        payment_text = (
            f"💰 السعر: {price_val} ل.س

"
            f"📱 يرجى التحويل عبر سيرياتيل كاش إلى أحد الأرقام التالية:
"
            f" • 16954304
"
            f" • 81827789

"
            f"بعد التحويل، أرسل رقم العملية:"
        )
    else:
        # For subscriptions, can set fixed prices or instructions
        payment_text = (
            f"🧾 طلب الاشتراك: {user_data[user_id]['subscription']}

"
            f"📱 يرجى التحويل عبر سيرياتيل كاش إلى أحد الأرقام التالية:
"
            f" • 16954304
"
            f" • 81827789

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
        f"🆕 طلب جديد:
"
        f"👤 المستخدم: @{message.from_user.username or 'بدون يوزر'}
"
        f"🆔 تيليجرام: {user_id}
"
        f"🎮 اللعبة: {'PUBG' if data['game']=='pubg' else 'Free Fire'}
"
    )

    if data.get("selection_type") == "price":
        unit = "UC" if data['game'] == "pubg" else "💎"
        final_message += f"🎯 الكمية: {data['amount']} {unit}
"
    else:
        final_message += f"🎯 الاشتراك: {data.get('subscription', 'غير معروف')}
"

    final_message += (
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
    confirm_msg = f"تم شحن حسابك بـ {amount} {unit} على الـ ID التالي: 📱{game_id} بنجاح ✅  شكرا لتعاملك معنا 🌟"
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
    markup.add(types.InlineKeyboardButton("▶️ لإعادة المحاولة اضغط /start", callback_data='retry'))
    fail_text = "❌ فشلت العملية
يرجى التأكد من صحة المعلومات، ثم اضغط /start لإعادة المحاولة."
    bot.send_message(user_id, fail_text, reply_markup=markup)
    bot.answer_callback_query(call.id, "تم إعلام العميل بفشل العملية.")

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    clear_user_data(call.from_user.id)
    send_welcome(call.message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter_spam_messages(message):
    spam_keywords = ["http", "https", "www", "t.me", ".com", ".me", "₹", "free", "click", "promo", "join", "channel", "offer", "mil jayga"]
    if any(word in message.text.lower() for word in spam_keywords):
        bot.reply_to(message, "🚫 يمنع إرسال الروابط أو الرسائل الدعائية داخل البوت.")
        return
    if user_data.get(message.from_user.id, {}).get("step") not in ["transaction_number", "target_number", "game_id"]:
        bot.reply_to(message, "❗ يرجى استخدام الأزرار فقط للتعامل مع البوت.")
        return

bot.infinity_polling()
