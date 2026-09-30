import os

import discord

from Config._functions import is_whole
from Config._db import Database

from datetime import datetime as dt


def HELP(PREFIX):
	return {
		"COOLDOWN": 5,
		"MAIN": "Allows you to view B* programs made before deprecation.",
		"FORMAT": "info [page or program]",
		"CHANNEL": 0,
		"USAGE": f"""Using `tc/bstar info (page)` displays a paged list of all B* programs by historical use count, 
		while using `tc/bstar (program)` or `tc/bstar info (program)` displays information and the source code of
		a specific program. 
		""".replace("\n", "").replace("\t", "").replace("^n", "\n"),
		"CATEGORY": "Fun"
	}


PERMS = 1  # Member
ALIASES = ["B*"]
REQ = ["LOGIN"]

async def accept_file_or_message(message):
	if len(message.attachments) > 0:
		attachment = message.attachments[0]
		try:
			await attachment.save(f"Config/{message.id}.txt")
		except Exception:
			raise "Include a program to save!"
		file = open(f"Config/{message.id}.txt", "r", encoding="utf-8").read()
		os.remove(f"Config/{message.id}.txt")
		if attachment.size >= 150_000:
			raise "File is too large! (150KB MAX)"
		else:
			return file
	else:
		return " ".join(message.content.split(" ")[2:])


async def MAIN(message, args, level, perms, SERVER, LOGIN):
	bs_version = 1  # 0 = b++, 1 = b* (1.0)

	if message.channel.id == 598616636823437352 and perms < 2:
		return

	if level == 1:
		await message.channel.send("Include a subcommand!")
		return

	db = Database()
	subcommand = args[1].lower()

	# """Run B* code"""
	if subcommand == "run":
		await message.channel.send("B* has been deprecated, and you can no longer run code with it.")
		return

	if subcommand == "create":
		await message.channel.send("B* has been deprecated, and you can no longer create new programs with it.")
		return

	if subcommand == "info":
		tag_list = db.get_entries("bsprograms", columns=["name", "program", "author", "uses", "created", "lastused"])
		tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])

		tag_leaderboard = False
		if level == 2:  # If it's not specified, assume it's the first page
			tag_list = tag_list[:10]
			page = 1
			tag_leaderboard = True

		elif is_whole(args[2]):
			if (int(args[2]) - 1) * 10 >= len(tag_list):  # Detect if the page number is too big
				await message.channel.send(f"There is no page {args[2]} on the B* program list!")
				return

			else:  # This means the user specified a valid page number
				lower = (int(args[2]) - 1) * 10
				upper = int(args[2]) * 10
				tag_list = tag_list[lower:upper]
				page = int(args[2])
				tag_leaderboard = True

		if tag_leaderboard:
			beginning = f"```scala\nB++ Programs Page {page}\n\n"

			for program in tag_list:
				r = tag_list.index(program) + 1 + (page - 1) * 10

				line = f"{r}{' ' * (2 - len(str(r)))}: {program[0]} :: {program[3]} use{'s' if program[3] != 1 else ''}"

				member_id = program[2]
				try:  # Try to gather a username from the ID
					member = SERVER["MAIN"].get_member(int(member_id)).name
				except:  # If you can't, just display the ID
					member = str(member_id)

				created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
				line += f" (written by {member} at {created_on})\n"

				beginning += line  # Add this line to the final message

			beginning += "```"  # Close off code block

			await message.channel.send(beginning)
			return

		tag_name = args[2]


	else:
		tag_name = args[1]

	tag_list = db.get_entries("bsprograms", columns=["name", "program", "author", "uses"])

	if tag_name not in [x[0] for x in tag_list]:
		await message.channel.send("That tag does not exist.")
		return

	program = tag_list[[x[0] for x in tag_list].index(tag_name)]

	member_id = program[2]
	try:  # Try to gather a username from the ID
		member = SERVER["MAIN"].get_member(int(member_id)).name
	except:  # If you can't, just display the ID
		member = str(member_id)

	created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
	c_d = dt.now() - dt.utcfromtimestamp(program[4])

	d = c_d.days
	h, rm = divmod(c_d.seconds, 3600)
	m, s = divmod(rm, 60)

	c_d = (('' if d == 0 else f'{d} day{"s" if d != 1 else ""}, ') +
	       ('' if h == 0 else f'{h} hour{"s" if h != 1 else ""}, ') +
	       ('' if m == 0 else f'{m} minute{"s" if m != 1 else ""}, ') +
	       (f'{s} second{"s" if s != 1 else ""}'))

	msg = f"**{program[0]}** -- by {member} -- {program[3]} use{'s' if program[3] != 1 else ''}\n"
	msg += f"Created on {created_on} `({c_d} ago)`\n"

	if program[5] != 0:
		last_used = dt.utcfromtimestamp(program[5]).strftime('%Y-%m-%d %H:%M:%S UTC')
		u_d = dt.now() - dt.utcfromtimestamp(program[5])

		d = u_d.days
		h, rm = divmod(u_d.seconds, 3600)
		m, s = divmod(rm, 60)

		u_d = (('' if d == 0 else f'{d} day{"s" if d != 1 else ""}, ') +
		       ('' if h == 0 else f'{h} hour{"s" if h != 1 else ""}, ') +
		       ('' if m == 0 else f'{m} minute{"s" if m != 1 else ""}, ') +
		       (f'{s} second{"s" if s != 1 else ""}'))

		msg += f"Last used on {last_used} `({u_d} ago)`\n"

	if len(program[1]) > 1700:
		msg += f"The program is too long to be included in the message, so it's in the file below:"
		open(f'program_{program[0]}.txt', 'w', encoding="utf-8").write(program[1])
		await message.channel.send(msg, file=discord.File(f'program_{program[0]}.txt'))
		os.remove(f'program_{program[0]}.txt')
	else:
		msg += f"```{program[1]}```"
		await message.channel.send(msg)

	return
