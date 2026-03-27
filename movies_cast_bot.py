#!/usr/bin/env python3

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.themoviesdb import TheMoviesDB

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN_WALLE")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

CHANNEL_ID = int(os.getenv("IMDB_CHANNEL"))
CHANNEL_ID_SKYNET = int(os.getenv("IMDB_CHANNEL_SKYNET"))
ALLOWED = (CHANNEL_ID, CHANNEL_ID_SKYNET)

WALLE_THUMB = "https://lumiere-a.akamaihd.net/v1/images/p_walle_19736_3b3ed734.jpeg"


def in_channel(ctx):
    return ctx.channel.id in ALLOWED


def fmt_list(items: list, sep: str = ", ") -> str:
    return sep.join(items) if items else "—"


def rating_bar(score: float) -> str:
    filled = round(score / 2)
    return "⭐" * filled + "☆" * (5 - filled) + f"  {score:.1f}/10"


# ── Search embeds ──────────────────────────────────────────────────────────────

def build_movie_search_embed(results: list) -> discord.Embed:
    embed = discord.Embed(
        title="🎬 Resultados — Filmes",
        description="Use `$info <id>` para ver a ficha completa.",
        color=discord.Color.gold(),
    )
    for r in results:
        poster = r.get("poster_path")
        if poster and not embed.thumbnail.url:
            embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/w200{poster}")
        year = r["release_date"][:4] if r.get("release_date") else "—"
        embed.add_field(
            name=f"🎞️ {r['title']} ({year})",
            value=f"ID: `{r['id']}` · {r.get('original_title', '')}",
            inline=False,
        )
    embed.set_footer(text="The Movie DB")
    return embed


def build_tv_search_embed(results: list) -> discord.Embed:
    embed = discord.Embed(
        title="📺 Resultados — Séries",
        description="Use `$serieinfo <id>` para ver a ficha completa.",
        color=discord.Color.blue(),
    )
    for r in results:
        poster = r.get("poster_path")
        if poster and not embed.thumbnail.url:
            embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/w200{poster}")
        year = r["first_air_date"][:4] if r.get("first_air_date") else "—"
        embed.add_field(
            name=f"📺 {r['name']} ({year})",
            value=f"ID: `{r['id']}` · {r.get('original_name', '')}",
            inline=False,
        )
    embed.set_footer(text="The Movie DB")
    return embed


# ── Detail embeds ──────────────────────────────────────────────────────────────

def build_movie_info_embed(d: dict) -> discord.Embed:
    year = d["release_date"][:4] if d.get("release_date") else "—"
    embed = discord.Embed(
        title=f"🎬 {d['title']} ({year})",
        description=d.get("tagline") or d.get("overview", "")[:300],
        color=discord.Color.gold(),
    )
    if d.get("poster_path"):
        embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/w500{d['poster_path']}")
    if d.get("tagline") and d.get("overview"):
        embed.add_field(name="📝 Sinopse", value=d["overview"][:500], inline=False)

    embed.add_field(name="🎭 Gêneros",    value=fmt_list(d["genres"]),       inline=True)
    embed.add_field(name="⏱️ Duração",    value=f"{d['runtime']} min" if d.get("runtime") else "—", inline=True)
    embed.add_field(name="📅 Lançamento", value=d["release_date"],           inline=True)
    embed.add_field(name="⭐ Avaliação",  value=rating_bar(d["rating"]),     inline=False)
    embed.add_field(name="🎬 Direção",    value=fmt_list(d["directors"]),    inline=True)
    embed.add_field(name="✍️ Roteiro",    value=fmt_list(d["writers"]),      inline=True)
    if d.get("cinematographers"):
        embed.add_field(name="📷 Fotografia", value=fmt_list(d["cinematographers"]), inline=True)
    if d.get("composers"):
        embed.add_field(name="🎵 Trilha",     value=fmt_list(d["composers"]),        inline=True)
    embed.add_field(name="🎭 Elenco principal", value=fmt_list(d["cast"]), inline=False)
    if d.get("budget"):
        embed.add_field(name="💰 Orçamento", value=f"${d['budget']:,.0f}", inline=True)
    if d.get("revenue"):
        embed.add_field(name="💵 Bilheteria", value=f"${d['revenue']:,.0f}", inline=True)
    embed.add_field(name="🆔 TMDB ID", value=str(d["id"]), inline=True)
    embed.set_footer(text=f"The Movie DB · {d['vote_count']:,} votos")
    return embed


