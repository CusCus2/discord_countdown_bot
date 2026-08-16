import os
import asyncio
import time
import wave
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents = intents,
)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")



@bot.tree.command(
    name="countdown",
    description="Start a voice countdown based on user input"
)
@app_commands.describe(
    seconds="Number of seconds to countdown from (1-60)"
)
async def countdown(interaction: discord.Interaction, seconds: int):
    if seconds < 1 or seconds > 60:
        await interaction.response.send_message(
            "Please provide a number between 1 and 60.",
            ephemeral=True
        )
        return

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "You need to be in a voice channel first.",
        )
        return

    voice_channel = interaction.user.voice.channel
    # Tell Discord we received the command
    await interaction.response.defer()

    try:

        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()

        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

    except TimeoutError:

        await interaction.followup.send(
            "I couldn't connect to the voice channel."
        )
        return

    await interaction.followup.send(
        f"Starting countdown from {seconds}!"
    )

    print("Counting from: ", seconds)
    create_countdown_audio(
        start=seconds,
        output="countdown.wav"
    )
    if voice_client.is_playing():
        await interaction.followup.send("Please wait for the countdown to finish.")
        return
    audio = discord.FFmpegPCMAudio("countdown.wav")
    voice_client.play(audio)
    while voice_client.is_playing():
        await asyncio.sleep(0.05)

@bot.tree.command(
    name="stop",
    description="Stop a current countdown in progress"
)
async def stop(interaction: discord.Interaction):

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "You need to be in a voice channel first.",
        )
        return

    voice_client = interaction.guild.voice_client


    if voice_client is None:
        await interaction.response.send_message(
            "I'm not currently in a voice channel."
        )
        return

    elif voice_client.channel != interaction.user.voice.channel:
        await interaction.response.send_message(
            "You must be in the same voice channel as me."
        )
        return


    if not voice_client.is_playing():
        await interaction.followup.send(
            "There is no countdown currently playing."
        )
        return

    voice_client.stop()

    await interaction.response.send_message("Stopped countdown!")

@bot.tree.command(
    name="leave_call",
    description="Leave the current voice channel"
)
async def leave_call(interaction: discord.Interaction):

    if interaction.user.voice is None:
        await interaction.response.send_message(
            "You need to be in a voice channel first.",
        )
        return

    voice_client = interaction.guild.voice_client


    if voice_client is None:
        await interaction.response.send_message(
            "I'm not currently in a voice channel."
        )
        return

    elif voice_client.channel != interaction.user.voice.channel:
        await interaction.response.send_message(
            "You must be in the same voice channel as me."
        )
        return


    voice_client.channel.disconnect()

    await interaction.response.send_message("Left the voice channel!")


async def play_number(voice_client: discord.VoiceClient, number: int):
    if number == 0:
        audio = discord.FFmpegPCMAudio("audio/go.wav")
    else:
        audio = discord.FFmpegPCMAudio(f"audio/{number}.wav")
    voice_client.play(audio)
    await asyncio.sleep(1)
    while voice_client.is_playing():
        await asyncio.sleep(0.01)

def create_countdown_audio(start: int, output: str):
    files = [Path(f"audio/{number}.wav") for number in range(start, -1, -1)]

    # https://stackoverflow.com/questions/2890703/how-to-join-two-wav-files-using-python
    with wave.open(str(files[0]), "rb") as first:
        params = first.getparams()
    with wave.open(output, "wb") as outfile:
        outfile.setparams(params)

        for file in files:
            with wave.open(str(file), "rb") as infile:
                outfile.writeframes(infile.readframes(infile.getnframes()))

bot.run(TOKEN)

# def play_number(voice_client, number):
