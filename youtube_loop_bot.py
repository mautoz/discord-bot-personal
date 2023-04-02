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
MAX_MESSAGE_LENGTH = 1500


async def last_videos():
    """
    Fill
    """
    channel = client.get_channel(CHANNEL_ID)

    with GoogleYTAPI() as googleytapi:
        await channel.send(
            f"Verificando atualizações recentes nos canais de YouTube..."
        )

        message = ""
        for yt_channel, yt_id in CHANNELS_ID_YT.items():
            videos = googleytapi.search_last_videos(str(yt_id))

            if videos:
                for video in videos:
                    video_id = str(
                        video.get("id", None).get("videoId", None)
                    ).strip()
                    channel_name = str(
                        video.get("snippet", None).get("channelTitle", None)
                    ).strip()
                    publish_time = str(
                        video.get("snippet", None).get("publishTime", None)
                    ).strip()
                    title = str(
                        video.get("snippet", None).get("title", None)
                    ).strip()

                    buffer = f"""\u200bCanal: **{channel_name}**\n \
                    \u200bTítulo: {title}\n \
                    \u200bData de publicação: {publish_time}\n \
                    \u200bLink: https://www.youtube.com/watch?v={video_id}\n
                    """

                    if len(message) + len(buffer) > MAX_MESSAGE_LENGTH:
                        await channel.send(message)
                        message = buffer
                    else:
                        message += buffer

            else:
                message += f"\u200bSem atualizações recentes para o canal: **{yt_channel}**\n"

        await channel.send(message)


async def schedule_message():
    schedule.every().day.at("00:00").do(asyncio.create_task, last_videos())


client.loop.create_task(schedule_message())


async def start_loop():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


client.loop.create_task(start_loop())
client.run(TOKEN)
