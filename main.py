import os
from dotenv import load_dotenv
import discord


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))


def main():
    load_dotenv()
    client = MyClient()
    client.run(os.getenv("TOKEN"))

main()