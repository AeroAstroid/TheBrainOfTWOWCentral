# RESPONDING EVENT
# Used and can be activated when collecting responses for a speed TWOW, TWOW Roulette, etc.
###################################################################################

import time, discord, random, statistics, csv, asyncio, copy, math
from discord.ui import Button, View, Select
from Config._functions import grammar_list, word_count, formatting_fix
from Config._const import ALPHABET, BRAIN

EVENT_ANNOUNCE_CHANNEL = "staff-event-time"
EVENT_ADMIN_CHANNEL = "staff•commands"

DEFAULT_INFO = { # Define all the game information - This dictionary will be copied whenever there is a reset
	"MODIFICATION_OPEN": False, # Whether or not admins can still modify or not
	"USERS_RESPONDING": [], # The users who are able to respond
	"RESPONSES": {}, # The responses of players - key is user object, value is list of their responses
	"RESPONDING_OPEN": False, # Whether responding is open or not
	"RESPONDING_START_TIME": 0, # Timestamp of responding beginning
	"RESPONDING_END_TIME": 0 # Timestamp of responding ending
}

DEFAULT_PARAM = { # Define all the parameters necessary that could be changed
	"WORD_LIMIT": 10, # Word limit - if set to 0, there is none
	"CHARACTER_LIMIT": 0, # Character limit - if set to 0, there is none
	"TECHNICALS": [], # Functions used for technicals
	"RESPOND_LENGTH": 600, # The amount of time (seconds) contestants have to input responses
	"ROLES_IN_RESPONDING": [], # The roles that are allowed to respond to the prompt
	"USERS_IN_RESPONDING": [], # The users that are allowed to respond to the prompt that don't fall into the roles
	"DEFAULT_RESPONSE_AMOUNT": 1, # The default amount of responses everyone can send in
	"SPECIAL_RESPONSE_AMOUNT": {} # Any users who can send in a different amount of responses (key = amount of responeses, value = list of users)
}

CHARACTER_CAP = 200

######################################################
# FUNCTION FOR GETTING A POSITIVE INTEGER FROM ADMIN #

async def get_positive_integer(user, channel):
	
	admin_input = None
	while admin_input == None:

		msg = await BRAIN.wait_for('message', check=lambda m: (m.author == user and m.channel == channel))

		try:
			word_limit = int(msg.content)
			if word_limit >= 0:
				admin_input = word_limit
			else:
				await channel.send("Please send a non-negative integer!")
		except:
			if msg.content == "cancel":
				admin_input = "cancel"
			else:
				await channel.send("Please send a non-negative integer!")

	return admin_input

######################################################
### MAIN EVENT CLASS - WHERE EVERYTHING IS RUNNING ###

