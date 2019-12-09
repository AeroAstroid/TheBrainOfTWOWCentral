from Config._const import PREFIX
import random

HELP = {
	"MAIN": "Meme command",
	"FORMAT": "",
	"CHANNEL": 0,
	"USAGE": f"""Using `{PREFIX}tonguebattle` will kill God""".replace("\n", "").replace("\t", "")
}

PERMS = 0 # Non-members
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms):
	choice = random.choice(["won", "lost"])
	await message.channel.send(f"You {choice} the tongue battle.")
	return