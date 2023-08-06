#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
import asyncio
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time
import random

load_dotenv()

client = discord.Client()

URL_DEFAULT = (
    "https://api.themoviedb.org/3/movie/upcoming?language=pt-BR&page={0}"
)

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {os.getenv('TMDB_KEY')}",
}

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID_TROPA = int(os.getenv("TROPA_UPCOMING_CHANNEL"))
CHANNEL_ID_SKYNET = int(os.getenv("SKYNET_UPCOMING_CHANNEL"))
MAX_MESSAGE_LENGTH = 1500


def less_than_week(date: str) -> bool:
    """
    Check if difference between the current day and the release date is less
    than 7 seven days.

    Parameters
    ----------
    date: str
      Release date of the movie.

    Returns
    -------
      True if less than 7 days. False otherwise.
    """
    current_date = datetime.now()
    release_date = datetime.strptime(date, "%Y-%m-%d")

    if current_date - release_date <= timedelta(days=7):
        return True

    return False


def request_data(page: int):
    """
    Request the movies and their release dates.
    Sleep is used to avoid ip block.

    Parameters
    ----------
    page: int
      There are many movies been released everyday. We should select which
      page we want to collect data.

    Returns
    -------
      Raw list with the movies to be release in the next seven days.
    """
    try:
        sleep_time = random.randint(1, 3)
        time.sleep(sleep_time)
        response = requests.get(
            URL_DEFAULT.format(page), headers=HEADERS, timeout=5
        )

    except requests.exceptions.RequestException as error:
        print(error)
        return None

    else:
        return response


async def last_upcoming_movies():
    """
    Check every week the movies that will be release.
    """
    channel_tropa = client.get_channel(CHANNEL_ID_TROPA)
    channel_skynet = client.get_channel(CHANNEL_ID_SKYNET)

    response = request_data(1)
    data = response.json()
    try:
        total_pages = data["total_pages"]
        results = data["results"]
    except KeyError as error:
        print(error)

    await channel_tropa.send("Verificando próximos lançamentos nos cinemas...")
    await channel_skynet.send(
        "Verificando próximos lançamentos nos cinemas..."
    )

    message = ""

    if results:
        try:
            dates_max = data["dates"]["maximum"]
            dates_min = data["dates"]["minimum"]
            await channel_tropa.send(f"Período: {dates_min} até {dates_max}")
            await channel_skynet.send(f"Período: {dates_min} até {dates_max}")

            for result in results:
                if less_than_week(result["release_date"]) and (
                    result["original_language"] == "en"
                    or result["original_language"] == "pt"
                ):
                    buffer = f"\u200b{result['release_date']}: {result['title']} // {result['original_title']}\n"
                    if len(message) + len(buffer) > MAX_MESSAGE_LENGTH:
                        await channel_tropa.send(message)
                        await channel_skynet.send(message)
                        message = buffer
                    else:
                        message += buffer

            if total_pages > 1:
                for page in range(2, total_pages + 1):
                    print("Current page = %s", str(page))
                    response = request_data(page)
                    data = response.json()
                    results = data["results"]
                    for result in results:
                        if less_than_week(result["release_date"]) and (
                            result["original_language"] == "en"
                            or result["original_language"] == "pt"
                        ):
                            buffer = f"\u200b{result['release_date']}: {result['title']} // {result['original_title']}\n"
                            if len(message) + len(buffer) > MAX_MESSAGE_LENGTH:
                                await channel_tropa.send(message)
                                await channel_skynet.send(message)
                                message = buffer
                            else:
                                message += buffer

        except (KeyError, Exception) as error:
            print(error)

    else:
        message += "Sem novidades nos cinemas nos últimos 7 dias\n"

    await channel_tropa.send(message)
    await channel_skynet.send(message)


@client.event
async def on_ready():
    while True:
        await last_upcoming_movies()
        await asyncio.sleep(86400)


client.run(TOKEN)