def build_tv_info_embed(d: dict) -> discord.Embed:
    year = d["first_air_date"][:4] if d.get("first_air_date") else "—"
    embed = discord.Embed(
        title=f"📺 {d['name']} ({year})",
        description=d.get("tagline") or d.get("overview", "")[:300],
        color=discord.Color.blue(),
    )
    if d.get("poster_path"):
        embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/w500{d['poster_path']}")
    if d.get("tagline") and d.get("overview"):
        embed.add_field(name="📝 Sinopse", value=d["overview"][:500], inline=False)

    embed.add_field(name="🎭 Gêneros",      value=fmt_list(d["genres"]),         inline=True)
    embed.add_field(name="📡 Status",       value=d["status"],                   inline=True)
    embed.add_field(name="📅 Estreia",      value=d["first_air_date"],           inline=True)
    embed.add_field(name="🔚 Último ep.",   value=d["last_air_date"],            inline=True)
    embed.add_field(name="📦 Temporadas",   value=str(d["seasons"]),             inline=True)
    embed.add_field(name="🎬 Episódios",    value=str(d["episodes"]),            inline=True)
    embed.add_field(name="⭐ Avaliação",    value=rating_bar(d["rating"]),       inline=False)
    if d.get("creators"):
        embed.add_field(name="💡 Criado por",  value=fmt_list(d["creators"]),   inline=True)
    if d.get("directors"):
        embed.add_field(name="🎬 Direção",     value=fmt_list(d["directors"]),  inline=True)
    if d.get("writers"):
        embed.add_field(name="✍️ Roteiro",     value=fmt_list(d["writers"]),    inline=True)
    embed.add_field(name="🎭 Elenco principal", value=fmt_list(d["cast"]),      inline=False)
    embed.add_field(name="🆔 TMDB ID", value=str(d["id"]), inline=True)
    embed.set_footer(text=f"The Movie DB · {d['vote_count']:,} votos")
    return embed


# ── Commands ───────────────────────────────────────────────────────────────────

@bot.command()
async def help(ctx):
    """Show all commands."""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return

    embed = discord.Embed(
        title="🤖 Wall-E — Comandos",
        description="Busca informações de filmes e séries via The Movie DB.",
        color=discord.Color.gold(),
    )
    embed.set_thumbnail(url=WALLE_THUMB)
    embed.add_field(name="🔍 Busca", value=(
        "`$movie <título>` — Busca filmes\n"
        "`$serie <título>` — Busca séries"
    ), inline=False)
    embed.add_field(name="📋 Ficha completa", value=(
        "`$info <id>` — Diretor, roteiro, elenco, bilheteria e mais\n"
        "`$serieinfo <id>` — Criadores, temporadas, elenco e mais"
    ), inline=False)
    embed.add_field(name="🎭 Elenco", value=(
        "`$cast <id>` — Elenco completo do filme\n"
        "`$seriecast <id>` — Elenco completo da série"
    ), inline=False)
    embed.add_field(name="🖼️ Imagens", value=(
        "`$posters <id>` — Galeria de imagens do filme\n"
        "`$serieposters <id>` — Galeria de imagens da série"
    ), inline=False)
    embed.set_footer(text="The Movie DB")
    await ctx.send(embed=embed)


