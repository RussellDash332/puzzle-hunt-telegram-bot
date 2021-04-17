# puzzle-hunt-telegram-bot
<img alt="Python" src="https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/>

MSOC 2021 Puzzle Hunt Telegram Bot. Inspired by the [Royal Flush Telegram Bot](https://github.com/puzzlestory/t-royal-flush-telegram-bot)

[Link to the bot](https://t.me/msoc21ph_bot) here.

## How it works
First, run [**main.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/main.py), where it contains the regular commands such as ```/start```, ```/score```, and ```/hints```. It will then lead you to [**puzzles_menu.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/puzzles_menu.py) where it contains the main puzzle conversation handler and query handlers related to the ```/puzzles``` command. Inside is a list of methods handling different cases and options, depending on the user, such as asking for a hint and retrying a puzzle.

The puzzles are stored in a object-oriented manner inside [**cmd_base.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/cmd_base.py). In that same file, there are also methods regarding progress update because it has to be continuously updated with the DontPad database.

Finally, reading/writing the JSON-styled database from/to DontPad is implemented in [**dpad_manager.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/dpad_manager.py).

## Hidden files
+ **game_data/** directory, containing the puzzle data (**game_data.json**) and the images/texts (either in .jpg or .txt format) for the description.
+ **env.py**, containing the bot token **TOKEN** and the DontPad URL **DP_URL**.

## Deploying
+ Procfile and LICENSE files are for deploying purposes. They are not used currently because for now this bot will be used locally.