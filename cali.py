from process_command import process_command
from config import *
import discord
import json
import os

# if karma.json does not exist, create it
if not os.path.exists("karma.json"):
    with open("karma.json", 'w+') as f:
        f.write('{}')
    karma = {}
else:
    with open("karma.json", 'r') as f:
        karma = json.load(f)

client = discord.Client()

@client.event
async def on_ready():
    print('You have been authenticated as {0.user} on Discord'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif str(message.author).strip() != DISCORD_USERNAME:
        return

    to_send = process_command(message.content, karma)

    # tag user in all messages
    await message.channel.send(DISCORD_USERNAME + " " + to_send)

if __name__ == '__main__':
	client.run(DISCORD_BOT_TOKEN)