# Discord BTTV Emote Tracker Bot
Lets users track new [Better Twitch TV](https://betterttv.com/) emotes in different discord channels.

## Commands
- `!add <regex>`: Tracks emotes matching the regular expression in the channel
- `!remove <regex>`: Stops tracking emotes matching the regular expression in the channel
- `!reloaddb`: Reloads the database from the database file

## Install
- Install python and run `pip install -r requirements.txt`
- Create a bot on the [Discord API page](https://discord.com/developers) if you haven't and add it to a server
- Rename the template `.env.example` to `.env` to hold your Discord API token or pass your token with `--bot-id`
- Start the bot `python bot.py`
- Type `python bot.py --help` for more information about the arguments

## Technical
- Using a simple json file as database
- Uses [Discord.py](https://github.com/Rapptz/discord.py) for the Discord API
