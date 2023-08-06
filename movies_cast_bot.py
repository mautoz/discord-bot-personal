#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.themoviesdb import TheMoviesDB

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN_WALLE")
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="$", intents=intents)

CHANNEL_ID = int(os.getenv("IMDB_CHANNEL"))
CHANNEL_ID_SKYNET = int(os.getenv("IMDB_CHANNEL_SKYNET"))


@bot.command()
async def getmovie(ctx, arg):
    """
    Get movie ID for the title previously searched on.
    Example: $getmovie 'Oppenheimmer'
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        themoviesdb = TheMoviesDB()
        results_list = themoviesdb.search_movie(str(arg))
        if results_list:
            await ctx.send("\n".join(results_list))
        else:
            await ctx.send(
                "Sua busca não obteve retorno! Tente usar outro termo!"
            )

        del themoviesdb

    else:
        await ctx.send("Comando exclusivo do #IMDB.")


@bot.command()
async def getcast(ctx, arg):
    """
    Get all cast names from the movie with the ID passed by the user.
    Example: $getcast 872585
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        themoviesdb = TheMoviesDB()
        cast = themoviesdb.get_cast(str(arg))
        if cast:
            await ctx.send(cast)
        else:
            await ctx.send("Verifique o ID digitado")

        del themoviesdb

    else:
        await ctx.send("Comando exclusivo do #IMDB.")


@bot.command()
async def getserie(ctx, arg):
    """
    Get serie ID for the title previously searched on.
    Example: $getserie 'Breaking Bad'
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        themoviesdb = TheMoviesDB()
        results_list = themoviesdb.search_tv_show(str(arg))
        if results_list:
            await ctx.send("\n".join(results_list))
        else:
            await ctx.send(
                "Sua busca não obteve retorno! Tente usar outro termo!"
            )

        del themoviesdb
    else:
        await ctx.send("Comando exclusivo do #IMDB.")


@bot.command()
async def getcastserie(ctx, arg):
    """
    Get all cast names from the serie with the ID passed by the user.
    Example: $getcastserie 1396
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        themoviesdb = TheMoviesDB()
        cast = themoviesdb.get_cast_tv_show(str(arg))
        if cast:
            await ctx.send(cast)
        else:
            await ctx.send("Verifique o ID digitado")

        del themoviesdb

    else:
        await ctx.send("Comando exclusivo do #IMDB.")


@bot.command()
async def getmovieposter(ctx, arg):
    """
    Get all images (in English or Portuguese) from the movie with the ID passed
    by the user. Example: $getmovieposter 872585
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        themoviesdb = TheMoviesDB()
        cast = themoviesdb.get_poster_movie(str(arg))
        if cast:
            max_chunk_size = 1500
            for i in range(0, len(cast), max_chunk_size):
                chunk = cast[i : i + max_chunk_size]
                await ctx.send(chunk)

        else:
            await ctx.send("Verifique o ID digitado")

        del themoviesdb

    else:
        await ctx.send("Comando exclusivo do #IMDB.")


@bot.command()
async def getserieposter(ctx, arg):
    """
    Get all images (in English or Portuguese) from the serie with the ID passed by the user.
    Example: $getserieposter 4313
    """
    if ctx.channel.id == CHANNEL_ID or ctx.channel.id == CHANNEL_ID_SKYNET:
        themoviesdb = TheMoviesDB()
        cast = themoviesdb.get_poster_serie(str(arg))
        if cast:
            max_chunk_size = 1500
            for i in range(0, len(cast), max_chunk_size):
                chunk = cast[i : i + max_chunk_size]
                await ctx.send(chunk)

        else:
            await ctx.send("Verifique o ID digitado")

        del themoviesdb

    else:
        await ctx.send("Comando exclusivo do #IMDB.")


bot.run(TOKEN)
