from Config._const import BRAIN
from Config._functions import grammar_list
import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Displays a screen containing every command you can use and information on it",
		"FORMAT": "(command)",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}help` shows you a list of commands and aliases. Filling in the parameter 
		`(command)` shows you information on a specific command. In command help pages, parameters marked 
		with [brackets] are mandatory. Those marked with (parentheses) are optional.""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Utility"
	}

PERMS = 0 # Everyone
ALIASES = ["H"]
REQ = ["COMMANDS"]

async def MAIN(message, args, level, perms, SERVER, COMMANDS):
	# Embed color is constant
	embed = discord.Embed(color=0x31D8B1)
	com = list(COMMANDS.keys())
	
	alias_list = {}
	for c in com:
		for a in COMMANDS[c]['ALIASES']:
			alias_list[a] = c

	# Category indices for sorting. Values above 100 will cause commands to appear after a space separator.
	ci = {
		"Utility" : 1,
		"Community" : 2,
		"Fun" : 3,
		"Games" : 4,
		"Other" : 90,
		"Staff" : 101,
		"Developer" : 102
	}

	if level == 1: # If command is `tc/help`
		embed.title = "The Brain of TWOW Central"

		embed.description = f"""A general-purpose bot for TWOW Central, made by <@184768535107469314>
		These are all the commands available. Use `{SERVER["PREFIX"]}help (command)` to find out more about a specific command.
		\u200b""".replace("\t", "")

		# Set Brain PFP for the default help page
		embed.set_thumbnail(url=BRAIN.user.display_avatar.url)

		comlist = {}

		for c in com:
			if 'HIDE' not in COMMANDS[c]['HELP'](SERVER["PREFIX"]).keys():
				hide_command = 0
			else:
				hide_command = COMMANDS[c]['HELP'](SERVER["PREFIX"])['HIDE']
			if hide_command == 0:
				try:
					comcat = COMMANDS[c]['HELP'](SERVER["PREFIX"])["CATEGORY"]
				except:
					comcat = "Other"
				if comcat not in comlist.keys():
					comlist[comcat] = []
				comlist[comcat].append(c)
		
		categories = list(comlist.keys())
		for cat in categories:
			if cat not in ci.keys():
				ci[cat] = 89 # adds un-indexed categories right before Other
		categories = sorted(categories, key = lambda x: ci[x])

		for cat in categories:
			values = ""
			comlist[cat].sort()
			for cn in comlist[cat]:
				values += "`" + SERVER["PREFIX"] + cn.lower() + "`\n"
			embed.add_field(name=cat, value=values)

		await message.channel.send(embed=embed)
		return
	
	# COMMANDS keys are in uppercase so this is helpful
	c = args[1].upper()
	
	if c in alias_list.keys(): # Checks list of aliases in case user input an alias to get help for
		c = alias_list[c]
	
	if c not in com:
		await message.channel.send("Invalid command to get help for!")
		return
	
	# I might remake this part later because it feels too hardcodey. Corresponds to ["HELP"]["CHANNEL"] of each command
	channel_list = [
		"Can be used in DMs, bot or game channels",
		"Can be used in DMs and bot channels",
		"Can be used by staff in any channel",
		"Where it's used depends on the subcommand",
		"Can be used in DMs and game channels",
		"Can only be used in game channels",
		"Can only be used in DMs"
	]

	# Usage perms
	perms = COMMANDS[c]['PERMS']
	
	if level == 2:
		# Title is the command syntax, description is the basic info on the command
		embed.title = f"{SERVER['PREFIX']}{c.lower()}"
		embed.description = COMMANDS[c]["HELP"](SERVER['PREFIX'])["MAIN"]

		# Extra bit is added in case there's any aliases to list
		if len(COMMANDS[c]['ALIASES']) > 0:
			embed.description += f"\nAliases: {grammar_list([SERVER['PREFIX'] + x.lower() for x in COMMANDS[c]['ALIASES']])}"

		# Once again, having more vertical whitespace prevents things from looking too cluttered
		embed.description += "\n\u200b"

		# Formatting and usage information (plus the newline zero-width space again)
		embed.add_field(name=f"**{(SERVER['PREFIX'])}{c.lower()} {COMMANDS[c]['HELP'](SERVER['PREFIX'])['FORMAT']}**",
		value=COMMANDS[c]["HELP"](SERVER['PREFIX'])["USAGE"] + "\n\u200b", inline=False)

		try: # Some commands have USAGE strings longer than the maximum allowed of 1024 characters and can't fit
			# So I split them up into two strings and add the second one (only if it exists, that is.)
			embed.add_field(name="\u200b", value=COMMANDS[c]["HELP"](SERVER['PREFIX'])["USAGE2"] + "\n\u200b", inline=False)
		except:
			pass
		
		embed.add_field(name="Cooldown Time", value=f'{COMMANDS[c]["HELP"](SERVER["PREFIX"])["COOLDOWN"]}sec \n\u200b', inline=False)

		# Conditions are usage permissions followed by channel permissions (as denoted in channel_list)
		embed.add_field(name="Conditions",
		value = f"""Requires {'developer' if perms == 3 else ('staff' if perms == 2 else ('member' if perms == 1 else 'no'))} permissions
		{channel_list[COMMANDS[c]['HELP'](SERVER['PREFIX'])['CHANNEL']]}""".replace("\t", ""), inline=False)
		# Usually, after every multiline string I have to add .replace("\n", "").replace("\t", "") because I don't
		# want the newlines and tabs to actually show up. Here, there's actually an intended newline, so I just
		# separate the two lines in the script file and I only erase the tab characters
	
	else:
		# Most of this else code is copy pasted from the above, adapted with the `sc` variable instead of `c`
		# Not much else to say for this part other than what's above

		sc = args[2].upper()

		if sc not in COMMANDS[c]["HELP"](SERVER['PREFIX']).keys():
			await message.channel.send(f"Invalid `{c.lower()}` subcommand to get help for!")
			return
		
		embed.title = f"{(SERVER['PREFIX'])}{c.lower()} {sc.lower()}"
		embed.description = COMMANDS[c]["HELP"](SERVER['PREFIX'])[sc]["MAIN"] + "\n\u200b"

		embed.add_field(name=f"**{(SERVER['PREFIX'])}{c.lower()} {sc.lower()} {COMMANDS[c]['HELP'](SERVER['PREFIX'])[sc]['FORMAT']}**",
		value=COMMANDS[c]["HELP"](SERVER['PREFIX'])[sc]["USAGE"] + "\n\u200b", inline=False)

		try:
			embed.add_field(name="\u200b", value=COMMANDS[c]["HELP"](SERVER['PREFIX'])[sc]["USAGE2"] + "\n\u200b", inline=False)
		except:
			pass

		embed.add_field(name="Conditions",
		value = f"""Requires {'developer' if perms == 3 else ('staff' if perms == 2 else ('member' if perms == 1 else 'no'))} permissions
		{channel_list[COMMANDS[c]['HELP'](SERVER['PREFIX'])[sc]['CHANNEL']]}""".replace("\t", ""), inline=False)

	await message.channel.send(embed=embed)
	return
