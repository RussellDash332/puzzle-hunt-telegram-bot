from cmd_base import Puzzle, get_options_keyboard, save_user_progress, send_description, DATA_DIR
from json import loads, dumps
from os import path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from dpad_manager import read_dp

CHOOSE_PUZZLE, CHOOSE_OPTION, CHECK_ANSWER, CHOOSE_VOID, CHOOSE_HINT, CHOOSE_CONTINUE_OPTION = range(6)

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

    # We need to check whether the selected puzzle is the final puzzle
    user_data_str = read_dp(str(user_id))

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
        user_voids = loads(user_data_str)['voids']
    else:
        user_progress = list()
        user_voids = list()

    bot = context.bot

    if not puzzles[puzzle_idx].is_final or len(user_progress) + len(user_voids) >= len(puzzles) - 1:
        context.user_data['cur_puzzle_idx'] = puzzle_idx
        context.user_data['score'] = puzzles[puzzle_idx].score
        context.user_data['username'] = update.effective_user.username
        context.user_data['is_voided'] = puzzles[puzzle_idx].is_voided

        name = puzzles[puzzle_idx].name
        description = puzzles[puzzle_idx].description
        is_completed = puzzles[puzzle_idx].is_completed
        is_voided = puzzles[puzzle_idx].is_voided

        bot.delete_message(chat_id=user_id, message_id=query.message.message_id)

        keyboard = [
            [
                InlineKeyboardButton(text='Try this puzzle 🧩', callback_data='try'),
                InlineKeyboardButton(text='Back to puzzles\' list 📃', callback_data='back')
            ],
            [
                InlineKeyboardButton(text='Void this puzzle ❌', callback_data='ask_void'),
                InlineKeyboardButton(text='Ask for hint ❓', callback_data='ask_hint')
            ],
            [
                InlineKeyboardButton(text='Done ✔️', callback_data='done')
            ]
        ]

        txt = [f'Showing "{name}".']
        # Update response for completed puzzle
        if is_completed or is_voided:
            first_answer = puzzles[puzzle_idx].answers[0]

            if is_completed:
                txt.append(f'\nYou already completed this puzzle! The answer was "{first_answer}".')
            elif is_voided:
                txt.append(f'\nYou already voided this puzzle!')
                # txt.append(f' You already voided this puzzle! No way back, but the answer was "{first_answer}".\n')

            keyboard = [[keyboard[0][1],keyboard[2][0]]] # only back and done

        reply_markup = InlineKeyboardMarkup(keyboard)

        context.user_data['last_description'] = send_description(description, user_id, bot)
        query.message.reply_text(text=''.join(txt), reply_markup=reply_markup)

        return CHOOSE_OPTION
    else:
        reply_markup = get_options_keyboard(context.chat_data, user_id)
        try:
            query.edit_message_text('Final puzzle still locked! Choose another puzzle to view...', reply_markup=reply_markup)
        except:
            pass # unmodified message

        return CHOOSE_PUZZLE

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