class EVENT:

	# Executes when loaded
	def __init__(self):

		self.RUNNING = False

		# Reset game info and parameters
		self.info = copy.deepcopy(DEFAULT_INFO)
		self.param = copy.deepcopy(DEFAULT_PARAM)
		self.default_parameters = DEFAULT_PARAM

	# Executes when deactivated
	def end(self): # Reset the parameters

		# Reset game info and parameters
		self.info = copy.deepcopy(DEFAULT_INFO)
		self.param = copy.deepcopy(DEFAULT_PARAM)

		# End the event
		self.RUNNING = False

	# Executes when activated
	def start(self, SERVER): # Set the parameters
		
		self.RUNNING = True

		self.SERVER = SERVER
		self.EVENT_ADMIN_ROLE = 959155078844010546 # Event participant role

		# Set the parameter for the event admin role
		self.param["ADMIN_ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ADMIN_ROLE)

		# Set the parameter for the event announcement channel and admin channel
		self.param["ANNOUNCE_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name="staff-event-time") # Post messages in here
		self.param["ADMIN_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name="staff•commands")

		# Add participating role
		self.param["ROLES_IN_RESPONDING"].append(discord.utils.get(SERVER["MAIN"].roles, name="Participating"))

		# Let admins modify parameters
		self.info["MODIFICATION_OPEN"] = True

	# Allow admins to modify parameters from main modification message
	# This function sends the main modification message
	async def admin_modify(self):

		# Create embed
		admin_embed = discord.Embed(title="Responding - Modify Parameters", description="Select a parameter to change in the dropdown menu, or select `Confirm` to confirm the parameters.", color=0x31d8b1)
		
		# Add fields listing the word/character limits
		limits_description = ""
		if self.param["WORD_LIMIT"] > 0:
			limits_description += "Word limit: **{}**".format(self.param["WORD_LIMIT"])
		else:
			limits_description += "No word limit"

		if self.param["CHARACTER_LIMIT"] > 0:
			limits_description += "\nCharacter limit: **{}**".format(self.param["CHARACTER_LIMIT"])
		else:
			limits_description += "\nNo character limit"
		admin_embed.add_field(name="❗ Responding limits", value=limits_description, inline=False)

		# Add fields listing the responding deadline
		if self.param["RESPOND_LENGTH"] > 3600:
			# If the responding deadline number is larger than 3600, that means the deadline is a timestamp
			admin_embed.add_field(name="⌛ Responding deadline", value="<t:{}:T>".format(self.param["RESPOND_LENGTH"]), inline=False)
		else:
			# Responding deadline is in seconds
			minutes = math.floor(self.param["RESPOND_LENGTH"] / 60)
			seconds = self.param["RESPOND_LENGTH"] % 60
			admin_embed.add_field(name="⌛ Responding deadline", value=f"{minutes} minutes, {seconds} seconds", inline=False)

		# Add fields listing the roles that can respond
		if len(self.param["ROLES_IN_RESPONDING"] + self.param["USERS_IN_RESPONDING"]) == 0:
			admin_embed.add_field(name="✏️ Roles + members that can respond", value="None", inline=False)
		else:
			roles_mention = []
			for role in self.param["ROLES_IN_RESPONDING"]:
				roles_mention.append(role.mention)
			users_mention = []
			for user in self.param["USERS_IN_RESPONDING"]:
				users_mention.append(user.mention)
			admin_embed.add_field(name="✏️ Roles + members that can respond", value="\n".join(roles_mention) + "\n" + "\n".join(users_mention), inline=False)

		# Add fields listing the default amount of responses
		admin_embed.add_field(name="🗳️ Amount of responses", value=str(self.param["DEFAULT_RESPONSE_AMOUNT"]), inline=False)

		# Add fields listing the extra amount of responses if there are any
		if len(list(self.param["SPECIAL_RESPONSE_AMOUNT"].keys())) > 0:

			value_str = ""
			for amount in list(self.param["SPECIAL_RESPONSE_AMOUNT"].keys()):
				
				value_str += f"**{amount}:** " + "".join(x.mention for x in self.param["SPECIAL_RESPONSE_AMOUNT"][amount]) + "\n"

			admin_embed.add_field(name="🗳️ Extra responses", value=value_str, inline = False)

		# Add fields listing the active technicals
		if len(self.param["TECHNICALS"]) == 0:
			admin_embed.add_field(name="⚙️ Technicals active", value="None", inline=False)
		else:
			admin_embed.add_field(name="⚙️ Technicals active", value="\n".join(self.param["TECHNICALS"]), inline=False)

		# Creating dropdown menu for admins to use
		select_view = View()

		options_list = [
			discord.SelectOption(label = "Modify word limit", value = "wordlimit", emoji = "❗"),
			discord.SelectOption(label = "Modify character limit", value = "characterlimit", emoji = "❗"),
			discord.SelectOption(label = "Modify responding deadline", value = "deadline", emoji = "⌛"),
			discord.SelectOption(label = "Modify default amount of responses", value = "responseamount", emoji = "🗳️"),
			discord.SelectOption(label = "Modify active technicals", value = "technicals", emoji = "⚙️"),
			discord.SelectOption(label = "Confirm", value = "confirm", emoji = "✅"),
		]

		modification_menu = Select(custom_id = "MOD_MENU", placeholder = "Choose an option...", options = options_list)

		##########################################################################
		#### CALLBACK FUNCTION FOR WHEN OPTION IN MODIFICATION MENU IS CHOSEN ####
		##########################################################################
		async def mod_menu_press(interaction):
			
			if interaction.user in self.param["ADMIN_ROLE"].members:

				# Check what option is selected
				try:
					option_selected = modification_menu.values[0]
				except Exception as e:
					print(e)
					await interaction.response.defer()
					return

				await interaction.response.edit_message(embed = interaction.message.embeds[0], view = None)

				# Make an action depending on the option selected
				if option_selected == "wordlimit":
					# WORD LIMIT - Get user to select word limit
					await self.param["ADMIN_CHANNEL"].send("Set a word limit by typing an integer amount of words that players are limited to or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])

					if admin_input != "cancel":		
						# Change word limit to user's input
						self.param["WORD_LIMIT"] = admin_input
						if admin_input == 0:
							await self.param["ADMIN_CHANNEL"].send("Word limit disabled!")
						else:
							await self.param["ADMIN_CHANNEL"].send(f"Word limit set to {admin_input}!")
				
					await self.admin_modify()

				elif option_selected == "characterlimit":
					# CHARACTER LIMIT - Get user to select character limit
					await self.param["ADMIN_CHANNEL"].send("Set a character limit by typing an integer amount of characters that players are limited to or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])

					if admin_input != "cancel":		
						# Change word limit to user's input
						self.param["CHARACTER_LIMIT"] = admin_input
						if admin_input == 0:
							await self.param["ADMIN_CHANNEL"].send("Character limit disabled!")
						else:
							await self.param["ADMIN_CHANNEL"].send(f"Character limit set to {admin_input}!")
				
					await self.admin_modify()

				elif option_selected == "responseamount":
					# CHARACTER LIMIT - Get user to select character limit
					await self.param["ADMIN_CHANNEL"].send("Set the default amount of responses by typing an integer amount of responses that players have by default or send `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])

					if admin_input != "cancel":		
						# Change word limit to user's input
						self.param["DEFAULT_RESPONSE_AMOUNT"] = admin_input
						await self.param["ADMIN_CHANNEL"].send(f"Default amount of responses set to {admin_input}!")
				
					await self.admin_modify()

				elif option_selected == "deadline":
					# CHARACTER LIMIT - Get user to select character limit
					await self.param["ADMIN_CHANNEL"].send("Set the length of the responding period by either putting in a UNIX timestamp or the amount of seconds the deadline will last for.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])

					if admin_input != "cancel":		
						# Change word limit to user's input
						self.param["RESPOND_LENGTH"] = admin_input
						if admin_input > 3600:
							# Responding deadline is in a UNIX stamp format
							await self.param["ADMIN_CHANNEL"].send(f"Deadline set to <t:{admin_input}:T>, or <t:{admin_input}:R>")
						else:
							# Responding deadline is in seconds
							minutes = math.floor(admin_input / 60)
							seconds = admin_input % 60
							if seconds == 0:
								await self.param["ADMIN_CHANNEL"].send(f"Responding period length set to {minutes} minutes!")
							else:
								await self.param["ADMIN_CHANNEL"].send(f"Responding period length set to {minutes} minutes and {seconds} seconds!")
				
					await self.admin_modify()

				elif option_selected == "confirm":
					# CONFIRM - Admin is confirming

					# Create start and cancel buttons
					button_view = View()

					# BUTTON FUNCTIONS - START AND CANCEL
					########################################################
					async def start_button_pressed(interaction):

						if interaction.user not in self.param["ADMIN_ROLE"].members:
							await interaction.response.defer()
							return

						# BEGIN THE RESPONDING PERIOD
						await interaction.response.edit_message(content = "**Responding has begun!**", view = None)

						# Start game
						await self.begin_responding()

					async def cancel_button_pressed(interaction):

						if interaction.user not in self.param["ADMIN_ROLE"].members:
							await interaction.response.defer()
							return

						# BEGIN THE RESPONDING PERIOD
						await interaction.response.edit_message(content = "**Responding period cancelled!** You will now return to the admin modification menu.", view = None)

						# Start game
						await self.admin_modify()
					###############################################################

					# Creating button objects
					start_button = Button(style = discord.ButtonStyle.green, label = "Start")
					start_button.callback = start_button_pressed				
					button_view.add_item(start_button)

					# Creating 
					cancel_button = Button(style = discord.ButtonStyle.red, label = "Cancel")
					cancel_button.callback = cancel_button_pressed				
					button_view.add_item(cancel_button)

					await self.param["ADMIN_CHANNEL"].send("✅ **Parameters confirmed!** Press the Start button to start the responding period. If you would like to cancel, press the Cancel button.", view = button_view)
				
			else:

				# Defer interaction
				await interaction.response.defer()

		##########################################################################
		##########################################################################

		modification_menu.callback = mod_menu_press
		select_view.add_item(modification_menu)

		await self.param["ADMIN_CHANNEL"].send(embed = admin_embed, view = select_view)

	# Begin the responding period
	async def begin_responding(self):

		# Set up all players in a role that is in ROLES_IN_RESPONDING
		for role in self.param["ROLES_IN_RESPONDING"]:
			for member in role.members:
				if not member in self.info["USERS_RESPONDING"]:
					# If user not found in user list, add them to the to the list
					self.info["USERS_RESPONDING"].append(member)

		# Set up all players in the USERS_IN_RESPONDING list
		for member in self.param["USERS_IN_RESPONDING"]:
			if not member in self.info["USERS_RESPONDING"]:
				# If user not found in user list, add them to the to the list
				self.info["USERS_RESPONDING"].append(member)

		# Set up the amount of responses that each contestant gets
		special_amount_contestants = []
		for respamount in list(self.param["SPECIAL_RESPONSE_AMOUNT"].keys()):
			contestants = self.param["SPECIAL_RESPONSE_AMOUNT"][respamount] # The contestants who get a special amount of responses
			for contestant in contestants:
				special_amount_contestants.append(contestant)
				# Set the amount of responses they get to the response amount they are assigned to
				self.info["RESPONSES"][contestant] = [None] * respamount

		# For contestants who don't get a special amount of responses, give them the default amount
		for contestant in self.info["USERS_RESPONDING"]:
			if contestant in special_amount_contestants: continue
			self.info["RESPONSES"][contestant] = [None] * self.param["DEFAULT_RESPONSE_AMOUNT"]

		# Set starting time
		self.info["RESPONDING_START_TIME"] = time.time()

		# Finding the timestamp of the deadline
		if self.param["RESPOND_LENGTH"] <= 3600:
			# Find the timestamp of the deadline by adding the RESPOND_LENGTH parameter to the start time
			self.info["RESPONDING_END_TIME"] = round(self.info["RESPONDING_START_TIME"]) + self.param["RESPOND_LENGTH"]
		else:
			# The timestamp of the deadline is the respond length set in self.param
			self.info["RESPONDING_END_TIME"] = self.param["RESPOND_LENGTH"]

		# Define the two timestamp strings that will be displayed to users
		deadline_time_string = "<t:{}:t>".format(self.info["RESPONDING_END_TIME"])
		deadline_relative_string = "<t:{}:R>".format(self.info["RESPONDING_END_TIME"])

		default_responses = self.param["DEFAULT_RESPONSE_AMOUNT"]

		# Write announcement message that responding has opened
		announcement_str = "__**Responding is open!**__\n\n"
		announcement_str += f"Send your response to {BRAIN.user.mention} using the command `tc/respond` followed by your response(s) in DMs.\n"
		# If players have more than one response by default, tell them that
		if default_responses > 1:
			announcement_str += f"Everyone gets to send in **{default_responses}** responses!\n"
		# If some players have a special amount of responses, tell them that
		if len(list(self.param["SPECIAL_RESPONSE_AMOUNT"].keys())) != 0:
			# Iterate through the amount of special responses
			for respamount in list(self.param["SPECIAL_RESPONSE_AMOUNT"].keys()):
				contestants = self.param["SPECIAL_RESPONSE_AMOUNT"][respamount]
				announcement_str += "".join(x.mention for x in contestants) + f" get to send in **{respamount}** responses!\n"

		# Add deadline to announcement string
		announcement_str += (f"\nYou have until **{deadline_time_string}** which is **{deadline_relative_string}**.")

		await self.param["ANNOUNCE_CHANNEL"].send(announcement_str)

		# Open responding and close admin modification
		self.info["MODIFICATION_OPEN"] = False
		self.info["RESPONDING_OPEN"] = True

	# Function that sorts leaderboard and writes CSV
	async def sort_leaderboard(self):

		try:

			# Creating list of all players
			player_list = list(self.info["PLAYERS"].values())

			# Function that the sorted() method uses to sort the players
			def get_player_score(player):
				return player.score

			sorted_player_list = sorted(player_list, reverse = True, key = get_player_score)

			# Write to CSV
			with open("Events/ddscores_R{}.csv".format(self.info["ROUND_NUMBER"]), 'w', encoding='UTF-8', newline='') as f:

				writer = csv.writer(f)

				# Write first row of titles
				title_row = ["Name", "UserId", "Total"]

				# Write each individual round title
				for i in range(self.info["ROUND_NUMBER"]):
					title_row.append(str(i + 1))

				writer.writerow(title_row)

				for player in sorted_player_list:

					# Get player list and write it onto csv
					writer.writerow([player.user.name, player.user.id, player.score] + player.round_scores)

			# Send leaderboard to administration channel
			await self.param["ADMIN_CHANNEL"].send(content = "**Description Detective - Leaderboard after Round {}**".format(self.info["ROUND_NUMBER"]), file = discord.File("Events/ddscores_R{}.csv".format(self.info["ROUND_NUMBER"])))
		except Exception as e:
			print(e)

	# Function that runs every two seconds
	async def on_two_second(self):

		pass

	# Function that runs on each message
	async def on_message(self, message):

		user = message.author
		channel = message.channel 

		# Responding has not started and admins are still able to modify the parameters
		if self.info["MODIFICATION_OPEN"] == True:

			# Check if the message "modify" has been sent
			if message.content.strip().lower() == "modify" and user in self.param["ADMIN_ROLE"].members and channel == self.param["ADMIN_CHANNEL"]:

				try:
					await self.admin_modify()
				except Exception as e:
					print(e)

		# Responding is open, anyone can respond
		elif self.info["RESPONDING_OPEN"] == True:

			print("TEST 1: Responding is open")

			# Check if in DMs or not
			if isinstance(channel, discord.channel.DMChannel):

				print("TEST 2: In a DM channel")
				
				# Is in DMs, split the content of the message
				message_words = message.content.split(" ")

				# Check if user is responding
				if message_words[0].lower() == "tc/respond":

					print("TEST 3: Bot detects command correctly")

					# Check if user is able to respond, and if not return and send message
					if user not in self.info["USERS_RESPONDING"]:
						await channel.send("❌ You are not allowed to use this command!")

					print("TEST 4: Bot detects user in responding")

					# Check if user has already submitted all their responses
					response_list = self.info["RESPONSES"][user]
					if not None in response_list:
						if len(response_list >= 2):
							await channel.send("❌ You've already sent your responses! If you want to edit, use `tc/edit` followed by the number of the response you want to edit, followed by your new response.")
						else:
							await channel.send("❌ You've already sent a response! If you want to edit, use `tc/edit` followed by your new response.")
						return

					print("TEST 5: User has not already sent response")

					# Check if user actually sent a response
					if len(message_words) == 1:
						await channel.send("❌ You need to send your response after the `tc/respond` command!")
						return

					print("TEST 6: Response has more than 0 words")

					# Get user's response and put it together
					try:
						
						message_words.pop(0)
						response = " ".join(message_words)

						# Do actions to response to ensure validity of it
						response = await self.response_valid(response, channel)

						if response == False: return

						# Record response by replacing the earliest NoneType inside the user's response list
						for i, responseobj in enumerate(self.info["RESPONSES"][user]):
							if responseobj == None:
								self.info["RESPONSES"][user][i] = response
								break

						# Get response information
						response_info_string = self.response_info(response)

						# Send response recorded message if the user only has one response
						if len(self.info["RESPONSES"][user]) == 1:
							await message.reply(content = f"☑️ **Response recorded!** ☑️\n\nYour response was recorded as: `{response}`\n{response_info_string}\n\nTo edit your response, use the command `tc/edit` followed by your new response.", mention_author=False)
						# Send response recorded message if the user has two or more responses
						else:
							# Add a list of the user's responses
							user_response_strings = ["**`{}:`**`{}`".format(num + 1, self.info["RESPONSES"][user][num]) for num in range(len(self.info["RESPONSES"][user])) if self.info["RESPONSES"][user][num] != None]

							# If user still has more responses to send in, tell them to do so
							# Find the amount of None's in the user's response list
							responses_to_send = self.info["RESPONSES"][user].count(None)
							if responses_to_send == 0: resp_to_send_str = "You've submitted all your responses!"
							else: resp_to_send_str = f"You have {responses_to_send} response(s) left to submit." 

							# User response string - showing the user's current responses
							user_resp_string = "\n".join(user_response_strings)

							# Send message
							await message.reply(content = f"""
								☑️ **Response recorded!** ☑️
								
								Your response was recorded as: `{response}`
								{response_info_string}
								{resp_to_send_str}

								To edit your response, use the command `tc/edit` followed by the number of the response you want to edit, followed by your new response.
								
								Your current responses are:
								{user_resp_string}
							""", mention_author=False)
						
					except Exception as e:
						print(e)
						await channel.send("❌ An error occured while trying to record your response.")

	# Function that creates information for a response recorded message
	def response_info(self, response):

		info_list = []

		# Count the amount of words and characters in the response
		word_count = word_count(response)
		character_count = len(response)

		word_limit = self.param["WORD_LIMIT"]
		character_limit = self.param["CHARACTER_LIMIT"]

		# Check if a word limit exists
		if word_limit > 0:
			# Check if response is under that word limit
			if word_limit <= word_count: 
				valid_word_count = True
				info_list.append("Your response follows the word limit!")
			else:
				valid_word_count = False
				info_list.append(f"**Your response does NOT follow the {word_limit} word limit, as your response is {word_count} words long.**")

		# Check if a character limit exists
		if character_limit > 0:
			# Check if response is under that character limit
			if character_limit <= character_count: 
				valid_chr_count = True
				info_list.append("Your response follows the character limit!")
			else:
				valid_chr_count = False
				info_list.append(f"**Your response does NOT follow the {character_limit} character limit, as your response is {character_count} characters long.**")

		return "\n".append(info_list)

	# Function that checks response's validity
	async def response_valid(self, original_response, channel):

		# Run the formatting_fix function, remove characters that might cause issues and strip unnecessary whitespace
		response = formatting_fix(response.replace("`", "").replace("\t", "").replace("\n", "")).strip()

		# Convert response to UTF-8 only characters
		response = original_response.encode('UTF-8', 'ignore').decode("UTF-8")

		# Check if user is over the character cap
		if len(response) > CHARACTER_CAP:
			
			await channel.send(f"❌ Your response has gone over the character cap of {CHARACTER_CAP}!")
			return False

		# Convert response's quotes to curly quotes
		try:
			for i in range(response.count('"') / 2 + 1):
				response = text.replace('"', '“', 1)
				response = text.replace('"', '”', 1)

		except Exception as e:
			print("\n[ERROR] Exception whilst converting response to curly quotes")
			print(e)
			print("")
		
		return response
		
	# Change a parameter of the event
	async def edit_event(self, message, new_params):
		incorrect = []
		correct = []
		for parameter in new_params.keys():
			try:
				self.param[parameter] = new_params[parameter]
				correct.append(parameter)
			except KeyError:
				incorrect.append(parameter)
		
		if len(correct) > 0:
			await message.channel.send(f"Successfully changed the parameters: {grammar_list(correct)}")
		if len(incorrect) > 0:
			await message.channel.send(f"The following parameters are invalid: {grammar_list(incorrect)}")
		
		return

