import random 
import asyncio

def load_questions(self):
    with open("data/questions.txt", "r") as file:
        return [q.strip() for q in file if q.strip()]

async def select_question(self, ctx, game_state, questions):
    current = game_state.current_player

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
    current = game_state.current_player
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
    def check(m): return m.author == game_state.current_player and m.channel == ctx.channel
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
    answer_authors[game_state.answer] = game_state.current_player

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
        result += f"{emoji} ({text}) — {len(voters)} vote(s): {names}\n"

    scoreboard = "\n🏅 **Current Scores:**\n"
    for player, score in sorted(game_state.scores.items(), key=lambda x: -x[1]):
        scoreboard += f"{player.display_name}: {score} points\n"

    await ctx.send(result + scoreboard)

async def prompt_continue(self, ctx, game_state):
    await ctx.send("Round Finished. Play Another Round? (y/n)")

    def check(m): return m.author == game_state.current_player and m.channel == ctx.channel

    try:
        msg = await self.bot.wait_for("message", check=check, timeout=30)
        return msg.content.lower().strip() == "y"
    except asyncio.TimeoutError:
        return False
