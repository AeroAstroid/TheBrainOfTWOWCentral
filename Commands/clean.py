def HELP(PREFIX):
	return {
		"COOLDOWN": 5,
		"MAIN": "Deletes past messages under certain conditions",
		"FORMAT": "[limit:] (after:) (user:) ('silent')",
		"CHANNEL": 2,

		"USAGE": f"""Using `{PREFIX}clean [limit:]` cleans the number of messages specified in `[limit:]` in the channel 
		the command was used in. The parameters `(after:)` and `(user:)` can be used to specify a limit of when to stop 
		deleting or whose messages to delete. Including the parameter `('silent')` performs the operation "silently", 
		sending no confirmation message and deleting the command message as well.""".replace("\n", "").replace("\t", "")
	}

PERMS = 2 # Staff
ALIASES = ["PRUNE"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Provide information on which messages to clean!")
		return
	
	# Variables for all the different parameters for the clean command
	limit = 1
	after = None
	user = None
	silent = False

	for arg in args:
		try: # Try to detect message limit
			if arg.lower().startswith("limit:"):
				limit = int(arg[6:])
		except Exception:
			await message.channel.send("Invalid message limit!")
			return
		
		try: # Try to detect time boundary ID
			if arg.lower().startswith("after:"):
				after = int(arg[6:])
		except Exception:
			await message.channel.send("Invalid ID to take as time boundary!")
			return
		
		try: # Try to detect specific user from whom to target
			if arg.lower().startswith("user:"):
				user = int(arg[5:])
		except Exception:
			await message.channel.send("Invalid user ID!")
			return
		
		if arg.lower() == "silent": # Detect silent mode
			silent = True
	
	# This is necessary in both silent *and* non-silent, so that it can start counting [limit] messages
	# *after* it checks the command message itself. Whether or not that command message is deleted depends
	# on whether silent is activated, but it always has to be checked
	limit += 1
	
	def check(msg):
		status = True

		if not silent and message.id == msg.id:
			return False # Signal that this is the command message and silent == False, so it shouldn't be deleted

		if after is not None: # if [after] is specified, enforce it
			status = status and msg.id >= after
		
		if user is not None: # if [user] is specified, enforce it
			status = status and msg.author.id == user
		
		return status
	
	deleted = await message.channel.purge(limit=limit, check=check)

	if not silent: # confirmation message only if it's not silent
		limit -= 1 # display the limit as the original value chosen by the command user
		await message.channel.send(f"Searched {limit} message{'' if limit == 1 else 's'}, deleted {len(deleted)}.")
	return