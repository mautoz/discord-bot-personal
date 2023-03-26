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
    channel = client.get_channel(CHANNEL_ID) # Replace CHANNEL_ID with the ID of your welcome channel
    #role_channel = client.get_channel(ROLE_CHANNEL_ID) # Replace ROLE_CHANNEL_ID with the ID of your roles channel
    server_name = member.guild.name
    message = f"Bem-vindo/bem-vinda {member.mention} ao {server_name}! Por favor, leia as #regras antes de começar a utilizar o server!"
    #button = Button(style=ButtonStyle.URL, label="Go to #roles", url=f"https://discord.com/channels/{member.guild.id}/{role_channel.id}")
    embed = discord.Embed(title="Welcome!", description=message, color=discord.Color.green())
    embed.set_thumbnail(url=member.avatar_url)
    await channel.send(embed=embed)

client.run(TOKEN) 
