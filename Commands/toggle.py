import discord

HELP = "Can toggle access to a channel on or off"
PERMS = 2
ALIASES = []
REQ = ["TWOW_CENTRAL", "BRAIN", "PUBLIC_CHANNELS", "LOGS"]

async def MAIN(message, args, level, perms, TWOW_CENTRAL, BRAIN, PUBLIC_CHANNELS, LOGS):
	if level == 1:
		await message.channel.send("Include channels to toggle!")
		return

	mode = None
	if args[1].lower() in ["on", "off"]:
		mode = args[1].lower() == "on"
		channels = args[2:]
	else:
		channels = args[1:]

	lines = ["Toggle command started.\n\n"]
	actions = []

	for ch in channels:
		if ch.startswith("<#") and ch.endswith(">"):
			try:
				if (discord.utils.get(TWOW_CENTRAL.channels, id=int(ch[2:-1])) is None
				or int(ch[2:-1]) not in PUBLIC_CHANNELS):
					add = f"The channel with ID {ch[2:-1]} is either invalid or not a public channel. No action will be taken.\n"
					if len(lines[-1] + add) > 1950:
						lines.append("")
					lines[-1] += add

				else:
					target_c = discord.utils.get(TWOW_CENTRAL.channels, id=int(ch[2:-1]))
					c_perm = target_c.overwrites_for(TWOW_CENTRAL.default_role).send_messages

					if mode is None:
						if c_perm in [None, True]:
							add = f"The channel {target_c.mention} will be toggled **off.**\n"
							actions.append([target_c, False])
						else:
							add = f"The channel {target_c.mention} will be toggled **on.**\n"
							actions.append([target_c, None])

					elif mode:
						if c_perm is False:
							add = f"The channel {target_c.mention} will be toggled **on.**\n"
							actions.append([target_c, None])
						else:
							add = f"{target_c.mention} is already on. No action will be taken.\n"

					else:
						if c_perm in [None, True]:
							add = f"The channel {target_c.mention} will be toggled **off.**\n"
							actions.append([target_c, False])
						else:
							add = f"{target_c.mention} is already off. No action will be taken.\n"

					if len(lines[-1] + add) > 1950:
						lines.append("")
					lines[-1] += add

			except Exception:
				add = f"The channel with ID {ch[2:-1]} is invalid. No action will be taken.\n"
				if len(lines[-1] + add) > 1950:
					lines.append("")
				lines[-1] += add
	
	for z in lines:
		await message.channel.send(z)

	if len(actions) == 0:
		await message.channel.send("There's no action to be taken. The toggle command has been cancelled.")
		return

	await message.channel.send("""**To confirm these actions, send `confirm` in this channel.
	Send anything else to cancel the command.**""".replace('\t', ''))

	def check(m):
		return m.author == message.author and m.channel == message.channel

	msg = await BRAIN.wait_for('message', check=check)

	if msg.content.lower() != "confirm":
		await message.channel.send("Toggle command cancelled.")
		return

	lines = ["**The toggle command has been executed.**\n\n"]
	log_lines = [""]

	for act in actions:
		await act[0].set_permissions(
			TWOW_CENTRAL.default_role, send_messages=act[1], add_reactions=act[1])

		add = f"**{act[0].mention} has been toggled {'ON' if act[1] is None else 'OFF'}.**\n"
		add_log = f"> {act[0].mention} has been toggled **{'ON' if act[1] is None else 'OFF'}**."

		if len(lines[-1] + add) > 1950:
			lines.append("")
		lines[-1] += add

		if len(log_lines[-1] + add_log) > 1950:
			log_lines.append("")
		log_lines[-1] += add_log

	for z in lines:
		await message.channel.send(z)
	for z in log_lines:
		await LOGS.send(z)
	return