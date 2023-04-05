#!/usr/bin/env python3.8

import tweepy
import asyncio
from datetime import datetime, timedelta
import pytz
import os
import textwrap
import discord
from dotenv import load_dotenv

load_dotenv()


client = discord.Client()


TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_ID = int(os.getenv("TROPA_TWITTER_CHANNEL"))

MAX_LENGTH = 1700
TWITTER_PROFILES = {
    # "DCOfficial": "DCOfficial",
    # "Marvel Brasil": "MarvelBR",
    "Empire Magazine": "empiremagazine",
    # "Disney+ Brasil": "DisneyPlusBR",
    "Lionsgate": "LionsgateMovies",
    "Sony Pictures": "SonyPictures",
    "Warner Bros. Pictures Brasil": "wbpictures_br",
    # "Star+ Brasil": "StarPlusBR",
    "netflixbrasil": "NetflixBrasil",
}

auth = tweepy.OAuthHandler(
    str(os.getenv("CONSUMER_KEY")), str(os.getenv("CONSUMER_SECRET"))
)
auth.set_access_token(
    str(os.getenv("ACCESS_KEY")), str(os.getenv("ACCESS_SECRET"))
)

# Creating an API object
api = tweepy.API(auth)


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


async def get_tweets() -> list:
    today = datetime.now(tz=pytz.UTC)
    start_date = today - timedelta(days=1)
    channel = client.get_channel(CHANNEL_ID)

    tweets = ""
    for account, account_screen_name in TWITTER_PROFILES.items():
        new_tweets = tweepy.Cursor(
            api.user_timeline,
            screen_name=account_screen_name,
            tweet_mode="extended",
        ).items(15)
        tweets += textwrap.dedent(
            f"\u200bÚltimos tweets do perfil ***{account}***\n"
        )
        for tweet in new_tweets:
            if tweet.created_at >= start_date:
                text = tweet._json["full_text"]

                buffer = textwrap.dedent(
                    f"""
                    \u200b```{insert_brackets(text)}\n
                    \u200bData de publicação: {tweet.created_at}
                    """
                )

                if hasattr(tweet, "retweeted_status"):
                    tweet_url = f"https://twitter.com/{tweet.retweeted_status.user.screen_name}/status/{tweet.retweeted_status.id}"
                else:
                    tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"

                buffer += textwrap.dedent(
                    f"""
                \u200bLink original: <{tweet_url}>```\n
                """
                )

                if len(tweets) + len(buffer) > MAX_LENGTH:
                    await channel.send(tweets)
                    tweets = buffer

                else:
                    tweets += buffer

        await channel.send(tweets)


@client.event
async def on_ready():
    while True:
        await get_tweets()
        await asyncio.sleep(86400)


client.run(TOKEN)
