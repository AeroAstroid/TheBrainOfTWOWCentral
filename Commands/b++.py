from Config._const import PREFIX
from Config._functions import strip_alpha, find_all
from Config._bpp_parsing import parenthesis_parser
from Config._bpp_functions import list_to_array, array_to_list
from Config._db import Database
import discord

HELP = {
	"MAIN": "Allows you to write short tags and/or programs with a simplified instruction set",
	"FORMAT": "[subcommand]",
	"CHANNEL": 0,
	"USAGE": f"""The full documentation for all B++ functionality is displayed in this document: 
	https://docs.google.com/document/d/1-UOafQ0qW0AzpR1xxCYU_2__VulfofMDeD62vjhptMM/edit
	""".replace("\n", "").replace("\t", "")
}

PERMS = 1 # Member
ALIASES = ["TAG"]
REQ = []

async def MAIN(message, args, level, perms):
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	VARIABLES = {}

	db = Database()

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
				c_line.replace("\\=", "\n")
				c_line.replace("==", "\t\t")
				
				sides = c_line.split("=")
				sides[1] = "=".join(sides[1:])

				c_line.replace("\n", "=")
				c_line.replace("\t\t", "==")

				sides[0] = parenthesis_parser(sides[0].strip(), VARIABLES, OUTPUT)[0]
				sides[1] = parenthesis_parser(sides[1].strip(), VARIABLES, OUTPUT)[0]

				VARIABLES[sides[0]] = sides[1]
				continue

			line_info, OUTPUT = parenthesis_parser(c_line.strip(), VARIABLES, OUTPUT)
		
	except Exception as e:
		await message.channel.send(f'{type(e).__name__} in line `{c_line}`:\n\t{e}')
		return

	try:
		await message.channel.send(OUTPUT.replace("<@", "<\@")[:1950])
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