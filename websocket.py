import os
import ssl
import json
import time
import asyncio
import logging
import datetime
import websockets
import process_command

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', filename='cali.log', filemode='w')

if not os.path.exists("messages.txt"):
    with open("messages.txt", "w+") as f:
        f.write("")

    messages = []
else:
    with open("messages.txt", "r") as f:
        messages = [l.split("]")[1].replace("\n", "").strip() for l in f.readlines()[:10]]

# if karma.json does not exist, create it
if not os.path.exists("karma.json"):
    with open("karma.json", 'w+') as f:
        f.write('{}')
    karma = {}
else:
    with open("karma.json", 'r') as f:
        karma = json.load(f)

username = "[cali]: "

def send_message(message, websocket):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")

    with open("messages.txt", "a+") as f:
        f.write(timestamp + message + "\n")

    messages.append(message)
    return websocket.send(message)

async def echo(websocket, port):
    async for message in websocket:
        original_message = message
        
        if ":" in message:
            message = message.split(":")[1].strip()
        
        if message == "connect":
            for m in messages[:5]:
                await websocket.send(m)

            current_time = datetime.datetime.now().strftime("%H:%M")

            await send_message(username + "Hello! 👋 It is currently {}.".format(current_time), websocket)
        else:
            await send_message(original_message, websocket)

        time.sleep(0.5)

        response = process_command.process_command(message, karma)

        if response != "" and response != "connect":
            await send_message(username + response, websocket)

async def main():
    async with websockets.serve(echo, 'localhost', 8765):
        await asyncio.Future()

asyncio.run(main())