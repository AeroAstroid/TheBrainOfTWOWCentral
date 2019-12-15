from Config._const import PREFIX, DB_LINK, BRAIN
from Config._functions import is_whole, is_float
from Config._db import Database
from Config._words import WORDS
import random, time

HELP = {
	"MAIN": "Test your typing speed",
	"FORMAT": "",
	"CHANNEL": 0,
	"USAGE": f"""Using `{PREFIX}typingtest` will prompt you to type a sequence of random common English words,
    and will report your speed and accuracy when you finish.""".replace("\n", "").replace("\t", ""),
	"HIDE" : 1
}

a = "tc/db add typingtest id-text totype-text start-text best-text"

PERMS = 1 # Members
ALIASES = ["TT"]
REQ = []

db = Database()
zws = "​"

async def MAIN(message, args, level, perms):
	totype = " ".join(random.sample(WORDS, random.randrange(45, 61, 1)))
	if len(db.get_entries("typingtest", conditions={"id" : str(message.author.id)})) == 0:
		db.add_entry("typingtest", [str(message.author.id), totype, str(time.time()), "0"])
	else:
		db.edit_entry("typingtest", entry={"totype" : totype, "start" : str(time.time())}, conditions={"id" : str(message.author.id)})
	spaced_text = ""
	for i in range(len(totype)):
		spaced_text += totype[i]
		spaced_text += "​"
	await message.channel.send(f"<@{message.author.id}>: Type these {len(totype.split(' '))} words:\n\n{spaced_text}")
	return
