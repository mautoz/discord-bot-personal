#!/usr/bin/env python3.8
import logging
from typing import Union
import os
from datetime import datetime, timedelta
import asyncio
import textwrap
from newsapi import NewsApiClient
import discord
from dotenv import load_dotenv
import requests

load_dotenv()

client = discord.Client()


TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID_SKYNET = int(os.getenv("SKYNET_NEWS_CHANNEL"))
CHANNEL_ID_TROPA = int(os.getenv("TROPA_NEWS_CHANNEL"))

MAX_LENGTH = 1700

API_KEY = os.getenv("NEWS_API_KEY")

newsapi = NewsApiClient(api_key=API_KEY)
endpoint = f"https://newsapi.org/v2/top-headlines/sources?language=en&category=entertainment&apiKey={API_KEY}"

def retrive_url(url: str) -> Union[dict, None]:
    r = requests.get(url, timeout=5)
    logging.info("Status code: %s", str(r.status_code))

    if r.status_code == 200:
        return r.json()

    return None

HOJE = datetime.today()
ONTEM = HOJE - timedelta(days=1)
SUBJECTS = ['movie', 'trailer', 'teaser', 'game', 'tv']


def retrive_url(url: str) -> Union[dict, None]:
    r = requests.get(url, timeout=5)
    logging.info("Status code: %s", str(r.status_code))

    if r.status_code == 200:
        return r.json()

    return None


def get_raw_data(subject: str):
    all_articles = newsapi.get_everything(q=subject,
                                          sources='entertainment-weekly,mashable,ign',
                                          from_param=ONTEM,
                                          to=HOJE,
                                          language='en',
                                          sort_by='relevancy')
    
    return all_articles

async def get_news() -> list:
    channel = client.get_channel(CHANNEL_ID_SKYNET)
    channel_tropa = client.get_channel(CHANNEL_ID_TROPA)

    for subject in SUBJECTS:
        news = get_raw_data(subject)
        if news.get("totalResults", None) == 0:
            await channel.send(f"**Não tem notícias novas de {subject} nas últimas 24hs**")
            await channel_tropa.send(f"**Não tem notícias novas de {subject} nas últimas 24hs**")        

        else:
            await channel.send("**Notícias das últimas 24hs**")
            await channel_tropa.send("**Notícias das últimas 24hs**")
            for article in news.get("articles"):
                last_news = ""            

                buffer = textwrap.dedent(
                    f"""
                    \u200b```Title: {article.get('title', None)}\n
                    \u200bContent: {article.get('content', None)}\n
                    \u200bPublished At: {article.get('publishedAt', None)}\n
                    \u200bURL: {article.get('url', None)}\n
                    ```\n
                    """
                )

                buffer += textwrap.dedent(
                    f"""
                    \u200bURL Image: {article.get('urlToImage', None)}\n
                    """
                )

                if len(last_news) + len(buffer) > MAX_LENGTH:
                    await channel.send(last_news)
                    await channel_tropa.send(last_news)
                    last_news = buffer

                else:
                    last_news += buffer

            await channel.send(last_news)
            await channel_tropa.send(last_news)


@client.event
async def on_ready():
    while True:
        await get_news()
        await asyncio.sleep(86400)


client.run(TOKEN)