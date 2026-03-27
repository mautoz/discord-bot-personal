#!/usr/bin/env python3

import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GERAL_CHANNEL = int(os.getenv("GERAL_CHANNEL"))

client = discord.Client(intents=intents)


@client.event
async def on_member_join(member):
    channel = client.get_channel(GERAL_CHANNEL)
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
    channel = client.get_channel(GERAL_CHANNEL)
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
