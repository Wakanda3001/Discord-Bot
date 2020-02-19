import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_message(message):
    attachments = False
    if len(message.attachments) != 0:
        attachments = True
    if message.channel.name == "emoji-suggestions" and attachments == True:
        await message.add_reaction("\U00002705")
        await message.add_reaction("\U0001F1FD")


bot.run(token)