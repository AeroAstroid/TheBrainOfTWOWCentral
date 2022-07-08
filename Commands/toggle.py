import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 5,
		"MAIN": "Toggles speaking at a public channel",
		"FORMAT": "('on'/'off') [channels] ('confirm')",
		"CHANNEL": 2,
		"USAGE": f"""Using `{PREFIX}toggle [channels]` will prompt a confirmation message to toggle all channels included. 
		By default, it'll switch locked channels to unlocked and vice-versa. Including `('on'/'off')` before `[channels]` 
		specifies to unlock all channels or lock all channels. Including `('confirm')` anywhere in the command bypasses 
		the confirmation message and triggers the toggling action instantly.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Staff"
	}

PERMS = 2 # Staff
ALIASES = ["LOCK"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include channels to toggle!")
		return

	# Detect whether you should switch the on/off channels around, or turn them all on or them all off
	# Note: Discord channel permissions are separated into check mark (True), slash (None), and X (False)
	mode = None
	if args[1].lower() in ["on", "off"]:
		mode = args[1].lower() == "on" # True if "on", False if "off"
		channels = args[2:]
	else: # If there isn't a keyword, that means the list of channels begins one argument sooner
		channels = args[1:]

	# Array to split messages in as to not break the character limit
	lines = ["Toggle command started.\n\n"]
	actions = []

	for ch in channels: # For every channel mentioned...
		if ch.startswith("<#") and ch.endswith(">"): # Don't bother if it's not an actual channel mention
			try:
				if (discord.utils.get(SERVER["MAIN"].channels, id=int(ch[2:-1])) is None
				or int(ch[2:-1]) not in SERVER["PUBLIC_CHANNELS"]): # If it's invalid or not a public channel, point so out
					add = f"The channel with ID {ch[2:-1]} is either invalid or not a public channel. No action will be taken.\n"
					if len(lines[-1] + add) > 1950:
						lines.append("")
					lines[-1] += add

				else: # Otherwise, it's valid, so add it
					target_c = discord.utils.get(SERVER["MAIN"].channels, id=int(ch[2:-1]))
					c_perm = target_c.overwrites_for(SERVER["MAIN"].default_role).send_messages

					if mode is None: # If the user wants to switch the permissions...
						if c_perm in [None, True]: # Channels that allow speaking...
							add = f"The channel {target_c.mention} will be toggled **off.**\n"
							actions.append([target_c, False]) # ...no longer allow it.
						else: # Channels that don't allow speaking...
							add = f"The channel {target_c.mention} will be toggled **on.**\n"
							actions.append([target_c, None]) # ...now do.

					elif mode: # If the user wants all channels to be turned on...
						if c_perm is False: # Channels that are turned off...
							add = f"The channel {target_c.mention} will be toggled **on.**\n"
							actions.append([target_c, None]) # ...are turned on.
						else: # Channels that are already turned on need no action.
							add = f"{target_c.mention} is already on. No action will be taken.\n"

					else: # If the user wants all channels to be turned off...
						if c_perm in [None, True]: # Channels that are turned on...
							add = f"The channel {target_c.mention} will be toggled **off.**\n"
							actions.append([target_c, False]) # are turned off.
						else: # Channels that are already turned off need no action.
							add = f"{target_c.mention} is already off. No action will be taken.\n"

					# This detects if the message is about to reach the character limit, and splits it up into another
					# message if so (this also appears above and is explained in other both mmt and database comments)
					if len(lines[-1] + add) > 1950:
						lines.append("")
					lines[-1] += add

			except Exception: # If something goes wrong, assume the channel is invalid
				add = f"The channel with ID {ch[2:-1]} is invalid. No action will be taken.\n"
				if len(lines[-1] + add) > 1950:
					lines.append("")
				lines[-1] += add

	if len(actions) == 0: # If no actual changes are to be made, nothing will happen
		await message.channel.send("There's no action to be taken. The toggle command has been cancelled.")
		return

	# Once again, in case it ends up over the character limit
	lines = ["**The toggle command has been executed.**\n\n"]
	log_lines = [""]

	for act in actions:
		# Toggle the channel (changing its send messages and add reactions permissions)
		await act[0].set_permissions(
			SERVER["MAIN"].default_role, send_messages=act[1], add_reactions=act[1])

		# Lines to be added to the confirmation and/or log message
		add = f"**{act[0].mention} has been toggled {'ON' if act[1] is None else 'OFF'}.**\n"
		add_log = f"> {act[0].mention} has been toggled **{'ON' if act[1] is None else 'OFF'}**."

		# Split up into multiple messages if necessary
		if len(lines[-1] + add) > 1950:
			lines.append("")
		lines[-1] += add

		if len(log_lines[-1] + add_log) > 1950:
			log_lines.append("")
		log_lines[-1] += add_log

	for z in lines:
		await message.channel.send(z)
	return