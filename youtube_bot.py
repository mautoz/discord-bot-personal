#!/usr/bin/env python3

import os
import schedule
import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.googleytapi import GoogleYTAPI, CHANNELS_ID_YT


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="$", intents=intents)

CHANNEL_ID = int(os.getenv("YOUTUBE_CHANNEL"))


@bot.command()
async def getid(ctx, arg):
    """
    Fill
    """
    channel = str(arg).strip()

    if str(arg).strip():
        await ctx.send(f"Channel ID:\t{CHANNELS_ID_YT[channel]}")
        return

    await ctx.send("Verifique se você digitou corretamente o nome do canal!")


@bot.command()
async def channels(ctx):
    """
    Fill
    """
    buffer = []
    for channel, _ in CHANNELS_ID_YT.items():
        buffer.append(channel)

    result = "\n".join(buffer)

    await ctx.send(result)


@bot.command()
async def last(ctx, arg):
    """
    Fill
    """
    if ctx.channel.id == CHANNEL_ID:
        googleytapi = GoogleYTAPI()
        videos = googleytapi.search_last_videos(str(arg))
        if videos:
            for video in videos:
                channel = video.get("snippet", None).get("channelTitle", None)
                publish_time = video.get("snippet", None).get(
                    "publishTime", None
                )
                thumbnails = (
                    video.get("snippet", None)
                    .get("thumbnails", None)
                    .get("default", None)
                    .get("url", None)
                )
                title = video.get("snippet", None).get("title", None)
                await ctx.send(
                    f"{channel}\t{title}\t{publish_time}\t{thumbnails}"
                )

        else:
            await ctx.send(
                "Não houve resultado para este canal! Tente outros!"
            )

        del googleytapi

    else:
        await ctx.send("Comando exclusivo do #Youtube.")


# @bot.command()
# async def id(ctx, arg):
#     """
#     Search for the imdb title using the imdb id.
#     """
#     if ctx.channel.id == CHANNEL_ID:
#         googleytapi = GoogleYTAPI()
#         result = googleytapi.search_imdb_id(str(arg), is_full=True)
#         await ctx.send(result)
#         del googleytapi
#     else:
#         await ctx.send("Comando exclusivo do #IMDB.")


bot.run(TOKEN)
