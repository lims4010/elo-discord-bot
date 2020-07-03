import os
import discord
import configparser
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
db_MatchStats = cluser["Data"]["MatchStats"]

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
            await message.channel.send('User already registered.')

    elif 'match' in command:

        command = command.replace('match', '')

        msg = Command.queue_match(message, command, db_UserData,
                                  db_UserQueue, db_MatchQueue)

        await message.channel.send(msg)

    elif 'confirm' in command:

        await message.channel.send('Got it!')

# Set up the base bot


class DiscordBot(object):
    def __init__(self):
        self.token = discordToken

    def run(self):
        client.run(self.token)
