from Config._const import PREFIX

HELP = "Displays a screen containing every command you can use and information on it"
PERMS = 0
ALIASES = ["H"]
REQ = ["COMMANDS"]

async def MAIN(message, args, level, perms, COMMANDS):
	com = list(COMMANDS.keys())

	help_m = "\n```This is The Brain of TWOW Central!\n> Here are all the commands you can use.```\n"

	for c in com:
		if perms >= COMMANDS[c]['PERMS']:
			help_m += f"\n**`{PREFIX + c.lower()}`** - {COMMANDS[c]['HELP']}"
			if COMMANDS[c]['ALIASES'] != []:
				help_m += f"\n*Aliases: `{', '.join([PREFIX + a.lower() for a in COMMANDS[c]['ALIASES']])}`*"
			help_m += "\n"

	await message.channel.send(help_m)
	return