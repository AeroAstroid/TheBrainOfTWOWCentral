from Config._const import PREFIX, BRAIN
from Config._functions import grammar_list
import discord

HELP = {
	"MAIN": "Displays a screen containing every command you can use and information on it",
	"FORMAT": "(command)",
	"CHANNEL": 0,
	"USAGE": f"""Using `{PREFIX}help` shows you a list of commands and aliases. Filling in the parameter 
	`(command)` shows you information on a specific command. In command help pages, parameters marked 
	with [brackets] are mandatory. Those marked with (parentheses) are optional.""".replace("\n", "").replace("\t", "")
}

PERMS = 0 # Everyone
ALIASES = ["H"]
REQ = ["COMMANDS"]

async def MAIN(message, args, level, perms, COMMANDS):
	# Embed color is constant
	embed = discord.Embed(color=0x31D8B1)
	com = list(COMMANDS.keys())
	
	alias_list = {}
	for c in com:
		for a in c['ALIASES']:
			alias_list[a] = c

	# Lambda returns the permissions, so it's sorted with lower permissions first (so that staff commands are
	# displayed last)
	com = sorted(com, key = lambda x: COMMANDS[x]["PERMS"])

	if level == 1: # If command is `tc/help`
		embed.title = "The Brain of TWOW Central"

		embed.description = f"""A general-purpose bot for TWOW Central, made by <@184768535107469314>
		These are all the commands available. Use `{PREFIX}help (command)` to find out more about a specific command.
		\u200b""".replace("\t", "")

		# Set Brain PFP for the default help page
		embed.set_thumbnail(url=BRAIN.user.avatar_url_as(static_format="png"))

		perm = 0 # This variable serves to check for boundaries between commands of different permission requirements

		for c in com:
			# If the last command wasn't a staff command but this one is, add a non-inline field as a separator
			# This has the effect of creating a vertical space separation between non-staff and staff commands
			if perm != 2 and COMMANDS[c]['PERMS'] == 2:
				embed.add_field(name="\u200b", value="\u200b", inline=False)

			# This variable is the "last command's permissions" one that gets checked above to determine separations
			perm = COMMANDS[c]['PERMS']
			# 2 = Staff; 1 = Member; 0 = Non-Member
			values = '**{Staff}\n**' if perm == 2 else ('{Member}\n' if perm == 1 else '{Non-Member}\n')

			# Add aliases, if any
			command_alias_list = [f"{PREFIX}{command.lower()}" for command in COMMANDS[c]['ALIASES']]
			values += "\n".join(command_alias_list)

			# Adding a newline and zero-width space creates a sort of vertical buffer between each line of
			# embed fields, making it less cluttered
			values += "\n\u200b"

			# Add the command's field finally
			embed.add_field(name=f"**{PREFIX}{c.lower()}**", value=values)
		
		await message.channel.send(embed=embed)
		return
	
	# COMMANDS keys are in uppercase so this is helpful
	c = args[1].upper()
	
	if c in alias_list.keys(): # Checks list of aliases in case user input an alias to get help for
		c = alias_list[c]
	
	if c not in com:
		await message.channel.send("Invalid command to get help for! this is a test " + c)
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
		embed.title = f"{PREFIX}{c.lower()}"
		embed.description = COMMANDS[c]["HELP"]["MAIN"]

		# Extra bit is added in case there's any aliases to list
		if len(COMMANDS[c]['ALIASES']) > 0:
			embed.description += f"\nAliases: {grammar_list([PREFIX + x.lower() for x in COMMANDS[c]['ALIASES']])}"

		# Once again, having more vertical whitespace prevents things from looking too cluttered
		embed.description += "\n\u200b"

		# Formatting and usage information (plus the newline zero-width space again)
		embed.add_field(name=f"**{PREFIX}{c.lower()} {COMMANDS[c]['HELP']['FORMAT']}**",
		value=COMMANDS[c]["HELP"]["USAGE"] + "\n\u200b", inline=False)

		# Conditions are usage permissions followed by channel permissions (as denoted in channel_list)
		embed.add_field(name="Conditions",
		value = f"""Requires {'staff' if perms == 2 else ('member' if perms == 1 else 'no')} permissions
		{channel_list[COMMANDS[c]['HELP']['CHANNEL']]}""".replace("\t", ""), inline=False)
		# Usually, after every multiline string I have to add .replace("\n", "").replace("\t", "") because I don't
		# want the newlines and tabs to actually show up. Here, there's actually an intended newline, so I just
		# separate the two lines in the script file and I only erase the tab characters
	
	else:
		# Most of this else code is copy pasted from the above, adapted with the `sc` variable instead of `c`
		# Not much else to say for this part other than what's above

		sc = args[2].upper()

		if sc not in COMMANDS[c]["HELP"].keys():
			await message.channel.send(f"Invalid `{c.lower()}` subcommand to get help for!")
			return
		
		embed.title = f"{PREFIX}{c.lower()} {sc.lower()}"
		embed.description = COMMANDS[c]["HELP"][sc]["MAIN"] + "\n\u200b"

		embed.add_field(name=f"**{PREFIX}{c.lower()} {sc.lower()} {COMMANDS[c]['HELP'][sc]['FORMAT']}**",
		value=COMMANDS[c]["HELP"][sc]["USAGE"] + "\n\u200b", inline=False)

		embed.add_field(name="Conditions",
		value = f"""Requires {'staff' if perms == 2 else ('member' if perms == 1 else 'no')} permissions
		{channel_list[COMMANDS[c]['HELP'][sc]['CHANNEL']]}""".replace("\t", ""), inline=False)

	await message.channel.send(embed=embed)
	return
