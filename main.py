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

def clear_user_data(user_id):
    user_data.pop(user_id, None)

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

    clear_user_data(user_id)
    user_data[user_id] = {"step": "start"}
    welcome_text = "ðŸ‘‹ Ø£Ù‡Ù„Ø§Ù‹ Ø¨Ùƒ ÙÙŠ Ù…ØªØ¬Ø± YAROB Ù„Ø´Ø­Ù† Ø§Ù„Ø£Ù„Ø¹Ø§Ø¨ ðŸ’³\nðŸ”½ Ø§Ø®ØªØ± Ø§Ù„Ù„Ø¹Ø¨Ø© Ø§Ù„ØªÙŠ ØªØ±ØºØ¨ Ø¨Ø´Ø­Ù†Ù‡Ø§:"
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("ðŸ“± PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("ðŸŽ® Free Fire", callback_data="freefire")
    )
    bot.send_message(user_id, welcome_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["pubg", "freefire"])
def choose_game(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("âŒ Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹ØŒ Ù„Ø§ ÙŠÙ…ÙƒÙ† Ø¥ØªÙ…Ø§Ù… Ø§Ù„Ø·Ù„Ø¨ Ø§Ù„Ø¢Ù†. ÙŠØ±Ø¬Ù‰ Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø© Ù„Ø§Ø­Ù‚Ø§Ù‹.",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        return

    user_id = call.from_user.id
    user_data[user_id] = {'game': call.data, "step": "choose_game"}

    if call.data == "pubg":
        prices = prices_pubg
        game_name = "Pubg"
        price_label = "UC"
    else:
        prices = prices_freefire
        game_name = "Free"
        price_label = "ðŸ’Ž"

    welcome_text = f"ðŸŽ Ø¹Ø±ÙˆØ¶ {game_name} Ø§Ù„Ù…ØªÙˆÙÙ‘Ø±Ø©:\nØ§Ø®ØªØ± Ø¨Ø§Ù‚ØªÙƒ:"
    markup = types.InlineKeyboardMarkup()
    for amount, price in prices.items():
        markup.add(types.InlineKeyboardButton(f"{game_name} {amount}{price_label} - {price} Ù„.Ø³", callback_data=amount))

    bot.edit_message_text(welcome_text, chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in prices_pubg or call.data in prices_freefire)
def handle_selection(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("âŒ Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹ØŒ Ù„Ø§ ÙŠÙ…ÙƒÙ† Ø¥ØªÙ…Ø§Ù… Ø§Ù„Ø·Ù„Ø¨ Ø§Ù„Ø¢Ù†. ÙŠØ±Ø¬Ù‰ Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø© Ù„Ø§Ø­Ù‚Ø§Ù‹.",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        return

    user_id = call.from_user.id
    game = user_data[user_id]['game']
    amount = call.data
    prices = prices_pubg if game == "pubg" else prices_freefire
    user_data[user_id].update({'amount': amount, "step": "choose_amount"})

    payment_text = (
        f"ðŸ’° Ø§Ù„Ø³Ø¹Ø±: {prices[amount]} Ù„.Ø³\n\n"
        f"ðŸ“± ÙŠØ±Ø¬Ù‰ Ø§Ù„ØªØ­ÙˆÙŠÙ„ Ø¹Ø¨Ø± Ø³ÙŠØ±ÙŠØ§ØªÙŠÙ„ ÙƒØ§Ø´ (ØªØ­ÙˆÙŠÙ„ ÙŠØ¯ÙˆÙŠ) Ø¥Ù„Ù‰ Ø£Ø­Ø¯ Ø§Ù„Ø£Ø±Ù‚Ø§Ù… Ø§Ù„ØªØ§Ù„ÙŠØ©:\n"
        f"â€¢ `16954304`\n"
        f"â€¢ `81827789`\n\n"
        f"Ø¨Ø¹Ø¯ Ø§Ù„ØªØ­ÙˆÙŠÙ„ØŒ Ø£Ø±Ø³Ù„ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ©:"
    )
    bot.edit_message_text(payment_text, chat_id=user_id, message_id=call.message.message_id)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

def get_transaction_number(message):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "ðŸš« Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹.")
        return

    if not message.text.isdigit():
        bot.send_message(user_id, "âš ï¸ Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ© Ø¨Ø´ÙƒÙ„ Ø±Ù‚Ù…ÙŠ ÙÙ‚Ø·.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_transaction_number)

    transaction_number = message.text
    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id][transaction_number] = {
        "transaction_number": transaction_number,
        "step": "transaction_number",
        "game": user_data[user_id].get("game"),
        "amount": user_data[user_id].get("amount")
    }
    bot.send_message(user_id, "ðŸ“ž Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ Ø§Ù„Ø±Ù‚Ù… Ø§Ù„Ø°ÙŠ Ù‚Ù…Øª Ø¨Ø§Ù„ØªØ­ÙˆÙŠÙ„ Ø¹Ù„ÙŠÙ‡ (`16954304` Ø£Ùˆ `81827789`):")
    bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_target_number(msg, transaction_number))

def get_target_number(message, transaction_number):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "ðŸš« Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹.")
        return

    if message.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "âš ï¸ Ø§Ù„Ø±Ù‚Ù… ØºÙŠØ± ØµØ­ÙŠØ­ØŒ Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ Ø£Ø­Ø¯ Ø§Ù„Ø±Ù‚Ù…ÙŠÙ† ÙÙ‚Ø·.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_target_number(msg, transaction_number))

    user_data[user_id][transaction_number]["target_number"] = message.text
    user_data[user_id][transaction_number]["step"] = "target_number"
    bot.send_message(user_id, "ðŸŽ® Ø£Ø±Ø³Ù„ Ø§Ù„Ø¢Ù† ID Ø­Ø³Ø§Ø¨Ùƒ Ø¯Ø§Ø®Ù„ Ø§Ù„Ù„Ø¹Ø¨Ø©:")
    bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_game_id(msg, transaction_number))

