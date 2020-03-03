import os
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
from datetime import datetime 

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
emote_scores = {}
emoji_suggestions = 0


def full_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


@bot.event
async def on_message(message):
    if len(message.attachments) == 0:
        return
    if message.channel.name == "emoji-suggestions":
        await message.add_reaction("\U00002705")  # check
        await message.add_reaction("\U0001F1FD")  # x

    await asyncio.sleep(0.1)
    timeout_counter = int(datetime.utcnow().timestamp())
    while message.reactions[0].count + message.reactions[1].count < 3:
        await asyncio.sleep(1)
        if int(datetime.utcnow().timestamp()) > 3600 + timeout_counter:
            print("timed out")
            return
    await asyncio.sleep(0.1)  # Voting Period

    score = message.reactions[0].count - message.reactions[1].count

    name = message.attachments[0].filename.split(".")[0]
    file_type = message.attachments[0].filename.split(".")[1]

    if message.content:
        name = message.content

    if score > 0:
        await message.channel.send("Emoji: " + name + " has been passed")
        emoji_dir = os.path.join(os.path.dirname(__file__), "Downloads/" + name + '.'+file_type)
        await message.attachments[0].save(emoji_dir)
    else:
        return

    file_size = os.stat(emoji_dir).st_size
    if file_size > 256000:
        await message.channel.send("Emoji failed: file is too large. Emoji must be under 256kb.")
        os.remove(emoji_dir)
        return

    if len(name) > 32 or len(name) < 2:
        await message.channel.send("Emoji failed: Emoji name needs to be between 2 and 32 characters")
        os.remove(emoji_dir)
        return

    with open(emoji_dir, "rb") as image:
        image_bytes = bytes(image.read())

    new_emoji = await message.guild.create_custom_emoji(name=name, image=image_bytes)
    await message.channel.send(new_emoji)

bot.run(token)
