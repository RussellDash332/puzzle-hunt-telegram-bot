# puzzle-hunt-telegram-bot
<img alt="Python" src="https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/>

MSOC 2021 Puzzle Hunt Telegram Bot. Inspired by the [Royal Flush Telegram Bot](https://github.com/puzzlestory/t-royal-flush-telegram-bot)

[Link to the bot](https://t.me/msoc21ph_bot) here.

## How it works
First, run **main.py**, where it contains the regular commands such as ```/start```, ```/score```, and ```/hints```. It will then lead you to **puzzles_menu.py** where it contains the main puzzle conversation handler and query handlers. Inside is a list of commands handling different cases and options, depending on the user.

The puzzle itself is stored in a object-oriented manner inside **cmd_base.py**. In that same file, there are also methods regarding progress update because it has to be continuously updated with the DontPad database.

Finally, reading and writing the JSON-styled database from and to DontPad is implemented in **dpad_manager.py**.

## Hidden files
+ **game_data/** directory, containing the puzzle data (**game_data.json**) and the images/texts (either in .jpg or .txt format) for the description.
+ **env.py**, containing the bot token **TOKEN** and the DontPad URL **DP_URL**.