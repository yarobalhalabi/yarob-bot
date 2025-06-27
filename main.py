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
    "180": "30,000",
    "325": "50,000",
    "385": "60,000",
    "660": "100,000",
    "985": "150,000",
    "1320": "200,000",
    "1800": "250,000",
    "3850": "500,000"
}

prices_freefire = {
    "110": "8,500",
    "210": "17,000",
    "341": "25,000",
    "572": "45,000",
    "1166": "90,000",
    "2400": "200,000"
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
        bot.send_message(message.chat.id, "âœ… ØªÙ… ØªÙØ¹ÙŠÙ„ Ø§Ù„Ø¨ÙˆØª.")
    else:
        bot.send_message(message.chat.id, "ðŸš« Ù‡Ø°Ø§ Ø§Ù„Ø£Ù…Ø± Ù…Ø®ØµØµ Ù„Ù„Ø¥Ø¯Ø§Ø±Ø© ÙÙ‚Ø·.")

@bot.message_handler(commands=['off'])
def deactivate_bot(message):
    global BOT_ACTIVE
    if message.from_user.id == ADMIN_ID:
        BOT_ACTIVE = False
        bot.send_message(message.chat.id, "â›” ØªÙ… Ø¥ÙŠÙ‚Ø§Ù Ø§Ù„Ø¨ÙˆØª.")
    else:
        bot.send_message(message.chat.id, "ðŸš« Ù‡Ø°Ø§ Ø§Ù„Ø£Ù…Ø± Ù…Ø®ØµØµ Ù„Ù„Ø¥Ø¯Ø§Ø±Ø© ÙÙ‚Ø·.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "ðŸš« Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹ØŒ Ù†Ø´ÙƒØ± ØªÙÙ‡Ù…ÙƒÙ… â¤ï¸")
        return

    orders = get_user_orders(user_id)
    orders['current'] = {"step": "start"}
    save_user_orders(user_id, orders)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ðŸ“± PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("ðŸŽ® Free Fire", callback_data="freefire")
    )
    bot.send_message(user_id, "ðŸ‘‹ Ø£Ù‡Ù„Ø§Ù‹ Ø¨Ùƒ ÙÙŠ Ù…ØªØ¬Ø± YAROB Ù„Ø´Ø­Ù† Ø§Ù„Ø£Ù„Ø¹Ø§Ø¨ ðŸ’³\nðŸ”½ Ø§Ø®ØªØ± Ø§Ù„Ù„Ø¹Ø¨Ø© Ø§Ù„ØªÙŠ ØªØ±ØºØ¨ Ø¨Ø´Ø­Ù†Ù‡Ø§:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("ðŸš« Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹ØŒ Ù†Ø´ÙƒØ± ØªÙÙ‡Ù…ÙƒÙ… â¤ï¸", chat_id=call.message.chat.id, message_id=call.message.message_id)
        return

    user_id = call.from_user.id
    orders = get_user_orders(user_id)
    orders['current'] = {'game': call.data, "step": "choose_game"}
    save_user_orders(user_id, orders)

    game_name = "Pubg" if call.data == "pubg" else "Free"
    price_label = "UC" if call.data == "pubg" else "ðŸ’Ž"
    prices = prices_pubg if call.data == "pubg" else prices_freefire

    markup = types.InlineKeyboardMarkup()
    for amount, price in prices.items():
        btn_text = f"ðŸ’Ž {game_name} {amount}{price_label}\nðŸ’° Ø§Ù„Ø³Ø¹Ø±: {price} Ù„.Ø³"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=amount))

    bot.edit_message_text(f"ðŸŽ Ø¹Ø±ÙˆØ¶ {game_name} Ø§Ù„Ù…ØªÙˆÙÙ‘Ø±Ø©:\nØ§Ø®ØªØ± Ø¨Ø§Ù‚ØªÙƒ:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in prices_pubg or call.data in prices_freefire)
def handle_selection(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("ðŸš« Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹ØŒ Ù†Ø´ÙƒØ± ØªÙÙ‡Ù…ÙƒÙ… â¤ï¸", chat_id=call.message.chat.id, message_id=call.message.message_id)
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
        f"ðŸ’° Ø§Ù„Ø³Ø¹Ø±: {prices[amount]} Ù„.Ø³\n\n"
        f"ðŸ“Œ Ù‚Ù… Ø¨Ø¥Ø±Ø³Ø§Ù„ Ø§Ù„Ù…Ø¨Ù„Øº Ø§Ù„Ù…Ø·Ù„ÙˆØ¨ \"ØªØ­ÙˆÙŠÙ„ ÙŠØ¯ÙˆÙŠ Ø­ØµØ±Ø§Ù‹\" Ø¥Ù„Ù‰ Ø£Ø­Ø¯ Ø§Ù„Ø±Ù…ÙˆØ² Ø§Ù„ØªØ§Ù„ÙŠØ©:\n\n"
        f"ØªØ­ÙˆÙŠÙ„ ÙŠØ¯ÙˆÙŠ â¬…              16954304\n"
        f"ØªØ­ÙˆÙŠÙ„ ÙŠØ¯ÙˆÙŠ â¬…              81827789\n\n"
        f"Ù…Ù„Ø§Ø­Ø¸Ø©ðŸš¨ : ÙŠØ±Ø¬Ù‰ Ø§Ø±Ø³Ø§Ù„ Ø§Ù„Ù…Ø¨Ù„Øº ØªØ­ÙˆÙŠÙ„ ÙŠØ¯ÙˆÙŠ ÙˆÙ„ÙŠØ³ Ø¯ÙØ¹ ÙŠØ¯ÙˆÙŠ\n\n"
        f"Ø«Ù… Ø£Ø±Ø³Ù„ Ø±Ù‚Ù… Ø¹Ù…Ù„ÙŠØ© Ø§Ù„ØªØ­ÙˆÙŠÙ„:",
        chat_id=user_id,
        message_id=call.message.message_id
    )
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

def get_transaction_number(message):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "âš ï¸ Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ© Ø¨Ø´ÙƒÙ„ Ø±Ù‚Ù…ÙŠ ÙÙ‚Ø·.")
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

    bot.send_message(user_id, "ðŸ“ž Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ Ø§Ù„Ø±Ù‚Ù… Ø§Ù„Ø°ÙŠ Ù‚Ù…Øª Ø¨Ø§Ù„ØªØ­ÙˆÙŠÙ„ Ø¹Ù„ÙŠÙ‡ (`16954304` Ø£Ùˆ `81827789`):")
    bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_target_number(msg, transaction_number))

