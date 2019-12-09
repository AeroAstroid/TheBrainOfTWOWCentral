import discord, os
from datetime import datetime

# These are both secret, so I keep them as environment variables
TOKEN = os.getenv("BRAIN_DEBUG") # Debug bot's token
DB_LINK = os.getenv("BRAIN_DB") # Postgres DB link

BRAIN = discord.Client() # The bot object

CURRENT_DAY = datetime.utcnow().day # For event handler purposes

PREFIX = "tc/" # Command prefix

STAFF_ID = 653673640357003297 # Staff role
TWOW_CENTRAL_ID = 653673010821201920 # Server
MEMBER_ID = 653673666491449345 # Member role

PUBLIC_CHANNELS = (
	653673010821201923, #general
	653673194171006996, #game-room
	653673209291341834  #bots-memes
)

BOT_CHANNELS = (
	653673194171006996, #game-room
	653673209291341834  #bots-memes
)

GAME_CHANNEL = 653673194171006996 #game-room
LOG_CHANNEL = 653673395954647095 #logs

# For MMT purposes
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"