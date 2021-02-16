from Config._functions import strip_alpha, find_all, is_whole, strip_front
from Config._bpp_parsing import parenthesis_parser
from Config._bpp_functions import list_to_array, array_to_list
from Config._db import Database
import discord

def HELP(PREFIX):
	return {
		"COOLDOWN": 3,
		"MAIN": "Allows you to write short tags and/or programs with a simplified instruction set",
		"FORMAT": "[subcommand]",
		"CHANNEL": 0,
		"USAGE": f"""The full documentation for all B++ functionality is displayed in this document: 
		https://docs.google.com/document/d/1-UOafQ0qW0AzpR1xxCYU_2__VulfofMDeD62vjhptMM/edit
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 1 # Member
ALIASES = ["TAG"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	VARIABLES = {}

	db = Database()

	if args[1].lower() == "info":
		tag_list = db.get_entries("b++programs", columns=["name", "program", "author", "uses"])
		tag_list = sorted(tag_list, reverse=True, key=lambda m: m[3])

		tag_leaderboard = False
		if level == 2: # If it's not specified, assume it's the first page
			tag_list = tag_list[:10]
			page = 1
			tag_leaderboard = True
		
		elif is_whole(args[2]):
			if (int(args[2]) - 1) * 10 >= len(tag_list): # Detect if the page number is too big
				await message.channel.send(f"There is no page {args[2]} on the B++ program list!")
				return
		
			else: # This means the user specified a valid page number
				lower = (int(args[2]) - 1) * 10
				upper = int(args[2]) * 10
				tag_list = tag_list[lower:upper]
				page = int(args[2])
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

				line += f" (written by {member})\n"
			
				beginning += line # Add this line to the final message
			
			beginning += "```" # Close off code block

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
		
		if len(program[1]) + 6 >= 1900:
			program_code_msg = program[1]
			if len(program_code_msg) >= 1990:
				await message.channel.send(f"**{program[0]}** (written by {member})")
				await message.channel.send(f"```{program_code_msg[:1000]}```")
				await message.channel.send(f"```{program_code_msg[1000:]}```")
				await message.channel.send(f"Used {program[3]} time{'s' if program[3] != 1 else ''})
			else:
				await message.channel.send(f"**{program[0]}** (written by {member})")
				await message.channel.send(f"```{program_code_msg}```")
				await message.channel.send(f"Used {program[3]} time{'s' if program[3] != 1 else ''})
		else:
			await message.channel.send(f"""**{program[0]}** (written by {member})
			```{program[1]}```
			Used {program[3]} time{'s' if program[3] != 1 else ''}""".replace("\n", "").replace("\t", ""))
		return

	if args[1].lower() == "delete":
		if level == 2:
			await message.channel.send("Include the name of the program you want to delete!")
			return
		
		tag_name = args[2]

		tag_list = db.get_entries("b++programs", columns=["name", "author"])
		if tag_name in [x[0] for x in tag_list]:

			ind = [x[0] for x in tag_list].index(tag_name)
			if tag_list[ind][1] != str(message.author.id) and perms != 2:
				await message.channel.send(f"You can only delete a program you created!")
				return
			
			db.remove_entry("b++programs", conditions={"name": tag_name})
			await message.channel.send(f"Succesfully deleted program {tag_name}!")

		else:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")

		return

	if args[1].lower() == "edit":
		if level == 2:
			await message.channel.send("Include the name of the program you want to edit!")
			return
		
		if level == 3:
			await message.channel.send("Include the new code for the program you want to edit!")
			return
		
		tag_name = args[2]

		program = " ".join(args[3:])

		if program.startswith("```") and program.endswith("```"):
			program = program[3:-3]
		if program.startswith("``") and program.endswith("``"):
			program = program[2:-2]
		if program.startswith("`") and program.endswith("`"):
			program = program[1:-1]

		tag_list = db.get_entries("b++programs", columns=["name", "author"])
		if tag_name in [x[0] for x in tag_list]:

			ind = [x[0] for x in tag_list].index(tag_name)
			if tag_list[ind][1] != str(message.author.id) and perms != 2:
				await message.channel.send(f"You can only edit a program you created!")
				return
			
			db.edit_entry("b++programs", entry={"program": program}, conditions={"name": tag_name})
			await message.channel.send(f"Succesfully edited program {tag_name}!")

		else:
			await message.channel.send(f"There's no program under the name `{tag_name}`!")

		return


	if args[1].lower() not in ["run", "create"]:
		tag_name = args[1]
		if (tag_name,) in db.get_entries("b++programs", columns=["name"]):
			program, uses = db.get_entries(
				"b++programs", columns=["program", "uses"], conditions={"name": tag_name})[0]
			
			uses += 1
			db.edit_entry("b++programs", entry={"uses": uses}, conditions={"name": tag_name})
		
		else:
			await message.channel.send(f"There's no tag under the name `{args[1]}`!")
			return

	else:
		if args[1].lower() == "run":
			if level == 2:
				await message.channel.send("Include a program to run!")
				return
			
			program = " ".join(args[2:])
		

		if args[1].lower() == "create":
			if level == 2:
				await message.channel.send("Include the name of your new program!")
				return
			
			if level == 3:
				await message.channel.send("Include the code for your program!")
				return
		
			tag_name = args[2]

			if len(tag_name) > 30:
				await message.channel.send("That tag name is too long. 30 characters maximum.")
				return
			
			program = " ".join(args[3:])

		if program.startswith("```") and program.endswith("```"):
			program = program[3:-3]
		if program.startswith("``") and program.endswith("``"):
			program = program[2:-2]
		if program.startswith("`") and program.endswith("`"):
			program = program[1:-1]

		if args[1].lower() == "create":
			if (tag_name,) in db.get_entries("b++programs", columns=["name"]):
				await message.channel.send("There's already a program with that name!")
				return
			
			db.add_entry("b++programs", [tag_name, program, message.author.id, 0])
			await message.channel.send(f"Successfully created program `{tag_name}`!")
			return

	semicolon_inds = find_all(program, ";")
	semicolon_inds = [x for x in semicolon_inds if program[x-1] != "\\"]

	program_chars = list(program)
	for ind in semicolon_inds:
		program_chars[ind] = "\n"
	program = ''.join(program_chars).replace("\t", "")

	lines = program.split("\n")

	context = []
	OUTPUT = ""
	try:
		try:
			tag_vars = db.get_entries("b++variables", columns=["name", "value"], conditions={"tag": tag_name})
			for var in tag_vars:
				value = var[1]
				if value.startswith("[") and value.endswith("]"):
					value = array_to_list(value)
				VARIABLES[var[0]] = value
		except:
			pass

		for line in lines:
			c_line = line

			if len(context) == 0:
				declaration = " = " in c_line
				array_context = "[" in c_line.replace("\[", "") and "]" not in c_line.replace("\]", "")

				if array_context:
					context.append(["array", c_line, c_line[c_line.find("["):]])
					continue
			else:
				context_list = [x[0] for x in context]
				if "array" in context_list:
					this_context = context[context_list.index("array")]

					this_context[1] += "\t" + c_line
					if "]" not in line.replace("\]", ""):
						this_context[2] += "\t" + c_line
						continue
					else:
						this_context[2] += c_line[:c_line.find("]")+1]
						c_line = this_context[1]
						del context[context_list.index("array")]
						declaration = " = " in c_line

			if declaration: # Deal with variable declaration
				c_line = c_line.replace("\\=", "\n")
				c_line = c_line.replace("==", "\t\t")
				
				sides = c_line.split("=")
				sides[1] = "=".join(sides[1:])

				sides = [x.replace("\n", "\=") for x in sides]
				sides = [x.replace("\t\t", "==") for x in sides]
				c_line = c_line.replace("\n", "=")
				c_line = c_line.replace("\t\t", "==")

				sides[0] = parenthesis_parser(sides[0].strip(), VARIABLES, OUTPUT)[0]
				sides[1] = parenthesis_parser(strip_front(sides[1]), VARIABLES, OUTPUT, var=True)[0]

				VARIABLES[sides[0]] = sides[1]
				continue

			line_info, OUTPUT = parenthesis_parser(c_line.strip(), VARIABLES, OUTPUT)
		
	except Exception as e:
		await message.channel.send(f'{type(e).__name__} in line `{c_line}`:\n\t{e}')
		return

	try:
		await message.channel.send(
		OUTPUT.replace("<@", "<\@").replace("\\\\", "\t\t").replace("\\", "").replace("\t\t", "\\").replace(u"\uF000","\n",50)[:1950])
	except discord.errors.HTTPException:
		pass
	
	try:
		tag_name
		tag_vars = db.get_entries("b++variables", columns=["name"], conditions={"tag": tag_name})

		for var in VARIABLES.keys():
			if var.startswith("__"):
				if type(VARIABLES[var]) == list:
					VARIABLES[var] = list_to_array(VARIABLES[var])

				if (var,) in tag_vars:
					db.edit_entry("b++variables", entry={"value": str(VARIABLES[var])}, conditions={"name": var})
					continue
				
				db.add_entry("b++variables", entry=[var, str(VARIABLES[var]), tag_name])
	except:
		pass
	return
