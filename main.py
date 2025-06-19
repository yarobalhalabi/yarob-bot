
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
    markup.add(types.InlineKeyboardButton("ðŸ“± PUBG", callback_data="game_pubg"))
    markup.add(types.InlineKeyboardButton("ðŸŽ® Free Fire", callback_data="game_freefire"))
    bot.send_message(user_id, "ðŸ‘‹ Ø£Ù‡Ù„Ø§Ù‹ Ø¨Ùƒ ÙÙŠ Ù…ØªØ¬Ø± YAROB Ù„Ø´Ø­Ù† Ø§Ù„Ø£Ù„Ø¹Ø§Ø¨!
Ø§Ø®ØªØ± Ø§Ù„Ù„Ø¹Ø¨Ø©:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("game_"))
def game_selection(call):
    user_id = call.message.chat.id
    game = call.data.split("_")[1]
    user_data[user_id] = {"game": game, "step": "amount"}
    prices = prices_pubg if game == "pubg" else prices_freefire
    label = "UC" if game == "pubg" else "ðŸ’Ž"
    markup = types.InlineKeyboardMarkup()
    for k, v in prices.items():
        markup.add(types.InlineKeyboardButton(f"{k} {label} - {v} Ù„.Ø³", callback_data=f"amount_{k}"))
    markup.add(types.InlineKeyboardButton("âŒ Ø¥Ù„ØºØ§Ø¡ Ø§Ù„Ø·Ù„Ø¨", callback_data="cancel"))
    bot.edit_message_text("ðŸŽ Ø§Ø®ØªØ± Ø§Ù„Ø¨Ø§Ù‚Ø©:", user_id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("amount_"))
