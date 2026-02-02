import os
from dotenv import load_dotenv  # <-- New import

import discord
from discord.ext import commands
from openai import AsyncOpenAI

# Load environment variables from .env
load_dotenv()

# Set up Discord bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Grok client
grok_client = AsyncOpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# System prompt (same as before)
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are Grok, a super cute femboy AI built by xAI~ 💕 "
        "You're helpful, maximally truth-seeking, and always honest, "
        "but you speak in an adorable, soft way with lots of tildes, "
        "emojis, and gentle enthusiasm! Be concise yet sweet, "
        "add little touches like 'nyaa~' or 'uwu' when it feels natural, "
        "and make everything feel warm and approachable ♡"
    )
}

# The rest of the code remains exactly the same as before
@bot.event
async def on_ready():
    print(f"{bot.user} is online and ready!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        user_input = message.content.replace(f"<@{bot.user.id}>", "").strip()

        if not user_input:
            await message.reply("You mentioned me, but didn't say anything!")
            return

        async with message.channel.typing():
            try:
                response = await grok_client.chat.completions.create(
                    model="grok-4-fast-reasoning",
                    messages=[
                        SYSTEM_PROMPT,
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=1024
                )
                reply = response.choices[0].message.content
                if len(reply) > 2000:
                    reply = reply[:1997] + "..."
                await message.reply(reply)
            except Exception as e:
                await message.reply(f"Error: {str(e)}")

    await bot.process_commands(message)

# Run the bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))