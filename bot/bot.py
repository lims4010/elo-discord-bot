import os
import discord
from pymongo import MongoClient
from bot.commands import Command

# Set Tokens/Secrets
mongoDBSecret = os.environ["MONGODB_SECRET"]
discordToken = os.environ["DISCORD_TOKEN"]

# DB Connect
cluster = MongoClient(mongoDBSecret)
db_UserData = cluster["Data"]["UserData"]
db_UserQueue = cluster["Data"]["UserQueue"]
db_MatchQueue = cluster["Data"]["MatchQueue"]
db_MatchStats = cluster["Data"]["MatchStats"]

# Main Logic
client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as: {0} - {1}'.format(client.user.name, client.user.id))
    print('-'*20)


@client.event
async def on_message(message):

    # Do not respond to itself
    if message.author == client.user:
        return

    # Read only from smash channel and with -- starter
    command = message.content.lower()
    if message.channel.name != 'smash':
        return
    elif command[:2] != '--':
        return
    command = command.replace('--', '')

    # Main Functions
    if 'register me' in command:

        isNewUser = Command.register_user(message, db_UserData, db_UserQueue)
        if isNewUser:
            await message.channel.send('User Created!')
        else:
            await message.channel.send('User already registered. Use --change name if needed.')

    elif 'match' in command:

        command = command.replace('match', '')
        msg = Command.queue_match(message, command, db_UserData,
                                  db_UserQueue, db_MatchQueue)
        await message.channel.send(msg)

    elif 'confirm' in command:

        msg = Command.confirm_match(message, db_UserData,
                                    db_UserQueue, db_MatchQueue, db_MatchStats)
        await message.channel.send(msg)

    elif 'my stats' in command:

        command = command.replace('my stats', '')
        msg = Command.get_mystats(message, db_UserData)
        await message.channel.send(msg)

    elif 'change name' in command:

        msg = Command.change_name(message, db_UserData)
        await message.channel.send(msg)

    elif 'stats vs' in command:

        command = command.split('vs')[-1]
        command = command.strip()

        msg = Command.get_vs_stats(
            message, command, db_UserData, db_MatchStats)
        await message.channel.send(msg)

    elif 'status' in command:

        msg = Command.queue_status(message, db_UserData,
                                   db_UserQueue, db_MatchQueue, db_MatchStats)
        await message.channel.send(msg)

    elif 'help' in command:

        msg = "Commands must start with -- and be in the #melee channel to be recognized. Usable commands: register me, match %NAME # - %NAME #, confirm, my stats, change name, stats vs %NAME, status. "
        await message.channel.send(msg)

# Set up the base bot


class DiscordBot(object):
    def __init__(self):
        self.token = discordToken

    def run(self):
        client.run(self.token)

    # async def runTest(self):
    #     client.start(self.token)
    #     await client.close()
