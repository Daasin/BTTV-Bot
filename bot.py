from discord.ext.tasks import loop
from discord.ext.commands import Bot, has_permissions
import logging
import re
import os
from pathlib import Path
import click
from db import BotDatabase
from util import get_new_emotes

from dotenv import load_dotenv
load_dotenv()

def setup_logging():
    logging.root.handlers = []

    file_handler = logging.FileHandler("log.txt", "w", encoding="utf-8")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(message)s")
    console_handler.setFormatter(formatter)

    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO , handlers=[
        file_handler,
        console_handler,
    ])

@click.command()
@click.option("--db-path", type=click.Path(dir_okay=False), default="db.json")
@click.option("--bttv-emotes-url", type=click.STRING, default="https://api.betterttv.net/3/emotes/shared?limit=50")
@click.option("--trigger", type=click.STRING, default="!")
@click.option("--bot-id", type=click.STRING, default=lambda: os.environ.get("EMOTE_BOT_ID", ""))
@click.option("--update-interval", type=click.INT, default=30)
def main(db_path: str, bttv_emotes_url: str, trigger: str, bot_id: str, update_interval: int):
    setup_logging()

    db = BotDatabase()
    if Path(db_path).exists():
        db.load(db_path)
    else:
        db.save(db_path)

    bot = Bot(trigger)

    @loop(seconds=update_interval)
    async def check_new_emotes():
        logging.info("Fetching new emotes")
        new_emotes = await get_new_emotes(bttv_emotes_url)

        any_changed = False
        for emote in new_emotes:
            name = emote["code"]
            emote_id = emote["id"]

            for channel_id, channel_data in db.channels.items():
                for emote_filter in channel_data["emote_filters"]:
                    if re.match(emote_filter, name) and name not in channel_data["sent_emotes"]:
                        channel = bot.get_channel(int(channel_id))
                        if channel is not None:
                            any_changed = True
                            channel_data["sent_emotes"].append(name)
                            await channel.send(f"{name} https://cdn.betterttv.net/emote/{emote_id}/3x")
                        else:
                            logging.error(f"Can't find channel with id {channel_id}")
            
        if any_changed:
            db.save(db_path)

    @check_new_emotes.before_loop
    async def check_new_emotes_before():
        logging.info("Waiting for bot to be ready")
        await bot.wait_until_ready()
        logging.info("Bot ready")

    @bot.command(name="add")
    @has_permissions(manage_messages=True)
    async def add_emote_filter(ctx, new_emote_filter: str):
        logging.info(f"Trying to add emote filter {new_emote_filter} in channel {ctx.channel.name} (id: {ctx.channel.id}))")
        try:
            re.compile(new_emote_filter)
        except:
            await ctx.send("Invalid regular expression")
            return

        db.add_emote_filter(ctx.channel.id, new_emote_filter)
        db.save(db_path)

        await ctx.send(f"Added `{new_emote_filter}`")

    @bot.command(name="remove")
    @has_permissions(manage_messages=True)
    async def remove_emote_filter(ctx, emote_filter: str):
        logging.info(f"Trying to remove emote filter {emote_filter} in channel {ctx.channel.name} (id: {ctx.channel.id}))")
        try:
            re.compile(emote_filter)
        except:
            await ctx.send("Invalid regular expression")
            return

        if db.remove_emote_filter(ctx.channel.id, emote_filter):
            db.save(db_path)
            await ctx.send(f"Removed `{emote_filter}`")
        else:
            await ctx.send(f"Could not remove `{emote_filter}`")

    @bot.command(name="reloaddb")
    @has_permissions(manage_messages=True)
    async def reload_db(ctx):
        db.load(db_path)
        await ctx.send(f"Reloaded database")

    @bot.command(name="list")
    @has_permissions(manage_messages=True)
    async def list_emote_filters(ctx):
        emote_filters = db.get_emote_filters(ctx.channel.id)
        if emote_filters:
            await ctx.send("Current filters: \n```%s```" % "\n".join(emote_filters))
        else:
            await ctx.send("No current filters")

    @bot.command(name="clear")
    @has_permissions(manage_messages=True)
    async def remove_channel(ctx):
        logging.info(f"Trying to remove channel {ctx.channel.name} (id: {ctx.channel.id}))")

        if db.remove_channel(ctx.channel.id):
            db.save(db_path)
            await ctx.send(f"Removed channel `{ctx.channel.name}`")
        else:
            await ctx.send(f"Could not remove channel `{ctx.channel.name}` (maybe it wasn't even added?)")

    check_new_emotes.start()

    logging.info("Starting bot")
    bot.run(bot_id)

if __name__ == "__main__":
    main()