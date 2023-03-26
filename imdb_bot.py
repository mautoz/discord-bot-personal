#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.omdbapi import OMDBAPI


load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="$", intents=intents)

CHANNEL_ID = int(os.getenv("IMDB_CHANNEL"))


@bot.command()
async def title(ctx, arg):
    """
    Search for the title of the movie, tv show...
    """
    if ctx.channel.id == CHANNEL_ID:
        omdbapi = OMDBAPI()
        results_list = omdbapi.search_title(str(arg))
        if results_list:
            results = "\n".join(results_list)
            await ctx.send(results)
        else:
            await ctx.send(
                "Sua busca não obteve retorno! Tente usar outro termo! "
            )

        del omdbapi

    else:
        await ctx.send("Comando exclusivo do #IMDB.")


@bot.command()
async def id(ctx, arg):
    """
    Search for the imdb title using the imdb id.
    """
    if ctx.channel.id == CHANNEL_ID:
        omdbapi = OMDBAPI()
        result = omdbapi.search_imdb_id(str(arg), is_full=True)
        await ctx.send(result)
        del omdbapi
    else:
        await ctx.send("Comando exclusivo do #IMDB.")


bot.run(TOKEN)
