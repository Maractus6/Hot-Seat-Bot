# cogs/hotseat.py

import discord
from discord.ext import commands
from cogs.player_manager import PlayerManager
import random
import re
import asyncio

class HotSeat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player_manager = PlayerManager()
        self.games = {}

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.mention}!")

    @commands.command()
    async def join(self, ctx):
        if self.player_manager.add_player(ctx.author):
            await ctx.send(f"{ctx.author.mention} joined the game!")
        else:
            await ctx.send(f"{ctx.author.mention}, you're already in the game.")

    @commands.command()
    async def leave(self, ctx):
        if self.player_manager.remove_player(ctx.author):
            await ctx.send(f"{ctx.author.mention} has left the game.")
        else:
            await ctx.send(f"{ctx.author.mention}, you're not in the game.")
    
    @commands.command()
    async def players(self, ctx):
        if not self.player_manager.players: # don't forget to use self.player_manager
            await ctx.send("No players have joined the game yet.")
        else:
            player_names = [player.display_name for player in self.player_manager.players]
            await ctx.send("Players currently in the game: " + ", ".join(player_names))

    @commands.command()
    async def start(self, ctx):
        players = self.player_manager.get_players()
        if not self.player_manager.has_enough_players():
            return await ctx.send("Need at least 3 players to start Hot Seat.")
        
        await ctx.send(f"It's Hot Seat time for {ctx.author.mention}! Select one of the three questions.")

        with open("data/questions.txt", "r") as file:
            questions = [q.strip() for q in file.readlines() if q.strip()]

        selected = []
        while True:
            selected = random.sample(questions, 3)
            formatted = "\n".join(f"{i+1}. {q}" for i, q in enumerate(selected))
            formatted += "\n\n type \"n\" to get new questions or any key to quit"
            await ctx.send(formatted)

            def check(m):
                return (
                    m.author == ctx.author and
                    m.channel == ctx.channel
                )

            try:
                # Wait for user's response
                msg = await self.bot.wait_for("message", check=check, timeout=60)
                content = msg.content.strip().lower()
                if content == 'n':
                    continue
                elif content.isdigit() and 1 <= int(content) <= 3:
                    choice = int(content)
                    chosen_question = selected[choice - 1]
                    await ctx.send(f"You picked:\n**{chosen_question}**\nFeel free to answer when you're ready!")
                    break
                else:
                    await ctx.send("Quitting Hot Seat. See you next time!")
                    break
            except Exception as e:
                print(e)
        

    @commands.command()
    async def add_questions(self, ctx):
        await ctx.send(f"Hey {ctx.author.mention}, enter your questions in this format:\n"
                       +"\"question1\", \"question\", ...")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            questions = re.findall(r'"(.*?)"', msg.content)

            with open("data/questions.txt", "a") as f:
                for question in questions:
                    f.write(question.strip() + "\n")

            await ctx.send(f"Success: added {len(questions)} questions.")
        except Exception as e:
            await ctx.send(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(HotSeat(bot))
