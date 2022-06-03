# RESPONDING EVENT
# Used and can be activated when collecting responses for a speed TWOW, TWOW Roulette, etc.
###################################################################################

import time, discord, random, statistics, csv, asyncio, copy, math
from discord.ui import Button, View, Select
from Config._functions import grammar_list, word_count, elim_prize
from Config._const import ALPHABET, BRAIN

EVENT_ANNOUNCE_CHANNEL = "staff-event-time"
EVENT_ADMIN_CHANNEL = "staff•commands"

DEFAULT_INFO = { # Define all the game information - This dictionary will be copied whenever there is a reset
	"MODIFICATION_OPEN": False, # Whether or not admins can still modify or not
	"USER_IDS": [], # The user ids of players who are able to respond
	"RESPONSES": {}, # The responses of players - key is user's id, 
	"RESPONDING_OPEN": False, # Whether responding is open or not
	"RESPONDING_START_TIME": 0, # Timestamp of responding beginning
	"RESPONDING_END_TIME": 0 # Timestamp of responding ending
}

DEFAULT_PARAM = { # Define all the parameters necessary that could be changed
	"WORD_LIMIT": 10, # Word limit - if set to 0, there is none
	"CHARACTER_LIMIT": 0, # Character limit - if set to 0, there is none
	"TECHNICALS": [], # Functions used for technicals
	"RESPOND_LENGTH": 600, # The amount of time (seconds) contestants have to input responses
	"ROLES_IN_RESPONDING": [],
	"USERS_IN_RESPONDING": [],
}

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
			limits_description += "Character limit: **{}**".format(self.param["CHARACTER_LIMIT"])
		else:
			limits_description += "No character limit"
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
			admin_embed.add_field(name="✏️ Roles + members that can respond", value="\n".join(self.param["ROLES_IN_RESPONDING"]) + "\n" + "\n".join(self.param["USERS_IN_RESPONDING"]), inline=False)

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
			discord.SelectOption(label = "Modify active technicals", value = "technicals", emoji = "⚙️"),
			discord.SelectOption(label = "Confirm", value = "technicals", emoji = "✅"),
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
				except:
					await interaction.response.defer()
					return

				await interaction.response.edit_message(embed = interaction.message.embeds[0], view = None)

				# Make an action depending on the option selected
				if option_selected == "wordlimit":
					# WORD LIMIT - Get user to select word limit
					await self.param["ADMIN_CHANNEL"].send("Set a character limit by typing an integer amount of words that players are limited to or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])

					if admin_input != "cancel":		
						# Change word limit to user's input
						self.param["WORD_LIMIT"] = admin_input
						if admin_input == 0:
							await self.param["ADMIN_CHANNEL"].send("Word limit disabled!")
						else:
							await self.param["ADMIN_CHANNEL"].send(f"Word limit set to {admin_input}!")
				
					await self.admin_modify()

				if option_selected == "wordlimit":
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
					await self.param["ADMIN_CHANNEL"].send("✅ **Parameters confirmed!** Press the Start button to start. If you would like to cancel, press the Cancel button.")
				
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
				if not member.id in self.info["USER_IDS"]:
					# If user not found in user ids list, add their id to the to the list
					self.info["USER_IDS"].append(member.id)

		# Set up all players in the USERS_IN_RESPONDING list
		for member in self.param["USERS_IN_RESPONDING"]:
			if not member.id in self.info["USER_IDS"]:
				# If user not found in user ids list, add their id to the to the list
				self.info["USER_IDS"].append(member.id)

		# Set starting time
		self.info["RESPONDING_START_TIME"] = time.time()

		# Find the timestamp of the deadline by adding the RESPOND_LENGTH parameter to the start time
		self.info["RESPONDING_END_TIME"] = round(self.info["RESPONDING_START_TIME"]) + self.param["RESPOND_LENGTH"]

		# Define the two timestamp strings that will be displayed to users
		deadline_time_string = "<t:{}:t>".format(self.info["RESPONDING_END_TIME"])
		deadline_relative_string = "<t:{}:R>".format(self.info["RESPONDING_END_TIME"])

		# Send announcement message that responding has opened
		await self.param["ANNOUNCE_CHANNEL"].send(f"""**Responding is open!**
Send your response to <@638028859274559510>'s direct messages using the command `tc/respond` followed by your response! 
You have until **{deadline_time_string}** which is **{deadline_relative_string}**.""")

		# Open responding
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

		print("hello1")

		# Responding has not started and admins are still able to modify the parameters
		if self.info["MODIFICATION_OPEN"] == True:

			print("hello2")
			
			# Check if the message "modify" has been sent
			if message.content == "modify" and message.user in self.param["ADMIN_ROLE"].members and message.channel == self.param["ADMIN_CHANNEL"]:
				await self.admin_modify()

		# Responding is open, anyone can respond
		elif self.info["RESPONDING_OPEN"] == True:

			pass
		
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

