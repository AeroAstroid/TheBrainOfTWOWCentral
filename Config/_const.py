import discord, os
from datetime import datetime, timezone

WARNING_APP = os.getenv("WARNING_APP") # Link to warning sheet web app
DB_LINK = os.getenv("BRAIN_DB") # Postgres DB link

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


BRAIN = discord.Client(intents=intents) # The bot object

CURRENT_HOUR = datetime.now(timezone.utc).hour # For event handler purposes

# For MMT purposes
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

ALPHANUM_UNDERSCORE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"


ORIGINAL_DECK = [
	"10", "20", "30", "40", "11", "21", "31", "41", "12", "22", "32", "42", "13", "23", "33", "43",
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
