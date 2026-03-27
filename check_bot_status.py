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
MSG_STATUS_C3PO = int(os.getenv("MSG_STATUS_C3PO"))
MSG_STATUS_C3PO_TD = int(os.getenv("MSG_STATUS_C3PO_TD"))

BOTS = {
    "Welcome":            "welcome_member.py",
    "IMDB":               "imdb_bot.py",
    "Wall-E (Movies)":    "movies_cast_bot.py",
    "Youtube Search":     "youtube_bot.py",
    "Youtube Loop":       "youtube_loop_bot.py",
    "Games Deals":        "games_deals_bot.py",
    "Movies Upcoming":    "movies_upcoming_bot.py",
    "Entertainment News": "entertainment_news_bot.py",
}

THUMBNAIL = "https://i0.wp.com/www.setcenas.com.br/wp-content/uploads/2020/07/Terminator-Orion.jpg"
THUMBNAIL_C3PO = "https://static.wikia.nocookie.net/murderseries/images/e/ee/C_3PO.jpg"


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


async def build_c3po_embed() -> discord.Embed:
    status = "🟢 Online" if check_process("voice_transcription_bot.py") else "🔴 Offline"
    embed = discord.Embed(
        title="🤖 C-3PO — Voice Transcription",
        description="Telegram bot status",
        color=discord.Color.gold(),
    )
    embed.set_thumbnail(url=THUMBNAIL_C3PO)
    embed.add_field(name="C-3PO Voice Transcription", value=status, inline=False)
    last_update = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
    embed.set_footer(text=f"Última atualização: {last_update.strftime('%d/%m/%Y %H:%M:%S')}")
    return embed


async def update_status():
    embed = await build_embed()
    embed_c3po = await build_c3po_embed()

    for channel_id, msg_id, msg_c3po_id in (
        (SERVER_CHANNEL, MSG_DEFAULT, MSG_STATUS_C3PO),
        (SERVER_CHANNEL_HAL, MSG_DEFAULT_HAL, MSG_STATUS_C3PO_TD),
    ):
        channel = client.get_channel(channel_id)
        if channel is None:
            continue
        for e, mid in ((embed, msg_id), (embed_c3po, msg_c3po_id)):
            try:
                msg = await channel.fetch_message(mid)
                await msg.edit(embed=e)
            except discord.NotFound:
                await channel.send(embed=e)


@client.event
async def on_ready():
    print(f"Bot monitor conectado como {client.user}")
    while True:
        await update_status()
        await asyncio.sleep(3600)


client.run(TOKEN)
