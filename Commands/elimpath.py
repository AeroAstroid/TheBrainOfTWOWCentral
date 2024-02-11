import os, discord
from math import *

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Calculate a TWOW elimination path given a contestant count and elimination rate.",
		"FORMAT": "(contestants) (elim rate) (dx) (limit)",
		"CHANNEL": 0,
		"USAGE": f"""Contestants refers to the initial player count, which defaults to 491. 
  			Elim rate refers to the initial elimination rate of the TWOW, which defaults to 20%. 
     			DX is the change (positive or negative) in the elimination rate each round. This defaults to 0. 
			Limit is the limit of the elimination rate. It will never go above or below this number depending on if DX is positive or negative. This defaults to 1.
""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 1 # Non-members
ALIASES = []
REQ = []

def better_round(n):
	if n % 1 >= 0.5: return ceil(n)
	else: return floor(n)

def parse_str(n, x):
	try:
		float(n[:-1] if n[-1] == "%" else n)
	except:
		return None

	if n[-1] == "%":
		n = float(n[:-1]) / 100
	else:
		n = float(n)
	return max(n, x) if x is not None else n

async def MAIN(message, args, level, perms, SERVER):
  contestants = 491
  elimrate = "20%"
  dx = "0%"
  limit = "100%"

  if level > 1:
    contestants = args[1]
  if level > 2:
    elimrate = args[2]
  if level > 3:
    dx = args[3]
  if level > 4:
    limit = args[4]
  
  try: contestants = int(contestants)
  except: 
    await message.reply("Please enter a whole number of contestants greater than or equal to 2.")
    return

  if contestants < 2: 
    await message.reply("Please enter a contestant count greater than or equal to 2.")
    return

  elimrate = parse_str(elimrate, 0.00001)
  if elimrate is None:
    await message.reply("Please enter a valid value for the elimination rate, such as 0.2 or 20%.", ephemeral=True)

  dx = parse_str(dx, None)
  if dx is None:
    await message.reply("Please enter a valid value for dx, such as 0.05 or 5%.", ephemeral=True)

  limit = parse_str(limit, 0)
  if limit is None:
    await message.reply("Please enter a valid value for the limit, such as 0.5 or 50%.", ephemeral=True)

  rounds = []
  i = contestants
  while i > 1:
    rounds.append(i)
    i = max(1, min(i-1, i-better_round(i*elimrate)))			
    elimrate += dx
    if dx < 0: elimrate = max(limit, elimrate)
    else: elimrate = min(limit, elimrate)	
  rounds.append(1)	

  slist = rounds[:-1]
  sliced = False
  while len("'** > **".join([str(x) for x in slist])) > 1700 - len(str(contestants)):
    slist = slist[:-1]
    sliced = True
  
  if dx == 0:
    alumni_index = int((len(rounds)-1)//2)
  else:
    to_find = int(contestants**0.5//1)
    alumni_index = 0
    while rounds[alumni_index] > to_find: alumni_index += 1
    alumni_index -= 1

  plural = len(rounds) != 2

  out = f"Your TWOW will last **{len(rounds)-1}** round{'s' if plural else ''}, and here's how {'they' if plural else 'it'}'ll go:\n"
  out += f"**{'** > **'.join([str(x) for x in slist])}**{' ...' if sliced else ''} > **1**\n\n"
  out += f"Consider making **alumni-deciding** round{'s' if alumni_index != 0 else ''} {'**'+str(alumni_index)+'**' if alumni_index != 0 else ''}{' or ' if alumni_index != 0 else ''}**{alumni_index + 1}**! (Alumni count **{'** or **'.join([str(x) for x in rounds[alumni_index:alumni_index+2]])}**)"
  if dx == 0 and elimrate <= 0.05: out += "*Note that alumni counts are less accurate with lower elimination rates."
  await message.reply(out)
  return
