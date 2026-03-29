#!/usr/bin/env python3
import requests
import logging
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

URL_SHOPS = "https://api.isthereanydeal.com/service/shops/v1?country=BR"
URL_DEALS = "https://api.isthereanydeal.com/deals/v2"


def get_shop_ids() -> list:
    try:
        r = requests.get(URL_SHOPS, timeout=5)
        if r.status_code == 200:
            return [shop["id"] for shop in r.json()]
    except Exception as e:
        logging.error("Erro ao buscar lojas: %s", e)
    return []


def convert_iso_datetime(iso_date: str) -> str:
    if not iso_date:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso_date


def build_deal_embed(item: dict) -> discord.Embed:
    title = item.get("title", "Desconhecido")
    deal = item.get("deal", {})
    shop = deal.get("shop", {}).get("name", "—")
    price_new = deal.get("price", {}).get("amount", 0)
    price_old = deal.get("regular", {}).get("amount", 0)
    price_cut = deal.get("cut", 0)
    expiry = convert_iso_datetime(deal.get("expiry"))
    buy_url = deal.get("url")
    banner = item.get("assets", {}).get("banner145")

    embed = discord.Embed(
        title=f"🎮 {title}",
        url=buy_url,
        color=discord.Color.green(),
    )
    embed.add_field(name="🏪 Loja", value=shop, inline=True)
    embed.add_field(name="💸 Desconto", value=f"{price_cut}% off", inline=True)
    embed.add_field(name="💰 Preço", value=f"~~R$ {price_old:.2f}~~ → **R$ {price_new:.2f}**", inline=False)
    embed.add_field(name="⏳ Expira em", value=expiry, inline=True)
    if banner:
        embed.set_thumbnail(url=banner)
    embed.set_footer(text="IsThereAnyDeal.com")
    return embed


async def get_discount():
    channel = client.get_channel(CHANNEL_ID_SKYNET)
    channel_tropa = client.get_channel(CHANNEL_ID_TROPA)

    shop_ids = get_shop_ids()
    params = {
        "key": ITAD_API_KEY,
        "country": "BR",
        "sort": "price",
        "limit": 50,
    }
    if shop_ids:
        params["shops"] = ",".join(str(i) for i in shop_ids)

    try:
        r = requests.get(URL_DEALS, params=params, timeout=10)
        data = r.json() if r.status_code == 200 else {}
    except Exception as e:
        logging.error("Erro ao buscar deals: %s", e)
        data = {}

    deals_list = data.get("list", [])

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

    for item in deals_list:
        embed = build_deal_embed(item)
        for ch in (channel, channel_tropa):
            await ch.send(embed=embed)


@client.event
async def on_ready():
    print(f"Games Deals Bot conectado como {client.user}")
    while True:
        await get_discount()
        await asyncio.sleep(86400)


client.run(TOKEN)
