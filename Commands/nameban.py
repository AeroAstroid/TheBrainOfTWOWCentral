def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Temporary command",
		"FORMAT": "[name_string] [ignore_case]",
		"CHANNEL": 1,
		"USAGE": f"""(Testing command)""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 1 # Member
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a name.")
		return
	
	if level == 2:
		await message.channel.send("Specify case sensitivity.")
		return
	
	ignore_case = args[1].lower() in ["y", "yes", "1", "true"]
	search_key = " ".join(args[2:])
	
	search_key = search_key.lower() if ignore_case else search_key
	
	usernames = [(m.name.lower() if ignore_case else m.name) for m in SERVER['MAIN'].members]
	member_list = [SERVER['MAIN'].members[i] for i in len(usernames) if search_key in usernames[i]]
	usernames = [n for n in usernames if search_key in n]
	
	
	s = '' if len(usernames) == 1 else 's'
	msg = await message.channel.send(
	f"Found {len(member_list)} user{s}.\n{'\n'.join(sorted(usernames[:5]))}\n{'[...]' if len(member_list} > 5 else ''}")
																	
	await msg.add_reaction("🇾")
	await msg.add_reaction("🇳")

	def check(r, u):
		return (u == message.author
		and str(r.emoji) in ["🇾","🇳"]
		and r.message.id == msg.id)

	try:
		r, _ = await BRAIN.wait_for('reaction_add', timeout=30, check=check)

	except asyncio.TimeoutError:
		await message.channel.send("Ban function timed out.")
		return

	else:
		if str(r.emoji) == "🇳":
			await message.channel.send("User(s) will not be banned.")
			return

		try:
			for m in member_list:								
				await SERVER["MAIN"].ban(m, reason="Staff command", delete_message_days=0)
		except discord.Forbidden:
			await message.channel.send("No permission to perform bans.")
