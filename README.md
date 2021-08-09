# puzzle-hunt-telegram-bot
<img alt="Python" src="https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/>

MSOC 2021 Puzzle Hunt Telegram Bot. Inspired by the [Royal Flush Telegram Bot](https://github.com/puzzlestory/t-royal-flush-telegram-bot)

[Link to the bot](https://t.me/puzzlehunt_bot) here.

## How it works
The [**main.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/main.py) file contains the regular commands such as ```/start```, ```/score```, and ```/hints```. It will then lead you to [**puzzles_menu.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/puzzles_menu.py) where it contains the main puzzle conversation handler and query handlers related to the ```/puzzles``` command. Inside is a list of methods handling different cases and options, depending on the user, such as asking for a hint and retrying a puzzle.

The puzzles are stored in a object-oriented manner inside [**cmd_base.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/cmd_base.py). In that same file, there are also methods regarding progress update because it has to be continuously updated with the DontPad database.

Finally, reading/writing the JSON-styled database from/to DontPad is implemented in [**dpad_manager.py**](https://github.com/RussellDash332/puzzle-hunt-telegram-bot/blob/main/dpad_manager.py).

## Hidden files
+ **game_data/** directory, containing the puzzle data (**game_data.json**) and the images/texts (either in .jpg or .txt format) for the description.
+ **env.py**, containing the bot token **TOKEN** and the DontPad URL **DP_URL**.

## Deploying
This bot is currently deployed with Google Cloud SDK. Follow the provided guide to install GCloud SDK and prepare your terminal on this directory. On **main.py**, provide this function to be the first point of compilation.

```python
def FUNCTION_NAME(request):
    # Define the bot
    updater = Updater(token=TOKEN, use_context=True)

    if request.method == 'POST':
        <Some commands>

    return <Message>
```

Provide certain modules to be imported along with the versions inside **requirements.txt**, for example

```python
python-telegram-bot==13.4.1
```

#### First Deploy
Create a new project in Google Cloud, store it's name in ```<PROJECT-ID>```. Run this command on your terminal and replace ```<TOKEN>``` with your bot API token. Make sure you have turned on Cloud Build API for your project.

```sh
gcloud functions deploy FUNCTION_NAME --set-env-vars "TELEGRAM_TOKEN=<TOKEN>" --runtime python38 --trigger-http --project=<PROJECT-ID>
```

Once the deploy finishes (around 2 minutes), it will provide you an URL for the webhook setup. Copy the URL as ```<URL>``` and run this command.

```sh
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<URL>"
```

#### Re-deploying
Should you apply some changes in your code, you can re-deploy your bot using a similar command.

```sh
gcloud functions deploy FUNCTION_NAME --runtime python38 --trigger-http --project=<PROJECT-ID>
```

For double check, set the webhook again.

```sh
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<URL>"
```

## Note
I'm leaving Procfile here for now, it's actually for Heroku.
