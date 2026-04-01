#!/usr/bin/env python3
import logging
from typing import Union
import os
import sys
from datetime import datetime, timedelta
import asyncio
from newsapi import NewsApiClient
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID_SKYNET = int(os.getenv("SKYNET_NEWS_CHANNEL"))
CHANNEL_ID_TROPA = int(os.getenv("TROPA_NEWS_CHANNEL"))

API_KEY = os.getenv("NEWS_API_KEY")
newsapi = NewsApiClient(api_key=API_KEY)
endpoint = "https://newsapi.org/v2/top-headlines?country={0}&category=entertainment&apiKey={1}"


def retrive_url(url: str) -> Union[dict, None]:
    r = requests.get(url, timeout=5)
    logging.info("Status code: %s", str(r.status_code))
    if r.status_code == 200:
        return r.json()
    return None


def get_raw_data(country: str):
    url = endpoint.format(country, API_KEY)
    logging.info(url)
    return retrive_url(url)


def build_article_embed(article: dict, color: discord.Color) -> discord.Embed:
    title = article.get("title", "Sem título")
    source = article.get("source", {}).get("name") or article.get("author") or "Desconhecida"
    url = article.get("url")
    image = article.get("urlToImage")
    published = article.get("publishedAt", "")
    description = article.get("description") or ""

    try:
        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        published = dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass

    embed = discord.Embed(
        title=title,
        url=url,
        description=description[:200] + "..." if len(description) > 200 else description,
        color=color,
    )
    embed.add_field(name="📰 Fonte", value=source, inline=True)
    embed.add_field(name="🕐 Publicado", value=published, inline=True)
    if url:
        embed.add_field(name="🔗 Link", value=f"[Leia mais]({url})", inline=False)
    if image:
        embed.set_thumbnail(url=image)
    embed.set_footer(text="NewsAPI")
    return embed


async def send_news(ctx, country: str, label: str, color: discord.Color):
    news = get_raw_data(country)
    try:
        articles = news.get("articles", [])
    except Exception as error:
        logging.error(error)
        await ctx.send("**Sem novas notícias ou algum erro ocorreu. Notifique o admin!**")
        return

    if not articles:
        await ctx.send(embed=discord.Embed(
            title=f"📰 Notícias — {label}",
            description="Nenhuma notícia encontrada.",
            color=discord.Color.greyple(),
        ))
        return

    await ctx.send(embed=discord.Embed(
        title=f"📰 Notícias de entretenimento — {label}",
        description=f"{datetime.today().strftime('%d/%m/%Y')} · {len(articles)} artigos",
        color=color,
    ))

    for article in articles:
        title = article.get("title", "")
        if "removed" in str(title).lower():
            continue
        await ctx.send(embed=build_article_embed(article, color))


@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="📋 Guia dos Bots", color=discord.Color.blurple())
    embed.add_field(
        name="📰 Notícias (aqui, canal #News)",
        value="`$queronoticias` — Top notícias de entretenimento BR\n`$queronews` — Top notícias de entretenimento US",
        inline=False,
    )
    embed.add_field(
        name="🎬 Filmes e Séries (qualquer canal)",
        value="`$movie <título>` — Busca filme\n`$info <título>` — Detalhes de série\n`$cast <título>` — Elenco\n`$title <título>` — Busca IMDB",
        inline=False,
    )
    embed.add_field(
        name="🎮 Sven Co-op (qualquer canal)",
        value="`$svenstatus` — Status do servidor\n`$svenmapas [busca]` — Mapas instalados\n`$svenxp <steamid>` — XP e nível\n`$sventrocar <mapa>` — Troca mapa (admin)\n`$svenban` / `$svenunban` — Ban (admin)",
        inline=False,
    )
    embed.add_field(
        name="🎥 Outros (automáticos, sem comando)",
        value="🎬 Lançamentos nos cinemas — postado semanalmente\n🎮📚 RSS Feeds — games e editoras, postado quando sai novidade\n🤖 Monitor de bots — atualizado de hora em hora",
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.command()
async def queronoticias(ctx):
    if ctx.channel.id in (CHANNEL_ID_SKYNET, CHANNEL_ID_TROPA):
        await send_news(ctx, "br", "PT-BR 🇧🇷", discord.Color.green())
    else:
        await ctx.send("Comando exclusivo do canal #News.")


@bot.command()
async def queronews(ctx):
    if ctx.channel.id in (CHANNEL_ID_SKYNET, CHANNEL_ID_TROPA):
        await send_news(ctx, "us", "EN-US 🇺🇸", discord.Color.blue())
    else:
        await ctx.send("Comando exclusivo do canal #News.")


bot.run(TOKEN)
