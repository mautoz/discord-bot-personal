import subprocess
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import datetime
import pytz

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
SERVER_CHANNEL = int(os.getenv("SERVER_CHANNEL"))
MSG_DEFAULT = int(os.getenv("SERVER_DEFAULT_MSG"))
MSG_DEFAULT_TD = int(os.getenv("SERVER_DEFAULT_MSG_TD"))

BOTS = {
    "IMDB": "imdb_bot.py",
    "Welcome": "welcome_member.py",
    "Youtube_Search": "youtube_bot.py",
    "Youtube_News": "youtube_loop_bot.py",
}

BOTS_TROPA = {
    "IMDB": "imdb_bot_td.py",
    "Welcome": "welcome_member_td.py",
    "Youtube_Search": "youtube_bot_td.py",
    "Youtube_News": "youtube_loop_bot_td.py",
}


def check_process(script_name: str):
    """
    If we use command line, 'ps aux | grep <script name>' is
    useful to find your bot script running. This method follow
    the same idea!
    """
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    process_list = result.stdout.strip().split("\n")
    for process in process_list:
        if script_name in process:
            return True
    return False


intents = discord.Intents.all()
client = discord.Client()

# Skynet
status_embed = discord.Embed(
    title="Bots Monitor", description="Checking running bots", color=0x00FF00
)
status_embed.set_thumbnail(
    url="https://i0.wp.com/www.setcenas.com.br/wp-content/uploads/2020/07/Terminator-Orion.jpg"
)
status_embed.add_field(name="IMDB", value="Offline")
status_embed.add_field(name="Welcome", value="Offline")
status_embed.add_field(name="Youtube_Search", value="Offline")
status_embed.add_field(name="Youtube_News", value="Offline")
status_embed.add_field(name="Last update", value="Offline")

# Tropa
status_embed_td = discord.Embed(
    title="Bots Monitor", description="Checking running bots", color=0x00FF00
)
status_embed_td.set_thumbnail(
    url="https://2.bp.blogspot.com/-AnEJVXe3qGQ/XTuocTDXJ-I/AAAAAAAAGSA/eVdmXqqOuTA-92P1rbAuo7aTdv3pQ67-QCK4BGAYYCw/s1600/tropa_dercy_logo_escuro%2Bcopy.png"
)
status_embed_td.add_field(name="IMDB", value="Offline")
status_embed_td.add_field(name="Welcome", value="Offline")
status_embed_td.add_field(name="Youtube_Search", value="Offline")
status_embed_td.add_field(name="Youtube_News", value="Offline")
status_embed_td.add_field(name="Last update", value="Offline")


async def update_status():
    """
    Keep an embed with the status of all current bots.
    """
    green_ball = discord.utils.get(client.emojis, name="green_circle")
    red_ball = discord.utils.get(client.emojis, name="red_circle")

    for i, (name, script) in enumerate(BOTS.items()):
        status = (
            f"{green_ball} Online"
            if check_process(script)
            else f"{red_ball} Offline"
        )
        status_embed.set_field_at(i, name=name, value=status, inline=False)

    last_update = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
    status_embed.set_field_at(
        i + 1, name="Last update", value=str(last_update), inline=False
    )

    channel = client.get_channel(SERVER_CHANNEL)

    # Check if the embed already exists!
    status_message = await channel.fetch_message(MSG_DEFAULT)
    if status_message:
        await status_message.edit(embed=status_embed)
    else:
        await channel.send(embed=status_embed)


async def update_status_tropa():
    """
    Keep an embed with the status of all current bots.
    """
    green_ball = discord.utils.get(client.emojis, name="green_circle")
    red_ball = discord.utils.get(client.emojis, name="red_circle")

    for i, (name, script) in enumerate(BOTS_TROPA.items()):
        status = (
            f"{green_ball} Online"
            if check_process(script)
            else f"{red_ball} Offline"
        )
        status_embed_td.set_field_at(i, name=name, value=status, inline=False)

    last_update = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
    status_embed_td.set_field_at(
        i + 1, name="Last update", value=str(last_update), inline=False
    )

    channel = client.get_channel(SERVER_CHANNEL)

    # Check if the embed already exists!
    status_message = await channel.fetch_message(MSG_DEFAULT_TD)
    if status_message:
        await status_message.edit(embed=status_embed_td)
    else:
        await channel.send(embed=status_embed_td)


@client.event
async def on_ready():
    while True:
        await update_status()
        await update_status_tropa()
        await asyncio.sleep(3600)


client.run(TOKEN)
