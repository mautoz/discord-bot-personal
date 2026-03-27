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

TYPE_EMOJI = {
    "movie": "🎬",
    "series": "📺",
    "episode": "📋",
    "game": "🎮",
}


def build_search_embed(results: list) -> discord.Embed:
    embed = discord.Embed(
        title="🎬 Resultados da busca",
        color=discord.Color.gold(),
    )
    for result in results[:10]:
        imdb_id = result.get("imdbID", "—")
        title = result.get("Title", "—")
        year = result.get("Year", "—")
        media_type = result.get("Type", "")
        emoji = TYPE_EMOJI.get(media_type, "🎞️")
        embed.add_field(
            name=f"{emoji} {title} ({year})",
            value=f"`{imdb_id}`",
            inline=False,
        )
    embed.set_footer(text="Use $id <imdbID> para mais detalhes")
    return embed


def build_detail_embed(data: dict) -> discord.Embed:
    title = data.get("Title", "—")
    year = data.get("Year", "—")
    media_type = data.get("Type", "")
    emoji = TYPE_EMOJI.get(media_type, "🎞️")
    director = data.get("Director", "—")
    actors = data.get("Actors", "—")
    genre = data.get("Genre", "—")
    plot = data.get("Plot", "—")
    rating = data.get("imdbRating", "—")
    poster = data.get("Poster")
    runtime = data.get("Runtime", "—")
    country = data.get("Country", "—")

    embed = discord.Embed(
        title=f"{emoji} {title} ({year})",
        description=plot,
        color=discord.Color.gold(),
    )
    embed.add_field(name="🎭 Gênero", value=genre, inline=True)
    embed.add_field(name="⏱️ Duração", value=runtime, inline=True)
    embed.add_field(name="🌍 País", value=country, inline=True)
    embed.add_field(name="🎬 Diretor", value=director, inline=False)
    embed.add_field(name="🎭 Elenco", value=actors, inline=False)
    embed.add_field(name="⭐ IMDb Rating", value=rating, inline=True)
    if poster and poster != "N/A":
        embed.set_thumbnail(url=poster)
    embed.set_footer(text="OMDB API · imdb.com")
    return embed


@bot.command()
async def title(ctx, *, arg):
    """Search for the title of a movie, tv show..."""
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("Comando exclusivo do #IMDB.")
        return

    omdbapi = OMDBAPI()
    results = omdbapi.search_title_raw(str(arg))
    del omdbapi

    if results:
        await ctx.send(embed=build_search_embed(results))
    else:
        await ctx.send("Sua busca não obteve retorno! Tente usar outro termo!")


@bot.command()
async def id(ctx, arg):
    """Search for the imdb title using the imdb id."""
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("Comando exclusivo do #IMDB.")
        return

    omdbapi = OMDBAPI()
    result = omdbapi.search_imdb_id_raw(str(arg), is_full=True)
    del omdbapi

    if result and result.get("Response") == "True":
        await ctx.send(embed=build_detail_embed(result))
    else:
        await ctx.send("ID não encontrado! Verifique se o ID está correto.")


bot.run(TOKEN)
