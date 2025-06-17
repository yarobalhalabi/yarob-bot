from keep_alive import keep_alive
keep_alive()

import telebot
from telebot import types

BOT_TOKEN = '8083003172:AAFAkfpg9D6ZgqjtEsKCM5khqCYK2QHeTGM'
ADMIN_ID = 7188219652

BOT_ACTIVE = True

bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}
user_messages = {}

prices_pubg = {
    "60": "9,500 S.P",
    "120": "19,000 S.P",
    "180": "28,500 S.P",
    "325": "47,000 S.P",
    "660": "92,000 S.P",
    "1800": "240,000 S.P",
    "3850": "480,000 S.P"
}

prices_freefire = {
    "110": "11,000 S.P",
    "220": "22,000 S.P",
    "572": "55,000 S.P",
    "1266": "110,000 S.P"
}

def clear_user_data(user_id):
    user_data.pop(user_id, None)
    if user_id in user_messages:
        for msg_id in user_messages[user_id]:
            try:
                bot.delete_message(user_id, msg_id)
            except:
                pass
        user_messages[user_id] = []

def track_message(msg):
    user_id = msg.chat.id
    if user_id not in user_messages:
        user_messages[user_id] = []
    user_messages[user_id].append(msg.message_id)

@bot.message_handler(commands=['on'])
def activate_bot(message):
    global BOT_ACTIVE
    if message.from_user.id == ADMIN_ID:
        BOT_ACTIVE = True
        bot.send_message(message.chat.id, " تم تفعيل البوت.")
    else:
        bot.send_message(message.chat.id, " هذا الأمر مخصص للإدارة فقط.")

@bot.message_handler(commands=['off'])
def deactivate_bot(message):
    global BOT_ACTIVE
    if message.from_user.id == ADMIN_ID:
        BOT_ACTIVE = False
        bot.send_message(message.chat.id, " تم إيقاف البوت.")
    else:
        bot.send_message(message.chat.id, " هذا الأمر مخصص للإدارة فقط.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    if not BOT_ACTIVE:
        msg = bot.send_message(user_id, " البوت متوقف حالياً، شكراً لتفهمكم ")
        track_message(msg)
        return

    clear_user_data(user_id)
    user_data[user_id] = {}
    welcome_text = " أهلاً بك في متجر YAROB لشحن الألعاب "
 اختر اللعبة التي ترغب بشحنها:"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(" PUBG", callback_data="pubg"),
        types.InlineKeyboardButton(" Free Fire", callback_data="freefire")
    )
    msg = bot.send_message(user_id, welcome_text, reply_markup=markup)
    track_message(msg)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    user_id = call.from_user.id
    user_data[user_id] = {'game': call.data}

    if call.data == "pubg":
        prices = prices_pubg
        game_name = "PUBG"
        price_label = "شدة"
    else:
        prices = prices_freefire
        game_name = "Free Fire"
        price_label = "جوهره"

    welcome_text = f" اختر كمية {price_label} التي ترغب بشرائها ل {game_name}:"
    markup = types.InlineKeyboardMarkup()
    for amount, price in prices.items():
        markup.add(types.InlineKeyboardButton(f"{amount} {price_label} - {price}", callback_data=amount))
    markup.add(types.InlineKeyboardButton(" رجوع", callback_data="back_to_start"))
    markup.add(types.InlineKeyboardButton(" إلغاء الطلب", callback_data="cancel_order"))

    msg = bot.send_message(user_id, welcome_text, reply_markup=markup)
    track_message(msg)

@bot.callback_query_handler(func=lambda call: call.data in prices_pubg or call.data in prices_freefire)
def handle_selection(call):
    user_id = call.from_user.id
    game = user_data[user_id]['game']
    amount = call.data
    prices = prices_pubg if game == "pubg" else prices_freefire
    user_data[user_id].update({'amount': amount})

    payment_text = (
        f" السعر: {prices[amount]}

"
        f" يرجى التحويل عبر سيرياتيل كاش (تحويل يدوي) إلى أحد الأرقام التالية:
"
        f"• 16954304
"
        f"• 81827789

"
        f"بعد التحويل، أرسل رقم العملية:"
    )
    msg = bot.send_message(user_id, payment_text)
    track_message(msg)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

def get_transaction_number(message):
    user_id = message.from_user.id
    if not message.text.isdigit():
        msg = bot.send_message(user_id, " الرجاء إدخال رقم العملية بشكل رقمي فقط.")
        track_message(msg)
        return bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)
    user_data[user_id]['transaction_number'] = message.text
    msg = bot.send_message(user_id, " أرسل الآن المبلغ الذي قمت بتحويله:")
    track_message(msg)
    bot.register_next_step_handler_by_chat_id(user_id, get_amount)

def get_amount(message):
    user_id = message.from_user.id
    if not message.text.isdigit():
        msg = bot.send_message(user_id, " الرجاء إدخال المبلغ بشكل رقمي فقط.")
        track_message(msg)
        return bot.register_next_step_handler_by_chat_id(user_id, get_amount)
    user_data[user_id]['transferred_amount'] = message.text
    msg = bot.send_message(user_id, " أرسل الآن ID حسابك داخل اللعبة:")
    track_message(msg)
    bot.register_next_step_handler_by_chat_id(user_id, get_game_id)

def get_game_id(message):
    user_id = message.from_user.id
    if not message.text.isdigit():
        msg = bot.send_message(user_id, " الرجاء إدخال ID اللعبة بشكل رقمي فقط.")
        track_message(msg)
        return bot.register_next_step_handler_by_chat_id(user_id, get_game_id)

    data = user_data[user_id]
    data['game_id'] = message.text

    final_message = (
        f" طلب شحن جديد:
"
        f" المستخدم: @{message.from_user.username or 'بدون يوزر'}
"
        f" تيليجرام: {user_id}
"
        f" ID اللعبة: {data['game_id']}
"
        f" الكمية: {data['amount']} {data['game']}
"
        f" المبلغ: {data['transferred_amount']}
"
        f" رقم العملية: {data['transaction_number']}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(" تمت العملية", callback_data=f"confirm_{user_id}"),
        types.InlineKeyboardButton(" فشلت العملية", callback_data=f"fail_{user_id}")
    )

    bot.send_message(ADMIN_ID, final_message, reply_markup=markup)
    msg = bot.send_message(user_id, " تم استلام معلوماتك بنجاح! سيتم تنفيذ طلبك قريبًا ")
    track_message(msg)

@bot.callback_query_handler(func=lambda call: call.data == "cancel_order")
def cancel_order(call):
    user_id = call.from_user.id
    clear_user_data(user_id)
    bot.send_message(user_id, " تم إلغاء الطلب وحذف جميع الرسائل.")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_start")
def back_to_start(call):
    send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_delivery(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, " هذا الزر مخصص للإدارة فقط.")
        return
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, " تم تنفيذ عملية الشحن بنجاح! شكراً لتعاملك معنا ")
    bot.answer_callback_query(call.id, "تم إعلام العميل.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail_"))
def fail_delivery(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, " هذا الزر مخصص للإدارة فقط.")
        return

    user_id = int(call.data.split("_")[1])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(" إعادة المحاولة", callback_data='retry'))
    fail_text = " فشلت العملية
يرجى التأكد من صحة المعلومات وإعادة المحاولة."
    bot.send_message(user_id, fail_text, reply_markup=markup)
    bot.answer_callback_query(call.id, "تم إعلام العميل بفشل العملية.")

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    clear_user_data(call.from_user.id)
    send_welcome(call.message)

bot.infinity_polling()
