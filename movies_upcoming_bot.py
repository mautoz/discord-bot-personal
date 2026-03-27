#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
import asyncio
import requests
import discord
from dotenv import load_dotenv
import time
import random

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)

URL_DEFAULT = "https://api.themoviedb.org/3/movie/upcoming?language=pt-BR&page={0}"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w200"

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {os.getenv('TMDB_KEY')}",
}

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID_TROPA = int(os.getenv("TROPA_UPCOMING_CHANNEL"))
CHANNEL_ID_SKYNET = int(os.getenv("SKYNET_UPCOMING_CHANNEL"))


def less_than_week(date: str) -> bool:
    current_date = datetime.now()
    release_date = datetime.strptime(date, "%Y-%m-%d")
    return current_date - release_date <= timedelta(days=7)


def request_data(page: int):
    try:
        time.sleep(random.randint(1, 3))
        response = requests.get(URL_DEFAULT.format(page), headers=HEADERS, timeout=5)
    except requests.exceptions.RequestException as error:
        print(error)
        return None
    return response


def build_movie_embed(result: dict) -> discord.Embed:
    title = result.get("title", "Desconhecido")
    original_title = result.get("original_title", "")
    release_date = result.get("release_date", "—")
    overview = result.get("overview", "")
    poster_path = result.get("poster_path")

    try:
        dt = datetime.strptime(release_date, "%Y-%m-%d")
        release_fmt = dt.strftime("%d/%m/%Y")
    except Exception:
        release_fmt = release_date

    embed = discord.Embed(
        title=f"🎬 {title}",
        description=overview[:200] + "..." if len(overview) > 200 else overview,
        color=discord.Color.gold(),
    )
    if original_title and original_title != title:
        embed.add_field(name="Título original", value=original_title, inline=True)
    embed.add_field(name="📅 Estreia", value=release_fmt, inline=True)
    if poster_path:
        embed.set_thumbnail(url=f"{TMDB_IMAGE_BASE}{poster_path}")
    embed.set_footer(text="The Movie DB")
    return embed


async def last_upcoming_movies():
    channel_tropa = client.get_channel(CHANNEL_ID_TROPA)
    channel_skynet = client.get_channel(CHANNEL_ID_SKYNET)

    response = request_data(1)
    data = response.json()

    try:
        total_pages = data["total_pages"]
        results = data["results"]
        dates_min = data["dates"]["minimum"]
        dates_max = data["dates"]["maximum"]
    except KeyError as error:
        print(error)
        return

    header = discord.Embed(
        title="🎬 Próximos lançamentos nos cinemas",
        description=f"Período: **{dates_min}** até **{dates_max}**",
        color=discord.Color.blurple(),
    )
    for ch in (channel_tropa, channel_skynet):
        await ch.send(embed=header)

    movies = []
    for result in results:
        if less_than_week(result["release_date"]) and result.get("original_language") in ("en", "pt"):
            movies.append(result)

    if total_pages > 1:
        for page in range(2, total_pages + 1):
            print("Current page = %s", str(page))
            response = request_data(page)
            data = response.json()
            for result in data.get("results", []):
                if less_than_week(result["release_date"]) and result.get("original_language") in ("en", "pt"):
                    movies.append(result)

    if not movies:
        no_movies = discord.Embed(
            description="Sem novidades nos cinemas nos últimos 7 dias.",
            color=discord.Color.greyple(),
        )
        for ch in (channel_tropa, channel_skynet):
            await ch.send(embed=no_movies)
        return

    for movie in movies:
        embed = build_movie_embed(movie)
        for ch in (channel_tropa, channel_skynet):
            await ch.send(embed=embed)


@client.event
async def on_ready():
    while True:
        await last_upcoming_movies()
        await asyncio.sleep(timedelta(weeks=1).total_seconds())


client.run(TOKEN)
