#!/usr/bin/env python3

import os
import subprocess
import discord
from discord.ext import commands
from dotenv import load_dotenv
import a2s

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("SVEN_ADMIN_IDS", "").split(",") if x.strip()]
SERVER_ADDR = ("127.0.0.1", 27015)
SERVER_PUBLIC_IP = os.getenv("SVEN_PUBLIC_IP", "10.2.126.118")
MAPCYCLE = os.path.expanduser("~/svencoop-server/svencoop/mapcycle.txt")
SCREEN_NAME = "svencoop"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents, help_command=None)


def get_maps():
    with open(MAPCYCLE) as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("//")]


def changelevel(mapname: str):
    # Limpa qualquer input pendente no buffer antes de enviar
    subprocess.run(["screen", "-S", SCREEN_NAME, "-X", "stuff", "\r"])
    subprocess.run(["screen", "-S", SCREEN_NAME, "-X", "stuff", f"changelevel {mapname}\r"])


@bot.command(name="svenstatus")
async def svenstatus(ctx):
    try:
        info = a2s.info(SERVER_ADDR, timeout=3)
        players = a2s.players(SERVER_ADDR, timeout=3)

        color = discord.Color.green() if info.player_count > 0 else discord.Color.blue()
        embed = discord.Embed(title="🎮 Mau Sven Co-op Server", color=color)
        embed.add_field(name="🗺️ Mapa", value=info.map_name, inline=True)
        embed.add_field(name="👥 Jogadores", value=f"{info.player_count}/{info.max_players}", inline=True)
        embed.add_field(name="📡 IP", value=f"{SERVER_PUBLIC_IP}:27015", inline=True)

        online = [p for p in players if p.name]
        if online:
            player_list = "\n".join(
                f"• {p.name} ({int(p.duration // 60)}min)" for p in online
            )
            embed.add_field(name="👤 Online agora", value=player_list, inline=False)

        await ctx.send(embed=embed)

    except Exception:
        await ctx.send(embed=discord.Embed(
            title="🔴 Servidor offline",
            description="Não foi possível conectar ao servidor.",
            color=discord.Color.red(),
        ))


@bot.command(name="svenmapas")
async def svenmapas(ctx, *, busca: str = None):
    maps = get_maps()

    if busca:
        maps = [m for m in maps if busca.lower() in m.lower()]
        title = f"🔍 '{busca}' — {len(maps)} mapa(s) encontrado(s)"
    else:
        title = f"📋 {len(maps)} mapas instalados"

    if not maps:
        await ctx.send(embed=discord.Embed(
            description=f"Nenhum mapa encontrado para `{busca}`.",
            color=discord.Color.red(),
        ))
        return

    # Paginação: 40 mapas por embed, máx 3 páginas
    chunks = [maps[i:i + 40] for i in range(0, len(maps), 40)]
    for i, chunk in enumerate(chunks[:3]):
        embed = discord.Embed(
            title=title if i == 0 else f"📋 Mapas (pág. {i + 1})",
            description="`" + "`, `".join(chunk) + "`",
            color=discord.Color.blurple(),
        )
        if len(chunks) > 1:
            embed.set_footer(text=f"Página {i + 1}/{min(len(chunks), 3)}")
        await ctx.send(embed=embed)


@bot.command(name="sventrocar")
async def sventrocar(ctx, *, mapname: str = None):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send(embed=discord.Embed(
            description="❌ Sem permissão.",
            color=discord.Color.red(),
        ))
        return

    if not mapname:
        await ctx.send(embed=discord.Embed(
            description="❌ Uso: `$sventrocar <nome_do_mapa>`",
            color=discord.Color.red(),
        ))
        return

    maps = get_maps()

    if mapname not in maps:
        matches = [m for m in maps if mapname.lower() in m.lower()]
        if not matches:
            await ctx.send(embed=discord.Embed(
                description=f"❌ Mapa `{mapname}` não encontrado. Use `$svenmapas {mapname}` para buscar.",
                color=discord.Color.red(),
            ))
            return
        if len(matches) == 1:
            mapname = matches[0]
        else:
            await ctx.send(embed=discord.Embed(
                title="🔍 Qual desses?",
                description="`" + "`, `".join(matches[:15]) + "`",
                color=discord.Color.orange(),
            ))
            return

    changelevel(mapname)
    await ctx.send(embed=discord.Embed(
        description=f"✅ Trocando para `{mapname}`...",
        color=discord.Color.green(),
    ))


@bot.command(name="svenajuda")
async def svenajuda(ctx):
    embed = discord.Embed(title="🎮 Sven Co-op Bot", color=discord.Color.blurple())
    embed.add_field(name="`$svenstatus`", value="Status do servidor (mapa, jogadores, IP)", inline=False)
    embed.add_field(name="`$svenmapas [busca]`", value="Lista mapas instalados. Ex: `$svenmapas secretcity`", inline=False)
    embed.add_field(name="`$sventrocar <mapa>`", value="Troca o mapa (só admin)", inline=False)
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Sven Status Bot conectado como {bot.user}")


bot.run(TOKEN)
