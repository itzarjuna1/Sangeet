# tictactoe.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from collections import defaultdict

# =======================
# Game and leaderboard storage
# =======================
games = {}  # {chat_id: game_data}
leaderboard = defaultdict(lambda: defaultdict(int))  # {chat_id: {user_id: wins}}

# =======================
# Helper functions
# =======================
def render_board(board):
    """Render the board as emoji"""
    symbols = {"X": "❌", "O": "⭕", "": "⬜"}
    return "\n".join("".join(symbols[cell] for cell in row) for row in board)

def check_winner(board):
    """Check if there's a winner"""
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != "":
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    return None

def build_keyboard(board):
    """Build inline keyboard for the board"""
    buttons = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = board[i][j]
            text = " " if cell == "" else cell
            row.append(InlineKeyboardButton(text=text, callback_data=f"{i}:{j}"))
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

# =======================
# Start Tic Tac Toe
# =======================
@Client.on_message(filters.command("tictactoe") & filters.group)
async def start_game(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id in games:
        return await message.reply_text("A Tic Tac Toe game is already running! Click ✅ Join Game to play.")

    games[chat_id] = {
        "board": [["" for _ in range(3)] for _ in range(3)],
        "players": [],
        "turn": 0,
        "started": False
    }

    join_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Join Game", callback_data="ttt_join")]]
    )

    await message.reply_text(
        "Tic Tac Toe started! Click ✅ Join Game to participate (2 players required).",
        reply_markup=join_button
    )

# =======================
# Handle button clicks
# =======================
@Client.on_callback_query()
async def tictactoe_buttons(client: Client, callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    game = games.get(chat_id)

    if not game:
        return await callback_query.answer("No game in progress.", show_alert=True)

    user = callback_query.from_user

    # ===== Join Game =====
    if callback_query.data == "ttt_join":
        if user.id in [p.id for p in game["players"]]:
            return await callback_query.answer("You already joined!", show_alert=True)
        if len(game["players"]) >= 2:
            return await callback_query.answer("Game already has 2 players!", show_alert=True)

        game["players"].append(user)
        if len(game["players"]) < 2:
            await callback_query.answer(f"{user.mention} joined! Waiting for another player...")
            await callback_query.message.edit_text(
                f"Tic Tac Toe waiting for players...\n"
                f"{len(game['players'])}/2 joined.",
                reply_markup=callback_query.message.reply_markup
            )
            return
        else:
            game["started"] = True
            board_text = render_board(game["board"])
            await callback_query.message.edit_text(
                f"Game started!\n"
                f"{game['players'][0].mention} (❌) vs {game['players'][1].mention} (⭕)\n"
                f"Turn: {game['players'][0].mention} (❌)\n\n{board_text}",
                reply_markup=build_keyboard(game["board"])
            )
            return await callback_query.answer("Game started!")

    # ===== Play Game =====
    if ":" in callback_query.data and game["started"]:
        i, j = map(int, callback_query.data.split(":"))
        board = game["board"]
        players = game["players"]
        turn = game["turn"]
        current_player = players[turn]

        if user.id != current_player.id:
            return await callback_query.answer("Not your turn!", show_alert=True)
        if board[i][j] != "":
            return await callback_query.answer("Cell already taken!", show_alert=True)

        board[i][j] = "X" if turn == 0 else "O"

        winner_symbol = check_winner(board)
        if winner_symbol:
            winner = current_player
            leaderboard[chat_id][winner.id] += 1
            await callback_query.message.edit_text(
                f"🏆 Game Over! {winner.mention} ({winner_symbol}) won!\n\n{render_board(board)}",
                reply_markup=None
            )
            del games[chat_id]
            return

        if all(cell != "" for row in board for cell in row):
            await callback_query.message.edit_text(
                f"🤝 Game Over! It's a draw!\n\n{render_board(board)}",
                reply_markup=None
            )
            del games[chat_id]
            return

        # Switch turn
        game["turn"] = 1 - turn
        next_player = players[game["turn"]]

        await callback_query.message.edit_text(
            f"Turn: {next_player.mention} ({'❌' if game['turn']==0 else '⭕'})\n\n{render_board(board)}",
            reply_markup=build_keyboard(board["board"])
        )
        await callback_query.answer()

# =======================
# Leaderboard command
# =======================
@Client.on_message(filters.command("ticlead") & filters.group)
async def show_leaderboard(client: Client, message: Message):
    chat_id = message.chat.id
    if chat_id not in leaderboard or not leaderboard[chat_id]:
        return await message.reply_text("No games played yet!")

    sorted_board = sorted(leaderboard[chat_id].items(), key=lambda x: x[1], reverse=True)
    text = "🏆 Tic Tac Toe Leaderboard 🏆\n\n"
    for idx, (user_id, wins) in enumerate(sorted_board[:10], 1):  # top 10
        text += f"{idx}. [User](tg://user?id={user_id}) - {wins} wins\n"

    await message.reply_text(text, disable_web_page_preview=True)
