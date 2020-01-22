from Config._const import PREFIX
import random

HELP = {
	"COOLDOWN": 1,
	"MAIN": "Obtain advice from the wisdom of Brain's 8 Ball.",
	"FORMAT": "",
	"CHANNEL": 0,
	"USAGE": f"""Using `{PREFIX}8ball` will generate advice from Brain's specialized 8 Ball.
	""".replace("\n", "").replace("\t", "")
}

PERMS = 0 # Non-members
ALIASES = ["8"]
REQ = []

async def MAIN(message, args, level, perms):
	act = random.choice(
		["invest in stocks", "create a bank account", "buy excessive amounts of lotion", "eat a berry",
		"adjust for inflation", "play Terraria Multiplayer with Dark", "vote", "become rich and successful",
		"breathe more often", "be considerate of your surroundings (except for that guy you want to kill)",
		"become a Doomer", "donate to charity", "hug your mother", "invent a new alphabet", "write",
		"eat ice cream", "forgive yourself", "stop coding this command and go to sleep", "respect people",
		"not start drama all of a sudden", "find love", "copyright your real name", "calculate the impedance",
		"fulfill a technical", "buy a building", "discover how chairs are made", "provide helpful advice",
		"use protection", "listen", "jump off a two meter hill", "co-author a paper with Paul Erdős",
		"convert all your data to base e", "play my game", "measure your words", "draw a 50 degree angle",
		"turn left then move onward three hundred meters before turning right to arrive at your destination",
		"count", "acknowledge the corn", "understand", "drink more water", "buy a tree", "rent a satellite",
		"innovate in the field of electromagnetism", "make a speech about motorbikes", "leave", "appreciate",
		"think about our future", "be responsible", "use this command from time to time", "go to the kitchen",
		"look north", "get ready", "book a flight", "spy on some squirrels", "roll some dice",
		"pick up a sheet of paper and then put it back down again", "draw four", "draw something pretty",
		"do the dishes", "create a new planet", "sleep occasionally", "smile", "reflect on the concept of a grid",
		"come up with a way to recycle door handles", "open the door"])
	await message.channel.send(f"🎱 The 8 Ball says you should {act}.")
	return