@bot.command()
async def movie(ctx, *, arg):
    """Search for a movie. Example: $movie Oppenheimer"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    results = db.search_movie(str(arg))
    if results:
        await ctx.send(embed=build_movie_search_embed(results))
    else:
        await ctx.send("Nenhum resultado encontrado! Tente outro termo.")


@bot.command()
async def serie(ctx, *, arg):
    """Search for a TV show. Example: $serie Breaking Bad"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    results = db.search_tv_show(str(arg))
    if results:
        await ctx.send(embed=build_tv_search_embed(results))
    else:
        await ctx.send("Nenhum resultado encontrado! Tente outro termo.")


@bot.command()
async def info(ctx, arg):
    """Full movie details. Example: $info 872585"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    details = db.get_movie_details(arg)
    if details:
        await ctx.send(embed=build_movie_info_embed(details))
    else:
        await ctx.send("ID não encontrado! Use `$movie <título>` para buscar o ID.")


@bot.command()
async def serieinfo(ctx, arg):
    """Full TV show details. Example: $serieinfo 1396"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    details = db.get_tv_details(arg)
    if details:
        await ctx.send(embed=build_tv_info_embed(details))
    else:
        await ctx.send("ID não encontrado! Use `$serie <título>` para buscar o ID.")


@bot.command()
async def cast(ctx, arg):
    """Full cast of a movie. Example: $cast 872585"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    data = db.get_full_cast(arg)
    if not data:
        await ctx.send("ID não encontrado!")
        return
    embed = discord.Embed(title="🎭 Elenco", color=discord.Color.gold())
    embed.add_field(name="🎬 Direção",  value=fmt_list(data["directors"]), inline=False)
    embed.add_field(name="✍️ Roteiro", value=fmt_list(data["writers"]),   inline=False)
    cast_text = fmt_list(data["cast"], "\n")
    for i in range(0, len(cast_text), 1000):
        embed.add_field(name="🎭 Atores" if i == 0 else "\u200b", value=cast_text[i:i+1000], inline=False)
    embed.set_footer(text="The Movie DB")
    await ctx.send(embed=embed)


@bot.command()
async def seriecast(ctx, arg):
    """Full cast of a TV show. Example: $seriecast 1396"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    data = db.get_full_cast(arg, is_tv=True)
    if not data:
        await ctx.send("ID não encontrado!")
        return
    embed = discord.Embed(title="🎭 Elenco da Série", color=discord.Color.blue())
    if data.get("directors"):
        embed.add_field(name="🎬 Direção",  value=fmt_list(data["directors"]), inline=False)
    if data.get("writers"):
        embed.add_field(name="✍️ Roteiro", value=fmt_list(data["writers"]),   inline=False)
    cast_text = fmt_list(data["cast"], "\n")
    for i in range(0, len(cast_text), 1000):
        embed.add_field(name="🎭 Atores" if i == 0 else "\u200b", value=cast_text[i:i+1000], inline=False)
    embed.set_footer(text="The Movie DB")
    await ctx.send(embed=embed)


@bot.command()
async def posters(ctx, arg):
    """Image gallery for a movie. Example: $posters 872585"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    images = db.get_images(arg)
    if not images:
        await ctx.send("Nenhuma imagem encontrada para este ID.")
        return
    for url in images[:5]:
        embed = discord.Embed(color=discord.Color.gold())
        embed.set_image(url=url)
        await ctx.send(embed=embed)


@bot.command()
async def serieposters(ctx, arg):
    """Image gallery for a TV show. Example: $serieposters 4313"""
    if not in_channel(ctx):
        await ctx.send("Comando exclusivo do #IMDB.")
        return
    db = TheMoviesDB()
    images = db.get_images(arg, is_tv=True)
    if not images:
        await ctx.send("Nenhuma imagem encontrada para este ID.")
        return
    for url in images[:5]:
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_image(url=url)
        await ctx.send(embed=embed)


bot.run(TOKEN)
