import discord, cexprtk, math

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Evaluates a mathematical expression.",
		"FORMAT": "[expression]",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}math` will evaluate the first provided argument as a mathematical expression.  
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 0 # Non-members
ALIASES = ["eval","calc"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Please enter a mathematical expression to evaluate.")
  else:
    try: 
      output = cexprtk.evaluate_expression(args[0],{"pi" : math.pi})
      if output % 1 == 0: output = int(output)
		  await message.channel.send(str(output)[:15])
	  except:
      await message.channel.send("Something went wrong. Please try again.")
    return
  
