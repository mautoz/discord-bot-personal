#!/usr/bin/env python3

import os
import schedule
import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.googleytapi import GoogleYTAPI, CHANNELS_ID_YT


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN_GERO")
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="$", intents=intents)

CHANNEL_ID = int(os.getenv("YOUTUBE_CHANNEL"))
CHANNEL_ID_SKYNET = int(os.getenv("YOUTUBE_CHANNEL_HAL"))

@bot.command()
async def getid(ctx, arg):
    """
    Get the ID from a Channel in the script.
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        channel = str(arg).strip()

        if str(arg).strip():
            await ctx.send(f"Channel ID:\t{CHANNELS_ID_YT[channel]}")
            return

        await ctx.send(
            "Verifique se você digitou corretamente o nome do canal!"
        )

    else:
        await ctx.send("Comando exclusivo do #Youtube.")


@bot.command()
async def channels(ctx):
    """
    Print a list with the current Youtube channels in the script.
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        buffer = []
        for channel, _ in CHANNELS_ID_YT.items():
            buffer.append(channel)

        result = "\n".join(buffer)

        await ctx.send(result)

    else:
        await ctx.send("Comando exclusivo do #Youtube.")


@bot.command()
async def last(ctx, arg):
    """
    Get the videos published in the last 24 hours.
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
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


@bot.command()
async def searchchannel(ctx, arg):
    """
    Search for the ID from a Youtube Channel. Example:
    $searchchannel DisneyPlus
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        googleytapi = GoogleYTAPI()
        id_channel = googleytapi.search_channel_id(str(arg))
        if id_channel:
            await ctx.send(f"O id do canal {str(arg)} é {id_channel}")

        else:
            await ctx.send(
                "Não encontramos o canal no Youtube! Copie diretamente do Youtube o nome e utilize aspas se necessário!"
            )

        del googleytapi

    else:
        await ctx.send("Comando exclusivo do #Youtube.")


bot.run(TOKEN)
