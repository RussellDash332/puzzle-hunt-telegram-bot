from cmd_base import Puzzle, get_options_keyboard, save_user_progress, send_description, DATA_DIR
from json import loads, dumps
from os import path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

CHOOSE_PUZZLE, CHOOSE_OPTION, CHECK_ANSWER, CHOOSE_CONTINUE_OPTION = range(4)

def show_puzzles_menu(update, context):
    msg = update.message
    user_id = msg.from_user.id

    reply_markup = get_options_keyboard(context.chat_data, user_id)
    msg.reply_text('Choose a puzzle to view ...', reply_markup=reply_markup)

    return CHOOSE_PUZZLE

def choose_puzzle(update, context):
    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()

    puzzle_idx = query.data
    puzzles = context.chat_data[user_id]
    context.user_data['cur_puzzle_idx'] = puzzle_idx

    name = puzzles[puzzle_idx].name
    description = puzzles[puzzle_idx].description
    is_completed = puzzles[puzzle_idx].is_completed

    bot = context.bot
    bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

    keyboard = [
        [
            InlineKeyboardButton(text='Try this puzzle 🧩', callback_data='try'),
            InlineKeyboardButton(text='Back to puzzles\' list 📃', callback_data='back')
        ],
        [
            InlineKeyboardButton(text='Done ✔️', callback_data='done')
        ]
    ]

    txt = [f'Showing "{name}".']
    # Update response for completed puzzle
    if is_completed:
        first_answer = puzzles[puzzle_idx].answers[0]
        txt.append(f' You already completed this puzzle! The answer was "{first_answer}".\n')

        keyboard[0].pop(0)
        keyboard[0].append(keyboard[1][0])
        keyboard.pop(1)

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.user_data['last_description'] = send_description(description, user_id, bot)
    query.message.reply_text(text=''.join(txt), reply_markup=reply_markup)

    return CHOOSE_OPTION

def return_to_puzzles_menu(update, context):
    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()
    bot = context.bot

    try:
        last_description = context.user_data['last_description']
        bot.delete_message(chat_id=user_id, message_id=last_description.message_id)
    except:
        pass
    bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

    reply_markup = get_options_keyboard(context.chat_data, user_id)
    query.message.reply_text('Choose a puzzle to view...', reply_markup=reply_markup)

    return CHOOSE_PUZZLE

def answer_puzzle(update, context):
    query = update.callback_query
    user_id = update.effective_user.id

    query.answer()

    puzzle_idx = context.user_data['cur_puzzle_idx']
    puzzles = context.chat_data[user_id]

    name = puzzles[puzzle_idx].name
    query.edit_message_text(text=f'Trying "{name}", type the answer')

    return CHECK_ANSWER

def check_answer(update, context):
    user_id = update.message.from_user.id
    puzzles = context.chat_data[user_id]
    puzzle_idx = context.user_data['cur_puzzle_idx']

    right_answers = puzzles[puzzle_idx].answers
    user_answer = update.message.text.lower()

    keyboard = [
        [
            InlineKeyboardButton(text='Back to puzzles\' list 📃', callback_data='back'),
            InlineKeyboardButton(text='Done ✔️', callback_data='done')
        ]
    ]

    if user_answer in right_answers:
        result = 'Right answer! Congratulations!'
        puzzles[puzzle_idx].is_completed = True
        save_user_progress(str(user_id), context)
    else:
        keyboard.insert(0, [InlineKeyboardButton(text='Try again 🔄', callback_data='try_again')])
        result = 'Wrong answer, want to try again?'

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(result, reply_markup=reply_markup)

    return CHOOSE_CONTINUE_OPTION

def try_again(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text('Trying puzzle again, type the answer')

    return CHECK_ANSWER

def leave_puzzles_menu(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text('Bye, see you later!')
    return ConversationHandler.END

puzzles_menu = ConversationHandler(
    entry_points=[CommandHandler('puzzles', show_puzzles_menu)],
    states={
        CHOOSE_PUZZLE: [
            CallbackQueryHandler(choose_puzzle)
        ],
        CHOOSE_OPTION: [
            CallbackQueryHandler(return_to_puzzles_menu, pattern='^back$'),
            CallbackQueryHandler(answer_puzzle, pattern='^try$')
        ],
        CHECK_ANSWER: [
            MessageHandler(~Filters.regex('^/'), check_answer)
        ],
        CHOOSE_CONTINUE_OPTION: [
            CallbackQueryHandler(try_again, pattern='^try_again$'),
            CallbackQueryHandler(return_to_puzzles_menu, pattern='^back$')
        ]
    },
    fallbacks=[CallbackQueryHandler(leave_puzzles_menu, pattern='^done$')]
)