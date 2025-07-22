import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random


load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "crazy" in message.content.lower(): 
        await message.channel.send(f"{message.author.mention} - Crazy? I was Crazy once...")
    
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    print(f"hello command triggered by {ctx.author}")
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def hot(ctx):
    await ctx.send(f"It's Hot Seat time for {ctx.author.mention}! \n" +
                   "Select one of the three questions")
        # Read questions from file
    with open("questions.txt", "r") as file:
        content = file.read()
        questions = [q.strip() for q in content.split(",") if q.strip()]

    # Randomly pick 3 questions
    selected_questions = random.sample(questions, 3)

    # Print them
    quotes = []
    for i, q in enumerate(selected_questions, 1):
        # print(f"{i}. {q}")
        quotes.append(q)
    formatted_questions = "\n".join(f"{i}. {q}" for i, q in enumerate(selected_questions, 1))
    print(formatted_questions)
    await ctx.send(formatted_questions)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)