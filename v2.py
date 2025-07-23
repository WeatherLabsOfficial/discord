import random
import logging
import subprocess
import sys
import os
import re
import time
import concurrent.futures
import discord
from discord.ext import commands, tasks
import docker
import asyncio
from discord import app_commands
from discord.ui import View, Button

TOKEN = 'MTM5MjM1NzQ2NTc2MDQ2OTA5NA.GiAFf_.oPaDk9ywEvxLIOdeYq-7Vmvwd0MA1BEn1vmWrs'  # TOKEN HERE
RAM_LIMIT = '64g'
SERVER_LIMIT = 1000
database_file = 'database.txt'

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='/', intents=intents)
client = docker.from_env()

def generate_random_port():
    return random.randint(1025, 65535)

def add_to_database(user, container_name, ssh_command):
    with open(database_file, 'a') as f:
        f.write(f"{user}|{container_name}|{ssh_command}\n")

def remove_from_database(ssh_command):
    if not os.path.exists(database_file):
        return
    with open(database_file, 'r') as f:
        lines = f.readlines()
    with open(database_file, 'w') as f:
        for line in lines:
            if ssh_command not in line:
                f.write(line)

class DeployRequestView(View):
    def __init__(self, requester: discord.User):
        super().__init__(timeout=None)
        self.requester = requester
        self.handled = False

    @discord.ui.button(label="✅ Accept", style=discord.ButtonStyle.green, custom_id="accept_button")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.handled:
            await interaction.response.send_message("This request has already been handled.", ephemeral=True)
            return
        self.handled = True

        await interaction.response.send_message(f"You accepted the VPS request from {self.requester.name}.", ephemeral=True)
        await self.requester.send("✅ Your VPS request has been accepted! It is now being deployed.")

        # VPS deployment logic goes here
        print(f"Deploy VPS for {self.requester.name}")
        # TODO: Insert your VPS deployment code here

    @discord.ui.button(label="❌ Deny", style=discord.ButtonStyle.red, custom_id="deny_button")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.handled:
            await interaction.response.send_message("This request has already been handled.", ephemeral=True)
            return
        self.handled = True

        await interaction.response.send_message("You denied the VPS request.", ephemeral=True)
        await self.requester.send("❌ Your VPS request has been denied.")

@bot.tree.command(name="deploy", description="Request a VPS")
async def deploy(interaction: discord.Interaction):
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name="VPS Provider")
    if not role:
        await interaction.response.send_message("❌ VPS Provider role not found.", ephemeral=True)
        return

    await interaction.response.send_message("📨 VPS request sent to the providers. Please wait for approval.", ephemeral=True)

    view = DeployRequestView(interaction.user)
    sent = 0

    for member in role.members:
        try:
            await member.send(
                f"📥 **New VPS Request**\nUser **{interaction.user.name}** is requesting a VPS.",
                view=view
            )
            sent += 1
        except:
            continue

    if sent == 0:
        await interaction.user.send("❗ None of the VPS Providers could be contacted. Please try again later.")

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print("Failed to sync commands:", e)

bot.run(TOKEN)