def get_target_number(message, transaction_number):
    user_id = message.from_user.id
    if message.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "âš ï¸ Ø§Ù„Ø±Ù‚Ù… ØºÙŠØ± ØµØ­ÙŠØ­ØŒ Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ Ø£Ø­Ø¯ Ø§Ù„Ø±Ù‚Ù…ÙŠÙ† ÙÙ‚Ø·.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_target_number(msg, transaction_number))

    orders = get_user_orders(user_id)
    orders[transaction_number]["target_number"] = message.text
    orders[transaction_number]["step"] = "target_number"
    save_user_orders(user_id, orders)

    bot.send_message(user_id, "ðŸŽ® Ø£Ø±Ø³Ù„ Ø§Ù„Ø¢Ù† ID Ø­Ø³Ø§Ø¨Ùƒ Ø¯Ø§Ø®Ù„ Ø§Ù„Ù„Ø¹Ø¨Ø©:")
    bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_game_id(msg, transaction_number))

def get_game_id(message, transaction_number):
    user_id = message.from_user.id
    if not message.text.isdigit():
        bot.send_message(user_id, "âš ï¸ Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ ID Ø§Ù„Ù„Ø¹Ø¨Ø© Ø¨Ø´ÙƒÙ„ Ø±Ù‚Ù…ÙŠ ÙÙ‚Ø·.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_game_id(msg, transaction_number))

    orders = get_user_orders(user_id)
    orders[transaction_number]['game_id'] = message.text
    orders[transaction_number]["step"] = "game_id"
    save_user_orders(user_id, orders)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("âœ… ØªÙ…Øª Ø§Ù„Ø¹Ù…Ù„ÙŠØ©", callback_data=f"confirm|{user_id}|{transaction_number}"),
        types.InlineKeyboardButton("âŒ ÙØ´Ù„Øª Ø§Ù„Ø¹Ù…Ù„ÙŠØ©", callback_data=f"fail|{user_id}|{transaction_number}")
    )

    bot.send_message(ADMIN_ID,
        f"ðŸ†• Ø·Ù„Ø¨ Ø´Ø­Ù† Ø¬Ø¯ÙŠØ¯:\n"
        f"ðŸ‘¤ Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…: @{message.from_user.username or 'Ø¨Ø¯ÙˆÙ† ÙŠÙˆØ²Ø±'}\n"
        f"ðŸ†” ØªÙŠÙ„ÙŠØ¬Ø±Ø§Ù…: {user_id}\n"
        f"ðŸŽ® ID Ø§Ù„Ù„Ø¹Ø¨Ø©: {orders[transaction_number]['game_id']}\n"
        f"ðŸŽ¯ Ø§Ù„ÙƒÙ…ÙŠØ©: {orders[transaction_number]['amount']} {orders[transaction_number]['game']}\n"
        f"ðŸ“ž Ø§Ù„Ø±Ù‚Ù… Ø§Ù„Ù…Ø­ÙˆÙ‘Ù„ Ø¹Ù„ÙŠÙ‡: {orders[transaction_number]['target_number']}\n"
        f"ðŸ”¢ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ©: {transaction_number}",
        reply_markup=markup
    )
    bot.send_message(user_id, "âœ… ØªÙ… Ø§Ø³ØªÙ„Ø§Ù… Ù…Ø¹Ù„ÙˆÙ…Ø§ØªÙƒ Ø¨Ù†Ø¬Ø§Ø­! Ø³ÙŠØªÙ… ØªÙ†ÙÙŠØ° Ø·Ù„Ø¨Ùƒ Ù‚Ø±ÙŠØ¨Ù‹Ø§ ðŸ’š")

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
            bot.send_message(ADMIN_ID, f"âŒ Ù„Ù… ÙŠØªÙ… Ø§Ù„Ø¹Ø«ÙˆØ± Ø¹Ù„Ù‰ Ø¨ÙŠØ§Ù†Ø§Øª Ø§Ù„Ø·Ù„Ø¨ Ù„Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ©: {transaction_number}")
            return

        unit = "UC" if data["game"] == "pubg" else "ðŸ’Ž"
        confirm_msg = f"ØªÙ… Ø´Ø­Ù† Ø­Ø³Ø§Ø¨Ùƒ Ø¨Ù€ {data['amount']} {unit} Ø¹Ù„Ù‰ Ø§Ù„Ù€ ID Ø§Ù„ØªØ§Ù„ÙŠ: ðŸ“±{data['game_id']} Ø¨Ù†Ø¬Ø§Ø­ âœ…  Ø´ÙƒØ±Ø§Ù‹ Ù„ØªØ¹Ø§Ù…Ù„Ùƒ Ù…Ø¹Ù†Ø§ ðŸŒŸ"
        bot.send_message(user_id, confirm_msg)
        bot.send_message(ADMIN_ID, f"ðŸ“¦ ØªÙ… Ø§Ù„Ø´Ø­Ù† Ø¥Ù„Ù‰ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ©: {transaction_number}")

        del orders[transaction_number]
        save_user_orders(user_id, orders)

    except Exception as e:
        bot.send_message(ADMIN_ID, f"â— Ø­Ø¯Ø« Ø®Ø·Ø£ Ø£Ø«Ù†Ø§Ø¡ ØªØ£ÙƒÙŠØ¯ Ø§Ù„Ø¹Ù…Ù„ÙŠØ©: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail|"))
