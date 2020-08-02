from Config._const import DB_LINK, BRAIN
from Config._functions import is_whole, is_float
from Config._db import Database
from Config._words import WORDS
import random, time

def HELP(PREFIX):
	return {
		"COOLDOWN": 20,
		"MAIN": "Test your typing speed",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}typingtest` will prompt you to type a sequence of random common English words,
		and will report your speed and accuracy when you finish.""".replace("\n", "").replace("\t", ""),
		"HIDE" : 0,
		"CATEGORY" : "Fun"
	}

a = "tc/db add typingtest id-text totype-text start-text best-text"

PERMS = 1 # Members
ALIASES = ["TT"]
REQ = []

db = Database()
zws = "​"

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		totype = " ".join(random.sample(WORDS, random.randrange(45, 61, 1))) # creates list of words

		# adding zero-width spaces between words to prevent copy+paste
		spaced_text = ""
		for i in range(len(totype)):
			spaced_text += totype[i]
			if totype[i] == " ":
				spaced_text += zws

		tt = await message.channel.send(f"""<@{message.author.id}>: 
						Type these {len(totype.split(' '))} words in any order:\n\n{spaced_text}""")

		# adding stuff to database
		if len(db.get_entries("typingtest", conditions={"id" : str(message.author.id)})) == 0:
			db.add_entry("typingtest", [str(message.author.id), totype, str(tt.created_at.timestamp()), "0"])
		else:
			db.edit_entry("typingtest", entry={"totype" : totype, "start" : str(tt.created_at.timestamp())},
				conditions={"id" : str(message.author.id)})

		msg = await BRAIN.wait_for('message', check=(lambda m: m.channel == message.channel and m.author == message.author))
		typed_words = msg.content.lower().split(' ')
		target_words = totype.split(' ')
		success = 0
		chars = 0
		duration = round(msg.created_at.timestamp() - float(db.get_entries("typingtest", limit=50, columns=["start"], 
			conditions={"id": str(message.author.id)})[0][0]), 3)

		# counting total successful characters typed
		for word in typed_words:
			if word in target_words:
				success += 1
				chars += len(word) + 1
				target_words.remove(word)
		chars += -1
		wpm = chars/len(totype) * chars/duration*12 # WPM = CPM / 5
		if success < 10:
			await message.channel.send("Typing test cancelled.") # cancel if there was no attempt
			return
		else:
			player_best = float(db.get_entries("typingtest", limit=50, columns=["best"],
				conditions={"id" : str(message.author.id)})[0][0])
			if wpm > player_best:
				record_message = f"^n^nThat's a new personal best, beating your old best of {round(player_best, 2)} WPM!"
				db.edit_entry("typingtest", entry={"best" : str(wpm)}, conditions={"id" : str(message.author.id)})
			else:
				record_message = ""
			# ^n is used because I want \n in the message but the dark-formatted string replaces \n with nothing
			await message.channel.send(f"""<@{message.author.id}> Typing test finished!^n^n
			Words typed correctly: {success} out of {len(totype.split(' '))} ({round(100*(success/len(totype.split(' '))), 1)}%)^n
			Time: {duration}^nWPM: **{round(wpm, 2)}**{record_message}^n
			""".replace("\n", "").replace("\t", "").replace("^n", "\n"))
		return
	if args[1].lower() == "top":
		await message.channel.send(db.get_entries("typingtest", columns=["best"])[0])
	return
