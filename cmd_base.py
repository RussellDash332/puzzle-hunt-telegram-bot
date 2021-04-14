from os import path
from json import load, loads, dump, dumps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from dpad_manager import read_dp, write_dp

DATA_DIR = path.join('.', 'game_data')
DATA_PATH = path.join(DATA_DIR, 'game_data.json')
PROGRESS_PATH = path.join('.', 'users_progress', 'users_progress.json')

class Puzzle:
    def __init__(self, idx, name, description, score, answers):
        self.idx = idx
        self.name = name
        if score == 1:
            self.title = f'{idx} {name} ({score} point)'
        else:
            self.title = f'{idx} {name} ({score} points)'
        self.description = description
        self.answers = answers
        self.score = score
        self.is_completed = None
        self.is_voided = False

    def set_void_title(self):
        self.title = f'{self.idx} {self.name} (VOIDED)'

def set_progress(puzzles, user_id):
    user_data_str = read_dp(user_id)

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
        user_voids = loads(user_data_str)['voids']
        user_score = loads(user_data_str)['score']
    else:
        user_progress = list()
        user_voids = list()
        user_data_str = dumps({'progress': user_progress, 'voids': user_voids, 'score': '0'}, indent=2)
        write_dp(user_id, user_data_str)

    for idx, p in puzzles.items():
        if idx in user_progress:
            p.is_completed = True
        elif idx in user_voids:
            p.is_voided = True
            p.set_void_title()

def load_data_from_json(user_id):
    with open(DATA_PATH, 'r') as f:
        game_data = load(f)

    puzzles = dict()
    for p_idx, data in game_data.items():
        puzzle = Puzzle(data['idx'], data['name'], data['description'], data['score'], data['answers'])
        puzzles[p_idx] = puzzle

    set_progress(puzzles, str(user_id))
    return puzzles

def get_options_keyboard(data, user_id):
    if user_id not in data: data[user_id] = load_data_from_json(user_id)
    puzzles = data[user_id]

    titles = [f'{c.title} ✅' if c.is_completed else f'{c.title} 💀' if c.is_voided else c.title for c in puzzles.values()]
    keys = puzzles.keys()

    keyboard = [[InlineKeyboardButton(t, callback_data=k)] for t, k in zip(titles, keys)]
    return InlineKeyboardMarkup(keyboard)

def save_user_progress(user_id, context):
    user_data_str = read_dp(user_id)

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
        user_voids = loads(user_data_str)['voids']
        user_score = int(loads(user_data_str)['score'])
    else:
        user_progress = list()
        user_voids = list()
        user_score = 0

    puzzle = context.user_data

    if puzzle['is_voided']:
        user_voids.append(puzzle['cur_puzzle_idx'])
    else:
        user_progress.append(puzzle['cur_puzzle_idx'])
        user_score += puzzle['score']
    user_name = puzzle['username']
    user_data_str = dumps({'username': user_name, 'progress': user_progress, 'voids': user_voids, 'score': str(user_score)}, indent=2)
    write_dp(user_id, user_data_str)

def send_description(description, chat_id, bot):
    for d_filename in description:
        d_filename = path.join(DATA_DIR, d_filename)

        if d_filename.endswith('.jpg') or d_filename.endswith('.png'):
            d_photo = open(d_filename, 'rb')
            bot_message = bot.send_photo(
                chat_id=chat_id,
                photo=d_photo
            )
        elif d_filename.endswith('.txt'):
            d_txt = open(d_filename).read()
            bot_message = bot.send_message(
                chat_id=chat_id,
                text=f'<code>{d_txt}</code>',
                parse_mode='HTML'
            )

    return bot_message