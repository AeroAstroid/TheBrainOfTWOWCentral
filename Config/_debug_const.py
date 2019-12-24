import discord, os
from datetime import datetime

# These are both secret, so I keep them as environment variables
TOKEN = os.getenv("BRAIN_DEBUG") # Debug bot's token
DB_LINK = os.getenv("BRAIN_DB") # Postgres DB link

BRAIN = discord.Client() # The bot object

CURRENT_HOUR = datetime.utcnow().hour # For event handler purposes

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

BIRTHDAY_ROLE = 653771648616366103
BOT_ROLE = 654094896562438154
MEMES = 656641155869704205

# For MMT purposes
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

ORIGINAL_DECK = ["10", "20", "30", "40", "11", "21", "31", "41", "12", "22", "32", "42", "13", "23", "33", "43", "14", "24", "34", "44", "15", "25", "35", "45", "16", "26", "36", "46", "17", "27", "37", "47", "18", "28", "38", "48", "19", "29", "39", "49", "1D", "2D", "3D", "4D", "1R", "2R", "3R", "4R", "1S", "2S", "3S", "4S", "10", "20", "30", "40", "11", "21", "31", "41", "12", "22", "32", "42", "13", "23", "33", "43", "14", "24", "34", "44", "15", "25", "35", "45", "16", "26", "36", "46", "17", "27", "37", "47", "18", "28", "38", "48", "19", "29", "39", "49", "1D", "2D", "3D", "4D", "1R", "2R", "3R", "4R", "1S", "2S", "3S", "4S", "0F", "0F", "0F", "0F", "0C", "0C", "0C", "0C"]

OPTION_DESC = {
	"0-7": "0 rotates hands, 7 trades hands",
	"d-skip": "Players hit with a +2/+4 are skipped",
	"start": "Starting card count ($)"
}

UNO_INFO = {
	"running": False,
	"status": 0,
	"players": [],
	"order": [],
	"hands": [],
	"host": 0,
	"current": 0,
	"deck": ORIGINAL_DECK,
	"last_card": "00",
	"draw_carryover": 0,
	"channel": 0,
	"config": {"0-7": False, "d-skip": True, "start": 7}
}