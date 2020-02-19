import os
from discord.ext import commands

token = os.getenv('Njc2NzUyNDYyNzkwNzg3MDk0.XkXcOg.HaRVN_gTsuMNO4PTOx8fE2l3z1E')

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
