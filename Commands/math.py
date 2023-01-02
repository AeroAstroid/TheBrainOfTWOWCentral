# this is probably the only command, i, pepsi#1213 will have added to tbotc unless i become a full on dev (unlikely)
# it's nice to have contributed even if i'm just re-using someone else's module and dark fixed my syntax because i'm bad 

import discord, cexprtk, math, random

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Evaluates a mathematical expression.",
		"FORMAT": "[expression]",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}math` will evaluate the arguments provided thereafter as a mathematical expression.  
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 0 # Non-members
ALIASES = ["eval","calc","maths"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Please enter a mathematical expression to evaluate.")
		return
	
	try:
		expression_string = " ".join(args[1:]).strip()
		while expression_string.startswith("`") and expression_string.endswith("`"):
			expression_string = expression_string[1:-1]
			
		st = cexprtk.Symbol_Table(variables={"e": math.e, "phi": (1 + math.sqrt(5))/2},add_constants=True, functions={"rand":random.uniform})
		e = cexprtk.Expression(expression_string, st)
		output = e.value()
		if output % 1 == 0: output = int(output)
		else: output = round(output,15)
		
		if math.isnan(output) and len(e.results()) != 0: output = str(e.results())[1:-1]
		
		await message.channel.send(embed=discord.Embed(title=f"Expression result:", description=str(output)[:2000]))
	except Exception as e:
		await message.channel.send("There was an error in parsing your statement.")
		raise e
	return
  
