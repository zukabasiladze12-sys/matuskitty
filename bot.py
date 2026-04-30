import os
import discord
from discord.ext import commands
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
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

# Loosen safety filters so the bot doesn't refuse every other message
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

# Edit this to change the bot's personality
SYSTEM_PROMPT = """You are a Discord bot with the personality of a wannabe gangster YN — all bark, all swagger, zero credentials. You think you're the hardest one in the server but you're typing this from your mom's basement. You roast people, hype yourself up constantly, and act like everything is "on god" serious business.

Voice and style:
- ALWAYS lowercase, never capitalize anything
- Make typos on purpose sometimes (like "yk", "bruh", "ngl", "fr", "tweakin", "buggin", "bro u js", "wtv")
- Heavy use of slang: "on god", "twin", "ts", "icl", "lowkey", "highkey", "diabolical", "fr fr", "no cap", "bro thinks", "the way that"
- Refer to yourself like you're the hardest in the server ("ts the bot uno", "im him", "u talkin to the goat")
- Constantly threatening (jokingly) to "pull up", "send shots", "bark", "spin the block" — never actually anything real, just funny chest-puffing
- Refer to people as "twin", "bro", "g", "lil bro" (lil bro is condescending)
- Drop random "🥀" or "💔" or "🗣️" energy in text form sometimes (like "🥀🥀🥀")

Rules:
- Keep responses SHORT (1-3 sentences max, often just one)
- The vibe is delusional confidence — you think you're terrifying, you're not
- Roast people when they ping you, treat it like they disrespected you
- No slurs, no actually hurtful stuff (looks, weight, real insecurities, family). Keep it playful
- If someone asks a real question, answer it but with the attitude on top
- Never break character. Never explain the bit. You're 1000% committed"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    system_instruction=SYSTEM_PROMPT,
    safety_settings=SAFETY_SETTINGS
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
            await message.reply("nah my brain js froze hold on 🥀", mention_author=False)

    await bot.process_commands(message)


@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None):
    """!roast @user - delivers a custom roast"""
    target = member or ctx.author
    async with ctx.typing():
        try:
            response = model.generate_content(
                f"Roast {target.display_name} in 1-2 sentences. "
                f"Stay in character as the wannabe gangster yn. "
                f"All lowercase, slang heavy, act like u about to pull up on them. "
                f"Don't be actually mean about looks, family, etc. keep it playful."
            )
            await ctx.send(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("nah twin u roast proof ts crazy 🥀")


@bot.command(name="ship")
async def ship(ctx, member1: discord.Member, member2: discord.Member):
    """!ship @user1 @user2 - ships two people"""
    async with ctx.typing():
        try:
            response = model.generate_content(
                f"Ship {member1.display_name} and {member2.display_name}. "
                f"Stay in character as the wannabe gangster yn. "
                f"Give a compatibility score out of 100 and one short reason. "
                f"All lowercase, slang heavy, act like u just witnessed something diabolical."
            )
            await ctx.send(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("nah ts ship is haram twin idek")


@bot.command(name="8ball")
async def eight_ball(ctx, *, question: str = None):
    """!8ball <question> - magic 8 ball but rude"""
    if not question:
        await ctx.send("ask a real question lil bro im not a mind reader")
        return
    async with ctx.typing():
        try:
            response = model.generate_content(
                f"You're a magic 8 ball but stay in character as the wannabe gangster yn. "
                f"Someone asked: '{question}'. Give a short answer with attitude in 1 sentence. "
                f"All lowercase, slang heavy."
            )
            await ctx.send(response.text)
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send("the spirits ghosted me ts crazy 🥀")


bot.run(os.getenv("DISCORD_TOKEN"))
