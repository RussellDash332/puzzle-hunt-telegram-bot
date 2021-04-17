import time
from os import path
from json import load, loads, dump, dumps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from env import GIVEN_HINTS, HINT_POINTS
from dpad_manager import read_dp, write_dp

DATA_DIR = path.join('.', 'game_data')
DATA_PATH = path.join(DATA_DIR, 'game_data.json')
PROGRESS_PATH = path.join('.', 'users_progress', 'users_progress.json')

class Puzzle:
    def __init__(self, idx, name, description, score, answers, hints):
        self.idx = idx
        self.name = name
        if score == 1:
            self.title = f'{idx} {name} ({score} point)'
        else:
            self.title = f'{idx} {name} ({score} points)'
        self.description = description
        self.answers = answers
        self.original_score = score
        self.score = score
        self.hints = hints
        self.used_hints = 0
        self.is_completed = None
        self.is_voided = False
        self.is_final = self.idx == "[FINAL]"

    def set_completed_title(self):
        self.title = f'{self.idx} {self.name} (COMPLETED)'

    def set_void_title(self):
        self.title = f'{self.idx} {self.name} (VOIDED)'

def set_progress(puzzles, user_id):
    user_data_str = read_dp(user_id)

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
        user_voids = loads(user_data_str)['voids']
        user_solved_time = loads(user_data_str)['solved_time']
        user_score = loads(user_data_str)['score']
        user_hints = loads(user_data_str)['hints']
    else:
        user_progress = list()
        user_voids = list()
        user_solved_time = list()
        user_hints = dict()
        user_data_str = dumps({'progress': user_progress, 'voids': user_voids, 'solved_time': user_solved_time, 'score': '0', 'hints': user_hints}, indent=2)
        write_dp(user_id, user_data_str)

    for idx, p in puzzles.items():
        if idx in user_progress:
            p.is_completed = True
            p.set_completed_title()
        elif idx in user_voids:
            p.is_voided = True
            p.set_void_title()

def load_data_from_json(user_id):
    with open(DATA_PATH, 'r') as f:
        game_data = load(f)

    puzzles = dict()
    for p_idx, data in game_data.items():
        puzzle = Puzzle(data['idx'], data['name'], data['description'], data['score'], data['answers'], data['hints'])
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

def save_user_progress(user_id, context, for_hint):
    user_data_str = read_dp(user_id)

    if user_data_str:
        user_progress = loads(user_data_str)['progress']
        user_voids = loads(user_data_str)['voids']
        user_solved_time = loads(user_data_str)['solved_time']
        user_score = int(loads(user_data_str)['score'])
        user_hints = loads(user_data_str)['hints']
    else:
        user_progress = list()
        user_voids = list()
        user_solved_time = list()
        user_score = 0
        user_hints = dict()

    puzzle = context.user_data
    puzzles = load_data_from_json(user_id)

    if puzzle['is_voided']:
        user_voids.append(puzzle['cur_puzzle_idx'])
    elif for_hint:
        user_hints[puzzle['cur_puzzle_idx']] = user_hints.get(puzzle['cur_puzzle_idx'],0) + 1
        user_score -= 1
    else:
        user_progress.append(puzzle['cur_puzzle_idx'])
        user_solved_time.append(time.time())
        user_score += puzzle['score']

    if len(user_voids) + len(user_progress) == len(puzzles):
        user_score += HINT_POINTS*(GIVEN_HINTS - sum(user_hints.values()))

    user_name = puzzle['username']
    user_data_str = dumps({'username': user_name, 'progress': user_progress, 'voids': user_voids, 'solved_time': user_solved_time, 'score': str(user_score), 'hints': user_hints}, indent=2)
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