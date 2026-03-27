#!/usr/bin/env python3

import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GERAL_CHANNELS = [
    int(os.getenv("GERAL_CHANNEL")),        # Skynet
    int(os.getenv("GERAL_CHANNEL_TD")),     # Tropa Dercy
]

client = discord.Client(intents=intents)


async def get_guild_channel(guild_id: int):
    for ch_id in GERAL_CHANNELS:
        ch = client.get_channel(ch_id)
        if ch is None:
            try:
                ch = await client.fetch_channel(ch_id)
            except Exception as e:
                print(f"fetch_channel({ch_id}) falhou: {e}")
                continue
        if ch and ch.guild.id == guild_id:
            return ch
    print(f"Nenhum canal encontrado para guild_id={guild_id}")
    return None


@client.event
async def on_member_join(member):
    print(f"on_member_join: {member.name} em {member.guild.name} ({member.guild.id})")
    channel = await get_guild_channel(member.guild.id)
    if channel is None:
        return

    embed = discord.Embed(
        title="👋 Bem-vindo(a)!",
        description=f"Olá {member.mention}, seja bem-vindo(a) ao **{member.guild.name}**!\nPor favor, leia as <#regras> antes de começar.",
        color=discord.Color.green(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"Membro #{member.guild.member_count}")
    await channel.send(embed=embed)


@client.event
async def on_member_remove(member):
    print(f"on_member_remove: {member.name} em {member.guild.name} ({member.guild.id})")
    channel = await get_guild_channel(member.guild.id)
    if channel is None:
        return

    farewell = (
        "Até logo, até mais ver, bon voyage, arrivederci, até mais, adeus, boa viagem, "
        "vá em paz, que a porta bata onde o sol não bate, não volte mais aqui, hasta la vista, "
        "baby, escafeda-se e saia logo."
    )

    embed = discord.Embed(
        title="👋 Até logo!",
        description=f"**{member.name}** saiu do servidor. Sentiremos sua falta!\n_{farewell}_",
        color=discord.Color.red(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text=f"{member.guild.name}")
    await channel.send(embed=embed)


client.run(TOKEN)
