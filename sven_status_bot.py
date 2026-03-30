#!/usr/bin/env python3

import os
import math
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
VAULT = os.path.expanduser("~/svencoop-server/svencoop/scripts/plugins/store/scxpm/data/main-vault.ini")
SCREEN_NAME = "svencoop"


def calc_level(xp: int) -> int:
    return math.ceil(-10.0 + math.sqrt(100.0 - (60.0 / 7.0 - ((xp + 1.0) / 3.5))))


def load_vault() -> dict:
    """Returns {steamid: {xp, level, medals}} for all saved players."""
    players = {}
    try:
        with open(VAULT) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split("\t", 1)
                if len(parts) < 2:
                    continue
                steamid = parts[0]
                fields = parts[1].split("#")
                xp = int(float(fields[0]))
                medals = int(fields[1]) if len(fields) > 1 else 0
                players[steamid] = {
                    "xp": xp,
                    "level": calc_level(xp),
                    "medals": medals,
                }
    except Exception:
        pass
    return players

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


@bot.command(name="svenxp")
async def svenxp(ctx, *, nick: str = None):
    if not nick:
        await ctx.send(embed=discord.Embed(
            description="❌ Uso: `$svenxp <nick ou steamid>`",
            color=discord.Color.red(),
        ))
        return

    # Try to get online players via A2S for nick→steamid mapping
    online = {}
    try:
        info = a2s.info(SERVER_ADDR, timeout=3)
        players = a2s.players(SERVER_ADDR, timeout=3)
        for p in players:
            if p.name:
                online[p.name.lower()] = p.name
    except Exception:
        pass

    vault = load_vault()

    # If nick looks like a SteamID, search directly
    if nick.upper().startswith("STEAM_"):
        steamid = nick.upper()
        data = vault.get(steamid)
        name = steamid
    else:
        # Try to find by partial nick match in vault keys isn't possible (vault has steamids)
        # Try to find online by nick
        match = None
        for name_lower, name_real in online.items():
            if nick.lower() in name_lower:
                match = name_real
                break

        if not match:
            await ctx.send(embed=discord.Embed(
                description=f"❌ Jogador `{nick}` não encontrado online. Use o SteamID para buscar offline.\nEx: `$svenxp STEAM_0:1:123456`",
                color=discord.Color.orange(),
            ))
            return

        # Find steamid from online players — need to check vault by cross-referencing
        # Since A2S doesn't return steamids, find best match in vault by trying online nick
        name = match
        data = None
        # Try to get steamid from server log or just search vault by last seen
        # For now, show message that we need steamid for offline lookup
        await ctx.send(embed=discord.Embed(
            description=f"ℹ️ `{match}` está online! Para ver os dados completos, use o SteamID do jogador.\nDigite `.afb_who` no console do servidor para ver os SteamIDs.",
            color=discord.Color.blue(),
        ))
        return

    if not data:
        await ctx.send(embed=discord.Embed(
            description=f"❌ Nenhum dado salvo para `{steamid}`.",
            color=discord.Color.red(),
        ))
        return

    embed = discord.Embed(title=f"📊 Stats — {name}", color=discord.Color.gold())
    embed.add_field(name="⭐ Nível", value=str(data["level"]), inline=True)
    embed.add_field(name="✨ XP", value=f"{data['xp']:,}".replace(",", "."), inline=True)
    embed.add_field(name="🏅 Medalhas", value=str(data["medals"]), inline=True)
    await ctx.send(embed=embed)


@bot.command(name="svenban")
async def svenban(ctx, steamid: str = None, duracao: str = None, *, motivo: str = "Sem motivo"):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send(embed=discord.Embed(description="❌ Sem permissão.", color=discord.Color.red()))
        return

    if not steamid or not duracao:
        await ctx.send(embed=discord.Embed(
            description="❌ Uso: `$svenban <steamid> <minutos|permanente> [motivo]`\nEx: `$svenban STEAM_0:1:123456 60 Flood`\nEx: `$svenban STEAM_0:1:123456 permanente Cheater`",
            color=discord.Color.red(),
        ))
        return

    if duracao.lower() in ("permanente", "perm", "0"):
        minutos = 0
        duracao_txt = "permanente"
    else:
        try:
            minutos = int(duracao)
            duracao_txt = f"{minutos} minuto(s)"
        except ValueError:
            await ctx.send(embed=discord.Embed(
                description="❌ Duração inválida. Use um número de minutos ou `permanente`.",
                color=discord.Color.red(),
            ))
            return

    # Use admin_banlate (AFBase) — works for offline players too
    cmd = f".admin_ban {steamid} {motivo} {minutos}"
    subprocess.run(["screen", "-S", SCREEN_NAME, "-X", "stuff", "\r"])
    subprocess.run(["screen", "-S", SCREEN_NAME, "-X", "stuff", f"{cmd}\r"])

    embed = discord.Embed(
        title="🔨 Ban aplicado",
        color=discord.Color.red(),
    )
    embed.add_field(name="SteamID", value=steamid, inline=True)
    embed.add_field(name="Duração", value=duracao_txt, inline=True)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    await ctx.send(embed=embed)


@bot.command(name="svenajuda")
async def svenajuda(ctx):
    embed = discord.Embed(title="🎮 Sven Co-op Bot", color=discord.Color.blurple())
    embed.add_field(name="`$svenstatus`", value="Status do servidor (mapa, jogadores, IP)", inline=False)
    embed.add_field(name="`$svenmapas [busca]`", value="Lista mapas instalados. Ex: `$svenmapas secretcity`", inline=False)
    embed.add_field(name="`$svenxp <steamid>`", value="XP, nível e medalhas de um jogador", inline=False)
    embed.add_field(name="`$sventrocar <mapa>`", value="Troca o mapa (só admin)", inline=False)
    embed.add_field(name="`$svenban <steamid> <minutos|permanente> [motivo]`", value="Bane jogador (só admin)", inline=False)
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Sven Status Bot conectado como {bot.user}")


bot.run(TOKEN)
