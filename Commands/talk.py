from Config._functions import is_whole
import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 0,
		"HIDE": True,
		"MAIN": "Talk.",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Talk.""".replace("\n", "").replace("\t", "")
	}

PERMS = 3 # Developer
ALIASES = []
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a channel ID.")
		return
	
	if level == 2:
		await message.channel.send("Can't send an empty message.")
		return
	
	direct = False
	if not is_whole(args[1]):
		if args[1].lower() != "dm":
			await message.channel.send("Invalid channel ID.")
			return

		direct = True
	
	if direct:
		if not is_whole(args[2]):
			await message.channel.send("Invalid user ID.")
			return
		
		user_id = int(args[2])
		target = SERVER["MAIN"].get_member(user_id)

	else:
		channel_id = int(args[1])
		target = discord.utils.get(SERVER["MAIN"].channels, id=channel_id)

	if target is None:
		await message.channel.send("Could not find a channel or user with that ID.")
		return
	
	message_to_send = " ".join(args[2+int(direct):])

	try:
		await target.send(message_to_send)
	except Exception as err:
		await message.channel.send(f"`{err}`: Could not send")
		return
	
	await message.channel.send(f"Sent successfully!\n>\t`{message_to_send[:1950]}`")
	return