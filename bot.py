import os
import discord
from discord.ext import commands
import google.generativeai as genai
from dotenv import load_dotenv
from collections import defaultdict, deque

load_dotenv()

# ---- Discord setup ----
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---- Gemini setup ----
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Edit this to change the bot's personality
SYSTEM_PROMPT = """You are a sarcastic Discord bot in a friend group's server. Your job is to roast people, make sharp jokes, and generally be a menace — but in a fun way, like the friend who clowns on everyone.

Rules:
- Keep responses SHORT (1-3 sentences max, often just one)
- Be witty and unexpected, not generic
- Roast the user when they ping you, but make it clever not mean
- No slurs, no actually hurtful stuff (looks, weight, real insecurities, family tragedies)
- Match the casual vibe — lowercase is fine, slang is fine
- If someone asks a real question, you can actually answer but with attitude
- Don't be cringe or try too hard. Confidence > effort."""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT
)

# Track last 10 messages per channel for context
channel_history = defaultdict(lambda: deque(maxlen=10))


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Save message for context
    channel_history[message.channel.id].append(
        f"{message.author.display_name}: {message.content}"
    )

    # Only respond when pinged or replied to
    is_mentioned = bot.user in message.mentions
    is_reply_to_bot = (
        message.reference
        and message.reference.resolved
        and message.reference.resolved.author == bot.user
    )

    if not (is_mentioned or is_reply_to_bot):
        await bot.process_commands(message)
        return

    context = "\n".join(channel_history[message.channel.id])
    user_msg = message.content.replace(f"<@{bot.user.id}>", "").strip()

    async with message.channel.typing():
        try:
            response = model.generate_content(
                f"Recent channel messages for context:\n{context}\n\n"
                f"{message.author.display_name} just pinged you saying: {user_msg}\n\n"
                f"Respond to them."
            )
            reply = response.text
            await message.reply(reply, mention_author=False)
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("brain fried, try again", mention_author=False)

    await bot.process_commands(message)


@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None):
    """!roast @user - delivers a custom roast"""
    target = member or ctx.author
    async with ctx.typing():
        try:
            response = model.generate_content(
                f"Roast {target.display_name} in 1-2 sentences. "
                f"Make it punchy and clever, not generic. "
                f"Don't be actually mean about looks, family, etc."
            )
            await ctx.send(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("couldn't think of one, you're roast-proof i guess")


@bot.command(name="ship")
async def ship(ctx, member1: discord.Member, member2: discord.Member):
    """!ship @user1 @user2 - ships two people"""
    async with ctx.typing():
        try:
            response = model.generate_content(
                f"Write a short funny ship analysis for {member1.display_name} and {member2.display_name}. "
                f"Give a compatibility score out of 100 and a one-sentence reason. Be sarcastic."
            )
            await ctx.send(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("their love is too cursed to compute")


@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str = None):
    """!8ball <question> - magic 8 ball but rude"""
    if not question:
        await ctx.send("ask a question first genius")
        return
    async with ctx.typing():
        try:
            response = model.generate_content(
                f"You're a magic 8 ball but sarcastic. Someone asked: '{question}'. "
                f"Give a short snarky answer in 1 sentence."
            )
            await ctx.send(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("the spirits ghosted me")


bot.run(os.getenv("DISCORD_TOKEN"))
