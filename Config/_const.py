import discord, os
from datetime import datetime

# These are both secret, so I keep them as environment variables
TOKEN = os.getenv("BRAIN_TOKEN") # Bot's token
DB_LINK = os.getenv("BRAIN_DB") # Postgres DB link

BRAIN = discord.Client() # The bot object

CURRENT_HOUR = datetime.utcnow().hour # For event handler purposes

PREFIX = "tc/" # Command prefix

STAFF_ID = 481991172106092554 # Staff role
TWOW_CENTRAL_ID = 481509601590771724 # Server
MEMBER_ID = 481950361783894017 # Member role

PUBLIC_CHANNELS = (
	481509602035236865, #general
	481534463608619038, #rec-room
	598616636823437352, #game-room
	481535292541501452, #twow-discussion
	481534865045717013, #art-studio
	481534925997211658, #server-discussion
	481534942279630856, #bots-memes
	534909693580017685, #voting
	481535329199980564, #general-hosting
	481549073401511952, #aesthetics
	481549091298344961, #technologies
	481549106662211588, #presentation
	481549059656777739, #innovations
	614117909693857819  #vc-general
)

BOT_CHANNELS = (
	481534942279630856, #bots-memes
	598616636823437352  #game-room
)

GAME_CHANNEL = 598616636823437352 #game-room
LOG_CHANNEL = 653677748832698378 #brain-logs
MEMES = 656639194415759371 #memés

BIRTHDAY_ROLE = 653630098813222943
BOT_ROLE = 654072824318918677

# For MMT purposes
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

ORIGINAL_DECK = ["10", "20", "30", "40", "11", "21", "31", "41", "12", "22", "32", "42", "13", "23", "33", "43",
                 "14", "24", "34", "44", "15", "25", "35", "45", "16", "26", "36", "46", "17", "27", "37", "47",
                 "18", "28", "38", "48", "19", "29", "39", "49", "1D", "2D", "3D", "4D", "1R", "2R", "3R", "4R",
                 "1S", "2S", "3S", "4S", "10", "20", "30", "40", "11", "21", "31", "41", "12", "22", "32", "42",
                 "13", "23", "33", "43", "14", "24", "34", "44", "15", "25", "35", "45", "16", "26", "36", "46",
                 "17", "27", "37", "47", "18", "28", "38", "48", "19", "29", "39", "49", "1D", "2D", "3D", "4D",
                 "1R", "2R", "3R", "4R", "1S", "2S", "3S", "4S", "0F", "0F", "0F", "0F", "0C", "0C", "0C", "0C"]


OPTION_DESC = {
	"0-7": "0 rotates hands, 7 trades hands",
	"d-skip": "Players hit with a +2/+4 are skipped",
	"start": "Starting card count ($)",
	"no-cards": "Publicly announces when you have no cards to play"
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
	"carryover": 0,
	"channel": 0,
	"config": {"0-7": False, "d-skip": True, "start": 7, "no-cards": True}
}