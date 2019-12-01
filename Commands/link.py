from Config._links import LINKS
from Config._const import PREFIX
from Config._functions import grammar_list

HELP = {
	"MAIN": "Provides useful links to community sheets and/or projects",
	"FORMAT": "(link)",
	"CHANNEL": 1,
	"USAGE": f"""Using `{PREFIX}link` returns a list of available links. Including one of those as the `(link)` 
	parameter will grant you that link, and information on it.""".replace("\n", "").replace("\t", "")
}

PERMS = 1
ALIASES = ["L"]
REQ = []

async def MAIN(message, args, level, perms):
	if level == 1:
		await message.channel.send(f"Here's a list of link commands available:\n\n{grammar_list(list(LINKS.keys()))}")
		return

	if args[1].upper() not in LINKS.keys():
		await message.channel.send("That link cannot be found.")
		return
	
	requested = args[1].upper()
	await message.channel.send(f"{LINKS[requested]['INFO']}\n\n**Link :** {LINKS[requested]['MAIN']}")
	return