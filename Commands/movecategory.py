import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Moves a category to above or below another one",
		"FORMAT": "[category_to_move] [`-above`/`-below`] [reference_category]",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}movecategory A -above B` moves the category A to right above the category B. 
		Using `{PREFIX}movecategory A -below B` moves category A to right below category B.
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 2 # Staff
ALIASES = ["MOVEC"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Please enter a category to move.")
		return
	
	modes = ["-above", "-below"]
	mode_picked = [m for m in modes if m in args]

	if not mode_picked:
		await message.channel.send("Please include either `-above` or `-below` as a move mode!")
		return
	
	mode_picked = mode_picked[0]

	delimiter_ind = args.index(mode_picked)
	to_move = " ".join(args[1:delimiter_ind])
	reference = " ".join(args[(delimiter_ind+1):])

	category_list = [c for c, ch_list in SERVER["MAIN"].by_category() if c is not None]
	category_names = [c.name.lower() for c in category_list]

	if to_move.lower() not in category_names:
		await message.channel.send(f"Couldn't find category {to_move}!")
		return
	
	if reference.lower() not in category_names:
		await message.channel.send(f"Couldn't find category {reference}!")
		return
	
	to_move_obj = category_list[category_names.index(to_move.lower())]
	reference_obj = category_list[category_names.index(reference.lower())]

	if mode_picked == "-above":
		await to_move_obj.move(before=reference_obj)
	elif mode_picked == "-below":
		await to_move_obj.move(after=reference_obj)
	
	await message.channel.send("Successfully moved category!")
	return
  