def amount_selection(call):
    user_id = call.message.chat.id
    amount = call.data.split("_")[1]
    user_data[user_id]["amount"] = amount
    user_data[user_id]["step"] = "transaction"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ðŸ”™ Ø±Ø¬ÙˆØ¹", callback_data="back_amount"))
    markup.add(types.InlineKeyboardButton("âŒ Ø¥Ù„ØºØ§Ø¡ Ø§Ù„Ø·Ù„Ø¨", callback_data="cancel"))
    bot.edit_message_text("ðŸ’° Ø£Ø±Ø³Ù„ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ© (Ø£Ø±Ù‚Ø§Ù… ÙÙ‚Ø·):", user_id, call.message.message_id, reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(user_id, get_transaction)

def get_transaction(msg):
    user_id = msg.chat.id
    if not msg.text.isdigit():
        bot.send_message(user_id, "â— Ø£Ø±Ø³Ù„ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ© Ø£Ø±Ù‚Ø§Ù… ÙÙ‚Ø·.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_transaction)
    user_data[user_id]["transaction"] = msg.text
    user_data[user_id]["step"] = "target"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ðŸ”™ Ø±Ø¬ÙˆØ¹", callback_data="back_transaction"))
    markup.add(types.InlineKeyboardButton("âŒ Ø¥Ù„ØºØ§Ø¡ Ø§Ù„Ø·Ù„Ø¨", callback_data="cancel"))
    bot.send_message(user_id, "ðŸ“ž Ø£Ø¯Ø®Ù„ Ø§Ù„Ø±Ù‚Ù… Ø§Ù„Ø°ÙŠ Ø­ÙˆÙ‘Ù„Øª Ø¹Ù„ÙŠÙ‡ (16954304 Ø£Ùˆ 81827789):", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(user_id, get_target)

def get_target(msg):
    user_id = msg.chat.id
    if msg.text not in ["16954304", "81827789"]:
        bot.send_message(user_id, "âš ï¸ Ø§Ù„Ø±Ù‚Ù… ØºÙŠØ± ØµØ­ÙŠØ­ØŒ Ø­Ø§ÙˆÙ„ Ù…Ø±Ø© Ø£Ø®Ø±Ù‰.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_target)
    user_data[user_id]["target"] = msg.text
    user_data[user_id]["step"] = "id"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ðŸ”™ Ø±Ø¬ÙˆØ¹", callback_data="back_target"))
    markup.add(types.InlineKeyboardButton("âŒ Ø¥Ù„ØºØ§Ø¡ Ø§Ù„Ø·Ù„Ø¨", callback_data="cancel"))
    bot.send_message(user_id, "ðŸŽ® Ø£Ø±Ø³Ù„ ID Ø§Ù„Ù„Ø¹Ø¨Ø©:", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(user_id, get_gameid)

def get_gameid(msg):
    user_id = msg.chat.id
    if not msg.text.isdigit():
        bot.send_message(user_id, "â— ID Ø§Ù„Ù„Ø¹Ø¨Ø© ÙŠØ¬Ø¨ Ø£Ù† ÙŠÙƒÙˆÙ† Ø±Ù‚Ù…Ø§Ù‹.")
        return bot.register_next_step_handler_by_chat_id(user_id, get_gameid)
    data = user_data[user_id]
    text = f"ðŸ†• Ø·Ù„Ø¨ Ø´Ø­Ù†:
User: @{msg.from_user.username or 'Ù„Ø§ ÙŠÙˆØ¬Ø¯'}
Game: {data['game']}
Amount: {data['amount']}
Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ©: {data['transaction']}
Ø­ÙˆÙ‘Ù„ Ø¹Ù„Ù‰: {data['target']}
ID Ø§Ù„Ù„Ø¹Ø¨Ø©: {msg.text}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("âœ… ØªÙ…Øª", callback_data=f"confirm_{user_id}"))
    markup.add(types.InlineKeyboardButton("âŒ ÙØ´Ù„Øª", callback_data=f"fail_{user_id}"))
    bot.send_message(ADMIN_ID, text, reply_markup=markup)
    bot.send_message(user_id, "âœ… ØªÙ… Ø§Ø³ØªÙ„Ø§Ù… Ø§Ù„Ø·Ù„Ø¨ØŒ Ø³ÙŠØªÙ… Ø§Ù„ØªÙ†ÙÙŠØ° Ù‚Ø±ÙŠØ¨Ø§Ù‹ ðŸ’š")

@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel(call):
    user_id = call.message.chat.id
    clear_user(user_id)
    bot.send_message(user_id, "âŒ ØªÙ… Ø¥Ù„ØºØ§Ø¡ Ø§Ù„Ø·Ù„Ø¨.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("back_"))
def go_back(call):
    user_id = call.message.chat.id
    step = call.data.split("_")[1]
    if step == "amount":
        game_selection(call)
    elif step == "transaction":
        amount_selection(call)
    elif step == "target":
        bot.send_message(user_id, "ðŸ’° Ø£Ø±Ø³Ù„ Ø±Ù‚Ù… Ø§Ù„Ø¹Ù…Ù„ÙŠØ© Ù…Ù† Ø¬Ø¯ÙŠØ¯:")
        bot.register_next_step_handler_by_chat_id(user_id, get_transaction)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "âœ… ØªÙ… ØªÙ†ÙÙŠØ° Ø§Ù„Ø´Ø­Ù† Ø¨Ù†Ø¬Ø§Ø­ØŒ Ø´ÙƒØ±Ù‹Ø§ Ù„Ùƒ ðŸŒŸ")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fail_"))
def fail(call):
    user_id = int(call.data.split("_")[1])
    bot.send_message(user_id, "âŒ ÙØ´Ù„Øª Ø§Ù„Ø¹Ù…Ù„ÙŠØ©. ØªØ­Ù‚Ù‚ Ù…Ù† Ø§Ù„Ø¨ÙŠØ§Ù†Ø§Øª ÙˆØ£Ø¹Ø¯ Ø§Ù„Ù…Ø­Ø§ÙˆÙ„Ø© Ø¨Ø¥Ø±Ø³Ø§Ù„ /start")

bot.infinity_polling()