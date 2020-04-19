import os
import json
import time
from discord.ext import commands
from dotenv import load_dotenv
import random
from math import floor
import discord

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX')

bot = commands.Bot(command_prefix=PREFIX)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    with open('users.json', 'r') as json_file:
        users = json.load(json_file)
        if not users:
            await user_insert(users, message.author)
            with open("users.json", "w") as f:
                json.dump(users, f)
            await message.channel.send("You are now in the list you can level up (write some message to lvl up)")
        try:
            print (users[str(message.author.id)])
        except:
            await user_insert(users, message.author)
            with open("users.json", "w") as f:
                json.dump(users, f)
            await message.channel.send("You are now in the list you can level up (write some message to lvl up)")

        if time.time() - users[str(message.author.id)]["last_message"] > 5:
            number = random.randint(1, 5)
            await add_experience(users, message.author, number)
            await add_money(users, message.author)
            await level_up(users, message.author, message.channel)
            with open("users.json", 'w') as f:
                json.dump(users, f)
    await bot.process_commands(message)

async def user_insert(users, user):
    if not user.id in users:
        users[user.id] = {}
        users[user.id]["experience"] = 0
        users[user.id]["level"] = 1
        users[user.id]["last_message"] = time.time()
        users[user.id]["money"] = 0

async def add_experience(users, user, number):
    experience = floor(9.5 + number + (users[str(user.id)]['level'] - 2))
    users[str(user.id)]["experience"] += experience
    users[str(user.id)]["last_message"] = time.time()

async def add_money(users, user):
    money = floor((9.5 + users[str(user.id)]['level'] + 50.75 + (users[str(user.id)]['level'] - 2) / 4 * 2 * ((users[str(user.id)]['level']) % 4) + 1 + (users[str(user.id)]['level'] - 6) / 4 * 2) / 18)
    users[str(user.id)]["money"] += money

async def level_up(users, user, channel):
    experience = users[str(user.id)]["experience"]
    current_level = users[str(user.id)]["level"]
    next_level = int(experience ** (1 / 4))

    if current_level < next_level:
        await channel.send(f":tada: {user.mention}, tu as atteint le niveau {next_level} !")
        users[str(user.id)]["level"] = next_level


@bot.command(pass_context=True)
async def join(ctx):
    channel = ctx.message.author.voice.channel
    await channel.connect(reconnect=True)

@bot.command(pass_context=True)
async def leave(ctx):
    voiceBot = ctx.guild.voice_client
    await voiceBot.disconnect()

@bot.command(pass_context=True)
async def tts(ctx):
    finalMessage = ctx.message.content.replace('./tts', '')
    await ctx.send(finalMessage, tts=True)

@bot.command(pass_context=True)
async def userinfo(ctx, member: discord.Member = None):
    member = ctx.author if not member else member
    member_id = str(member.id)

    with open("users.json", "r") as f:
        users = json.load(f)

        embed = discord.Embed(color=member.color, timestamp=ctx.message.created_at)
        embed.set_author(name=f"{member}", icon_url=member.avatar_url)
        embed.add_field(name="Niveau", value=users[str(member_id)]["level"])
        embed.add_field(name="Money", value=users[str(member_id)]["money"])
        embed.add_field(name="XP", value=users[str(member_id)]["experience"])
        await ctx.send(embed=embed)

@bot.command(pass_context=True)
async def rank(ctx):
    with open('users.json', 'r') as fp:
        users = json.load(fp)
        lb = []
        z = 0
        for member in ctx.message.guild.members:
            if str(member.id) in users:
                lb.append([users[str(member.id)].get('experience', 0), member.id])

        for i in sorted(lb, reverse=True):
            z += 1
            if z == 4:
                break

            embed = discord.Embed(color=bot.get_user(i[1]).color, timestamp=ctx.message.created_at)
            embed.set_author(name=f"{bot.get_user(i[1])}", icon_url=bot.get_user(i[1]).avatar_url)
            embed.add_field(name="Niveau", value=users[str(i[1])]["level"])
            embed.add_field(name="Money", value=users[str(i[1])]["money"])
            embed.add_field(name="XP", value=users[str(i[1])]["experience"])
            await ctx.send(embed=embed)

bot.run(TOKEN)