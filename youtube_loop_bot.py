#!/usr/bin/env python3

import os
import time
import asyncio
import schedule
import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.googleytapi import GoogleYTAPI, CHANNELS_ID_YT


load_dotenv()

client = discord.Client()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("YOUTUBE_CHANNEL"))


async def last_videos():
    """
    Fill
    """
    channel = client.get_channel(CHANNEL_ID)
    googleytapi = GoogleYTAPI()
    await channel.send(
        f"Verificando atualizações recentes nos canais de YouTube..."
    )
    for yt_channel, yt_id in CHANNELS_ID_YT.items():
        videos = googleytapi.search_last_videos(str(yt_id))
        if videos:
            for video in videos:
                channel_name = str(
                    video.get("snippet", None).get("channelTitle", None)
                ).strip()
                publish_time = str(
                    video.get("snippet", None).get("publishTime", None)
                ).strip()
                thumbnails = (
                    video.get("snippet", None)
                    .get("thumbnails", None)
                    .get("default", None)
                    .get("url", None)
                )
                title = str(
                    video.get("snippet", None).get("title", None)
                ).strip()
                await channel.send(
                    f"Canal: {channel_name}\n \
                    Título: {title}\n \
                    Data de publicação: {publish_time}\n \
                    {thumbnails}"
                )

        else:
            await channel.send(
                f"Sem atualizações recentes para o canal: {yt_channel}"
            )

    del googleytapi


async def send_message():
    channel = client.get_channel(CHANNEL_ID)
    await channel.send("Your message goes here")


async def schedule_message():
    schedule.every().day.at("13:05").do(asyncio.ensure_future, last_videos())
    schedule.every().day.at("00:00").do(asyncio.ensure_future, last_videos())


client.loop.create_task(schedule_message())


async def start_loop():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


client.loop.create_task(start_loop())
client.run(TOKEN)
