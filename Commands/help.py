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

	# Lambda returns the permissions, so it's sorted with lower permissions first (so that staff commands are
	# displayed last)
	com = sorted(com, key = lambda x: COMMANDS[x]["PERMS"])

	if level == 1:
		embed.title = "The Brain of TWOW Central"

		embed.description = f"""A general-purpose bot for TWOW Central, made by <@184768535107469314>
		These are all the commands available. Use `{PREFIX}help (command)` to find out more about a specific command.
		\u200b""".replace("\t", "")

		embed.set_thumbnail(url=BRAIN.user.avatar_url_as(static_format="png"))

		perm = 0

		for c in com:
			if perm != 2 and COMMANDS[c]['PERMS'] == 2:
				embed.add_field(name="\u200b", value="\u200b", inline=False)

			perm = COMMANDS[c]['PERMS']
			values = '**{Staff}\n**' if perm == 2 else ('{Member}\n' if perm == 1 else '{Non-Member}\n')

			command_alias_list = [f"{PREFIX}{command.lower()}" for command in COMMANDS[c]['ALIASES']]
			values += "\n".join(command_alias_list)

			values += "\n\u200b"

			embed.add_field(name=f"**{PREFIX}{c.lower()}**", value=values)
		
		await message.channel.send(embed=embed)
		return
	
	elif args[1].upper() not in com:
		await message.channel.send("Invalid command to get help for!")
		return

	c = args[1].upper()
	
	channel_list = [
		"Can be used in DMs, bot or game channels",
		"Can be used in DMs and bot channels",
		"Can be used by staff in any channel",
		"Where it's used depends on the subcommand",
		"Can be used in DMs and game channels",
		"Can only be used in game channels",
		"Can only be used in DMs"
	]
	perms = COMMANDS[c]['PERMS']
	
	if level == 2:
		embed.title = f"{PREFIX}{c.lower()}"
		embed.description = COMMANDS[c]["HELP"]["MAIN"]

		if len(COMMANDS[c]['ALIASES']) > 0:
			embed.description += f"\nAliases: {grammar_list([PREFIX + x.lower() for x in COMMANDS[c]['ALIASES']])}"

		embed.description += "\n\u200b"

		embed.add_field(name=f"**{PREFIX}{c.lower()} {COMMANDS[c]['HELP']['FORMAT']}**",
		value=COMMANDS[c]["HELP"]["USAGE"] + "\n\u200b", inline=False)

		embed.add_field(name="Conditions",
		value = f"""Requires {'staff' if perms == 2 else ('member' if perms == 1 else 'no')} permissions
		{channel_list[COMMANDS[c]['HELP']['CHANNEL']]}""".replace("\t", ""), inline=False)
	
	else:
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