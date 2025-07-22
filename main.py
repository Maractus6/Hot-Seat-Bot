import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import random
import asyncio
import re


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
        questions = [q.strip() for q in content.split("\n") if q.strip()]

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

@bot.command()
async def add_questions(ctx):
    await ctx.send(f"Hey {ctx.author.mention}! \n" +
                   "Write some of your questions in the format \"question1\", \"question2\", ...\"")
        # Read questions from file
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for("message", check=check)
        message_text = msg.content
        questions = re.findall(r'"(.*?)"', message_text)
        questions[0] = questions[0].lstrip('"')
        questions[-1] = questions[-1].rstrip('"')
        with open("questions.txt", "a") as file:
            for question in questions:
                file.write(question + "\n")

        

        with open("questions.txt", "r") as file:
            content = file.read()
            all_questions = [q.strip() for q in content.split("\n") if q.strip()]
            formatted_questions = "\n".join(f"{i}. {q}" for i, q in enumerate(all_questions, 1))
            await ctx.send(formatted_questions)

    except Exception as e:
        await ctx.send(e)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)