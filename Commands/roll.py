from random import randint
import os, discord
import re, cexprtk, math


def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Rolls up to 10,000 dice that can also be used in arbitrary mathematical statements.",
		"FORMAT": "(rolls)",
		"CHANNEL": 0,
		"USAGE": f"""	Rolls up to 10,000 dice that can also be used in arbitrary mathematical statements. You can separate sets of dice with semicolons. 
  The syntax for a die roll is as follows: `[number of dice rolled]d[size of dice]`. For example, `1d6` will roll one six-sided die. 
  If you wish to only keep certain rolls, you can follow up the roll with `kh[num]` (for keep highest) or `kl[num]` (for keep lowest). 
  For example, `2d20kh1` will keep the highest one roll out of two 20-sided dice. You can use this dice syntax alongside basic arithmetic operations, such as 2d8+3d6+5, or 1d20-2. The maximum dice size is 100,000.
""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}
  
PERMS = 1 # Non-members
ALIASES = ["dice"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.reply("Please enter a roll! Example: `2d6`")
		return
  
	args = args[1:].join(" ")
	
	while "  " in args:
		args = args.replace("  ", " ")
	
	maxval = 0
	minval = 0
	outStr = ""
	total = 0
	total_rolls = 0
	
	roll_strings = args.split(";")
	print(roll_strings)
	
	for roll_str in roll_strings:
		finalRolls = []
		try:
	
			expression_string = roll_str.strip()
			expression_string = expression_string.replace("while","#####")
	
			match = re.finditer(r"[0-9]*d[0-9]*(k.[0-9]*)?", expression_string)
			if match:
				for s in match:
					s = s[0]
					try:
						groups = s.replace("k","d").split("d")
						rollct = int(groups[0]) if groups[0] != "" else 1
						rollsize = min(100000,int(groups[1]))
	
						total_rolls += rollct
						if total_rolls > 10000:
							await message.reply("Sorry, but you can only roll up to 10,000 dice at once.")
							return
	
						rolls = [randint(1,rollsize) for x in range(rollct)]
						keepct = rollct
	
						if len(groups) >= 3:
							keepct = int(groups[2][1:])
							rollsKept = sorted([(rolls[x], x) for x in range(rollct)], key=lambda x: x[0],reverse=groups[2][0]=='h')[:keepct]
							rollsKept = {x[1]: x[0] for x in rollsKept}
						else:
							rollsKept = {x: rolls[x] for x in range(rollct)}
						
						keptKeys = rollsKept.keys()
						outrolls = [["**"+str(rollsKept[x])+"**" if x in keptKeys and rollct != keepct else rolls[x] for x in range(rollct)], sum(rollsKept.values()), s]
						finalRolls.append(outrolls)
	
						expression_string = expression_string.replace(s, str(outrolls[1]), 1)
						maxval += keepct*rollsize
						minval += keepct
	
					except Exception as ignored:
						print(ignored)
						await message.reply(f"Sorry, but {s} is not a valid die roll.")
						return
	
				
			output = cexprtk.evaluate_expression(expression_string, {})
			if output % 1 == 0: output = int(output)
			else: output = round(output,5)
			
			current_total = output
			total += output
	
		except Exception as e:
			await message.reply("There was an error in parsing your rolls. Are you sure your syntax is correct?")
			return
			
		for x in finalRolls: 
			temp = ",".join([str(y) for y in x[0]])
			if len(temp) > 250:	temp = temp[0:250]+"..."
			outStr += f'\n**{x[2]}** : {temp} => {x[1]}'
		outStr += f'\nTotal: **{current_total}**'
	
	try: hue = max(0,min(1,(total-minval)/(maxval-minval))*0.42)
	except: hue = 0.21
	color = discord.Colour.from_hsv(hue,.80,.80)
	print(color.r, color.g, color.b, color.value)
	e = discord.Embed(title=f"🎲 Rolling {args.strip()} 🎲",description=outStr, color=color.value)
	await message.reply(embed=e)
			
