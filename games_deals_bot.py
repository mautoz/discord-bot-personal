#!/usr/bin/env python3
import requests
import logging
from typing import Union
import os
from datetime import datetime

import asyncio
import discord
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID_SKYNET = int(os.getenv("SKYNET_GAMES_CHANNEL"))
CHANNEL_ID_TROPA = int(os.getenv("TROPA_GAMES_CHANNEL"))
ITAD_API_KEY = os.getenv("ITAD_API_KEY")

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
    stores = []
    if response.get("data") is not None:
        for store in response.get("data"):
            stores.append(store.get("id"))
    return stores


def convert_unix_datetime(unix_date: int):
    if unix_date is None:
        return "—"
    return datetime.utcfromtimestamp(unix_date).strftime("%d/%m/%Y %H:%M")


def build_deal_embed(game: dict) -> discord.Embed:
    title = game.get("title", "Desconhecido")
    shop = game.get("shop", {}).get("name", "—")
    price_new = game.get("price_new", 0)
    price_old = game.get("price_old", 0)
    price_cut = game.get("price_cut", 0)
    expiry = convert_unix_datetime(game.get("expiry"))
    buy_url = game.get("urls", {}).get("buy", None)

    embed = discord.Embed(
        title=f"🎮 {title}",
        url=buy_url,
        color=discord.Color.green(),
    )
    embed.add_field(name="🏪 Loja", value=shop, inline=True)
    embed.add_field(name="💸 Desconto", value=f"{price_cut}% off", inline=True)
    embed.add_field(name="💰 Preço", value=f"~~R$ {price_old:.2f}~~ → **R$ {price_new:.2f}**", inline=False)
    embed.add_field(name="⏳ Expira em", value=expiry, inline=True)
    if buy_url:
        embed.add_field(name="🔗 Comprar", value=f"[Clique aqui]({buy_url})", inline=True)
    embed.set_footer(text="IsThereAnyDeal.com")
    return embed


async def get_discount():
    channel = client.get_channel(CHANNEL_ID_SKYNET)
    channel_tropa = client.get_channel(CHANNEL_ID_TROPA)
    stores = get_stores()

    deals = retrive_url(
        URL_DEALS_BR.format(os.getenv("ITAD_API_KEY"), "%2C".join(stores))
    )
    deals_list = deals.get("data").get("list")

    if not deals_list:
        for ch in (channel, channel_tropa):
            await ch.send(embed=discord.Embed(
                title="🎮 Descontos do dia",
                description="Nenhum desconto encontrado hoje!",
                color=discord.Color.greyple(),
            ))
        return

    header = discord.Embed(
        title="🎮 Descontos do dia",
        description=f"{len(deals_list)} ofertas encontradas!",
        color=discord.Color.blurple(),
    )
    for ch in (channel, channel_tropa):
        await ch.send(embed=header)

    for game in deals_list:
        embed = build_deal_embed(game)
        for ch in (channel, channel_tropa):
            await ch.send(embed=embed)


@client.event
async def on_ready():
    while True:
        await get_discount()
        await asyncio.sleep(86400)


client.run(TOKEN)