def fail_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return
    _, user_id_str, transaction_number = call.data.split("|", 2)
    user_id = int(user_id_str)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("â–¶ï¸ Ù„Ø¥Ø¹Ø§Ø¯Ø© Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø© Ø§Ø¶ØºØ· start", callback_data='retry'))
    bot.send_message(user_id, "âŒ ÙØ´Ù„Øª Ø§Ù„Ø¹Ù…Ù„ÙŠØ©\nÙŠØ±Ø¬Ù‰ Ø§Ù„ØªØ£ÙƒØ¯ Ù…Ù† ØµØ­Ø© Ø§Ù„Ù…Ø¹Ù„ÙˆÙ…Ø§ØªØŒ Ø«Ù… Ø§Ø¶ØºØ· /start Ù„Ø¥Ø¹Ø§Ø¯Ø© Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø©.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("ðŸš« Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹ØŒ Ù†Ø´ÙƒØ± ØªÙÙ‡Ù…ÙƒÙ… â¤ï¸", chat_id=call.message.chat.id, message_id=call.message.message_id)
        return
    orders = get_user_orders(call.from_user.id)
    orders['current'] = {"step": "start"}
    save_user_orders(call.from_user.id, orders)
    send_welcome(call.message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter_spam_messages(message):
    if not BOT_ACTIVE:
        return
    spam_keywords = ["http", "https", "www", "t.me", ".com", ".me", "â‚¹", "free", "click", "promo", "join", "channel", "offer", "mil jayga"]
    if any(word in message.text.lower() for word in spam_keywords):
        bot.reply_to(message, "ðŸš« ÙŠÙ…Ù†Ø¹ Ø¥Ø±Ø³Ø§Ù„ Ø§Ù„Ø±ÙˆØ§Ø¨Ø· Ø£Ùˆ Ø§Ù„Ø±Ø³Ø§Ø¦Ù„ Ø§Ù„Ø¯Ø¹Ø§Ø¦ÙŠØ© Ø¯Ø§Ø®Ù„ Ø§Ù„Ø¨ÙˆØª.")
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
        bot.reply_to(message, "â— ÙŠØ±Ø¬Ù‰ Ø§Ø³ØªØ®Ø¯Ø§Ù… Ø§Ù„Ø£Ø²Ø±Ø§Ø± ÙÙ‚Ø· Ù„Ù„ØªØ¹Ø§Ù…Ù„ Ù…Ø¹ Ø§Ù„Ø¨ÙˆØª.")
        return

bot.infinity_polling()