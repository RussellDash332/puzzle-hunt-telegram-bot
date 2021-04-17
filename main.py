from puzzles_menu import puzzles_menu
from env import TOKEN
from os import path
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from json import load, loads
from dpad_manager import read_dp

def start(update, context):
    welcome_txt = [
        'Welcome to the MSOC 2021 Puzzle Hunt!',
        'There are currently 6 puzzles and we can\'t wait to see you solving these puzzles!',
        'Do take note that the final puzzle is unlocked only when you have solved or voided all the remaining puzzles!',
        'Now type /puzzles to look at the list of puzzles to solve.'
        ]

    update.message.reply_text('\n\n'.join(welcome_txt))

def score(update, context):
    msg = update.message
    user_id = msg.from_user.id

    user_data_str = read_dp(str(user_id))

    if user_data_str:
        user_score = loads(user_data_str)['score']
    else:
        user_score = 0

    update.message.reply_text(f'Your current score is {user_score}.')

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("score", score))
    dp.add_handler(puzzles_menu)

    updater.start_polling()
    print("++++++++++ STARTING BOT +++++++++++")
    updater.idle()
    print("++++++++++  KILLING BOT  ++++++++++")


if __name__ == '__main__':
    print("Press CTRL + C to kill the bot")
    main()