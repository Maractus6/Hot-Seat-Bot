# cogs/hotseat.py

import discord
from discord.ext import commands
from cogs.player_manager import PlayerManager
from state.game_state import GameState
import random
import re
import asyncio
import cogs.utils as utils


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
    async def questions(self, ctx):
        await self.show_questions_menu(ctx)


    @commands.command()
    async def info(self, ctx):
        await ctx.send(
            "**Welcome!**\n"
            "To join, type `!join` and to leave, type `!leave`.\n"
            "When you are ready, type `!start`."
        )

    @commands.command()
    async def start(self, ctx):
        players = self.player_manager.get_players()
        # if not self.player_manager.has_enough_players():
        #     return await ctx.send("Need at least 3 players to start Hot Seat.")
        
        game_state = GameState(players)
        self.games[ctx.guild.id] = game_state
        play = True
        while play:  # One round per player
            play = await self.play_round(ctx, game_state)
            game_state.next_player()
            # when end game flag is True stop the game

        await ctx.send("Thanks for playing!")

    
    
    async def play_round(self, ctx, game_state: GameState):
        print("Test Start Round")
        game_state.start_round()
        print("Test Start Round After")
        current_player = game_state.get_current_player()
        print(current_player)
        await ctx.send(f"**{current_player.display_name}** is selecting a question")
        print("Test After sending message")

        questions = self.load_questions()
        question = await self.select_question(ctx, game_state, questions)
        if not question:
            return False

        await ctx.send(f"{current_player.mention} picked:\n**{question}**")

        await self.collect_answers(ctx, game_state)
        emoji_to_answer, message = await self.present_answers(ctx, game_state)

        await ctx.send("Everyone vote for your answer!\nWrite `continue` to continue onwards.")
        await self.wait_for_continue(ctx, game_state)

        vote_details = await self.collect_votes(ctx, message, emoji_to_answer)
        await self.award_points(game_state, emoji_to_answer, vote_details)
        await self.display_results(ctx, game_state, emoji_to_answer, vote_details)

        return await self.prompt_continue(ctx, game_state)


    @commands.command()
    async def remove_questions(self, ctx):
        await self.show_questions_menu(ctx)
        # You can now prompt for input and handle removal afterwards
        await ctx.send("Type the numbers of the questions to remove, separated by commas (e.g., `1,3,5`).")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60.0)
            indices_to_remove = [int(i.strip()) - 1 for i in msg.content.split(",")]
            
            # Remove questions by index
            self.remove_questions_by_indices(indices_to_remove)
            await ctx.send("Selected questions have been removed.")
        except Exception as e:
            await ctx.send(f"Failed to remove questions: {e}")

    def get_questions(self):
        with open("data/Clean_Questions.txt", "r") as file:
            return [q for q in file if q.strip()]
        
    def remove_questions_by_indices(self, indices):
        questions = self.get_questions()
        for i in sorted(indices, reverse=True):
            if 0 <= i < len(questions):
                del questions[i]
        with open("data/Clean_Questions.txt", "w") as f:
            for q in questions:
                f.write(q + "\n")

    async def show_questions_menu(self, ctx):
        try:
            questions = self.get_questions()
            source = utils.QuestionMenuSource(questions)
            menu = utils.ContinuablePages(
                source=source,
                clear_reactions_after=True,
            )
            await menu.start(ctx)
        except Exception as e:
            print("Failed to send message:", e)

    @commands.command()
    async def add_questions(self, ctx):
        await ctx.send(f"Hey {ctx.author.mention}, enter your questions in this format:\n"
                       +"\"question1\", \"question\", ...")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=60)
            questions = re.findall(r'"(.*?)"', msg.content)

            with open("data/Clean_Questions.txt", "a") as f:
                for question in questions:
                    f.write(question.strip() + "\n")

            await ctx.send(f"Success: added {len(questions)} questions.")
        except Exception as e:
            await ctx.send(f"Error: {e}")


    def load_questions(self):
        with open("data/Clean_Questions.txt", "r") as file:
            return [q.strip() for q in file if q.strip()]

    async def select_question(self, ctx, game_state, questions):
        current = game_state.get_current_player()
        print(current)

        while True:
            selected = random.sample(questions, 3)
            formatted = "\n".join(f"{i+1}. {q}" for i, q in enumerate(selected))
            formatted += f"\n\n{current.mention}, type a number to pick a question or 'n' to get new ones:"
            await current.send(formatted)

            def check_dm(m):
                return m.author == current and isinstance(m.channel, discord.DMChannel)

            try:
                msg = await self.bot.wait_for("message", check=check_dm, timeout=60)
                if msg.content.lower().strip() == "n":
                    continue
                elif msg.content.isdigit() and 1 <= int(msg.content) <= 3:
                    question = selected[int(msg.content) - 1]
                    game_state.set_question(question)
                    return question
            except asyncio.TimeoutError:
                await ctx.send("Timed out waiting for a response.")
                return None

    async def collect_answers(self, ctx, game_state):
        current = game_state.get_current_player()
        await current.send(f"{current.mention}, please DM me your real answer to the question:\n**{game_state.question}**")

        def check_dm(m): return m.author == current and isinstance(m.channel, discord.DMChannel)

        real_msg = await self.bot.wait_for("message", check=check_dm, timeout=60)
        game_state.answer = real_msg.content
        await ctx.send("Real answer received")

        for player in self.player_manager.get_players():
            if player == current:
                continue
            await player.send(f"Write a fake answer for:\n**{game_state.question}**")

            def check_fake(m): return m.author == player and isinstance(m.channel, discord.DMChannel)

            fake_msg = await self.bot.wait_for("message", check=check_fake, timeout=60)
            game_state.fake_answers[player] = fake_msg.content
            await ctx.send(f"Received answer from **{player.display_name}**")


    async def present_answers(self, ctx, game_state):
        all_answers = list(game_state.fake_answers.values()) + [game_state.answer]
        random.shuffle(all_answers)

        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        emoji_to_answer = {number_emojis[i]: all_answers[i] for i in range(len(all_answers))}

        text = "\n".join(f"{i+1}. {ans}" for i, ans in enumerate(all_answers))
        message = await ctx.send(text)

        for i in range(len(all_answers)):
            await message.add_reaction(number_emojis[i])

        return emoji_to_answer, message


    async def wait_for_continue(self, ctx, game_state):
        def check(m): return m.author == game_state.get_current_player() and m.channel == ctx.channel
        try:
            await self.bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Timed out waiting for continue. Ending round.")


    async def collect_votes(self, ctx, message, emoji_to_answer):
        vote_details = {}
        message = await ctx.fetch_message(message.id)

        for reaction in message.reactions:
            emoji = str(reaction.emoji)
            if emoji not in emoji_to_answer:
                continue

            voters = []
            async for user in reaction.users():
                if not user.bot:
                    voters.append(user)

            vote_details[emoji] = voters

        return vote_details


    async def award_points(self, game_state, emoji_to_answer, vote_details):
        answer_authors = {v: k for k, v in game_state.fake_answers.items()}
        answer_authors[game_state.answer] = game_state.get_current_player()

        for emoji, voters in vote_details.items():
            answer_text = emoji_to_answer[emoji]
            author = answer_authors.get(answer_text)

            for voter in voters:
                if author and voter != author:
                    game_state.scores[author] += 1


    async def display_results(self, ctx, game_state, emoji_to_answer, vote_details):
        result = "📊 **Vote Tally:**\n"
        for emoji, voters in vote_details.items():
            text = emoji_to_answer[emoji]
            names = ", ".join(voter.display_name for voter in voters)
            if text == game_state.answer:
                result += f"✅ **{emoji} ({text})** — {len(voters)} vote(s): {names}\n"
            else:
                result += f"{emoji} ({text}) — {len(voters)} vote(s): {names}\n"

        scoreboard = "\n🏅 **Current Scores:**\n"
        for player, score in sorted(game_state.scores.items(), key=lambda x: -x[1]):
            scoreboard += f"{player.display_name}: {score} points\n"

        await ctx.send(result + scoreboard)

    async def prompt_continue(self, ctx, game_state):
        await ctx.send(
            "Round finished! Type `y` if you're ready to play the next round or `n` to stop.\n"
            "New players can type `!join` to enter. Type `!leave` to leave the game."
        )

        def check(m):
            return (
                m.channel == ctx.channel
                and (
                    m.content.lower().strip() == "y"
                    or m.content.lower().strip() in {"!join", "!leave"}
                )
            )

        continue_game = False

        try:
            while True:
                msg = await self.bot.wait_for("message", check=check, timeout=90)
                content = msg.content.lower().strip()

                if content == "y":
                    continue_game = True
                    await ctx.send("Got it! Starting the next round shortly...")
                    break  # one confirmation is enough

                elif content == "!join":
                    # Spoof a ctx object using the message for self.join
                    fake_ctx = await self.bot.get_context(msg)
                    await self.join(fake_ctx)

                elif content == "!leave":
                    fake_ctx = await self.bot.get_context(msg)
                    await self.leave(fake_ctx)
        except asyncio.TimeoutError:
            return False

        return continue_game

async def setup(bot):
    await bot.add_cog(HotSeat(bot))
