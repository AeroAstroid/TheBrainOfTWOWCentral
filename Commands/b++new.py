from Config._functions import strip_alpha, find_all, is_whole, strip_front

from Config._bppnew_parsing import *

from Config._db import Database

import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Allows you to write short tags and/or programs",
		"FORMAT": "[subcommand]",
		"CHANNEL": 0,
		"USAGE": f"""w.i.p. new version of B++
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 1 # Member
ALIASES = ["TAGNEW"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	if args[1].lower() == "run":
		program = " ".join(args[2:])

		while program.startswith("`") and program.endswith("`"):
			program = program[1:-1]
		
		program.replace("{}", "\t")
		
		try:
			program_output = run_bpp_program(program).replace("<@", "<\\@")
		except Exception as e:
			await message.channel.send(f'{type(e).__name__}:\n```{e}```')
			return

		if len(program_output) > 1950:
			program_output = "⚠️ `Output too long! First 1900 characters:`\n\n" + program_output[:1900]
		
		await message.channel.send(program_output)
		return