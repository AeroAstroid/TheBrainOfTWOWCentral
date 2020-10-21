import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 10,
		"MAIN": "Searches between two message IDs",
		"FORMAT": "[channel:] (before:) (after:) (limit:) (content:)",
		"CHANNEL": 2,
		"USAGE": f"""Using `{PREFIX}search` will trigger a search command using bot message history. 
		You can specify different options for searching `(before:)` an ID, `(after:)` an ID, searching only though a 
		certain `(limit:)` of messages and in a specific `[channel:]`. **You must include at least one of `(after:)` or 
		`(limit:)`.**""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 2 # Staff
ALIASES = ["S"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include the channel(s) to search in!")
		return
	
	if perms == 3 and args[1].lower() == "findsmiley":
		recorded_count = 0
		counter = await message.channel.send(f"Searching for le smiley... Found 0 messages so far.")
		msg_links = []

		print(SERVER["MAIN"].text_channels)

		for chnl in SERVER["MAIN"].text_channels:
			try:
				async for msg_history in chnl.history():
					recorded_count += 1
					if recorded_count % 1000 == 0:
						await counter.edit(
						content=f"Searching for le smiley... Found {len(msg_links)} / {recorded_count} messages so far.")
					
					for r in msg_history.reactions:
						if r.emoji == "😃":
							print(f"smiley in {msg_history.id}")
							async for user in r.users():
								if user.id == 322153346020671488:
									msg_links.append(msg_history.jump_url)
									print(msg_history.jump_url)
			except discord.errors.Forbidden:
				continue
		
		if len(msg_links) == 0:
			await message.channel.send("found none")
		else:
			await message.channel.send("\n".join(msg_links[:10]))
		return
	
	included_args = {
		"channel": message.content.lower().find("channel:") > -1,
		"after": message.content.lower().find("after:") > -1,
		"before": message.content.lower().find("before:") > -1,
		"limit": message.content.lower().find("limit:") > -1
	}

	if not included_args["channel"]:
		await message.channel.send("Include the channel(s) to search in!")
		return
	
	if not included_args["after"] and not included_args["limit"]:
		await message.channel.send("Include either an `after:` or a `limit:`!")
		return
	
	msg = message.content.lower()

	if msg[msg.find("channel:") + 8] == "[":
		end_index = msg[msg.find("channel:") + 8:].find("]")
		if end_index == -1:
			await message.channel.send("You forgot to close the square brackets!")
			return

		end_index += msg.find("channel:") + 8

		try:
			channels = [int(x[2:-1]) for x in msg[msg.find("channel:") + 9:end_index].split(" ")]
		except ValueError:
			await message.channel.send(f"Invalid channel! Make sure all specified channels are valid.")
			return
		
		channels = [discord.utils.get(SERVER["MAIN"].channels, id=x) for x in channels]
		channels = [x for x in channels if x is not None]

	else:
		for param in args[1:]:
			if param.lower().startswith("channel:"):
				try:
					channel = int(param[8:][2:-1])
					break
				except ValueError:
					await message.channel.send(f"Invalid channel `{param[8:]}`! Make sure it's a valid channel.")
					return
		
		if discord.utils.get(SERVER["MAIN"].channels, id=channel) is None:
			await message.channel.send(f"Invalid channel `{param[8:]}`! Make sure it's a valid channel.")
			return
		
		channels = [discord.utils.get(SERVER["MAIN"].channels, id=channel)]

	after = None
	before = None
	limit = 100000
	content = None

	for param in args[1:]:
		if param.lower().startswith("after:"):
			try:
				after = int(param[6:])
				after = discord.Object(after)
			except ValueError:
				await message.channel.send(f"Invalid message ID for `after:` parameter!")
				return
		
		if param.lower().startswith("before:"):
			try:
				before = int(param[7:])
				before = discord.Object(before)
			except ValueError:
				await message.channel.send(f"Invalid message ID for `before:` parameter!")
				return
		
		if param.lower().startswith("limit:"):
			try:
				limit = int(param[6:])
			except ValueError:
				await message.channel.send(f"Invalid message ID for `limit:` parameter!")
				return
		
		if param.lower().startswith("content:"):
			end_index = msg[msg.find("content:") + 8:].find("]")
			if end_index == -1:
				await message.channel.send("You forgot to close the square brackets!")
				return

			end_index += msg.find("content:") + 8

			content = msg[msg.find("content:") + 9:end_index]

	recorded_count = 0
	counter = await message.channel.send(f"Searching... Found 0 messages so far.")
	messages = []

	for chnl in channels:
		async for msg_history in chnl.history(limit=limit, before=before, after=after):
			if content is None or msg_history.content.lower().find(content) > -1:
				messages.append(msg_history)

			if len(messages) - recorded_count >= 1000:
				recorded_count += 1000
				await counter.edit(content=f"Searching... Found {recorded_count} messages so far.")
	
	messages = [x for x in sorted(messages, key=lambda x: x.id) if (x.id != message.id and x.id != counter.id)]
	message_count = len(messages)
	oldest = messages[0]
	newest = messages[-1]

	await counter.edit(content=f"""**Finished searching.** Found {message_count} messages fitting the criteria.
	Oldest message: https://discordapp.com/channels/{oldest.guild.id}/{oldest.channel.id}/{oldest.id}
	Newest message: https://discordapp.com/channels/{newest.guild.id}/{newest.channel.id}/{newest.id}
	""".replace("\t", ""))
	return
