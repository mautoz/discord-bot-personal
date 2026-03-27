#!/usr/bin/env python3

import subprocess
import os
import discord
from dotenv import load_dotenv
import asyncio
import datetime
import pytz

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
SERVER_CHANNEL = int(os.getenv("SERVER_CHANNEL"))
SERVER_CHANNEL_HAL = int(os.getenv("SERVER_CHANNEL_HAL"))
MSG_DEFAULT = int(os.getenv("SERVER_DEFAULT_MSG"))
MSG_DEFAULT_HAL = int(os.getenv("SERVER_DEFAULT_MSG_HAL"))

BOTS = {
    "Welcome":           "welcome_member.py",
    "IMDB":              "imdb_bot.py",
    "Youtube":           "youtube_bot.py",
    "Games Deals":       "games_deals_bot.py",
    "Movies Upcoming":   "movies_upcoming_bot.py",
    "Entertainment News":"entertainment_news_bot.py",
}

THUMBNAIL = "https://i0.wp.com/www.setcenas.com.br/wp-content/uploads/2020/07/Terminator-Orion.jpg"


def check_process(script_name: str) -> bool:
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    return any(script_name in line for line in result.stdout.splitlines())


intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def build_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🤖 Bots Monitor",
        description="Status dos bots em tempo real",
        color=discord.Color.blurple(),
    )
    embed.set_thumbnail(url=THUMBNAIL)

    for name, script in BOTS.items():
        status = "🟢 Online" if check_process(script) else "🔴 Offline"
        embed.add_field(name=name, value=status, inline=True)

    last_update = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
    embed.set_footer(text=f"Última atualização: {last_update.strftime('%d/%m/%Y %H:%M:%S')}")
    return embed


async def update_status():
    embed = await build_embed()

    for channel_id, msg_id in (
        (SERVER_CHANNEL, MSG_DEFAULT),
        (SERVER_CHANNEL_HAL, MSG_DEFAULT_HAL),
    ):
        channel = client.get_channel(channel_id)
        if channel is None:
            continue
        try:
            msg = await channel.fetch_message(msg_id)
            await msg.edit(embed=embed)
        except discord.NotFound:
            await channel.send(embed=embed)


@client.event
async def on_ready():
    print(f"Bot monitor conectado como {client.user}")
    while True:
        await update_status()
        await asyncio.sleep(3600)


client.run(TOKEN)
