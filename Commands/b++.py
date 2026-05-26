from Config._functions import strip_alpha, find_all, is_whole, strip_front

from Config._bxe_parsing import run_bxe_program, get_ext_docs, format_doc
from Config._bpp_program_cache import BrainProgramCache

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
		"USAGE": f"""
		
		- `tc/b++ run [code]`^n
		  - [code] is run as B++ source code.^n
		  - If `debug` is added before `run`, the code is ran in debug mode.^n
		- `tc/b++ info (page or program)`^n
		  - Using a page number (or nothing) displays a paged list of all B++ programs by uses.^n
		  - Using a program name displays information about that program as well as source code.^n
		- `tc/b++ create [program] [code]`^n
		  - Creates a tag under the name [program], with the source code being [code].^n
		- `tc/b++ edit [program] [code]`^n
		  - Edits the source code of [program] if it belongs to you.^n
		- `tc/b++ delete [program]`^n
		  - Deletes the specified program if it belongs to you.^n
		- `tc/b++ tags (page)`^n
		  - Displays a paged list of all B++ programs that belong to you by uses.^n
		- `tc/b++ docs (function)`^n
		  - Shows the description of a specified function. If no function is provided, shows the list of all B++ functions.^n
		- `tc/b++ [program] (args)^n
		  - Runs the program with any specified args. Putting `debug` before the program name runs it in debug mode.^n
		""".replace("\n", "").replace("\t", "").replace("^n", "\n"),
		"CATEGORY" : "Fun"
	}

PERMS = 1 # Member
ALIASES = ["TAG", "B++NEW", "TAGNEW", "NEWB++", "NEWTAG", "BPP", "BXE"]
REQ = []

LATEST_BUTTONS = {}

BUTTON_STYLE_ALIASES = {
	"gray": discord.ButtonStyle.secondary,
	"grey": discord.ButtonStyle.secondary,
	"secondary": discord.ButtonStyle.secondary,
	"default": discord.ButtonStyle.secondary,
	"blue": discord.ButtonStyle.primary,
	"primary": discord.ButtonStyle.primary,
	"blurple": discord.ButtonStyle.primary,
	"green": discord.ButtonStyle.success,
	"success": discord.ButtonStyle.success,
	"red": discord.ButtonStyle.danger,
	"danger": discord.ButtonStyle.danger
}

def resolve_button_style(button_color):
	if button_color is None:
		return discord.ButtonStyle.secondary
	style_key = str(button_color).strip().lower()
	return BUTTON_STYLE_ALIASES.get(style_key, discord.ButtonStyle.secondary)

BUTTON_LOCK_ALIASES = {
	"true", "t", "1", "yes", "y", "on", "lock", "locked"
}

def resolve_button_lock(button_lock):
	if button_lock is None:
		return False
	return bool(button_lock)

def format_debug_warnings(warnings):
	if len(warnings) == 0:
		return "Debug mode: no syntax warnings."

	lines = [f"Debug mode: {len(warnings)} warning{'s' if len(warnings) != 1 else ''} detected."]
	for i, warning in enumerate(warnings, 1):
		lines.append(f"{warning.message}\n{warning.range.debug_info()}")
	
	return "\n\n".join(lines)

