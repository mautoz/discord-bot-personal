#!/usr/bin/env python3

import os
import re
import json
import asyncio
import feedparser
import discord
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN_HAL")
CHANNEL_GAMES = int(os.getenv("RSS_GAMES_CHANNEL", "0"))
CHANNEL_BOOKS = int(os.getenv("RSS_BOOKS_CHANNEL", "0"))
SEEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "rss_seen.json")
CHECK_INTERVAL = 3600  # segundos — altere aqui para mudar a frequência
MAX_NEW_PER_FEED = 5   # máximo de posts por feed por checagem (anti-flood)

# ---------------------------------------------------------------------------
# FEEDS — adicione novos aqui:
# "Nome": ("games" ou "books", "url_do_feed")
# ---------------------------------------------------------------------------
FEEDS = {
    # Games — RSS nativo
    "PlayStation": ("games", "https://blog.playstation.com/feed/"),
    "Xbox":        ("games", "https://news.xbox.com/en-us/feed/"),
    # Games — Google News
    "Nintendo":    ("games", "https://news.google.com/rss/search?q=Nintendo+site:nintendo.com&hl=en&gl=US&ceid=US:en"),
    "Rockstar":    ("games", "https://news.google.com/rss/search?q=Rockstar+Games+site:rockstargames.com&hl=en&gl=US&ceid=US:en"),
    "Ubisoft":     ("games", "https://news.google.com/rss/search?q=Ubisoft&hl=en&gl=US&ceid=US:en"),
    "Blizzard":    ("games", "https://news.google.com/rss/search?q=Blizzard+Entertainment&hl=en&gl=US&ceid=US:en"),
    "Valve":       ("games", "https://news.google.com/rss/search?q=Valve+Steam+announcement&hl=en&gl=US&ceid=US:en"),
    "EA":          ("games", "https://news.google.com/rss/search?q=Electronic+Arts&hl=en&gl=US&ceid=US:en"),
    "Capcom":      ("games", "https://news.google.com/rss/search?q=Capcom&hl=en&gl=US&ceid=US:en"),
    "SEGA":        ("games", "https://news.google.com/rss/search?q=SEGA&hl=en&gl=US&ceid=US:en"),
    # Books — RSS nativo
    "JBC":         ("books", "https://editorajbc.com.br/feed/"),
    "New Pop":     ("books", "https://www.newpop.com.br/feed/"),
    "Intrínseca":  ("books", "https://intrinseca.com.br/feed/"),
    "Rocco":       ("books", "https://rocco.com.br/feed/"),
    "Sextante":    ("books", "https://sextante.com.br/blogs/listas-de-leitura.atom"),
    # Books — Google News
    "Panini":      ("books", "https://news.google.com/rss/search?q=Panini+editora+comics+manga&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    "Mythos":      ("books", "https://news.google.com/rss/search?q=Mythos+Books+editora&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    "Aleph":       ("books", "https://news.google.com/rss/search?q=Editora+Aleph&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    "Companhia das Letras": ("books", "https://news.google.com/rss/search?q=Companhia+das+Letras&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    "Globo Livros": ("books", "https://news.google.com/rss/search?q=Globo+Livros&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
    "L&PM":        ("books", "https://news.google.com/rss/search?q=L%26PM+editores&hl=pt-BR&gl=BR&ceid=BR:pt-419"),
}

COLORS = {"games": discord.Color.blue(), "books": discord.Color.green()}
EMOJIS = {"games": "🎮", "books": "📚"}


def load_seen() -> dict:
    os.makedirs(os.path.dirname(SEEN_FILE), exist_ok=True)
    try:
        with open(SEEN_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_seen(seen: dict):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)


def get_item_id(entry) -> str:
    return entry.get("id") or entry.get("link") or entry.get("title", "")


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def build_embed(entry, name: str, category: str) -> discord.Embed:
    title = entry.get("title", "Sem título")
    link = entry.get("link", "")
    summary = strip_html(entry.get("summary", ""))
    summary = summary[:300] + "..." if len(summary) > 300 else summary

    published = ""
    if entry.get("published_parsed"):
        try:
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            published = dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            pass

    embed = discord.Embed(
        title=f"{EMOJIS[category]} {title}",
        url=link or None,
        description=summary or None,
        color=COLORS[category],
    )
    embed.set_author(name=name)
    if published:
        embed.set_footer(text=published)

    for media in entry.get("media_thumbnail", []):
        embed.set_thumbnail(url=media.get("url", ""))
        break
    if not embed.thumbnail and entry.get("media_content"):
        for media in entry.get("media_content", []):
            if media.get("url"):
                embed.set_thumbnail(url=media["url"])
                break

    return embed


intents = discord.Intents.default()
client = discord.Client(intents=intents)


async def check_feeds():
    seen = load_seen()
    channels = {
        "games": client.get_channel(CHANNEL_GAMES),
        "books": client.get_channel(CHANNEL_BOOKS),
    }

    for name, (category, url) in FEEDS.items():
        try:
            feed = feedparser.parse(url)
            entries = feed.entries[:20]

            feed_seen = seen.get(name, [])
            is_first_run = len(feed_seen) == 0
            new_seen = list(feed_seen)
            new_items = []

            for entry in entries:
                item_id = get_item_id(entry)
                if item_id not in feed_seen:
                    new_items.append(entry)
                    new_seen.append(item_id)

            seen[name] = new_seen[-100:]  # mantém só os últimos 100

            if is_first_run:
                print(f"[RSS] {name}: primeiro boot, {len(new_items)} itens marcados como vistos.")
            elif new_items:
                ch = channels.get(category)
                if ch:
                    for entry in reversed(new_items[:MAX_NEW_PER_FEED]):
                        await ch.send(embed=build_embed(entry, name, category))
                        await asyncio.sleep(1)
                    print(f"[RSS] {name}: {len(new_items[:MAX_NEW_PER_FEED])} novidade(s) postada(s).")

        except Exception as e:
            print(f"[RSS] Erro em {name}: {e}")

    save_seen(seen)


@client.event
async def on_ready():
    print(f"RSS Bot conectado como {client.user}")
    while True:
        await check_feeds()
        await asyncio.sleep(CHECK_INTERVAL)


client.run(TOKEN)
