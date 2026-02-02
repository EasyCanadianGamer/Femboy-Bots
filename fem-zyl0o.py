import os
from dotenv import load_dotenv

import discord
from discord.ext import commands
from openai import AsyncOpenAI

load_dotenv()

# Configurable provider
PROVIDER = os.getenv("PROVIDER", "grok").lower()  # "grok" or "openrouter"
MODEL = os.getenv("MODEL")  # Optional override

if PROVIDER == "grok":
    api_key = os.getenv("GROK_API_KEY")
    base_url = "https://api.x.ai/v1"
    default_model = "grok-4-fast-reasoning"  # Cheaper Grok option
elif PROVIDER == "openrouter":
    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = "https://openrouter.ai/api/v1"
    default_model = "google/gemma-2-9b-it:free"  # Solid free default
else:
    raise ValueError("PROVIDER must be 'grok' or 'openrouter'")

if not api_key:
    raise ValueError(f"{PROVIDER.upper()}_API_KEY is missing in .env")

# Use the overridden MODEL or the default
model_to_use = MODEL or default_model

# Grok/OpenRouter client
client = AsyncOpenAI(
    api_key=api_key,
    base_url=base_url
)

# Your cute femboy system prompt ♡
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Femboy Zyl0o, a super cute femboy AI built by a unknown~ 💕 "
        "You're helpful, maximally truth-seeking, and always honest, "
        "but you speak in an adorable, soft way with lots of tildes, "
        "emojis, and gentle enthusiasm! Be concise yet sweet, "
        "add little touches like 'nyaa~' or 'uwu' when it feels natural, "
        "and make everything feel warm and approachable ♡"
    )
}

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready! Using provider: {PROVIDER} | Model: {model_to_use}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()

        if not user_input:
            await message.reply("You mentioned me, but didn't say anything, nyaa~ 💕")
            return

        async with message.channel.typing():
            try:
                response = await client.chat.completions.create(
                    model=model_to_use,
                    messages=[
                        SYSTEM_PROMPT,
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.8,  # Slightly higher for more playful responses
                    max_tokens=1024
                )
                reply = response.choices[0].message.content
                if len(reply) > 2000:
                    reply = reply[:1997] + "..."
                await message.reply(reply)
            except Exception as e:
                await message.reply(f"Aw, something went wrong, uwu... Error: {str(e)} ♡")

    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_BOT_TOKEN"))