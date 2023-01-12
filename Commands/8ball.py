import random

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Obtain advice from the wisdom of Brain's 8 Ball.",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}8ball` will generate advice from Brain's specialized 8 Ball.
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 0 # Non-members
ALIASES = ["8", "8b"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	a = random.choice(
		["invest in [stock]", "create a/an [item]", "buy excessive amounts of [item]", "eat a/an [food]",
		"adjust for [in/deflation]", "play [game] multiplayer with [staff member]", "vote", "become rich and successful",
		"breathe more often", "be considerate of your surroundings ([threat])", "become a [letterCapital]oomer"]
	#       "donate to charity", "hug your mother", "invent a new alphabet", "write",
	#	"eat ice cream", "forgive yourself", "stop coding this command and go to sleep", "respect people",
	#	"not start drama all of a sudden", "find love", "copyright your real name", "calculate the impedance",
	#	"fulfill a technical", "buy a building", "discover how chairs are made", "provide helpful advice",
	#	"use protection", "listen", "jump off a two meter hill", "co-author a paper with Paul Erdős",
	#	"convert all your data to base e", "play my game", "measure your words", "draw a 50 degree angle",
	#	"turn left then move onward three hundred meters before turning right to arrive at your destination",
	#	"count", "acknowledge the corn", "understand", "drink more water", "buy a tree", "rent a satellite",
	#	"innovate in the field of electromagnetism", "make a speech about motorbikes", "leave", "appreciate",
	#	"think about our future", "be responsible", "use this command from time to time", "go to the kitchen",
	#	"look north", "get ready", "book a flight", "spy on some squirrels", "roll some dice",
	#	"pick up a sheet of paper and then put it back down again", "draw four", "draw something pretty",
	#	"do the dishes", "create a new planet", "sleep occasionally", "smile", "reflect on the concept of a grid",
	#	"come up with a way to recycle door handles", "open the door"]
		)
	act = parse_brackets(a) # keep in mind that it replaces all instances with the same
	await message.channel.send(f"🎱 The 8 Ball says you should {act}.")
	return

# parse brackets like [item] #

def parse_brackets(string):
	string = string.replace("[item]",
		random.choice(
			["blackberry", "stock", "stonks", "lotion", "games", "food", "toilet paper"]
		)	       
	)
	
	string = string.replace("[stock]",
		random.choice(
			["blackberry", "stock", "stonks", "lotion brands", "game corporations", "apple", "microsoft", "twow central corp"]
		)	       
	)
	
	string = string.replace("[food]",
		random.choice(
			["blackberry", "berry", "blueberry", "apple", "tomato", "pizza"]
		)	       
	)
	
	string = string.replace("[in/deflation]",
		random.choice(
			["inflation", "deflation"]
		)	       
	)
	
	string = string.replace("[game]",
		random.choice(
			["minecraft", "roblox", "terraria", "geometry dash"]
		)	       
	)
	
	string = string.replace("[staff member]",
		random.choice(
			["Dark"] # i don't want to add staff members if they don't want to be here, original prompt had dark
		)	       
	)
		
	string = string.replace("[game]",
		random.choice(
			["minecraft", "roblox", "terraria", "geometry dash"]
		)	       
	)
	
	string = string.replace("[threat]",
		random.choice(
			["except for that guy you want to kill", "except when you want to destroy twow central",
			 "except when they don't let you alphabet vote", "even though the swat team is at your house"]
		)	       
	)
	
	string = string.replace("[letterCapital]",
		random.choice("QWERTYUIOPASDFGHJKLZXCVBNM")	       
	)
