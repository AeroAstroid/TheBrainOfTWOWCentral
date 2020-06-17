import discord
from Config._db import Database

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Team flair distribution command",
		"FORMAT": "('count'/'options'/'get'/'remove') (team_name/contestant)",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}team options` or just `{PREFIX}team` gives you a list of the current team flairs. 
		Using `{PREFIX}team count` gives you a list of all team flairs and how many people have each one. To get a 
		team flair, use `{PREFIX}team get` followed by either the name of the team or the name of its contestant.
		To remove a team flair that you have, use `{PREFIX}team remove`, followed by either the name of the team or 
		the name of its contestant.""".replace("\n", "").replace("\t", "")
	}

PERMS = 1 # Member
ALIASES = [""]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	db = Database()

	id_search_key = str(SERVER["MAIN"].id)

	roles, contestants, contnames, emojis, limit = db.get_entries(
		"teamdata", columns=["roles", "contestants", "contname", "emojis", "teamlimit"],
		conditions={"server":id_search_key}
	)[0]

	if level == 1:
		role_list = roles.split(" ")

		if contnames != "":
			cont_list = contnames.split(" / ")
		
		if emojis != "":
			emoji_list = emojis.split(" ")

		output = ["Here's a list of available team flairs:\n\n"]

		for t in range(len(role_list)):
			line = ""

			try:
				line += emoji_list[t] + " - "
			except:
				pass

			try:
				line += cont_list[t] + " - "
			except:
				pass

			line += "<@&" + role_list[t] + ">\n"

			if len(output) + len(line) > 1980:
				output.append("")
			
			output[-1] += line

		for m in output:
			await message.channel.send(m)
		return