def get_game_id(message, transaction_number):
    user_id = message.from_user.id
    if not BOT_ACTIVE:
        bot.send_message(user_id, "ðŸš« Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹.")
        return

    if not message.text.isdigit():
        bot.send_message(user_id, "âš ï¸ Ø§Ù„Ø±Ø¬Ø§Ø¡ Ø¥Ø¯Ø®Ø§Ù„ ID Ø§Ù„Ù„Ø¹Ø¨Ø© Ø¨Ø´ÙƒÙ„ Ø±Ù‚Ù…ÙŠ ÙÙ‚Ø·.")
        return bot.register_next_step_handler_by_chat_id(user_id, lambda msg: get_game_id(msg, transaction_number))

    data = user_data[user_id][transaction_number]
    data['game_id'] = message.text
    data["step"] = "game_id"

    final_message = (
        f"ðŸ†• Ø·Ù„Ø¨ Ø´Ø­Ù† Ø¬Ø¯ÙŠØ¯:\n"
        f"ðŸ‘¤ Ø§Ù„Ù…Ø³ØªØ®Ø¯Ù…: @{message.from_user.username or 'Ø¨Ø¯ÙˆÙ† ÙŠÙˆØ²Ø±'}\n"
        f"ðŸ†” ØªÙŠÙ„ÙŠØ¬Ø±Ø§Ù…: {user_id}\n"
        f"ðŸŽ® ID Ø§Ù„Ù„Ø¹Ø¨Ø©: {data['game_id']}\n"
        f"ðŸŽ¯ Ø§Ù„ÙƒÙ…ÙŠØ©: {data['amount']} {data['game']}\n"
        f"ðŸ“ž Ø§Ù„Ø±Ù‚Ù… Ø§Ù„Ù…Ø­ÙˆÙ‘Ù„ Ø¹Ù„ÙŠÙ‡: {data['target_number']}\n"
        f"ðŸ”¢ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ©: {transaction_number}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("âœ… ØªÙ…Øª Ø§Ù„Ø¹Ù…Ù„ÙŠØ©", callback_data=f"confirm_{user_id}_{transaction_number}"),
        types.InlineKeyboardButton("âŒ ÙØ´Ù„Øª Ø§Ù„Ø¹Ù…Ù„ÙŠØ©", callback_data=f"fail_{user_id}_{transaction_number}")
    )

    bot.send_message(ADMIN_ID, final_message, reply_markup=markup)
    bot.send_message(user_id, "âœ… ØªÙ… Ø§Ø³ØªÙ„Ø§Ù… Ù…Ø¹Ù„ÙˆÙ…Ø§ØªÙƒ Ø¨Ù†Ø¬Ø§Ø­! Ø³ÙŠØªÙ… ØªÙ†ÙÙŠØ° Ø·Ù„Ø¨Ùƒ Ù‚Ø±ÙŠØ¨Ù‹Ø§ ðŸ’š")

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return
    _, user_id, transaction_number = call.data.split("_")
    user_id = int(user_id)

    data = user_data.get(user_id, {}).get(transaction_number)
    if not data:
        bot.send_message(ADMIN_ID, "âŒ Ù„Ù… ÙŠØªÙ… Ø§Ù„Ø¹Ø«ÙˆØ± Ø¹Ù„Ù‰ Ø¨ÙŠØ§Ù†Ø§Øª Ø§Ù„Ø·Ù„Ø¨.")
        return

    unit = "UC" if data["game"] == "pubg" else "ðŸ’Ž"
    confirm_msg = f"ØªÙ… Ø´Ø­Ù† Ø­Ø³Ø§Ø¨Ùƒ Ø¨Ù€ {data['amount']} {unit} Ø¹Ù„Ù‰ Ø§Ù„Ù€ ID Ø§Ù„ØªØ§Ù„ÙŠ: ðŸ“±{data['game_id']} Ø¨Ù†Ø¬Ø§Ø­ âœ…  Ø´ÙƒØ±Ø§ Ù„ØªØ¹Ø§Ù…Ù„Ùƒ Ù…Ø¹Ù†Ø§ ðŸŒŸ"
    bot.send_message(user_id, confirm_msg)
    bot.send_message(ADMIN_ID, f"ðŸ“¦ ØªÙ… Ø§Ù„Ø´Ø­Ù† Ø¥Ù„Ù‰ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ©: {transaction_number}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail_"))
