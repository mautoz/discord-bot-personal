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
    """
    Show a message to the new user.
    """
    channel = client.get_channel(GERAL_CHANNEL)
    server_name = member.guild.name
    message = f"Bem-vindo/bem-vinda {member.mention} ao {server_name}! Por favor, leia as #regras antes de começar a utilizar o server!"
    embed = discord.Embed(
        title="Welcome!", description=message, color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar_url)
    await channel.send(embed=embed)


@client.event
async def on_member_remove(member):
    """
    Show a goodbye message when a user leaves the server.
    """
    # Get the server's general text channel dynamically
    channel = discord.utils.get(member.guild.text_channels, name="geral")
    
    if channel is None:
        print(f"No channel named 'geral' found in server: {member.guild.name}")
        return
    
    server_name = member.guild.name
    message = f"""{member.name} saiu do {server_name}. Sentiremos sua falta!
    Até logo, até mais ver, bon voyage, arrivederci, até mais, adeus, boa viagem, 
    vá em paz, que a porta bata onde o sol não bate, não volte mais aqui, hasta la vista, 
    baby, escafeda-se e saia logo.
    """
    embed = discord.Embed(
        title="Goodbye!", description=message, color=discord.Color.red()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await channel.send(embed=embed)

client.run(TOKEN)