def ask_void(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text('If you really want to void this puzzle, type "confirm". Otherwise, type "back".')

    return CHOOSE_VOID

def void(update, context):
    user_id = update.effective_user.id
    puzzles = context.chat_data[user_id]
    puzzle_idx = context.user_data['cur_puzzle_idx']
    user_answer = update.message.text

    if user_answer == "confirm" or user_answer == "Confirm":
        context.user_data['is_voided'] = True
        puzzles[puzzle_idx].is_voided = True
        puzzles[puzzle_idx].set_void_title()

        reply_markup = get_options_keyboard(context.chat_data, user_id)
        update.message.reply_text('You have just voided the puzzle! Now choose a puzzle to view ...', reply_markup=reply_markup)
        save_user_progress(str(user_id), context)
        return CHOOSE_PUZZLE
    elif user_answer == "back" or user_answer == "Back":
        reply_markup = get_options_keyboard(context.chat_data, user_id)
        update.message.reply_text('You have canceled to void the puzzle! Now choose a puzzle to view ...', reply_markup=reply_markup)
        return CHOOSE_PUZZLE
    else:
        return CHOOSE_VOID

def ask_hint(update, context):
    query = update.callback_query
    query.answer()

    query.edit_message_text('If you really want to ask for a hint, type "confirm". Otherwise, type "back".\n\nWARNING: Asking for a hint will decrease the maximum point from this puzzle by 1!')

    return CHOOSE_HINT

def hint(update, context):
    user_id = update.effective_user.id
    puzzles = context.chat_data[user_id]
    puzzle_idx = context.user_data['cur_puzzle_idx']
    puzzle_hints = puzzles[puzzle_idx].hints
    user_answer = update.message.text

    if user_answer == "confirm" or user_answer == "Confirm":
        if puzzles[puzzle_idx].used_hints < len(puzzle_hints):
            update.message.reply_text(f'Hint #{puzzles[puzzle_idx].used_hints+1} for "{puzzles[puzzle_idx].name}"\n\n{puzzle_hints[puzzles[puzzle_idx].used_hints]}')
            
            puzzles[puzzle_idx].used_hints += 1
            puzzles[puzzle_idx].set_new_score()

            reply_markup = get_options_keyboard(context.chat_data, user_id)
            update.message.reply_text('That was a hint for the puzzle! Now choose a puzzle to view again ...', reply_markup=reply_markup)
            return CHOOSE_PUZZLE
        else:
            reply_markup = get_options_keyboard(context.chat_data, user_id)
            update.message.reply_text('You have no more available hints for the puzzle! Now choose a puzzle to view again ...', reply_markup=reply_markup)
            return CHOOSE_PUZZLE
    elif user_answer == "back" or user_answer == "Back":
        reply_markup = get_options_keyboard(context.chat_data, user_id)
        update.message.reply_text('You have canceled to ask a hint for the puzzle! Now choose a puzzle to view ...', reply_markup=reply_markup)
        return CHOOSE_PUZZLE
    else:
        return CHOOSE_HINT

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
    user_name = context.user_data['username']

    right_answers = puzzles[puzzle_idx].answers
    user_answer = update.message.text

    keyboard = [
        [
            InlineKeyboardButton(text='Back to puzzles\' list 📃', callback_data='back'),
            InlineKeyboardButton(text='Done ✔️', callback_data='done')
        ]
    ]

    if user_answer in right_answers:
        # Simply to display current score and number of solved puzzles
        user_data_str = read_dp(str(user_id))
        if user_data_str:
            user_progress = loads(user_data_str)['progress']
            user_voids = loads(user_data_str)['voids']
            user_score = loads(user_data_str)['score']
        else:
            user_progress = list()
            user_voids = list()
            user_score = 0
        if len(user_progress) + len(user_voids) == len(puzzles) - 1:
            result = f'Right answer! Congratulations @{user_name}! You have completed the whole puzzle! Your final score is {int(user_score) + puzzles[puzzle_idx].score}!'
        elif len(user_progress) + len(user_voids) == len(puzzles) - 2:
            result = f'Right answer! Congratulations @{user_name}! You have unlocked the final puzzle! Your score is currently {int(user_score) + puzzles[puzzle_idx].score}!'
        elif user_progress:
            result = f'Right answer! Congratulations @{user_name}! You have solved {len(user_progress) + 1} puzzles and your score is now {int(user_score) + puzzles[puzzle_idx].score}!'
        else:
            result = f'Right answer! Congratulations @{user_name}! You have solved 1 puzzle and your score is now {int(user_score) + puzzles[puzzle_idx].score}!'
        
        puzzles[puzzle_idx].is_completed = True
        puzzles[puzzle_idx].set_completed_title()
        save_user_progress(str(user_id), context)
    else:
        keyboard = [
            [
                InlineKeyboardButton(text='Try again 🔄', callback_data='try_again')
            ],
            [
                InlineKeyboardButton(text='Void this puzzle ❌', callback_data='ask_void'),
                InlineKeyboardButton(text='Ask for hint ❓', callback_data='ask_hint')
            ]
        ] + keyboard
        result = 'Sorry, wrong answer! Want to try again? Or void the puzzle?'

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

    query.edit_message_text('Bye, see you later! Feel free to come back and type /puzzles 😊')
    return ConversationHandler.END

puzzles_menu = ConversationHandler(
    entry_points=[CommandHandler('puzzles', show_puzzles_menu)],
    states={
        CHOOSE_PUZZLE: [
            CallbackQueryHandler(choose_puzzle)
        ],
        CHOOSE_OPTION: [
            CallbackQueryHandler(return_to_puzzles_menu, pattern='^back$'),
            CallbackQueryHandler(answer_puzzle, pattern='^try$'),
            CallbackQueryHandler(ask_void, pattern='^ask_void$'),
            CallbackQueryHandler(ask_hint, pattern='^ask_hint$')
        ],
        CHECK_ANSWER: [
            MessageHandler(~Filters.regex('^/'), check_answer)
        ],
        CHOOSE_VOID: [
            MessageHandler(~Filters.regex('^/'), void)
        ],
        CHOOSE_HINT: [
            MessageHandler(~Filters.regex('^/'), hint)
        ],
        CHOOSE_CONTINUE_OPTION: [
            CallbackQueryHandler(try_again, pattern='^try_again$'),
            CallbackQueryHandler(ask_void, pattern='^ask_void$'),
            CallbackQueryHandler(return_to_puzzles_menu, pattern='^back$'),
            CallbackQueryHandler(ask_hint, pattern='^ask_hint$')
        ]
    },
    fallbacks=[CallbackQueryHandler(leave_puzzles_menu, pattern='^done$')]
)