#!/usr/bin/env python3

import os
import asyncio
from datetime import datetime
import discord
from dotenv import load_dotenv
from tools.googleytapi import GoogleYTAPI, CHANNELS_ID_YT

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID = int(os.getenv("YOUTUBE_CHANNEL"))
CHANNEL_ID_HAL = int(os.getenv("YOUTUBE_CHANNEL_HAL"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def build_video_embed(video: dict) -> discord.Embed:
    snippet = video.get("snippet", {})
    video_id = video.get("id", {}).get("videoId", "")
    title = snippet.get("title", "Sem título")
    channel_name = snippet.get("channelTitle", "—")
    publish_time = snippet.get("publishTime", "")
    thumbnail = snippet.get("thumbnails", {}).get("high", {}).get("url") \
             or snippet.get("thumbnails", {}).get("default", {}).get("url")

    try:
        dt = datetime.fromisoformat(publish_time.replace("Z", "+00:00"))
        publish_fmt = dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        publish_fmt = publish_time

    embed = discord.Embed(
        title=title,
        url=f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
        color=discord.Color.red(),
    )
    embed.add_field(name="📺 Canal", value=channel_name, inline=True)
    embed.add_field(name="🕐 Publicado", value=publish_fmt, inline=True)
    if thumbnail:
        embed.set_image(url=thumbnail)
    embed.set_footer(text="YouTube")
    return embed


async def last_videos():
    channel = client.get_channel(CHANNEL_ID)
    channel_hal = client.get_channel(CHANNEL_ID_HAL)

    header = discord.Embed(
        title="📺 Atualizações do YouTube — últimas 24h",
        color=discord.Color.red(),
    )
    for ch in (channel, channel_hal):
        await ch.send(embed=header)

    total = 0
    with GoogleYTAPI() as googleytapi:
        for yt_channel, yt_id in CHANNELS_ID_YT.items():
            try:
                videos = googleytapi.search_last_videos(str(yt_id))
            except Exception as error:
                print(f"Erro na busca por {yt_channel}: {error}")
                continue

            if videos:
                for video in videos:
                    embed = build_video_embed(video)
                    for ch in (channel, channel_hal):
                        await ch.send(embed=embed)
                    total += 1

    summary = discord.Embed(
        description=f"✅ {total} vídeo(s) publicado(s) nas últimas 24h." if total else "😴 Nenhum vídeo novo nas últimas 24h.",
        color=discord.Color.green() if total else discord.Color.greyple(),
    )
    for ch in (channel, channel_hal):
        await ch.send(embed=summary)


@client.event
async def on_ready():
    print(f"Youtube Loop Bot conectado como {client.user}")
    while True:
        await last_videos()
        await asyncio.sleep(86400)


client.run(TOKEN)
