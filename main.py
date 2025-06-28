from keep_alive import keep_alive
keep_alive()

import telebot
from telebot import types
import os
import shelve

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = 7188219652

BOT_ACTIVE = True
bot = telebot.TeleBot(BOT_TOKEN)

prices_pubg = {
    "60": "10,000",
    "120": "20,000",
    "325": "50,000",
    "385": "60,000",
    "660": "100,000",
    "1320": "200,000",
    "1800": "250,000",
    "3850": "500,000",
    "Prime":"13,000",
    "Prime plus":"130,000"
}

prices_freefire = {
    "110": "9,000",
    "210": "18,000",
    "341": "27,000",
    "572": "45,000",
    "1166": "90,000",
    "2400": "190,000",
    "عضوية اسبوعية":"20,000",
    "عضوية شهرية": "70,000"
}

def get_user_orders(user_id):
    with shelve.open("orders_db") as db:
        return db.get(str(user_id), {})

def save_user_orders(user_id, orders):
    with shelve.open("orders_db") as db:
        db[str(user_id)] = orders

def clear_user_orders(user_id):
    with shelve.open("orders_db") as db:
        if str(user_id) in db:
            del db[str(user_id)]

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

    # امسح الطلب المؤقت 'current' فقط بدون حذف كل الطلبات القديمة
    orders = get_user_orders(user_id)
    orders['current'] = {"step": "start"}
    save_user_orders(user_id, orders)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("📱 PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("🎮 Free Fire", callback_data="freefire")
    )
    bot.send_message(user_id, "👋 أهلاً بك في متجر YAROB لشحن الألعاب 💳\n🔽 اختر اللعبة التي ترغب بشحنها:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("🚫 البوت متوقف حالياً، نشكر تفهمكم ❤️", chat_id=call.message.chat.id, message_id=call.message.message_id)
        return

    user_id = call.from_user.id
    orders = get_user_orders(user_id)
    orders['current'] = {'game': call.data, "step": "choose_game"}
    save_user_orders(user_id, orders)

    game_name = "Pubg" if call.data == "pubg" else "Free"
    price_label = "UC" if call.data == "pubg" else "💎"
    prices = prices_pubg if call.data == "pubg" else prices_freefire

    markup = types.InlineKeyboardMarkup()
    for amount, price in prices.items():
        markup.add(types.InlineKeyboardButton(f"{game_name} {amount}{price_label} - {price} ل.س", callback_data=amount))

    bot.edit_message_text(f"🎁 عروض {game_name} المتوفّرة:\nاختر باقتك:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in prices_pubg or call.data in prices_freefire)
def handle_selection(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("🚫 البوت متوقف حالياً، نشكر تفهمكم ❤️", chat_id=call.message.chat.id, message_id=call.message.message_id)
        return

    user_id = call.from_user.id
    orders = get_user_orders(user_id)
    current = orders.get('current', {})
    game = current.get('game')
    prices = prices_pubg if game == "pubg" else prices_freefire
    amount = call.data

    current.update({'amount': amount, "step": "choose_amount"})
    orders['current'] = current
    save_user_orders(user_id, orders)

    bot.edit_message_text(
        f"💰 السعر: {prices[amount]} ل.س\n\n"
        f"📱 يرجى التحويل عبر سيرياتيل كاش((تحويل يدوي)) إلى أحد الأرقام التالية:\n  • 16954304      ➡️تحويل يدوي\n  • 81827789      ➡️تحويل يدوي\n\n"
        f"ثم أرسل رقم العملية:",
        chat_id=user_id,
        message_id=call.message.message_id
    )
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

def get_transaction_number(message):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ الرجاء إدخال رقم العملية بشكل رقمي فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

    transaction_number = message.text
    orders = get_user_orders(user_id)
    current = orders.get('current', {})

    orders[transaction_number] = {
        "transaction_number": transaction_number,
        "step": "transaction_number",
        "game": current.get("game"),
        "amount": current.get("amount")
    }
    orders['current'] = {}
    save_user_orders(user_id, orders)

    bot.send_message(user_id, "📞 الرجاء إدخال الرقم الذي قمت بالتحويل عليه (`16954304` أو `81827789`):")
    bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_target_number(msg, transaction_number))

def get_target_number(message, transaction_number):
    user_id = message.from_user.id
    if message.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "⚠️ الرقم غير صحيح، الرجاء إدخال أحد الرقمين فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_target_number(msg, transaction_number))

    orders = get_user_orders(user_id)
    orders[transaction_number]["target_number"] = message.text
    orders[transaction_number]["step"] = "target_number"
    save_user_orders(user_id, orders)

    bot.send_message(user_id, "🎮 أرسل الآن ID حسابك داخل اللعبة:")
    bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_game_id(msg, transaction_number))

def get_game_id(message, transaction_number):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ الرجاء إدخال ID اللعبة بشكل رقمي فقط.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_game_id(msg, transaction_number))

    orders = get_user_orders(user_id)
    orders[transaction_number]['game_id'] = message.text
    orders[transaction_number]["step"] = "game_id"
    save_user_orders(user_id, orders)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ تمت العملية", callback_data=f"confirm|{user_id}|{transaction_number}"),
        types.InlineKeyboardButton("❌ فشلت العملية", callback_data=f"fail|{user_id}|{transaction_number}")
    )

    bot.send_message(ADMIN_ID,
        f"🆕 طلب شحن جديد:\n"
        f"👤 المستخدم: @{message.from_user.username or 'بدون يوزر'}\n"
        f"🆔 تيليجرام: {user_id}\n"
        f"🎮 ID اللعبة: {orders[transaction_number]['game_id']}\n"
        f"🎯 الكمية: {orders[transaction_number]['amount']} {orders[transaction_number]['game']}\n"
        f"📞 الرقم المحوّل عليه: {orders[transaction_number]['target_number']}\n"
        f"🔢 رقم العملية: {transaction_number}",
        reply_markup=markup
    )
    bot.send_message(user_id, "✅ تم استلام معلوماتك بنجاح! سيتم تنفيذ طلبك قريبًا 💚")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm|"))
