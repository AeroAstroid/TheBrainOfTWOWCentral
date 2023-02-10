from Config._links import LINKS
from Config._functions import grammar_list
from discord import Embed

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Provides useful links to community sheets and/or projects",
		"FORMAT": "(link)",
		"CHANNEL": 1,
		"USAGE": f"""Using `{PREFIX}link` returns a list of available links. Including one of those as the `(link)` 
		parameter will grant you that link, and information on it.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 1 # Member
ALIASES = ["L"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	# Note: this takes data from Config/_links.py, which is where I store all link info

	if level == 1: # If it's just `tc/l`, provide a list of the links available
		await message.channel.send(embed=Embed(color=0x6168d4,description=f"Here's a list of link commands available:\n\n{grammar_list(list(LINKS.keys()))}"))
		return

	if args[1].upper() not in LINKS.keys(): # The link does not exist
		await message.channel.send(embed=Embed(color=0xFF0000,description="That link cannot be found."))
		return
	
	requested = args[1].upper() # Provide the link and info on it
	await message.channel.send(embed=Embed(color=0x61e643,description=f"[{LINKS[requested]['INFO']}]({LINKS[requested]['MAIN']})")) # the [bla](domain) should make a link
	return
