from Config._const import PREFIX
import random

HELP = {
	"COOLDOWN": 1,
	"MAIN": "Meme command 2",
	"FORMAT": "",
	"CHANNEL": 0,
	"USAGE": f"""Using `{PREFIX}8ball` will sure do something""".replace("\n", "").replace("\t", "")
}

PERMS = 0 # Non-members
ALIASES = ["8"]
REQ = []

async def MAIN(message, args, level, perms):
	act = random.choice(
		["invest in stocks", "create a bank account", "buy excessive amounts of lotion", "eat a berry",
		"adjust for inflation", "play Terraria Multiplayer with Dark", "vote", "become rich and successful",
		"breathe more often", "be considerate of your surroundings, except for that guy you want to kill",
		"become a Doomer", "donate to charity", "hug your mother", "invent a new alphabet", "write",
		"eat ice cream", "forgive yourself", "stop coding this command and go to sleep"])
	await message.channel.send(f"🎱 The 8 Ball says you should {act}.")
	return