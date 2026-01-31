# rps.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from collections import defaultdict
import random

# =========================
# Storage
# =========================
games = {}  # {chat_id: {player_id: choice}}
leaderboards = defaultdict(lambda: defaultdict(int))  # leaderboards[chat_id][user_id] = wins
PREFIXES = ["/", ".", "!"]

OPTIONS = ["Rock", "Paper", "Scissors"]

# =========================
# Start RPS
# =========================
@Client.on_message(filters.command("rps", prefixes=PREFIXES) & filters.group)
async def start_rps(client: Client, message: Message):
    chat_id = message.chat.id
    text = "🪨📄✂️ **Rock Paper Scissors**!\nClick a button to play:"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(opt, callback_data=f"rps_play:{opt}")] for opt in OPTIONS]
    )
    await message.reply_text(text, reply_markup=keyboard)

# =========================
# Handle choices
# =========================
@Client.on_callback_query()
async def rps_callbacks(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    data = callback_query.data

    if not data.startswith("rps_play:"):
        return

    user_choice = data.split(":")[1]
    bot_choice = random.choice(OPTIONS)

    result = ""
    if user_choice == bot_choice:
        result = "🤝 It's a draw!"
    elif (user_choice == "Rock" and bot_choice == "Scissors") or \
         (user_choice == "Paper" and bot_choice == "Rock") or \
         (user_choice == "Scissors" and bot_choice == "Paper"):
        result = "🎉 You win!"
        leaderboards[chat_id][user.id] += 1
    else:
        result = "😢 You lose!"

    await callback_query.message.edit_text(
        f"{user.mention} chose **{user_choice}**\nBot chose **{bot_choice}**\n\n{result}"
    )
    await callback_query.answer()

# =========================
# Leaderboard
# =========================
@Client.on_message(filters.command("rpslead", prefixes=PREFIXES) & filters.group)
async def rps_leaderboard(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in leaderboards or not leaderboards[chat_id]:
        return await message.reply_text("No RPS games played yet!")

    text = "🏆 **Rock Paper Scissors Leaderboard** 🏆\n\n"
    sorted_players = sorted(leaderboards[chat_id].items(), key=lambda x: x[1], reverse=True)
    for idx, (user_id, wins) in enumerate(sorted_players[:10], 1):
        text += f"{idx}. [User](tg://user?id={user_id}) - {wins} wins\n"
    await message.reply_text(text, disable_web_page_preview=True)
