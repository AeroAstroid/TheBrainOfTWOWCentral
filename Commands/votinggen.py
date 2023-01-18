# VOTINGGEN command - Generates voting screens for TWOW Central SpeedTWOWs
# Code written by Neonic
################################
from Config._const import ALPHABET, ALPHANUM_UNDERSCORE, BRAIN
from Config._words import WORDS
from Config._screennames import SCREEN_NAMES
import time, discord, random, csv, asyncio, copy, math, textwrap, traceback, os, importlib
from Config._functions import grammar_list, word_count, formatting_fix
from discord.ui import Button, View, Select

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "Generating voting screens for TWOW Central SpeedTWOWs",
		"FORMAT": "",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}votinggen` with a .tsv file attached will generate voting 
			screens for you! This command is best used when it is used with the `tc/event responding` 
			event, which gives you a VOTING tsv that you can attach in the usage of this command.""".replace("\n", "").replace("\t", ""),
		"HIDE" : 0,
		"CATEGORY" : "Utility"
	}

PERMS = 2
ALIASES = ["GENVOTING", "GENERATEVOTING"]
REQ = []

RESPONSES_SAVE_PATH = "Commands/votinggenresponses.tsv"
RESPONSE_IDS_SAVE_PATH = "Commands/vottinggenresponseids.tsv"
SCREENS_SAVE_PATH = "Commands/votinggenscreens.tsv"
TEXT_SCREEN_PATH = "Commands/votinggentextscreens.txt"

VOTE_CHRS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&'()*+,-./0123456789:;<=>?@^_{|}~"

VALID_RESPONSE = "✔️"
NOT_VALID_RESPONSE = "❌"

async def integer_input (user, channel, message: str, min: int, max: int):

	input = None
	while input == None:

		await channel.send(message)
	
		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == user and m.channel == channel))
		try:

			if msg.content.lower() == "cancel":
				break

			i = int(msg.content)
			if i < min or i > max:
				raise ValueError
			else:
				input = i
				break

		except ValueError:
			channel.send(f"You must provide an integer higher than {min} and lower than {max} (inclusive)!")

	return input

async def boolean_input (user, channel, message: str):

	input = None
	while input == None:

		await channel.send(message)
	
		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == user and m.channel == channel))
		try:

			if msg.content.lower() == "cancel":
				break

			if msg.content.lower() in ["y", "yes", "true"]:
				input = True
				break
			elif msg.content.lower() in ["n", "no", "false"]:
				input = False
				break
			else:
				raise ValueError

		except ValueError:
			channel.send(f"You must either input 'Y' or 'N'!")

	return input

async def MAIN(message, args, level, perms, SERVER):

	# Finding TSV attachment which has all the responses
	if len(message.attachments) == 0: 
		await message.channel.send("You must include a TSV file!")
		return

	attachment = message.attachments[0]

	tsv_list = []

	# Try save the tsv file
	try:
		await attachment.save(RESPONSES_SAVE_PATH)
	except:
		pass

	# Open TSV and store results in a dictionary
	try: 
		with open(RESPONSES_SAVE_PATH, 'r', encoding='UTF-8') as tsv_file:
			reader = csv.reader(tsv_file, delimiter = "\t")
			for row in list(reader):
				tsv_list.append(row)
	except Exception:
		await message.channel.send(f"Error occured while attempting to open this TSV file: ```python\n{traceback.format_exc()}```")
		return

	# Remove the first row 
	tsv_list.pop(0)

	# Iterate through all rows of the TSV file
	# This checks for the first empty row and cuts the
	# TSV file off right before the first empty row.
	for row_num in range(len(tsv_list)):
		targeted_tsv_row = tsv_list[row_num]
		if targeted_tsv_row[0] == "":
			slice_obj = slice(row_num)
			tsv_list = tsv_list[slice_obj]
			break

	# Retrieve every response ID and put it in a dictionary
	responses_dict = {}
	for row in tsv_list:
		response_id = row[0]
		name = row[1] # Name of contestant who submitted
		response = row[2] # Response submitted
		validity = row[3] # Whether or not the response follows requirements
		responses_dict[response_id] = [name, response, validity]

	# Let user input the amount of sections they want
	response_amount = len(responses_dict)
	section_amount = await integer_input(message.author, message.channel, "**How many sections should be created?** (Must be between 1 and 6)", 1, 6)
	if section_amount == None:
		await message.channel.send("Voting generation cancelled.")
		return

	section_titles = [ALPHABET[i] for i in range(section_amount)]

	# Let user decide whether they want to generate a megascreen or not
	megascreen_generation = await boolean_input(message.author, message.channel, "**Should a megascreen be generated?** (Y/N)")
	if megascreen_generation == None:
		await message.channel.send("Voting generation cancelled.")
		return

	normal_section_titles = [ALPHABET[i] for i in range(section_amount)]
	megascreen_section_title = ""

	if megascreen_generation:
		megascreen_section_title = normal_section_titles.pop(-1)

	# Ask for amount of screens
	joined_section_titles = ", ".join(normal_section_titles)
	screen_size_target = await integer_input(message.author, message.channel, f"There are **{response_amount}** responses.\nFor sections **{joined_section_titles}, what screen size are you aiming for?**", 1, response_amount)
	if screen_size_target == None:
		await message.channel.send("Voting generation cancelled.")
		return

	# Calculate amount of responses for each screen
	screen_amount = round(response_amount / screen_size_target)

	screen_division = [0] * screen_amount
	screen_increment = 0
	for i in range(response_amount):
		screen_division[screen_increment] += 1
		screen_increment += 1
		if screen_increment == screen_amount:
			screen_increment = 0

	# Generate screens
	sections_list = []
	for sec_n in range(section_amount):
		section_screen_names = copy.deepcopy(SCREEN_NAMES[sec_n])
		responses_shuffled = copy.deepcopy(list(responses_dict.keys()))
		random.shuffle(responses_shuffled)
	
		section_screen_amounts = []
		if megascreen_generation == True and sec_n + 1 == section_amount:
			section_screen_amounts.append(response_amount)
		else:
			section_screen_amounts = screen_division

		# Go through every screen
		section_dict = {}
		for screen_size in section_screen_amounts:
			# Get screen name
			screen_name_lowercase = random.choice(section_screen_names) # Randomize screen name
			section_screen_names.remove(screen_name_lowercase) # Remove screen name from list
			screen_name = screen_name_lowercase.upper()
			screen_response_dict = {}
			# Add responses to dictionary
			for letter_num in range(screen_size):
				response_letter = VOTE_CHRS[letter_num] # Get letter
				response_id = responses_shuffled[0]
				screen_response_dict[response_letter] = response_id
				responses_shuffled.pop(0)
			section_dict[screen_name] = screen_response_dict
		sections_list.append(section_dict)

	# Generate TSV files
	header = ["Response ID", "Name", "Response"]
	with open(RESPONSE_IDS_SAVE_PATH, 'w', encoding='UTF-8', newline='') as f:
		f.write('\ufeff')
		writer = csv.writer(f, delimiter = "\t")
		writer.writerow(header)
		for response_id in list(responses_dict.keys()):
			writer.writerow([response_id, responses_dict[response_id][0], responses_dict[response_id][1]])

	header = ["Response ID", "Name", "Response"]
	with open(SCREENS_SAVE_PATH, 'w', encoding='UTF-8', newline='') as f:
		f.write('\ufeff')
		writer = csv.writer(f, delimiter = "\t")
		for section in sections_list: # Go through each section
			for screen_name in list(section.keys()): # Go through each screen
				writer.writerow([screen_name]) # Write the screen name at the top 
				screen_dict = section[screen_name]
				for response_letter in list(screen_dict.keys()): # Go through each response
					response_id = screen_dict[response_letter]
					# Find the response that correlates to the response id
					response = responses_dict[response_id][1]
					writer.writerow([response_letter, response, response_id]) # Write down the response letter, the response and the response's id
				# Add a line break
				writer.writerow([])

	# Create text screens with discord formatting
	lines = []
	for section in sections_list: # Go through each section
		lines.append(f"```SECTION {list(section.keys())[0][0]}```") # Add title of section
		for screen_name in list(section.keys()): # Go through each screen
			lines.append(f"__**{screen_name}**__") # Write the screen name at the top 
			screen_dict = section[screen_name]
			for response_letter in list(screen_dict.keys()): # Go through each response
				response_id = screen_dict[response_letter]
				# Find the response that correlates to the response id
				response = responses_dict[response_id][1]
				# Find the validity of the response and the emoji correlating to it 
				if responses_dict[response_id][2].upper() == "TRUE":
					valid_emoji = VALID_RESPONSE
				elif responses_dict[response_id][2].upper() == "FALSE":
					valid_emoji = NOT_VALID_RESPONSE
				else:
					valid_emoji = ""
				lines.append(f"**`{response_letter}`**`{valid_emoji}` {response}")
			# Add a line break
			lines.append("")
	with open(TEXT_SCREEN_PATH, 'w', encoding='UTF-8', newline='') as f:
		for line in lines:
			f.write(line)
			f.write('\n')

	# Send messages with files
	file_list = [
		discord.File(RESPONSE_IDS_SAVE_PATH),
		discord.File(SCREENS_SAVE_PATH),
		discord.File(TEXT_SCREEN_PATH)
	]

	await message.channel.send(content = "**Generated voting!**", files = file_list)

	# Ask if user wants to create channels and sections
	section_amount = await boolean_input(message.author, message.channel, "**Do you wish for the bot to send the screens?** (Y/N)")
	if section_amount == None or section_amount == False:
		await message.channel.send("Voting generation is complete.")
		return
	
	# Ask which text channel category to generate them
	category_found = None
	while category_found == None:
		await message.channel.send("**What category should the categories be created in? (Provide Channel ID)**")
		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == message.author and m.channel == message.channel))
		try:
			if msg.content.lower() == "cancel":
				break

			id = int(msg.content)
			category = discord.utils.get(message.author.guild.categories, id=id)
			if category == None:
				raise ValueError
			category_found = category

		except ValueError:
			message.channel.send(f"You must provide a category channel ID!")
			
	if category_found == None:
		await message.channel.send("Voting generation cancelled.")
		return

	await message.channel.send("Creating section channels and sending voting messages...")

	# Create text channels in the category

	section_channels = []

	for section in sections_list: # Go through each section
		
		section_name = f"SECTION {list(section.keys())[0][0]}" # Title of section
		# Create channel in category

		overwrites = {
			message.guild.default_role: discord.PermissionOverwrite(read_messages=False),
			BRAIN.user: discord.PermissionOverwrite(read_messages=True,send_messages=True),
		}
		section_channel = await category_found.create_text_channel(section_name, overwrites = overwrites)
		section_channels.append(section_channel)

		screens_lines = []
		for screen_name in list(section.keys()): # Go through each screen

			screen_lines = []

			screen_lines.append(f"__**{screen_name}**__") # Write the screen name at the top 
			screen_dict = section[screen_name]

			for response_letter in list(screen_dict.keys()): # Go through each response
				response_id = screen_dict[response_letter]
				# Find the response that correlates to the response id
				response = responses_dict[response_id][1]
				# Find the validity of the response and the emoji correlating to it 
				if responses_dict[response_id][2].upper() == "TRUE":
					valid_emoji = VALID_RESPONSE
				elif responses_dict[response_id][2].upper() == "FALSE":
					valid_emoji = NOT_VALID_RESPONSE
				else:
					valid_emoji = ""
				screen_lines.append(f"**`{response_letter}`**`{valid_emoji}` {response}")
			
			screens_lines.append(screen_lines)

		# Send messages
		messages_to_send = [f"```{section_name}```"]

		screen_number = 0
		for screen_line_strings in screens_lines:

			screen_number += 1
			screen_string = "\n".join(screen_line_strings)

			# Check if the screen string is larger than 1950 characters
			if len(screen_string) > 1950:
				# Go through each line
				screen_messages = [""]
				for line in screen_line_strings:
					# Check if the current screen can fit in the next message
					if len(screen_messages[-1]) + 2 + len(line) > 1950:
						screen_messages.append("")
					else:
						screen_messages[-1] += "\n"
					screen_messages[-1] += line
				for m in screen_messages:
					messages_to_send.append(m)
			else:
				# Check if the current screen can fit in the next message
				if len(messages_to_send[-1]) + 2 + len(screen_string) > 1950:
					messages_to_send.append("")
				else:
					if screen_number == 1:
						messages_to_send[-1] += "\n"
					else:
						messages_to_send[-1] += "\n\n"
				messages_to_send[-1] += screen_string

		for message_string in messages_to_send:
			await section_channel.send(message_string)

		await message.channel.send(f"Successfully generated **{section_name}** in channel {section_channel.mention}")

	button_view = View(timeout = None)
	button_view_only_delete = View(timeout = None)

	async def delete_channels(interaction):
		if interaction.user.id != message.author.id:
			await interaction.response.defer()
			return
		# Delete the section channels
		for channel in section_channels:
			try:
				await channel.delete()
			except:
				pass
		await interaction.response.edit_message(content = f"Deleted section channels (courtesy of **{interaction.user.name}**).", view = None)

	delete_button = Button(style = discord.ButtonStyle.red, label = "Delete channels")
	delete_button.callback = delete_channels				
	button_view.add_item(delete_button)

	delete_button_only = Button(style = discord.ButtonStyle.red, label = "Delete channels")
	delete_button_only.callback = delete_channels	
	button_view_only_delete.add_item(delete_button_only)

	# Creating buttons
	async def unlock_channels_button_pressed(interaction):
		if interaction.user.id != message.author.id:
			await interaction.response.defer()
			return
		# Unlock the section channels
		for channel in section_channels:
			try:
				await channel.set_permissions(message.guild.default_role, read_messages = True, send_messages = False, add_reactions = False)
			except:
				pass
		await interaction.response.edit_message(content = f"Unlocked the section channels (courtesy of **{interaction.user.name}**).", view = button_view_only_delete)

	# Creating button objects
	unlock_button = Button(style = discord.ButtonStyle.green, label = "Unlock channels")
	unlock_button.callback = unlock_channels_button_pressed				
	button_view.add_item(unlock_button)

	await message.channel.send("**Generated voting channels!**\nUse the button below to control the channels.", view = button_view)

	

