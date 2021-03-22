from puzzles_menu import puzzles_menu
from env import TOKEN
from os import path
from telegram.ext import Updater, CommandHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def start(update, context):
    welcome_txt = [
        'Welcome to the MSOC 2021 Puzzle Hunt!',
        'There are currently 4 puzzles and we can\'t wait to see you solving these puzzles!',
        'Now type /puzzles to look at the list of puzzles to solve.',
        ]

    update.message.reply_text('\n\n'.join(welcome_txt))

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(puzzles_menu)

    updater.start_polling()
    print("++++++++++ STARTING BOT +++++++++++")
    updater.idle()
    print("++++++++++  KILLING BOT  ++++++++++")


if __name__ == '__main__':
    print("Press CTRL + C to kill the bot")
    main()