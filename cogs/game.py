# cogs/hotseat.py

import discord
from discord.ext import commands
from cogs.player_manager import PlayerManager
from state.game_state import GameState
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
        # if not self.player_manager.has_enough_players():
        #     return await ctx.send("Need at least 3 players to start Hot Seat.")
        
        game_state = GameState(players)
        self.games[ctx.guild.id] = game_state

        # while True:  # One round per player
        await self.play_round(ctx, game_state)
        game_state.next_player()
            # when end game flag is True stop the game

    
    async def play_round(self, ctx, game_state: GameState):
        def check(m):
                return m.author == current_player and m.channel == ctx.channel
        def check_dm(m):
                return isinstance(m.channel, discord.DMChannel)
        
        current_player = game_state.get_current_player()
        game_state.start_round()

        # Load questions
        with open("data/questions.txt", "r") as file:
            all_questions = [q.strip() for q in file if q.strip()]
        
        # Present 3 random questions
        while True:
            selected = random.sample(all_questions, 3)
            formatted = "\n".join(f"{i+1}. {q}" for i, q in enumerate(selected))
            formatted += f"\n\n{current_player.mention}, type a number to pick a question or 'n' to get new ones:"
            await ctx.send(formatted)

            try:
                msg = await self.bot.wait_for("message", check=check)
                if msg.content.lower().strip() == "n":
                    continue
                elif msg.content.strip().isdigit():
                    choice = int(msg.content)
                    if 1 <= choice <= 3:
                        picked_question = selected[choice - 1]
                        game_state.set_question(picked_question)
                        await ctx.send(f"{current_player.mention} picked:\n**{picked_question}**")
                        break
            except asyncio.TimeoutError:
                await ctx.send("Timed out waiting for a response.")
                return

        # At this point, the question is selected — continue with answer/fakes/etc
        # For example:
        await ctx.send(f"{current_player.mention}, please DM me your real answer to this question.")
        await current_player.send(f"{current_player.mention}, please DM me your real answer to this question.")

        # try:
            
        #     real_answer_msg = await self.bot.wait_for("message", check=check_dm, timeout=60)
        #     game_state.answer = real_answer_msg.content
        #     print("real answer recieved")
        # except Exception as e:
        #     await current_player.send(e)
        #     return



        for player in self.player_manager.get_players():
            try:
                if player == current_player:
                    real_answer_msg = await self.bot.wait_for("message", check=check_dm, timeout=60)
                    game_state.answer = real_answer_msg.content
                    await ctx.send("real answer recieved")
                else:
                    await ctx.send(f" recieved")
                    await player.send(f"Write a fake answer for:\n**{game_state.question}**")
                    def check_fake(m):
                        return m.author == player and isinstance(m.channel, discord.DMChannel)

                    msg = await self.bot.wait_for("message", check=check_fake)
                    game_state.fake_answers[player] = msg.content
            except Exception as e:
                await current_player.send(e)
                return
        answers = list(game_state.fake_answers.values()) 
        answers.append(game_state.answer)
        answer = "\n".join(f"{i+1}. {value}" for i, value in enumerate(answers))
        fakes = await ctx.send(answer)
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        for i in range(len(game_state.players)):
            print(i)
            await fakes.add_reaction(number_emojis[i])
        await ctx.send("Everyone vote for your answer!" \
        "\n write \"continue\" to continue onwards")

        msg = await self.bot.wait_for("message", check=check)
        if msg.content.lower().strip() == "continue":
            vote_counts = {}
            vote_details = {}

            for reaction in fakes.reactions:
                emoji = str(reaction.emoji)
                vote_counts[emoji] = reaction.count - (len(game_state.players) - 1)  # Subtract bot's own reaction

                users = await reaction.users().flatten()
                vote_details[emoji] = [user.name for user in users if user != self.bot.user]

            # Print results
            result = "📊 **Vote Tally:**\n"
            for emoji, voters in vote_details.items():
                result += f"{emoji} — {len(voters)} votes ({', '.join(voters)})\n"

            await ctx.send(result)
            












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
