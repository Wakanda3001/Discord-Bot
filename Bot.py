import os
from discord.ext.commands import Bot, CommandNotFound
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from PIL import Image

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = Bot(command_prefix='!')
emoji_suggestions = {}
emoji_deletions = {}


def full_path(rel_path):
    return os.path.join(os.path.dirname(__file__), rel_path)


async def voting(message, channel, timeout=3600, vote_period=600):
    if message.channel.id == channel:
        await message.add_reaction("\U00002705")  # check
        await message.add_reaction("\U0001F1FD")  # x
    else:
        return None

    await asyncio.sleep(0.1)
    timeout_counter = int(datetime.utcnow().timestamp())
    while message.reactions[0].count + message.reactions[1].count < 3:
        await asyncio.sleep(1)
        if int(datetime.utcnow().timestamp()) > timeout + timeout_counter:
            print("timed out")
            return None
    await asyncio.sleep(vote_period)

    score = message.reactions[0].count - message.reactions[1].count
    return score


async def compress(image_path):
    emoji = Image.open(image_path)
    emoji = emoji.resize((100, 100), Image.ANTIALIAS)
    emoji.save(image_path, optimize=True, quality=85)
    print(os.stat(image_path).st_size)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


@bot.event
async def on_ready():
    global emoji_suggestions
    global emoji_deletions
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.name == "emoji-suggestions":
                emoji_suggestions[guild.name] = channel.id
            if channel.name == "emoji-deletions":
                emoji_deletions[guild.name] = channel.id
    print(bot.guilds)
    print("Ready!")


@bot.event
async def on_message(message):
    channel = emoji_suggestions[message.guild.name]
    if len(message.attachments) == 0:
        await bot.process_commands(message)
        return

    score = await voting(message, channel)
    if not score:
        await bot.process_commands(message)
        return

    name = message.attachments[0].filename.split(".")[0]
    file_type = message.attachments[0].filename.split(".")[1]

    if message.content:
        name = message.content

    if score > 0:
        await message.channel.send("Emoji: " + name + " has been passed")
        emoji_dir = os.path.join(os.path.dirname(__file__), "Downloads/" + name + '.'+file_type)
        await message.attachments[0].save(emoji_dir)
    else:
        await bot.process_commands(message)
        return

    while os.stat(emoji_dir).st_size > 256000:
        print(os.stat(emoji_dir).st_size)
        await compress(emoji_dir)

    if len(name) > 32 or len(name) < 2:
        await message.channel.send("Emoji failed: Emoji name needs to be between 2 and 32 characters")
        os.remove(emoji_dir)
        await bot.process_commands(message)
        return

    with open(emoji_dir, "rb") as image:
        image_bytes = bytes(image.read())

    new_emoji = await message.guild.create_custom_emoji(name=name, image=image_bytes)
    await message.channel.send(new_emoji)

    if len(await message.guild.fetch_emojis()) > 48:
        await message.channel.set_permissions(message.guild.default_role, read_messages=True, send_messages=False)
    os.remove(emoji_dir)
    await bot.process_commands(message)


@bot.command(pass_context=True)
async def delete(ctx):
    channel = emoji_deletions[ctx.guild.name]
    try:
        emoji_id = ctx.message.content.split(":")[2][:-1]
    except IndexError:
        return
    emoji = await ctx.guild.fetch_emoji(emoji_id)

    score = await voting(ctx.message, channel)
    if not score:
        return
    if score > 0:
        await ctx.channel.send("Emoji: " + emoji.name + " has been deleted.")
    else:
        return
    await emoji.delete()

    if len(await ctx.message.guild.fetch_emojis()) <= 48:
        suggestions = ctx.guild.get_channel(emoji_suggestions[ctx.guild.name])
        await suggestions.set_permissions(ctx.guild.default_role, read_messages=True, send_messages=True)


bot.run(token)
