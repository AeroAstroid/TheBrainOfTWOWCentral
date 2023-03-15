from Config._functions import is_whole
from Config._const import BRAIN
import random
import numpy as np

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "A simple, guess the number game",
		"FORMAT": "[mode] (upper_bound)",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}guessthenumber [mode] (upper_bound)` will make the bot generate a number between 
		1 and `upper_bound`. If the parameter is not specified, it'll default to 100. The bot will give you hints 
		depending on what mode you chose. Current available modes are `simple`: gives you no hints, `factors`: gives 
		you two factors of the number (or notifies you if it doesn't have enough non-trivial factors), `digits`: gives 
		you half of the number's digits in advance.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 0 # Non-members
ALIASES = ["GTN", "GUESS"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send(
			"Pick a mode for the guessing game! Current available modes are `simple`, `factors` and `digits`.")
		return
	
	mode = args[1].lower()

	if level == 2:
		upper_bound = 100
	elif not is_whole(args[2]):
		await message.channel.send("Pick an integer between 2 and 1000000000 for the upper bound!")
		return
	elif 2 > int(args[2]) or int(args[2]) > 1000000000:
		await message.channel.send("Pick an integer between 2 and 1000000000 for the upper bound!")
		return
	elif int(args[2]) > 100000 and mode == "factors":
		await message.channel.send("For the `factors` mode, pick an integer between 2 and 100000!")
		return
	else:
		upper_bound = int(args[2])
	
	number = random.randint(1, upper_bound)

	hint = ""

	if mode != "simple":
		if mode == "digits":
			hint = list(str(number))
			blanks = random.sample(range(len(hint)), int(len(hint)/2))
			for ind in blanks:
				hint[ind] = "█"
			hint = f"**{''.join(hint)}**"
		
		elif mode == "factors":
			factors = []
			for i in range(2, number):
				if number % i == 0:
					factors.append(i)
			if number == 1:
				hint = "The number is a perfect square (only one non-trivial factor)." # probably the best hint without entirely giving it away
			elif len(factors) == 0:
				hint = "The number is prime!"
			elif len(factors) == 1:
				hint = "The number is a perfect square (only one non-trivial factor)."
			else:
				factor_list = ", ".join([str(x) for x in random.sample(factors, 2)])
				hint = f"Two of its factors are **{factor_list}**."
		
		else:
			await message.channel.send(
				"That mode does not exist! Current available modes are `simple`, `factors` and `digits`.")
			return
	
		hint = f"**Number Hint** : {hint}"

	await message.channel.send(f"""**Generated a number between 1 and {upper_bound}.** Send a guess for the number!
	{hint}""".replace("\t", ""))

	msg = await BRAIN.wait_for('message', 
	check=lambda m: (m.author == message.author and m.channel == message.channel))

	if not is_whole(msg.content):
		await message.channel.send("Invalid number. Guess command cancelled.")
		return
	
	guess = int(msg.content)

	result = "**You've guessed correctly!**" if guess == number else "You were wrong."
	
	await message.channel.send(f"""{message.author.mention} {result}
	The number generated between **1** and **{upper_bound}** was **{number}**.
	Your guess was **{guess}**.
	You played on **`{mode}`** mode.""".replace("\t", ""))
	return
