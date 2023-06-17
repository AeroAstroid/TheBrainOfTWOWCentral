import os
import re
import time

import discord

from Config.b_star_interpreter.function_deco import setupFunctions
from Config.b_star_interpreter.run import runCode

from Config._functions import is_whole
from Config._db import Database

from datetime import datetime as dt


def HELP(PREFIX):
	return {
		"COOLDOWN": 15,
		"MAIN": "Allows you to write short tags and/or programs",
		"FORMAT": "[subcommand]",
		"CHANNEL": 0,
		"USAGE": f"""Using `tc/bstar run [code]` allows you to run `[code]` as B* source code. Using `tc/bstar info 
		(page)` displays a paged list of all B* programs by use count, while using `tc/bstar info (program)` 
		displays information and the source code of a specific program. `tc/bstar create [program] [code]` can be used 
		to save code into a specific program name, which can be edited by its creator with `tc/bstar edit [program] 
		[newcode]` or deleted with `tc/bstar delete [program]`. Finally, `tc/bstar [program] (args)` allows you to run any 
		saved program.^n^n
		The full documentation for all B* program functionality is displayed in this document:^n
		https://github.com/b-Development-Team/b-star/wiki
		""".replace("\n", "").replace("\t", "").replace("^n", "\n"),
		"CATEGORY": "Fun"
	}


PERMS = 1  # Member
ALIASES = ["B*"]
REQ = ["LOGIN"]

setupFunctions()


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

	if level == 1:
		await message.channel.send("Include a subcommand!")
		return

	db = Database()
	subcommand = args[1].lower()

	# """Run B* code"""
	if subcommand == "run":
		# TODO: Does this need to be replaced with b++.py version?
		# probably
		try:
			output = runCode(await accept_file_or_message(message), message.author, [], message.author.id)
			await message.channel.send(embed=discord.Embed(description=output))
		except Exception as e:
			await message.channel.send(e)
		return

	# """Creates a B* tag with your code"""
	if subcommand == "create":
		if level == 2:
			await message.channel.send("Include the name of your new program!")
			return

		tag_name = args[2]

		if re.search(r"[^0-9A-Za-z_]", tag_name) or re.search(r"[0-9]", tag_name[0]):
			await message.channel.send(
				"Tag name can only contain letters, numbers and underscores, and cannot start with a number!")
			return

		if tag_name in ["create", "edit", "delete", "info", "run", "help"]:
			await message.channel.send("The tag name must not be a reserved keyword!")
			return

		if len(tag_name) > 30:
			await message.channel.send("That tag name is too long. 30 characters maximum.")
			return

		if level > 3:
			program = " ".join(args[3:])

		elif len(message.attachments) != 0:
			try:
				if message.attachments[0].size >= 60000:
					await message.channel.send("Your program must be under **60KB**.")
					return

				await message.attachments[0].save(f"Config/{message.id}.txt")

			except Exception:
				await message.channel.send("Include a valid program to save!")
				return

			program = open(f"Config/{message.id}.txt", "r", encoding="utf-8").read()
			os.remove(f"Config/{message.id}.txt")

		else:
			await message.channel.send("Include a valid program to save!")
			return

		while program.startswith("`") and program.endswith("`"):
			program = program[1:-1]
		program.replace("{}", "\t")

		if (tag_name,) in db.get_entries("bsprograms", columns=["name"]):
			await message.channel.send("There's already a program with that name!")
			return

		# db.add_entry("bsprograms", [0, int(time.time()), 0, tag_name, program, message.author.id])
		db.add_entry("bsprograms", [tag_name, program, message.author.id, 0, int(time.time()), 0, 0, bs_version])
		await message.channel.send(f"Successfully created program `{tag_name}`!")
		return

	# except:
	#     await message.channel.send("Tag creation failed")

	# """Gives infomation and source code about a B* tag"""
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

	# 	"""Shows the leaderboard of tags sorted by uses"""
	# if subcommand == "leaderboard":
	# 	page = int(args[2])
	# 	await message.channel.send(await leaderboards(page))

	# 	"""Edit one of your B* tags"""
	if subcommand == "edit":
		if level == 2:
			await message.channel.send("Include the name of the program you want to edit!")
			return

		tag_name = args[2]

		tag_list = db.get_entries("bsprograms", columns=["name", "author"])

		if tag_name not in [x[0] for x in tag_list]:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")
			return

		ind = [x[0] for x in tag_list].index(tag_name)
		if tag_list[ind][1] != str(message.author.id) and perms < 2:
			await message.channel.send(f"You can only edit a program if you created it or if you're a staff member!")
			return

		if level > 3:
			program = " ".join(args[3:])

		elif len(message.attachments) != 0:
			try:
				if message.attachments[0].size >= 60000:
					await message.channel.send("Your program must be under **60KB**.")
					return

				await message.attachments[0].save(f"Config/{message.id}.txt")

			except Exception:
				await message.channel.send("Include a valid program to run!")
				return

			program = open(f"Config/{message.id}.txt", "r", encoding="utf-8").read()
			os.remove(f"Config/{message.id}.txt")

		else:
			await message.channel.send("Include a valid program to run!")
			return

		while program.startswith("`") and program.endswith("`"):
			program = program[1:-1]

		program = program.replace("{}", "\v")

		db.edit_entry("bsprograms", entry={"program": program}, conditions={"name": tag_name})
		await message.channel.send(f"Succesfully edited program {tag_name}!")
		return

	# 	"""Delete one of your B* tags"""
	if subcommand == "delete":
		if level == 2:
			await message.channel.send("Include the name of the program you want to delete!")
			return

		tag_name = args[2]

		tag_list = db.get_entries("bsprograms", columns=["name", "author"])

		if tag_name not in [x[0] for x in tag_list]:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")
			return

		ind = [x[0] for x in tag_list].index(tag_name)
		if tag_list[ind][1] != str(message.author.id) and perms < 2:
			await message.channel.send(f"You can only edit a program if you created it or if you're a staff member!")
			return

		db.remove_entry("bsprograms", conditions={"name": tag_name})
		await message.channel.send(f"Succesfully deleted program {tag_name}!")
		return

	# Find the tag
	# tagObject = getTag(message)
	# if tagObject is not None:
	#     code = tagObject["program"]
	#     # TODO: this is float only rn, do support for int in the future
	#     argument_list = args.split(" ")
	#
	#     output = runCode(code, message.author, argument_list)
	#     await message.channel.send(output)
	#
	#     # If all goes well, then increment the use
	#     updateTag(message)
	# else:
	#     await message.channel.send(f"There's no program under the name `{message}`!")

	tag_name = args[1]

	tag_list = db.get_entries("bsprograms", columns=["name", "program", "author", "uses"])

	if tag_name not in [x[0] for x in tag_list]:
		await message.channel.send(f"There's no program under the name `{tag_name}`!")
		return

	tag_info = [x for x in tag_list if x[0] == tag_name][0]
	program = tag_info[1]
	author = int(tag_info[2])

	uses = tag_info[3] + 1
	db.edit_entry("bsprograms", entry={"uses": uses, "lastused": time.time()}, conditions={"name": tag_name})

	program_args = args[2:]

	output = runCode(program, message.author, program_args, author)
	if len(output) > 1900: await message.channel.send(embed=discord.Embed(description=output[:4096]))
	else: await message.channel.send(output)