def confirm_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        _, user_id_str, transaction_number = call.data.split("|", 2)
        user_id = int(user_id_str)
        orders = get_user_orders(user_id)
        data = orders.get(transaction_number)

        if not data:
            bot.send_message(ADMIN_ID, f"❌ لم يتم العثور على بيانات الطلب لرقم العملية: {transaction_number}")
            return

        unit = "UC" if data["game"] == "pubg" else "💎"
        confirm_msg = f"تم شحن حسابك بـ {data['amount']} {unit} على الـ ID التالي: 📱{data['game_id']} بنجاح ✅  شكراً لتعاملك معنا 🌟"
        bot.send_message(user_id, confirm_msg)
        bot.send_message(ADMIN_ID, f"📦 تم الشحن إلى رقم العملية: {transaction_number}")

        # امسح الطلب بعد التأكيد
        del orders[transaction_number]
        save_user_orders(user_id, orders)

    except Exception as e:
        bot.send_message(ADMIN_ID, f"❗ حدث خطأ أثناء تأكيد العملية: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail|"))
def fail_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return
    _, user_id_str, transaction_number = call.data.split("|", 2)
    user_id = int(user_id_str)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("▶️ لإعادة المحاولة اضغط start", callback_data='retry'))
    bot.send_message(user_id, "❌ فشلت العملية\nيرجى التأكد من صحة المعلومات، ثم اضغط /start لإعادة المحاولة.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("🚫 البوت متوقف حالياً، نشكر تفهمكم ❤️", chat_id=call.message.chat.id, message_id=call.message.message_id)
        return
    orders = get_user_orders(call.from_user.id)
    orders['current'] = {"step": "start"}
    save_user_orders(call.from_user.id, orders)
    send_welcome(call.message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter_spam_messages(message):
    if not BOT_ACTIVE:
        return
    spam_keywords = ["http", "https", "www", "t.me", ".com", ".me", "₹", "free", "click", "promo", "join", "channel", "offer", "mil jayga"]
    if any(word in message.text.lower() for word in spam_keywords):
        bot.reply_to(message, "🚫 يمنع إرسال الروابط أو الرسائل الدعائية داخل البوت.")
        return
    current_step = None
    orders = get_user_orders(message.from_user.id)
    if isinstance(orders, dict):
        if 'current' in orders:
            current_step = orders['current'].get('step')
        else:
            for key, val in orders.items():
                if isinstance(val, dict) and 'step' in val:
                    current_step = val['step']
                    break
    allowed_steps = ["transaction_number", "target_number", "game_id"]
    if current_step not in allowed_steps:
        bot.reply_to(message, "❗ يرجى استخدام الأزرار فقط للتعامل مع البوت.")
        return

bot.infinity_polling()