from Config._const import PREFIX, BRAIN
from Config._functions import is_whole
import discord

HELP = {
	"COOLDOWN": 86400,
	"MAIN": "React to a message with an emoji",
	"FORMAT": "[message_id] [emoji] (channel)",
	"CHANNEL": 0,
	"USAGE": f"""Using `{PREFIX}react [message_id] [emoji] (channel_id)` will add the `[emoji]` reaction to the 
	message with ID `[message_id]`. If the message is in a channel different than the one specified, the (channel) 
	parameter must be a mention of the channel the message is in.""".replace("\n", "").replace("\t", "")
}

PERMS = 1
ALIASES = []
REQ = ["TWOW_CENTRAL"]

async def MAIN(message, args, level, perms, TWOW_CENTRAL):
	if level < 3:
		await message.channel.send("Include both a message ID and an emoji!")
		return
	
	if not is_whole(args[1]):
		await message.channel.send("Provide a valid message ID!")
		return
	
	if level == 3:
		try:
			msg = await message.channel.fetch_message(int(args[1]))
		except discord.HTTPException:
			await message.channel.send("The message was not found!")

	elif is_whole(args[3][2:-1]):
		chnl = discord.utils.get(TWOW_CENTRAL.channels, id=int(args[3][2:-1]))
		if chnl is None:
			await message.channel.send("Provide a valid channel!")
			return
		
		try:
			msg = await chnl.fetch_message(int(args[1]))
		except discord.HTTPException:
			await message.channel.send("The message was not found!")

	else:
		print(args[3][2:-1])
		print(is_whole(args[3][2:-1]))
		await message.channel.send("Provide a valid channel!")
		return
	
	try:
		await msg.add_reaction(args[2])
		await message.channel.send(f"Added {args[2]} reaction to message {args[1]}.")
	except discord.HTTPException:
		await message.channel.send("Include a valid emoji!")