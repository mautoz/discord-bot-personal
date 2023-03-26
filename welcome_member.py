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


client.run(TOKEN)
