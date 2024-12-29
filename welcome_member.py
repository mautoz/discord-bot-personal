#!/usr/bin/env python3

import discord
import os
from dotenv import load_dotenv

intents = discord.Intents.all()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

client = discord.Client(intents=intents)


@client.event
async def on_member_join(member):
    """
    Show a message to the new user.
    """
    channel = discord.utils.get(member.guild.text_channels, name="geral")
    if channel is None:
        print(f"No channel named 'geral' found in server: {member.guild.name}")
        return
    
    server_name = member.guild.name
    message = f"Bem-vindo/bem-vinda {member.mention} ao {server_name}! Por favor, leia as #regras antes de começar a utilizar o server!"
    embed = discord.Embed(
        title="Welcome!", description=message, color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    await channel.send(embed=embed)


client.run(TOKEN)
