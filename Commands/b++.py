from Config._functions import strip_alpha, find_all, is_whole, strip_front

from Config._bpp_parsing import *

from Config._bpp_functions import ProgramDefinedException

from Config._db import Database

import discord, os, re, time, traceback

from discord.ui import Button, View

from datetime import datetime as dt

from functools import partial

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
		[newcode]` or deleted with `tc/b++ delete [program]`. You can check your existing programs with `tc/b++ tags`.
		Finally, `tc/b++ [program] (args)` allows you to run any saved program.^n^n
		The full documentation for all B++ program functionality is displayed in this document:^n
		https://docs.google.com/document/d/1pU2ezYE505sAPEmnSMNx9yfzD7FT4_KmICOkEUpMSA8/edit?usp=sharing
		""".replace("\n", "").replace("\t", "").replace("^n", "\n"),
		"CATEGORY" : "Fun"
	}

PERMS = 1 # Member
ALIASES = ["TAG", "B++NEW", "TAGNEW", "NEWB++", "NEWTAG", "BPP"]
REQ = []

LATEST_BUTTONS = {}

async def MAIN(message, args, level, perms, SERVER):

	if message.channel.id == 598616636823437352 and perms < 2:
		return
	
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	db = Database()
	
	if args[1].lower() == "tags":
		tag_list = db.get_entries("b++2programs", columns=["name", "program", "author", "uses", "created"])
		
		tag_list = [tag for tag in tag_list if tag[2] == str(message.author.id)]
		tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])
		
		# basically the same as info here
		tag_leaderboard = False
		if level == 2: # If it's not specified, assume it's the first page
			tag_list = tag_list[:10]
			page = 1
			tag_leaderboard = True
			
		elif is_whole(args[2]):
			if (int(args[2]) - 1) * 10 >= len(tag_list): # Detect if the page number is too big
				await message.channel.send(f"There is no page {args[2]} on your tags list!")
				return
		
			else: # This means the user specified a valid page number
				lower = (int(args[2]) - 1) * 10
				upper = int(args[2]) * 10
				tag_list = tag_list[lower:upper]
				page = int(args[2])
				tag_leaderboard = True
	
		if tag_leaderboard:
			beginning = f"```diff\nB++ Programs Page {page} for user {message.author.name}\n\n"

			for program in tag_list:
				r = tag_list.index(program) + 1 + (page - 1) * 10
				
				line = f"{r}{' '*(2-len(str(r)))}: {program[0]} :: {program[3]} use{'s' if program[3] != 1 else ''}"

				created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
				line += f" (written at {created_on})\n"
				beginning += line # Add this line to the final message
			
			beginning += "```" # Close off code block

			await message.channel.send(beginning)
		return
		
	if args[1].lower() == "info":
		tag_list = db.get_entries("b++2programs", columns=["name", "program", "author", "uses", "created", "lastused"])
		tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])

		tag_leaderboard = False
		if level == 2: # If it's not specified, assume it's the first page
			tag_list = tag_list[:10]
			page = 1
			tag_leaderboard = True
		
		elif is_whole(args[2]):
			if (int(args[2]) - 1) * 10 >= len(tag_list): # Detect if the page number is too big
				await message.channel.send(f"There is no page {args[2]} on the New B++ program list!")
				return
		
			else: # This means the user specified a valid page number
				lower = (int(args[2]) - 1) * 10
				upper = int(args[2]) * 10
				tag_list = tag_list[lower:upper]
				page = int(args[2])
				tag_leaderboard = True

		elif args[2].lower() == "all":
			page = 1
			tag_leaderboard = True
	
		if tag_leaderboard:
			beginning = f"```diff\nB++ Programs Page {page}\n\n"

			for program in tag_list:
				r = tag_list.index(program) + 1 + (page - 1) * 10
				
				line = f"{r}{' '*(2-len(str(r)))}: {program[0]} :: {program[3]} use{'s' if program[3] != 1 else ''}"

				member_id = program[2]
				try: # Try to gather a username from the ID
					member = SERVER["MAIN"].get_member(int(member_id)).name
				except: # If you can't, just display the ID
					member = str(member_id)

				created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
				line += f" (written by {member} at {created_on})\n"
			
				beginning += line # Add this line to the final message
			
			beginning += "```" # Close off code block

			if len(tag_list) > 10:
				open(f'bpp_tags.txt', 'w', encoding="utf-8").write(beginning)
				await message.channel.send("Here's a list of all B++ tags:", file=discord.File(f'bpp_tags.txt'))
				os.remove(f'bpp_tags.txt')
			else:
				await message.channel.send(beginning)
			return

		tag_name = args[2]

		if tag_name not in [x[0] for x in tag_list]:
			await message.channel.send("That tag does not exist.")
			return
		
		program = tag_list[[x[0] for x in tag_list].index(tag_name)]

		member_id = program[2]
		try: # Try to gather a username from the ID
			member = SERVER["MAIN"].get_member(int(member_id)).name
		except: # If you can't, just display the ID
			member = str(member_id)
		
		created_on = dt.utcfromtimestamp(program[4]).strftime('%Y-%m-%d %H:%M:%S UTC')
		c_d = dt.now() - dt.utcfromtimestamp(program[4])

		d = c_d.days
		h, rm = divmod(c_d.seconds, 3600)
		m, s = divmod(rm, 60)

		c_d = (('' if d==0 else f'{d} day{"s" if d!=1 else ""}, ') +
		('' if h==0 else f'{h} hour{"s" if h!=1 else ""}, ') +
		('' if m==0 else f'{m} minute{"s" if m!=1 else ""}, ') +
		(f'{s} second{"s" if s!=1 else ""}'))
		
		msg = f"**{program[0]}** -- by {member} -- {program[3]} use{'s' if program[3]!=1 else ''}\n"
		msg += f"Created on {created_on} `({c_d} ago)`\n"

		if program[5] != 0:
			last_used = dt.utcfromtimestamp(program[5]).strftime('%Y-%m-%d %H:%M:%S UTC')
			u_d = dt.now() - dt.utcfromtimestamp(program[5])
			
			d = u_d.days
			h, rm = divmod(u_d.seconds, 3600)
			m, s = divmod(rm, 60)

			u_d = (('' if d==0 else f'{d} day{"s" if d!=1 else ""}, ') +
			('' if h==0 else f'{h} hour{"s" if h!=1 else ""}, ') +
			('' if m==0 else f'{m} minute{"s" if m!=1 else ""}, ') +
			(f'{s} second{"s" if s!=1 else ""}'))

			msg += f"Last used on {last_used} `({u_d} ago)`\n"

		if len(program[1]) > 1700:
			fprefix = "txt"
			
			if level >= 3 and args[-1].lower() == "bpp":
				fprefix = "bpp"
			
			msg += f"The program is too long to be included in the message, so it's in the file below:"
			open(f'program_{program[0]}.{fprefix}', 'w', encoding="utf-8").write(program[1])
			await message.channel.send(msg, file=discord.File(f'program_{program[0]}.{fprefix}'))
			os.remove(f'program_{program[0]}.{fprefix}')
		else:
			msg += f"```{program[1]}```"
			await message.channel.send(msg)
		
		return


	if args[1].lower() == "create":
		if level == 2:
			await message.channel.send("Include the name of your new program!")
			return
	
		tag_name = args[2]

		if re.search(r"[^0-9A-Za-z_]", tag_name) or re.search(r"[0-9]", tag_name[0]):
			await message.channel.send(
			"Tag name can only contain letters, numbers and underscores, and cannot start with a number!")
			return
		
		if tag_name in ["create", "edit", "delete", "info", "run", "help", "tags"]:
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

		if (tag_name,) in db.get_entries("b++2programs", columns=["name"]):
			await message.channel.send("There's already a program with that name!")
			return
		
		db.add_entry("b++2programs", [tag_name, program, message.author.id, 0, time.time(), 0])
		await message.channel.send(f"Successfully created program `{tag_name}`!")
		return


	if args[1].lower() == "edit":
		if level == 2:
			await message.channel.send("Include the name of the program you want to edit!")
			return
		
		tag_name = args[2]

		tag_list = db.get_entries("b++2programs", columns=["name", "author"])

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
		
		db.edit_entry("b++2programs", entry={"program": program}, conditions={"name": tag_name})
		await message.channel.send(f"Succesfully edited program {tag_name}!")
		return


	if args[1].lower() == "delete":
		if level == 2:
			await message.channel.send("Include the name of the program you want to delete!")
			return
		
		tag_name = args[2]

		tag_list = db.get_entries("b++2programs", columns=["name", "author"])

		if tag_name not in [x[0] for x in tag_list]:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")
			return

		ind = [x[0] for x in tag_list].index(tag_name)
		if tag_list[ind][1] != str(message.author.id) and perms < 2:
			await message.channel.send(f"You can only edit a program if you created it or if you're a staff member!")
			return
			
		db.remove_entry("b++2programs", conditions={"name": tag_name})
		await message.channel.send(f"Succesfully deleted program {tag_name}!")
		return


	if args[1].lower() == "run":
		if level > 2:
			program = " ".join(args[2:])

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

		program_args = []

		author = message.author.id

		runner = message.author
	
	else:
		tag_name = args[1]

		tag_list = db.get_entries("b++2programs", columns=["name", "program", "author", "uses"])

		if tag_name not in [x[0] for x in tag_list]:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")
			return
		
		tag_info = [x for x in tag_list if x[0] == tag_name][0]
		program = tag_info[1]

		uses = tag_info[3] + 1
		db.edit_entry("b++2programs", entry={"uses": uses, "lastused": time.time()}, conditions={"name": tag_name})

		program_args = args[2:]

		author = tag_info[2]

		runner = message.author

	async def evaluate_and_send(program, program_args, author, runner, message, is_button=False):
		try:
			program_output, buttons = run_bpp_program(program, program_args, author, runner, message.channel)
		except Exception as e:
			await message.channel.send(embed=discord.Embed(color=0xFF0000, title=f'{type(e).__name__}', description=f'```{e}```'),allowed_mentions=discord.AllowedMentions.none())
			#await message.channel.send(embed=discord.Embed(color=0xFF0000, title=f'{type(e).__name__}', description=f'```{e}\n\n{traceback.format_tb(e.__traceback__)}```'.replace("<@", "<\\@")))
			return
		if isinstance(program_output, Exception):
			color = 0xFF0000
			if isinstance(program_output, ProgramDefinedException): color = None
			await message.channel.send(embed=discord.Embed(color=color, title=f'{type(program_output).__name__}', description=f'```{program_output}```'),allowed_mentions=discord.AllowedMentions.none())
			return
		
		program_output = program_output
		if is_button:
			program_output = program_output.rstrip()+f"\n-# Button pressed by {runner.mention}"

		async def button_callback(program, interaction):
			try:
				custom_id = interaction.data['custom_id']
				tag_name = custom_id.split(" ")[1]
		
				tag_list = db.get_entries("b++2programs", columns=["name", "program", "author", "uses"])
		
				if tag_name in [x[0] for x in tag_list]:
					#await interaction.response.send_message(f"There's no program under the name `{tag_name}`!",allowed_mentions=discord.AllowedMentions.none())
					#return
				
					tag_info = [x for x in tag_list if x[0] == tag_name][0]
					program = tag_info[1]
			
					uses = tag_info[3] + 1
					db.edit_entry("b++2programs", entry={"uses": uses, "lastused": time.time()}, conditions={"name": tag_name})
				
					author = tag_info[2]
				else:
					author = interaction.user.id
					
				if hash(program) not in LATEST_BUTTONS.keys() or LATEST_BUTTONS[hash(program)] <= interaction.message.id:
					await evaluate_and_send(program, custom_id.split(" ")[2:], author, interaction.user, interaction.message, True)
				
				await interaction.response.edit_message(view=None)
			except:
				await interaction.response.send_message(embed=discord.Embed(color=0xFF0000, title=f'{type(e).__name__}', description=f'```{e}\n\n{traceback.format_tb(e.__traceback__)}```'))
				
	
		out_view = View()
		for button_value in buttons:
			if len(button_value) == 1: button_value += ["​"]
			button = Button(label = button_value[1] if button_value[1] != "" else "​", style = discord.ButtonStyle.secondary, custom_id = f"{time.time()} {args[1]} {button_value[0]}", disabled=button_value[0]=="null")
			button.callback = partial(button_callback, program)
			out_view.add_item(button)
	
		if len(program_output.strip()) == 0: program_output = "\u200b"
			
		if len(program_output) <= 2000:
			cmd_output = await message.reply(program_output,view=out_view,allowed_mentions=discord.AllowedMentions.none())
		elif len(program_output) <= 4096:
			cmd_output = await message.reply(embed = discord.Embed(description = program_output, type = "rich"),view=out_view,allowed_mentions=discord.AllowedMentions.none())
		else:
			open(f"Config/{message.id}out.txt", "w", encoding="utf-8").write(program_output[:150000])
			outfile = discord.File(f"Config/{message.id}out.txt")
			os.remove(f"Config/{message.id}out.txt")
			cmd_output = await message.reply("⚠️ `Output too long! Sending first 150k characters in text file.`", file=outfile,view=out_view,allowed_mentions=discord.AllowedMentions.none())

		if len(buttons) != 0:
			LATEST_BUTTONS[hash(program)] = cmd_output.id
	
	await evaluate_and_send(program, program_args, author, runner, message)
		
	
