from process_command import process_command
from config import *
import logging
import discord
import random
import time
import json
import os

# configure log file
logging.basicConfig(level=logging.INFO, filename="cali.log", format="%(asctime)s %(message)s")

# if karma.json does not exist, create it
if not os.path.exists("karma.json"):
    with open("karma.json", 'w+') as f:
        f.write('{}')
    karma = {}
else:
    with open("karma.json", 'r') as f:
        karma = json.load(f)

# create shortcuts.json and lists.json file sif necessary

if not os.path.exists("shortcuts.json"):
    with open("shortcuts.json", 'w+') as f:
        f.write('{}')

if not os.path.exists("lists.json"):
    with open("shortcuts.json", 'w+') as f:
        f.write('{}')

client = discord.Client()

@client.event
async def on_ready():
    print('You have been authenticated as {0.user} on Discord'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif str(message.author).strip() != DISCORD_USERNAME.strip("@"):
        return

    logging.info("Received message")
    logging.info(message)

    to_send = process_command(message.content, karma)

    logging.info("Sending message: " + to_send)

    # consider tagging user in all messages with DISCORD_USERNAME + " "
    if to_send != "":
        await message.channel.send(to_send)

if __name__ == '__main__':
	client.run(DISCORD_BOT_TOKEN)