async def MAIN(message, args, level, perms, SERVER):

	if message.channel.id == 598616636823437352 and perms < 2:
		return
	
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	program_cache = BrainProgramCache()
	
	if args[1].lower() == "tags":
		tag_list = program_cache.list_programs()
		
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
		tag_leaderboard = False
		if level == 2: # If it's not specified, assume it's the first page
			tag_list = program_cache.list_programs()
			tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])
			tag_list = tag_list[:10]
			page = 1
			tag_leaderboard = True
		
		elif is_whole(args[2]):
			tag_list = program_cache.list_programs()
			tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])
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
			tag_list = program_cache.list_programs()
			tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])
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
		program = program_cache.get_program(tag_name)
		if program is None:
			await message.channel.send("That tag does not exist.")
			return

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

	if args[1].lower() == "docs":
		docs = get_ext_docs()
		if level == 2:
			funcs = ", ".join([i.upper() for i in docs.keys()])
			embed = {"title": "All B++ functions", "description": funcs, "color": 0x93a5a6}
			await message.channel.send(embed=discord.Embed.from_dict(embed))
			return
		term = args[2].upper()
		func = ""
		for f in docs:
			if f.upper().startswith(term):
				func = f.upper()
		if not func:
			await message.channel.send("Could not find a function with that name!")
			return
		desc = docs[func]
		if desc:
			embed = format_doc(func, desc)
			embed["color"] = 0x93a5a6
		else:
			embed = {"title": func, "description": "No documentation was found for this function.", "color": 0x93a5a6}
		await message.channel.send(embed=discord.Embed.from_dict(embed))
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
		
		if tag_name in ["create", "edit", "delete", "info", "run", "help", "tags", "debug", "docs"]:
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

		if program_cache.get_program(tag_name) is not None:
			await message.channel.send("There's already a program with that name!")
			return
		
		program_cache.create_program(tag_name, program, message.author.id)
		await message.channel.send(f"Successfully created program `{tag_name}`!")
		return


	if args[1].lower() == "edit":
		if level == 2:
			await message.channel.send("Include the name of the program you want to edit!")
			return
		
		tag_name = args[2]

		tag_info = program_cache.get_program(tag_name)

		if tag_info is None:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")
			return

		if tag_info[2] != str(message.author.id) and perms < 2:
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
		
		program_cache.edit_program(tag_name, program)
		await message.channel.send(f"Succesfully edited program {tag_name}!")
		return


	if args[1].lower() == "delete":
		if level == 2:
			await message.channel.send("Include the name of the program you want to delete!")
			return
		
		tag_name = args[2]

		tag_info = program_cache.get_program(tag_name)

		if tag_info is None:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")
			return

		if tag_info[2] != str(message.author.id) and perms < 2:
			await message.channel.send(f"You can only edit a program if you created it or if you're a staff member!")
			return
			
		program_cache.delete_program(tag_name)
		await message.channel.send(f"Succesfully deleted program {tag_name}!")
		return


	debug_mode = False
	invocation_name = args[1]

	if args[1].lower() == "debug":
		debug_mode = True
		if level == 2:
			await message.channel.send("Include `run` or a tag name for debug mode!")
			return

		if args[2].lower() == "run":
			invocation_name = "run"
			if len(message.attachments) != 0:
				try:
					if message.attachments[0].size >= 60000:
						await message.channel.send("Your program must be under **60KB**.")
						return

					await message.attachments[0].save(f"Config/{message.id}.txt")

				except Exception:
					await message.channel.send("Include a valid program to run!")
					return

				program_args = args[3:]
				program = open(f"Config/{message.id}.txt", "r", encoding="utf-8").read()
				os.remove(f"Config/{message.id}.txt")

			elif level > 3:
				program_args = []
				program = " ".join(args[3:])

			else:
				await message.channel.send("Include a valid program to run!")
				return

			while program.startswith("`") and program.endswith("`"):
				program = program[1:-1]
			
			program = program.replace("{}", "\v")
			author = message.author.id
			runner = message.author
		else:
			tag_name = args[2]
			invocation_name = tag_name
			tag_info = program_cache.increment_uses(tag_name)

			if tag_info is None:
				await message.channel.send(f"There's no program under the name `{tag_name}`!")
				return
			
			program = tag_info[1]

			program_args = args[3:]
			author = tag_info[2]
			runner = message.author

	elif args[1].lower() == "run":
		invocation_name = "run"
		if len(message.attachments) != 0:
			try:
				if message.attachments[0].size >= 60000:
					await message.channel.send("Your program must be under **60KB**.")
					return

				await message.attachments[0].save(f"Config/{message.id}.txt")

			except Exception:
				await message.channel.send("Include a valid program to run!")
				return

			program_args = args[2:]
			program = open(f"Config/{message.id}.txt", "r", encoding="utf-8").read()
			os.remove(f"Config/{message.id}.txt")

		elif level > 2:
			program_args = []
			program = " ".join(args[2:])

		else:
			await message.channel.send("Include a valid program to run!")
			return

		while program.startswith("`") and program.endswith("`"):
			program = program[1:-1]
		
		program = program.replace("{}", "\v")
		author = message.author.id
		runner = message.author
	
	else:
		tag_name = args[1]
		invocation_name = tag_name

		tag_info = program_cache.increment_uses(tag_name)

		if tag_info is None:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")
			return
		
		program = tag_info[1]

		program_args = args[2:]
		author = tag_info[2]
		runner = message.author

	async def evaluate_and_send(program, program_args, author, runner, message, invocation_name, debug_mode=False, is_button=False):
		program_output, buttons, warnings = run_bxe_program(program, program_args, author, runner, message.channel)

		warning_prefix = ""
		if debug_mode:
			warning_output = format_debug_warnings(warnings)
			warning_prefix = f"```{warning_output}```\n\n"

		if isinstance(program_output, Exception):
			warning_path = None
			warning_file = None
			if debug_mode:
				warning_path = f"Config/{message.id}_warnings.txt"
				open(warning_path, "w", encoding="utf-8").write(format_debug_warnings(warnings))
				warning_file = discord.File(warning_path, filename="bpp_debug_warnings.txt")

			try:
				await message.channel.send(
					embed=discord.Embed(
						color=0xFF0000,
						title=f'{type(program_output).__name__}',
						description=f'```{program_output}```'
					),
					file=warning_file,
					allowed_mentions=discord.AllowedMentions.none()
				)
			finally:
				if warning_path is not None and os.path.exists(warning_path):
					os.remove(warning_path)
			return
		
		program_output = program_output
		if is_button:
			program_output = program_output.rstrip()+f"\n-# Button pressed by {runner.mention}"
		combined_output = f"{warning_prefix}{program_output}"

		async def button_callback(program, button_args, locked_runner_id, interaction):
			try:
				if locked_runner_id is not None and interaction.user.id != locked_runner_id:
					await interaction.response.send_message(
						"This button is locked to the user who ran this command.",
						ephemeral=True
					)
					return
		
				tag_info = program_cache.increment_uses(invocation_name)
		
				if tag_info is not None:
					program = tag_info[1]
				
					author = tag_info[2]
				else:
					author = interaction.user.id
					
				if hash(program) not in LATEST_BUTTONS.keys() or LATEST_BUTTONS[hash(program)] <= interaction.message.id:
					await evaluate_and_send(program, button_args, author, interaction.user, interaction.message, invocation_name, False, True)
				
				await interaction.response.edit_message(view=None)
			except Exception as e:
				await interaction.response.send_message(embed=discord.Embed(color=0xFF0000, title=f'{type(e).__name__}', description=f'```{e}\n\n{traceback.format_tb(e.__traceback__)}```'))
				
	
		out_view = View()
		for button_value in buttons:
			if len(button_value) == 1: button_value += ["​"]
			button_style = resolve_button_style(button_value[2]) if len(button_value) >= 3 else discord.ButtonStyle.secondary
			button_locked = resolve_button_lock(button_value[3]) if len(button_value) >= 4 else False
			button_args = button_value[0].split()
			button = Button(label = button_value[1] if button_value[1] != "" else "​", style = button_style, custom_id = f"{time.time()} {invocation_name} {button_value[0]}", disabled=button_value[0]=="null")
			button.callback = partial(button_callback, program, button_args, runner.id if button_locked else None)
			out_view.add_item(button)
	
		if len(combined_output.strip()) == 0: combined_output = "\u200b"
			
		if len(combined_output) <= 2000:
			cmd_output = await message.reply(combined_output,view=out_view,allowed_mentions=discord.AllowedMentions.none())
		elif len(combined_output) <= 4096:
			cmd_output = await message.reply(embed = discord.Embed(description = combined_output, type = "rich"),view=out_view,allowed_mentions=discord.AllowedMentions.none())
		else:
			open(f"Config/{message.id}out.txt", "w", encoding="utf-8").write(combined_output[:150000])
			outfile = discord.File(f"Config/{message.id}out.txt")
			os.remove(f"Config/{message.id}out.txt")
			cmd_output = await message.reply("`Output too long! Sending first 150k characters in text file.`", file=outfile,view=out_view,allowed_mentions=discord.AllowedMentions.none())

		if len(buttons) != 0:
			LATEST_BUTTONS[hash(program)] = cmd_output.id
	
	await evaluate_and_send(program, program_args, author, runner, message, invocation_name, debug_mode)
		
	
