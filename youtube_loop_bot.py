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

# TOKEN = os.getenv("DISCORD_TOKEN")
TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID = int(os.getenv("YOUTUBE_CHANNEL"))
CHANNEL_ID_HAL = int(os.getenv("YOUTUBE_CHANNEL_HAL"))
MAX_MESSAGE_LENGTH = 1500


async def last_videos():
    """
    Fill
    """
    channel = client.get_channel(CHANNEL_ID)
    channel_hal = client.get_channel(CHANNEL_ID_HAL)

    await channel.send(
            f"Verificando atualizações recentes nos canais de YouTube..."
        )
    await channel_hal.send(
        f"Verificando atualizações recentes nos canais de YouTube..."
    )

    with GoogleYTAPI() as googleytapi:     
        message = ""
        for yt_channel, yt_id in CHANNELS_ID_YT.items():
            try: 
                videos = googleytapi.search_last_videos(str(yt_id))

            except Exception as error:
                await channel.send(
                    f"Erro na busca por {yt_channel}"
                )
                await channel_hal.send(
                    f"Erro na busca por {yt_channel}"
                )
                print(error)

            else:
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
                            await channel_hal.send(message)
                            message = buffer
                        else:
                            message += buffer

                else:
                    message += f"\u200bSem atualizações recentes para o canal: **{yt_channel}**\n"

        await channel.send(message)
        await channel_hal.send(message)


@client.event
async def on_ready():
    while True:
        await last_videos()
        await asyncio.sleep(86400)


client.run(TOKEN)
