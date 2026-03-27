#!/usr/bin/env python3

import os
from datetime import datetime
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

ALLOWED_CHANNELS = (CHANNEL_ID, CHANNEL_ID_SKYNET)


@bot.command()
async def getid(ctx, arg):
    """Get the ID from a channel in the script."""
    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("Comando exclusivo do #Youtube.")
        return

    channel = str(arg).strip()
    if channel in CHANNELS_ID_YT:
        embed = discord.Embed(
            title="📺 Channel ID",
            color=discord.Color.red(),
        )
        embed.add_field(name="Canal", value=channel, inline=True)
        embed.add_field(name="ID", value=CHANNELS_ID_YT[channel], inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Verifique se você digitou corretamente o nome do canal!")


@bot.command()
async def channels(ctx):
    """Print a list with the current Youtube channels in the script."""
    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("Comando exclusivo do #Youtube.")
        return

    names = "\n".join(f"• {ch}" for ch in CHANNELS_ID_YT)
    embed = discord.Embed(
        title="📺 Canais monitorados",
        description=names,
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed)


@bot.command()
async def last(ctx, arg):
    """Get the videos published in the last 24 hours."""
    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("Comando exclusivo do #Youtube.")
        return

    googleytapi = GoogleYTAPI()
    videos = googleytapi.search_last_videos(str(arg))
    del googleytapi

    if not videos:
        await ctx.send("Não houve resultado para este canal! Tente outros!")
        return

    for video in videos:
        snippet = video.get("snippet", {})
        video_id = video.get("id", {}).get("videoId")
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
        await ctx.send(embed=embed)


@bot.command()
async def searchchannel(ctx, arg):
    """Search for the ID from a Youtube Channel. Example: $searchchannel DisneyPlus"""
    if ctx.channel.id not in ALLOWED_CHANNELS:
        await ctx.send("Comando exclusivo do #Youtube.")
        return

    googleytapi = GoogleYTAPI()
    id_channel = googleytapi.search_channel_id(str(arg))
    del googleytapi

    if id_channel:
        embed = discord.Embed(
            title="📺 Canal encontrado",
            color=discord.Color.red(),
        )
        embed.add_field(name="Nome", value=str(arg), inline=True)
        embed.add_field(name="ID", value=id_channel, inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send(
            "Não encontramos o canal no Youtube! Copie diretamente do Youtube o nome e utilize aspas se necessário!"
        )


bot.run(TOKEN)
