#!/usr/bin/env python3.8
import logging
from typing import Union
import os
import sys
from datetime import datetime, timedelta
import asyncio
import textwrap
from newsapi import NewsApiClient
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="$", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID_SKYNET = int(os.getenv("SKYNET_NEWS_CHANNEL"))
CHANNEL_ID_TROPA = int(os.getenv("TROPA_NEWS_CHANNEL"))

MAX_LENGTH = 1700

API_KEY = os.getenv("NEWS_API_KEY")


newsapi = NewsApiClient(api_key=API_KEY)
# endpoint = f"https://newsapi.org/v2/top-headlines/sources?language=en&category=entertainment&apiKey={API_KEY}"
# endpoint = "https://newsapi.org/v2/everything?language=en,pt&q={0}&apiKey={1}"
endpoint = "https://newsapi.org/v2/top-headlines?country={0}&category=entertainment&apiKey={1}"


def retrive_url(url: str) -> Union[dict, None]:
    r = requests.get(url, timeout=5)
    logging.info("Status code: %s", str(r.status_code))

    if r.status_code == 200:
        return r.json()

    return None

HOJE = datetime.today()
ONTEM = HOJE - timedelta(days=1)
SUBJECTS = ['movie', 'trailer', 'teaser', 'game', 'tv']

def get_raw_data(country: str):
    # all_articles = newsapi.get_everything(q=subject,
    #                                       sources='entertainment-weekly,mashable,ign',
    #                                       from_param=ONTEM,
    #                                       to=HOJE,
    #                                       language='en',
    #                                       sort_by='relevancy')
    url = endpoint.format(country, API_KEY)
    logging.info(url)
    news = retrive_url(url)
    
    if news:
        return news
    
    return None

@bot.command()
async def queronoticias(ctx):
    # for subject in SUBJECTS[:1]:
    if ctx.channel.id == CHANNEL_ID_SKYNET or ctx.channel.id == CHANNEL_ID_TROPA:
        news = get_raw_data("br")
        try:
            articles = news.get("articles", None)

        except Exception as error:
            logging.error(error)
            await ctx.send(f"**Sem novas notícias ou algum erro ocorreu. Notifique o admin!**")  

        else:
            logging.error("Existem notícias em PT-BR")

            await ctx.send(f"**Notícias ({datetime.today()}) das últimas 24hs em Português**")
            last_news = "" 
            for article in articles:
                title = article.get('title', None)
                if "removed" in str(title).lower():
                    continue

                logging.info(article)           

                buffer = textwrap.dedent(
                    f"""
                    \u200b```Título: {title}\n
                    \u200bFonte: {article.get('author', None)}\n
                    \u200bPublicado em: {article.get('publishedAt', None)}\n
                    \u200bURL: {article.get('url', None)}\n
                    ```\n
                    """
                )

                if len(last_news) + len(buffer) > MAX_LENGTH:
                    await ctx.send(last_news)

                    last_news = buffer

                else:
                    last_news += buffer

            await ctx.send(last_news)


    else:
        await ctx.send("Comando exclusivo do canal #News.")


@bot.command()
async def queronews(ctx):
# async def get_news() -> list:
    channel = client.get_channel(CHANNEL_ID_SKYNET)
    channel_tropa = client.get_channel(CHANNEL_ID_TROPA)

    # for subject in SUBJECTS[:1]:
    if ctx.channel.id == CHANNEL_ID_SKYNET or ctx.channel.id == CHANNEL_ID_TROPA:
        news = get_raw_data("us")
        try:
            articles = news.get("articles", None)

        except Exception as error:
            logging.error(error)
            await ctx.send(f"**Sem novas notícias ou algum erro ocorreu. Notifique o admin!**")  

        else:
            logging.error("Existem notícias em EN-US")

            await ctx.send(f"**Notícias ({datetime.today()}) das últimas 24hs em Inglês**")
            last_news = "" 
            for article in articles:
                logging.info(article)           

                buffer = textwrap.dedent(
                    f"""
                    \u200b```Título: {article.get('title', None)}\n
                    \u200bFonte: {article.get('author', None)}\n
                    \u200bPublicado em: {article.get('publishedAt', None)}\n
                    \u200bURL: {article.get('url', None)}\n
                    ```\n
                    """
                )

                # buffer += textwrap.dedent(
                #     f"""
                #     \u200bURL Image: {article.get('urlToImage', None)}\n
                #     """
                # )

                if len(last_news) + len(buffer) > MAX_LENGTH:
                    await ctx.send(last_news)

                    last_news = buffer

                else:
                    last_news += buffer

            await ctx.send(last_news)


    else:
        await ctx.send("Comando exclusivo do canal #News.")

bot.run(TOKEN)
