#!/usr/bin/env python3.8
import requests
import logging
from typing import Union
import os
from datetime import datetime

import asyncio
from datetime import datetime, timedelta
import textwrap
import discord
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()


TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID_SKYNET = int(os.getenv("SKYNET_GAMES_CHANNEL"))
CHANNEL_ID_TROPA = int(os.getenv("TROPA_GAMES_CHANNEL"))
ITAD_API_KEY = os.getenv("ITAD_API_KEY")

MAX_LENGTH = 1700

URL_STORES_BR2 = "https://api.isthereanydeal.com/v02/web/stores/?region=br2"
URL_DEALS_BR = "https://api.isthereanydeal.com/v01/deals/list/?key={0}&region=br2&shops={1}&sort=price%3Aasc"


def retrive_url(url: str) -> Union[dict, None]:
    r = requests.get(url, timeout=5)
    logging.info("Status code: %s", str(r.status_code))

    if r.status_code == 200:
        return r.json()

    return None


def get_stores() -> Union[list, None]:
    response = retrive_url(URL_STORES_BR2)

    if response is None:
        return None

    if response.get("data") is not None:
        stores = []
        for store in response.get("data"):
            stores.append(store.get("id"))

    return stores


def convert_unix_datetime(unix_date: int):
    if unix_date is None:
        return None
    return datetime.utcfromtimestamp(unix_date).strftime("%Y-%m-%d %H:%M:%S")


def insert_brackets(text: str) -> str:
    import re

    url_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    urls = url_pattern.findall(text)

    # Replace all URLs with <url> tags
    for url in urls:
        text = text.replace(url, f"<{url}>")

    return text.strip()


async def get_discount() -> list:
    channel = client.get_channel(CHANNEL_ID_SKYNET)
    channel_tropa = client.get_channel(CHANNEL_ID_TROPA)
    stores = get_stores()

    deals = retrive_url(
        URL_DEALS_BR.format(os.getenv("ITAD_API_KEY"), "%2C".join(stores))
    )
    deals_list = deals.get("data").get("list")
    if deals_list is None:
        await channel.send("**Não tem descontos hoje!**")
        await channel_tropa.send("**Não tem descontos hoje!**")

    else:
        discounts = ""
        await channel.send("**Descontos do dia**")
        await channel_tropa.send("**Não tem descontos hoje!**")
        for game in deals_list:
            buffer = textwrap.dedent(
                f"""
            \u200b```Game: {game.get('title', None)}\n
            \u200bShop: {game.get('shop', None).get('name', None)}\n
            \u200bPrice Cut: {game.get('price_cut', None)}\n
            \u200bPrice New: {game.get('price_new', None)}\n
            \u200bPrice Old: {game.get('price_old', None)}\n
            \u200bExpire: {convert_unix_datetime(game.get('expiry'))}```\n
            """
            )

            buffer += textwrap.dedent(
                f"""
            \u200bComprar: {game.get('urls', None).get('buy', None)}\n
            """
            )

            if len(discounts) + len(buffer) > MAX_LENGTH:
                await channel.send(discounts)
                await channel_tropa.send(discounts)
                discounts = buffer

            else:
                discounts += buffer

    await channel.send(discounts)
    await channel_tropa.send(discounts)


@client.event
async def on_ready():
    while True:
        await get_discount()
        await asyncio.sleep(86400)


client.run(TOKEN)
