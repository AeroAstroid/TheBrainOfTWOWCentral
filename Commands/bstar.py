from Config._functions import strip_alpha, find_all, is_whole, strip_front

from Config._bppnew_parsing import *

from Config._db import Database

import discord, os, re, time

from datetime import datetime as dt

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Allows you to write short tags and/or programs",
		"FORMAT": "[subcommand]",
		"CHANNEL": 0,
		"USAGE": f"""Using `tc/b++ run [code]` allows you to run `[code]` as B++ source code. Using `tc/b++ info 
		(page)` displays a paged list of all B++ programs by use count, while using `tc/b++ info (program)` 
		displays information and the source code of a specific program. `tc/b++ create [program] [code]` can be used 
		to save code into a specific program name, which can be edited by its creator with `tc/b++ edit [program] 
		[newcode]` or deleted with `tc/b++ delete [program]`. Finally, `tc/b++ [program] (args)` allows you to run any 
		saved program.^n^n
		The full documentation for all B++ program functionality is displayed in this document:^n
		https://docs.google.com/document/d/1o9uy-HBtwD5g584S_F_2dtTj6j_LGtTK16Lg1jUBgzg/edit?usp=sharing
		""".replace("\n", "").replace("\t", "").replace("^n", "\n"),
		"CATEGORY" : "Fun"
	}

PERMS = 1 # Member
# TODO: Add better aliases
ALIASES = ["B*", "BSTAR", "BS"]
REQ = []

async def MAIN(message, args, level, perms, SERVER, LOGIN):
	# 1000 * seconds = milliseconds
	delta = 1000 * (time.time() - LOGIN)

	abs_delta = [
		int(delta),  # Milliseconds
		int(delta / 1000),  # Seconds
		int(delta / (1000 * 60)),  # Minutes
		int(delta / (1000 * 60 * 60)),  # Hours
		int(delta / (1000 * 60 * 60 * 24))]  # Days

	ml = abs_delta[0] % 1000
	sc = abs_delta[1] % 60
	mi = abs_delta[2] % 60
	hr = abs_delta[3] % 24
	dy = abs_delta[4]

	await message.channel.send(f"Bot has been up for {dy}d {hr}h {mi}m {sc}s {ml}ms.")
	return