from discord import *
from discord.ext import bridge

import sys
import os
from time import time

if (DEBUG_MODE := "debug" in [a.lower() for a in sys.argv]):
	print("\nStarting up bot in development mode\n")
	
	TOKEN = os.getenv("DEBUG_TOKEN")
	DB_LINK = os.getenv("DEBUG_DB")
	MAIN_SERVER = 653673010821201920
	PREFIX = "debug/"

else:
	print("\nStarting up bot in production mode\n")

	TOKEN = os.getenv("DEBUG_TOKEN") # TOKEN = os.getenv("BRAIN_TOKEN")
	DB_LINK = os.getenv("DEBUG_DB") # DB_LINK = os.getenv("BRAIN_DB")
	MAIN_SERVER = 653673010821201920 # MAIN_SERVER = 481509601590771724
	PREFIX = "tc/"

intents = Intents.default()
intents.members = True
intents.message_content = True

BRAIN = bridge.Bot(command_prefix=PREFIX, intents=intents, debug_guilds=[653673010821201920])
BRAIN.allowed_mentions = AllowedMentions(replied_user=False, everyone=False)
BRAIN.remove_command('help')

STARTUP = time()