def fail_delivery(call):
    if call.from_user.id != ADMIN_ID:
        return

    _, user_id, transaction_number = call.data.split("_")
    user_id = int(user_id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("â–¶ï¸ Ù„Ø¥Ø¹Ø§Ø¯Ø© Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø© Ø§Ø¶ØºØ· start", callback_data='retry'))
    fail_text = "âŒ ÙØ´Ù„Øª Ø§Ù„Ø¹Ù…Ù„ÙŠØ©\nÙŠØ±Ø¬Ù‰ Ø§Ù„ØªØ£ÙƒØ¯ Ù…Ù† ØµØ­Ø© Ø§Ù„Ù…Ø¹Ù„ÙˆÙ…Ø§ØªØŒ Ø«Ù… Ø§Ø¶ØºØ· /start Ù„Ø¥Ø¹Ø§Ø¯Ø© Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø©."
    bot.send_message(user_id, fail_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'retry')
def retry_order(call):
    if not BOT_ACTIVE:
        bot.edit_message_text("âŒ Ø§Ù„Ø¨ÙˆØª Ù…ØªÙˆÙ‚Ù Ø­Ø§Ù„ÙŠØ§Ù‹ØŒ Ù„Ø§ ÙŠÙ…ÙƒÙ† Ø¥ØªÙ…Ø§Ù… Ø§Ù„Ø·Ù„Ø¨ Ø§Ù„Ø¢Ù†. ÙŠØ±Ø¬Ù‰ Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø© Ù„Ø§Ø­Ù‚Ø§Ù‹.",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        return
    clear_user_data(call.from_user.id)
    send_welcome(call.message)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def filter_spam_messages(message):
    if not BOT_ACTIVE:
        return
    spam_keywords = ["http", "https", "www", "t.me", ".com", ".me", "â‚¹", "free", "click", "promo", "join", "channel", "offer", "mil jayga"]
    if any(word in message.text.lower() for word in spam_keywords):
        bot.reply_to(message, "ðŸš« ÙŠÙ…Ù†Ø¹ Ø¥Ø±Ø³Ø§Ù„ Ø§Ù„Ø±ÙˆØ§Ø¨Ø· Ø£Ùˆ Ø§Ù„Ø±Ø³Ø§Ø¦Ù„ Ø§Ù„Ø¯Ø¹Ø§Ø¦ÙŠØ© Ø¯Ø§Ø®Ù„ Ø§Ù„Ø¨ÙˆØª.")
        return
    if isinstance(user_data.get(message.from_user.id), dict) and "step" in user_data[message.from_user.id]:
        if user_data[message.from_user.id]["step"] not in ["transaction_number", "target_number", "game_id"]:
            bot.reply_to(message, "â— ÙŠØ±Ø¬Ù‰ Ø§Ø³ØªØ®Ø¯Ø§Ù… Ø§Ù„Ø£Ø²Ø±Ø§Ø± ÙÙ‚Ø· Ù„Ù„ØªØ¹Ø§Ù…Ù„ Ù…Ø¹ Ø§Ù„Ø¨ÙˆØª.")
        return

bot.infinity_polling()