HELP = "Deletes past messages under certain conditions"
PERMS = 2
ALIASES = ["PRUNE"]
REQ = []

async def MAIN(message, args, level, perms):
	if level == 1:
		await message.channel.send("Provide information on which messages to clean!")
		return
	
	limit = 1
	after = None
	user = None
	silent = False

	for arg in args:
		try:
			if arg.lower().startswith("limit:"):
				limit = int(arg[6:])
		except Exception:
			await message.channel.send("Invalid message limit!")
			return
		
		try:
			if arg.lower().startswith("after:"):
				after = int(arg[6:])
		except Exception:
			await message.channel.send("Invalid ID to take as time boundary!")
			return
		
		try:
			if arg.lower().startswith("user:"):
				user = int(arg[5:])
		except Exception:
			await message.channel.send("Invalid user ID!")
			return
		
		if arg.lower() == "silent":
			silent = True
	
	if not silent:
		limit += 1
	
	def check(msg):
		status = True

		if not silent and message.id == msg.id:
			return False

		if after is not None:
			status = status and msg.id >= after
		
		if user is not None:
			status = status and msg.author.id == user
		
		return status
	
	deleted = await message.channel.purge(limit=limit, check=check)

	if not silent:
		limit -= 1
		await message.channel.send(f"Searched {limit} message{'' if limit == 1 else 's'}, deleted {len(deleted)}.")
	return