import os

import discord

from Commands.bstar.interpreter.function_deco import setupFunctions
from Commands.bstar.interpreter.run import runCode

from Commands.bstar.database.s3 import getTag, updateTag, createTag, infoTag, leaderboards, isOwnerProgram, editTag, \
	deleteTag


def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Allows you to write short tags and/or programs",
		"FORMAT": "[subcommand]",
		"CHANNEL": 0,
		"USAGE": f"""Using `tc/b* run [code]` allows you to run `[code]` as B* source code. Using `tc/b* info 
		(page)` displays a paged list of all B* programs by use count, while using `tc/b* info (program)` 
		displays information and the source code of a specific program. `tc/b* create [program] [code]` can be used 
		to save code into a specific program name, which can be edited by its creator with `tc/b* edit [program] 
		[newcode]` or deleted with `tc/b* delete [program]`. Finally, `tc/b* [program] (args)` allows you to run any 
		saved program.^n^n
		The full documentation for all B* program functionality is displayed in this document:^n
		https://www.google.com/
		""".replace("\n", "").replace("\t", "").replace("^n", "\n"),
		"CATEGORY": "Fun"
	}


PERMS = 1 # Member
ALIASES = ["B*", "BSTAR"]
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
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return

	subcommand = args[1].lower()

	# @bot.command()
	# async def run(ctx, *, message=None):
	# """Run B* code"""
	if subcommand == "run":
		try:
			output = runCode(await accept_file_or_message(message), message.author)
			await message.channel.send(embed=discord.Embed(description=output))
		except Exception as e:
			await message.channel.send(e)


	# @bot.command()
	# async def tag(ctx, message, *, args=""):
	# """Runs a B* tag"""
	if subcommand == "tag":
		tagObject = getTag(message)
		if tagObject is not None:
			code = tagObject["program"]
			# TODO: this is float only rn, do support for int in the future
			argument_list = args.split(" ")

			output = runCode(code, message.author, argument_list)
			await message.channel.send(output)

			# If all goes well, then increment the use
			updateTag(message)
		else:
			await message.channel.send(f"There's no program under the name `{message}`!")


	# @bot.command()
	# async def create(ctx, name, *, message=None):
	# """Creates a B* tag with your code"""
	if subcommand == "create":
		name = args[2]
		# try:
		if len(name) < 50:
			try:
				createTag(message.author, name, await accept_file_or_message(message))
				await message.channel.send(f"Tag `{name}` created!")
			except Exception as e:
				await message.channel.send(e)
		else:
			await message.channel.send(f"The name \"`{name}`\" is too long!")
		# except:
		#     await message.channel.send("Tag creation failed")


	# @bot.command()
	# async def info(ctx, message):
	# """Gives infomation and source code about a B* tag"""
	if subcommand == "info":
		await message.channel.send(await infoTag(message))


	# @bot.command()
	# async def leaderboard(ctx, page: int = 0):
	# 	"""Shows the leaderboard of tags sorted by uses"""
	if subcommand == "leaderboard":
		page = int(args[2])
		await message.channel.send(await leaderboards(page))


	# @bot.command()
	# async def edit(ctx, name, *, message=None):
	# 	"""Edit one of your B* tags"""
	if subcommand == "edit":
		if isOwnerProgram(name, message.author.id):
			try:
				editTag(name, await accept_file_or_message(message))
				await message.channel.send(f"Tag `{name}` edited!")
			except Exception as e:
				await message.channel.send(e)
		else:
			await message.channel.send(f"You aren't the owner of tag `{name}`!")


	# @bot.command()
	# async def delete(ctx, name):
	# 	"""Delete one of your B* tags"""
	if subcommand == "delete":
		if isOwnerProgram(name, message.author.id):
			deleteTag(name)
			await message.channel.send(f"Tag `{name}` deleted!")
		else:
			await message.channel.send(f"You aren't the owner of tag `{name}`!")