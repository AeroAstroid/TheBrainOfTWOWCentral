# RESPONDING EVENT
# Used and can be activated when collecting responses for a speed TWOW, TWOW Roulette, etc.
# Written by Neonic - ask him if you have any questions about how the code works
###################################################################################

import time, discord, random, statistics, csv, asyncio, copy, math, textwrap, traceback, os, importlib
from discord.ui import Button, View, Select
from Config._functions import grammar_list, word_count, formatting_fix
from Config._const import ALPHABET, BRAIN, ALPHANUM_UNDERSCORE

EVENT_ANNOUNCE_CHANNEL = "event-time"
TESTING_ANNOUNCE_CHANNEL = "staff-event-time"
ADMIN_CHANNEL = "staff•commands"

EVENT_PREFIX = "twow/"

DEFAULT_INFO = { # Define all the game information - This dictionary will be copied whenever there is a reset
	"MODIFICATION_OPEN": False, # Whether or not admins can still modify or not
	"USERS_RESPONDING": [], # The users who are able to respond
	"RESPONSES": {}, # The responses of players - key is user object, value is list of their responses
	"RESPONDING_OPEN": False, # Whether responding is open or not
	"RESPONDING_START_TIME": 0, # Timestamp of responding beginning
	"RESPONDING_END_TIME": 0, # Timestamp of responding ending
	"DEADLINE_PASSED": False, # Whether the deadline has passed or not
	"RESPONSES_RECEIVED": 0, # The amount of responses that have been sent by users
	"TOTAL_RESPONSES": 0, # The amount of total responses that the bot expects to get by the end of the responding period
	"TSV_TITLE_ROWS": ["ID", "Username", "Response", "Timestamp", "Relative Timestamp"] # The title rows for the information TSV file to be produced
}

DEFAULT_PARAM = { # Define all the parameters necessary that could be changed
	"TESTING": False,
	"WORD_LIMIT": 10, # Word limit - if set to 0, there is none
	"CHARACTER_LIMIT": 0, # Character limit - if set to 0, there is none
	"TECHNICALS": [], # Functions used for technicals
	"RESPOND_LENGTH": 600, # The amount of time (seconds) contestants have to input responses
	"ROLES_IN_RESPONDING": [], # The roles that are allowed to respond to the prompt
	"USERS_IN_RESPONDING": [], # The users that are allowed to respond to the prompt that don't fall into the roles
	"DEFAULT_RESPONSE_AMOUNT": 1, # The default amount of responses everyone can send in
	"SPECIAL_RESPONSE_AMOUNT": {} # Any users who can send in a different amount of responses (key = amount of responeses, value = list of users)
}

IMPORTED_TECHNICALS = {}

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
		self.param["ANNOUNCE_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name=EVENT_ANNOUNCE_CHANNEL) # Post messages in here
		self.param["ADMIN_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name="staff•commands")

		# Add participating role
		self.param["ROLES_IN_RESPONDING"].append(discord.utils.get(SERVER["MAIN"].roles, name="Participating"))

		# Let admins modify parameters
		self.info["MODIFICATION_OPEN"] = True

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
				self.info["TOTAL_RESPONSES"] += respamount
				self.info["RESPONSES"][contestant] = [None] * respamount

		# For contestants who don't get a special amount of responses, give them the default amount
		for contestant in self.info["USERS_RESPONDING"]:
			if contestant in special_amount_contestants: continue
			self.info["TOTAL_RESPONSES"] += self.param["DEFAULT_RESPONSE_AMOUNT"]
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

		# Setup technicals
		self.info["TECHNICALS"] = []
		for technical in self.param["TECHNICALS"]:
			try:
				technical_object = IMPORTED_TECHNICALS[technical](self)
				self.info["TECHNICALS"].append(technical_object)
				self.info["TSV_TITLE_ROWS"] += technical_object.extra_tsv_title_rows
				if hasattr(technical_object, "responding_start"):
					technical_object.responding_start()
				
			except Exception:
				try:
					traceback.print_exc()
					await self.param["ADMIN_CHANNEL"].send(f"Failed to start technical `**{technical}**`:\n```python\n{traceback.format_exc()}```")
				except: 
					pass

		# Write announcement message that responding has opened
		announcement_str = "__**Responding is open!**__\n\n"
		announcement_str += f"Send your response to {BRAIN.user.mention} using the command `{EVENT_PREFIX}respond` followed by your response(s) in DMs.\n"
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

	# Function that ends responding
	async def end_responding(self):

		# Set responding open to off
		self.info["RESPONDING_OPEN"] = False

		# Send announcement that responding has ended
		# Find the people who DNPed
		dnped_list = []
		for user in list(self.info["RESPONSES"].keys()):
			response_list = self.info["RESPONSES"][user]
			# If the entire response list is full of "None", that means they did not send in any responses
			if response_list.count(None) == len(response_list):
				dnped_list.append(user)

		# Mention people in the DNP list
		dnp_list_mention_str = "".join([user.mention for user in dnped_list])

		# Get statistics for responding
		total_responses = self.info["TOTAL_RESPONSES"]
		responses_recorded = self.info["RESPONSES_RECEIVED"]

		# Send message
		#await self.param["ANNOUNCE_CHANNEL"].send("__**Responding has closed!**__\nWe received **{}/{}** responses.\nThe DNPers were (sent in no responses): {}".format(responses_recorded, total_responses, dnp_list_mention_str))
		await self.param["ANNOUNCE_CHANNEL"].send("__**Responding has closed!**__")

		# CREATING TSV FILES
		################################################
		# Ask user for file names for TSV file
		await self.param["ADMIN_CHANNEL"].send("Set the file name of the TSV files by typing in the chat. It must be only letters, numbers or an underscore. (Don't include the filetype)")
		file_name = None
		while True:

			msg = await BRAIN.wait_for('message', check=lambda m: (m.author in self.param["ADMIN_ROLE"].members and m.channel == self.param["ADMIN_CHANNEL"]))
			# Check if alphanumeric or underscore
			if all([character in list(ALPHANUM_UNDERSCORE) for character in msg.content]):
				# Break out of loop
				file_name = msg.content
				break
			else:
				# Tell admin that there is invalid input
				await self.param["ADMIN_CHANNEL"].send("Invalid input. Please try again.")

		# Creating the Response Information TSV file
		resp_info_file_name = "Events/" + file_name + "_INFO.tsv"
		# Write to TSV
		with open(resp_info_file_name, 'w', encoding="UTF-8", newline='') as f:

			f.write('\ufeff')

			writer = csv.writer(f, delimiter = "\t")

			# Write first row of titles
			title_row = self.info["TSV_TITLE_ROWS"]

			writer.writerow(title_row)

			# Go through each user and go through each of their responses
			for user in list(self.info["RESPONSES"].keys()):

				response_list = self.info["RESPONSES"][user]
				for response in response_list:

					if response == None: continue

					# Add each response to the TSV
					resp_tsv_list = []
					resp_tsv_list.append(str(user.id)) # User's ID
					resp_tsv_list.append(user.name.encode('UTF-8', 'ignore').decode("UTF-8")) # User's username, which has all non UTF-8 characters filtered out
					resp_tsv_list.append(response[0]) # The user's actual response
					resp_tsv_list.append(str(round(response[2], 2))) # The timestamp of the user's response - when it was sent
					resp_tsv_list.append(str(round(response[2] - self.info["RESPONDING_START_TIME"], 2))) # The relative timestamp of the user's response - how long ago they sent a response
					# If any special information was passed onto the response
					if len(response) > 3:
						resp_tsv_list += response[3:] # Add any special information and write it in the TSV

					# Write to TSV
					writer.writerow(resp_tsv_list)

		# Creating the Voting Generation TSV file
		voting_gen_file_name = "Events/" + file_name + "_VOTING.tsv"
		# Write to TSV
		with open(voting_gen_file_name, 'w', encoding="UTF-8", newline='') as f: 

			f.write('\ufeff')

			writer = csv.writer(f, delimiter = "\t")

			# Write first row of titles
			writer.writerow(["RESPONSE ID", "NAME", "RESPONSE", "VALIDITY"])

			response_id = 0

			# Go through each user and go through each of their responses
			for user in list(self.info["RESPONSES"].keys()):

				response_list = self.info["RESPONSES"][user]
				for response in response_list:

					if response == None: continue

					response_id += 1

					# Add each response to the TSV
					resp_tsv_list = []
					resp_tsv_list.append(str(response_id)) # The number of the response
					resp_tsv_list.append(user.name.encode('UTF-8', 'ignore').decode("UTF-8")) # User's username, which has all non UTF-8 characters filtered out
					resp_tsv_list.append(response[0]) # The user's actual response
					resp_tsv_list.append(str(response[1])) # Whether or not the user's response was valid or not (in limits), either True or False
					# Write to TSV
					writer.writerow(resp_tsv_list)

		# Send TSV's to user and end event
		resp_info_file = discord.File(resp_info_file_name)
		voting_gen_file = discord.File(voting_gen_file_name)
		await self.param["ADMIN_CHANNEL"].send(content = "Here are the TSV files from this Responding event.", files = [resp_info_file, voting_gen_file])

	# Function that runs every two seconds
	async def on_two_second(self):

		# Check if responding is open
		if self.info["RESPONDING_OPEN"] == True:

			# Get current time
			current_timestamp = time.time()

			# Check if the deadline has passed - only run this once
			if current_timestamp > self.info["RESPONDING_END_TIME"] and self.info["DEADLINE_PASSED"] == False:

				# Make sure this only runs once
				self.info["DEADLINE_PASSED"] = True

				# Check which people have not sent responses yet - check how many None's are in a player's list
				# Dictionary: key is the amount of responses they have to send, value is a list of players who need to send that amount of responses
				players_to_respond = {}
				players_to_respond_list = []

				for user in list(self.info["RESPONSES"].keys()):
					response_list = self.info["RESPONSES"][user]
					if None in response_list:
						# Record how many responses the player has not sent
						responses_left = response_list.count(None)
						# If the amount of responses left already exists as a key in the players to respond dict, add the player to the list
						if responses_left in list(players_to_respond.keys()):
							players_to_respond[responses_left].append(user)
						# If the amount of responses left does not exist as a key in the players to respond dict, make it a key 
						else:
							players_to_respond[responses_left] = [user]
						# Append them to the players_to_respond_list (to be used later when sending a message in the admin channel)
						players_to_respond_list.append(user)

				# Turn the players to respond dict into a string that can be sent with the deadline message
				"""still_to_respond_strings = []
				for responses_left in list(players_to_respond.keys()):

					players_with_amount = players_to_respond[responses_left]
					player_mentions_str = "".join([user.mention for user in players_with_amount])
					if len(players_with_amount) == 1:
						if responses_left == 1: 
							still_to_respond_strings.append(f"{player_mentions_str} has 1 response left to submit.")
						else:
							still_to_respond_strings.append(f"{player_mentions_str} has {responses_left} responses left to submit.")
					else:
						if responses_left == 1: 
							still_to_respond_strings.append(f"{player_mentions_str} have 1 response left to submit.")
						else:
							still_to_respond_strings.append(f"{player_mentions_str} have {responses_left} responses left to submit.")

				# Put together all the strings in the still_to_respond_strings list
				still_to_respond_str = "\n".join(still_to_respond_strings)"""
				
				# Send a message saying deadline passed
				#if len(still_to_respond_strings) > 0:
					#deadline_passed_str = f"__**The deadline has passed!**__\n\n{still_to_respond_str}\n\nYou are still able to respond and edit responses. If you are still responding, please let anyone running the event know. The grace period will close soon."
				#else:
					#deadline_passed_str = f"__**The deadline has passed!**__\n\nYou are still able to respond and edit responses. If you are still responding, please let anyone running the event know. The grace period will close soon."

				deadline_passed_str = f"__**The deadline has passed!**__\n\nYou are still able to respond and edit responses. If you are still responding, please let anyone running the event know. The grace period will close soon."

				# Send a message in the admin channel about the responding period after the deadline
				# Check what users have not sent responses yet
				players_left_to_respond_strings = ["**The deadline has passed!**\n\nResponses received before the deadline: **{}/{}**\n__Users left to respond:__]".format(self.info["RESPONSES_RECEIVED"], self.info["TOTAL_RESPONSES"])]
				for user in players_to_respond_list:
					# Check how many responses they have submitted and how many they have in total
					user_total_responses = len(self.info["RESPONSES"][user])
					user_responses_submitted = user_total_responses - self.info["RESPONSES"][user].count(None)

					player_string = f"{user.mention} ({user_responses_submitted}/{user_total_responses})\n"	

					if len(players_left_to_respond_strings[-1]) + len(player_string) > 2000:
						players_left_to_respond_strings.append("")

					players_left_to_respond_strings[-1] += player_string		

				await self.param["ANNOUNCE_CHANNEL"].send(deadline_passed_str)

				# Create button for closing responding
				button_view = View(timeout = None)
				########################################################
				async def responding_end_pressed(interaction):

					if interaction.user not in self.param["ADMIN_ROLE"].members:
						await interaction.response.defer()
						return

					# END RESPONDING PERIOD
					await interaction.response.edit_message(content = "**Responding has been ended!**", view = None)

					# Start game
					await self.end_responding()

				# Creating button objects
				end_responding_button = Button(style = discord.ButtonStyle.blurple, label = "End responding")
				end_responding_button.callback = responding_end_pressed				
				button_view.add_item(end_responding_button)

				# Message has been split into chunks
				for string in players_left_to_respond_strings:
					await self.param["ADMIN_CHANNEL"].send(string)

				# Sending message
				await self.param["ADMIN_CHANNEL"].send(content = "Any further responses sent after the deadline will be sent here. Press the button to end responding.", view = button_view)

	# Function that runs on each message
	async def on_message(self, message):

		user = message.author
		channel = message.channel 

		###############################################################################
		# Responding has not started and admins are still able to modify the parameters
		if self.info["MODIFICATION_OPEN"] == True:

			# Check if the message "modify" has been sent
			if message.content.strip().lower() == "modify" and user in self.param["ADMIN_ROLE"].members and channel == self.param["ADMIN_CHANNEL"]:

				try:
					await self.admin_modify()
				except Exception as e:
					print(e)

		###############################################################################
		# Responding is open, anyone can respond or edit as long as they are allowed to
		elif self.info["RESPONDING_OPEN"] == True:

			# Check if in DMs or not
			if isinstance(channel, discord.channel.DMChannel):

				# Run technical on_message function
				for technical in self.info["TECHNICALS"]:
					if hasattr(technical, "on_player_message"):
						try:
							await technical.on_player_message(message, user)
						except Exception as e:
							print(f"[ERROR - RESPONDING] Exception in on_message portion of technical {technical.name}: {e}")
							pass
				
				# Is in DMs, split the content of the message
				message_words = message.content.split(" ")

				###############################################################################
				# RESPONDING COMMAND
				if message_words[0].lower() == f"{EVENT_PREFIX}respond":

					# Check if user is able to respond, and if not return and send message
					if user not in self.info["USERS_RESPONDING"]:
						await channel.send("❌ You are not allowed to use this command!")
						return

					# Check if user has already submitted all their responses
					response_list = self.info["RESPONSES"][user]
					if not None in response_list:
						if len(response_list) >= 2:
							await channel.send(f"❌ You've already sent your responses! If you want to edit, use `{EVENT_PREFIX}edit` followed by the number of the response you want to edit, followed by your new response.")
						else:
							await channel.send(f"❌ You've already sent a response! If you want to edit, use `{EVENT_PREFIX}edit` followed by your new response.")
						return

					# Check if user actually sent a response
					if len(message_words) == 1:
						await channel.send(f"❌ You need to send your response after the `{EVENT_PREFIX}respond` command!")
						return

					# Get user's response and put it together
					try:
						
						message_words.pop(0)
						response = " ".join(message_words)

						# Do actions to response to ensure validity of it
						response = await self.response_valid(response, channel)

						if response == False: return

						# Get response information
						response_is_valid, misc_response_info, response_info_string = self.response_info(response, user)

						# Record response by replacing the earliest NoneType inside the user's response list
						for i, responseobj in enumerate(self.info["RESPONSES"][user]):
							if responseobj == None:
								# Recording response information - response, whether or not it is valid, or the timestamp of the message and some other response info if given
								self.info["RESPONSES"][user][i] = [response, response_is_valid, message.created_at.timestamp()] + misc_response_info
								break

						# Add 1 to the recorded response amount
						self.info["RESPONSES_RECEIVED"] += 1

						# Send response recorded message if the user only has one response
						if len(self.info["RESPONSES"][user]) == 1:
							await message.reply(content = f"☑️ **Response recorded!** ☑️\n\nYour response was recorded as: `{response}`\n{response_info_string}\n\nTo edit your response, use the command `{EVENT_PREFIX}edit` followed by your new response.", mention_author=False)
						# Send response recorded message if the user has two or more responses
						else:
							# Add a list of the user's responses
							user_response_strings = ["**`{}:`**`{}`".format(num + 1, self.info["RESPONSES"][user][num][0]) for num in range(len(self.info["RESPONSES"][user])) if self.info["RESPONSES"][user][num] != None]

							# If user still has more responses to send in, tell them to do so
							# Find the amount of None's in the user's response list
							responses_to_send = self.info["RESPONSES"][user].count(None)
							if responses_to_send == 0: resp_to_send_str = "You've submitted all your responses!"
							else: resp_to_send_str = f"You have {responses_to_send} response(s) left to submit." 

							# User response string - showing the user's current responses
							user_resp_string = "\n".join(user_response_strings)

							# Send message
							await message.reply(content = textwrap.dedent(f"""
								☑️ **Response recorded!** ☑️
								
								Your response was recorded as: `{response}`
								{response_info_string}
								{resp_to_send_str}

								To edit your response, use the command `{EVENT_PREFIX}edit` followed by the number of the response you want to edit, followed by your new response.
								
								Your current responses are:
								""") + user_resp_string, mention_author=False)

						# Send message in admin channel that they submitted a response if it is after the deadline
						if self.info["DEADLINE_PASSED"] == True:

							user_total_responses = len(self.info["RESPONSES"][user])
							user_responses_submitted = user_total_responses - self.info["RESPONSES"][user].count(None)

							await self.param["ADMIN_CHANNEL"].send(textwrap.dedent("""
								{} **({}/{})** sent in a response after the deadline: `{}`
								The total response count is now **{}/{}**.""".format(user.mention, user_responses_submitted, user_total_responses, response, self.info["RESPONSES_RECEIVED"], self.info["TOTAL_RESPONSES"])))
						
					except Exception as e:
						print(e)
						await channel.send("❌ An error occured while trying to record your response.")

				###############################################################################
				# EDITING RESPONSE COMMAND
				if message_words[0].lower() == f"{EVENT_PREFIX}edit":

					message_words.pop(0)

					# Check if user is able to respond, and if not return and send message
					if user not in self.info["USERS_RESPONDING"]:
						await channel.send("❌ You are not allowed to use this command!")
						return

					# Check if user only has one response
					if len(self.info["RESPONSES"][user]) == 1:

						# Check if user has a response in this slot
						if self.info["RESPONSES"][user][0] == None:
							await channel.send(f"❌ You haven't submitted a response yet! To submit your response, use `{EVENT_PREFIX}respond` followed by your response.")
							return

						response_to_edit = 1

					# User has more than one response, therefore their second word in their command will be an integer
					else:

						# Check if user sent the number of the response they want to edit
						if len(message_words) == 0:
							await channel.send(f"❌ You need to specify which response you want to edit by using `{EVENT_PREFIX}edit [response number]`!")
							return

						try:
							response_to_edit = int(message_words[0])
							message_words.pop(0)
							# Check if the number is not within range
							if response_to_edit <= 0 or response_to_edit > len(self.info["RESPONSES"][user]):
								await channel.send("❌ No response of yours matches with this number. To look at which number represents which of your responses, look at your last response recorded message.")
								return

							# Check if user has a response in this slot
							if self.info["RESPONSES"][user][response_to_edit - 1] == None:
								await channel.send("❌ No response currently in this number slot!")
								return

						except ValueError:
							await channel.send("❌ You need to specify what response you want to edit using a number. To look at which number represents which of your responses, look at your last response recorded message.")
							return

					# Check if user actually sent their response
					if len(message_words) == 0:
						await channel.send(f"❌ You need to send your response after the `{EVENT_PREFIX}edit [response number]` command!")
						return
						
					# Check response for validity and send response
					try:
				
						response = " ".join(message_words)

						# Do actions to response to ensure validity of it
						response = await self.response_valid(response, channel)

						if response == False: return

						# Get response information
						response_is_valid, misc_response_info, response_info_string = self.response_info(response, user)

						# Record edited response
						# Recording response information - response and the timestamp of the message
						self.info["RESPONSES"][user][response_to_edit - 1] = [response, response_is_valid, message.created_at.timestamp()] + misc_response_info

						# Send response recorded message if the user only has one response
						if len(self.info["RESPONSES"][user]) == 1:
							await message.reply(content = f"☑️ **Response edited!** ☑️\n\nYour new response is recorded as: `{response}`\n{response_info_string}\n\nTo edit your response again, use the command `{EVENT_PREFIX}edit` followed by your new response.", mention_author=False)
						# Send response recorded message if the user has two or more responses
						else:
							# Add a list of the user's responses
							user_response_strings = ["**`{}:`**`{}`".format(num + 1, self.info["RESPONSES"][user][num][0]) for num in range(len(self.info["RESPONSES"][user])) if self.info["RESPONSES"][user][num] != None]

							# If user still has more responses to send in, tell them to do so
							# Find the amount of None's in the user's response list
							responses_to_send = self.info["RESPONSES"][user].count(None)
							if responses_to_send == 0: resp_to_send_str = "You've submitted all your responses!"
							else: resp_to_send_str = f"You have {responses_to_send} response(s) left to submit." 

							# User response string - showing the user's current responses
							user_resp_string = "\n".join(user_response_strings)

							# Send message
							await message.reply(content = textwrap.dedent(f"""
								☑️ **Response edited!** ☑️
								
								Your new response is recorded as: `{response}`
								{response_info_string}
								{resp_to_send_str}

								To edit your response again, use the command `{EVENT_PREFIX}/edit` followed by the number of the response you want to edit, followed by your new response.
								
								Your current responses are:
								""") + user_resp_string, mention_author=False)
						
					except Exception as e:
						print(e)
						await channel.send("❌ An error occured while trying to record your edit.")



	# Function that creates information for a response recorded message
	def response_info(self, response, user):

		info_list = []

		# Count the amount of words and characters in the response
		wc = word_count(response)
		character_count = len(response)

		word_limit = self.param["WORD_LIMIT"]
		character_limit = self.param["CHARACTER_LIMIT"]

		# This response info function also checks whether or not their response is within limits or not
		# This variable is set to True but will be set to false if it does not follow a limit
		response_is_valid = True

		# This response gets miscellaneous response info that is added depending on the technical
		misc_response_info = []

		# Check if a word limit exists
		if word_limit > 0:
			# Check if response is under that word limit
			if word_limit >= wc: 
				info_list.append("Your response follows the word limit!")
			else:
				info_list.append(f"**Your response does NOT follow the {word_limit} word limit, as your response is {wc} words long.**")
				response_is_valid = False

		# Check if a character limit exists
		if character_limit > 0:
			# Check if response is under that character limit
			if character_limit >= character_count: 
				info_list.append("Your response follows the character limit!")
			else:
				info_list.append(f"**Your response does NOT follow the {character_limit} character limit, as your response is {character_count} characters long.**")
				response_is_valid = False

		# Run technical on_response_submission function to add extra data and check if response is valid
		for technical in self.info["TECHNICALS"]:
			if hasattr(technical, "on_response_submission"):
				try:
					response, response_is_valid, misc_response_info, info_list = technical.on_response_submission(user, response, response_is_valid, misc_response_info, info_list) 
				except Exception as e:
					print(f"[ERROR - RESPONDING] Exception in response_info portion of technical {technical.name}: {e}")
					pass

		return response_is_valid, misc_response_info, "\n".join(info_list)

	# Function that checks response's validity
	async def response_valid(self, original_response, channel):

		# Run the formatting_fix function, remove characters that might cause issues and strip unnecessary whitespace
		response = formatting_fix(original_response.replace("`", "").replace("\t", "").replace("\n", "").replace("\u200b", "")).strip()

		# Convert response to UTF-8 only characters
		response = response.encode('UTF-8', 'ignore').decode("UTF-8")

		# Check if user is over the character cap
		if len(response) > CHARACTER_CAP:
			
			await channel.send(f"❌ Your response has gone over the character cap of {CHARACTER_CAP}!")
			return False

		# Convert response's quotes to curly quotes
		try:
			for i in range(math.floor(response.count('"') / 2)):
				response = response.replace('"', '“', 1)
				response = response.replace('"', '”', 1)

		except Exception as e:
			print("\n[ERROR] Exception whilst converting response to curly quotes")
			print(e)
			print("")
		
		return response

		# Allow admins to modify parameters from main modification message
	# This function sends the main modification message
	async def admin_modify(self):

		# Create embed
		admin_embed = discord.Embed(title="Responding - Modify Parameters", description="Select a parameter to change in the dropdown menu, or select `Confirm` to confirm the parameters.", color=0x31d8b1)
		
		# Add fields listing the word/character limits
		admin_embed.add_field(name="🧪 Testing event", value=str(self.param["TESTING"]), inline=False)

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
		select_view = View(timeout = None)

		options_list = [
			discord.SelectOption(label = "Toggle testing", value = "toggletesting", emoji = "🧪"),
			discord.SelectOption(label = "Modify word limit", value = "wordlimit", emoji = "❗"),
			discord.SelectOption(label = "Modify character limit", value = "characterlimit", emoji = "❗"),
			discord.SelectOption(label = "Modify responding deadline", value = "deadline", emoji = "⌛"),
			discord.SelectOption(label = "Modify default amount of responses", value = "responseamount", emoji = "🗳️"),
			discord.SelectOption(label = "Modify technicals", value = "technicals", emoji = "⚙️"),
			discord.SelectOption(label = "Modify active technicals parameters", value = "technicalsparameters", emoji = "⚙️"),
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
				if option_selected == "toggletesting":
					# TOGGLE TESTING
					if self.param["TESTING"] == True:
						self.param["TESTING"] = False
						self.param["ANNOUNCE_CHANNEL"] = discord.utils.get(self.SERVER["MAIN"].channels, name=EVENT_ANNOUNCE_CHANNEL)
						await self.param["ADMIN_CHANNEL"].send("Testing has been set to **False**")
					else:
						self.param["TESTING"] = True
						self.param["ANNOUNCE_CHANNEL"] = discord.utils.get(self.SERVER["MAIN"].channels, name=TESTING_ANNOUNCE_CHANNEL)
						await self.param["ADMIN_CHANNEL"].send("Testing has been set to **True**")
					await self.admin_modify()

				elif option_selected == "wordlimit":
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

				elif option_selected == "technicals":
					# TECHNICALS - User can add and toggle active technicals
					global IMPORTED_TECHNICALS

					while True:

						active_technicals = self.param["TECHNICALS"]
						non_active_technicals = [tech for tech in list(IMPORTED_TECHNICALS.keys()) if not tech in active_technicals]

						await self.param["ADMIN_CHANNEL"].send(textwrap.dedent(f"""
							:white_check_mark: **Active technicals:** {", ".join(active_technicals)}
							:x:**Technicals not active:** {", ".join(non_active_technicals)}

							Send `toggle [TECHNICAL]` to either activate or deactivate a technical.
							Send `new_technical` along with a .py file as an attachment to add technicals.
							Send `cancel` to go back to the modification menu.""")
						)

						# Wait for admin input
						admin_input = None
						input_message = None
						while True:
							msg = await BRAIN.wait_for('message', check=lambda m: (m.author == interaction.user and m.channel == self.param["ADMIN_CHANNEL"]))
							input_message = msg
							if msg.content.lower().startswith("toggle"):
								admin_input = "toggle"
								break
							elif msg.content.lower() == "new_technical":
								admin_input = "new"
								break
							elif msg.content.lower() == "cancel":
								admin_input = "cancel"
								break

						if admin_input == "cancel":
							# Cancelling technical modification
							break

						elif admin_input == "toggle":
							# Toggling a certain technical
							message_words = input_message.content.split()
							if len(message_words) == 1:
								await self.param["ADMIN_CHANNEL"].send(f"You must provide a technical to toggle!")
							else:
								technical = message_words[1].upper()
								
								if technical in IMPORTED_TECHNICALS:

									if technical in active_technicals:
										# Remove the technical from the technicals list
										self.param["TECHNICALS"].remove(technical)
										await self.param["ADMIN_CHANNEL"].send(f"Removed **{technical}** technical from the active technicals list!")

									elif technical in non_active_technicals:
										# Remove the technical from the technicals list
										self.param["TECHNICALS"].append(technical)
										await self.param["ADMIN_CHANNEL"].send(f"Added **{technical}** technical to the active technicals list!")
								
								else:
									await self.param["ADMIN_CHANNEL"].send("This technical is not in the technicals list!")

						elif admin_input == "new":

							if len(input_message.attachments) == 0:
								await input_message.channel.send(
								f"**You must send a file containing the technicals!**")

							else:

								try:
									await input_message.attachments[0].save(f"{input_message.id}_RESPONDING_TECHS.py")

									TEMP_TECHS = importlib.import_module(f"{input_message.id}_RESPONDING_TECHS")

									tech_objects = [attr for attr in dir(TEMP_TECHS) if attr.startswith("TECHNICAL_")]

									TECHS = [getattr(TEMP_TECHS, techobj) for techobj in tech_objects]
									TECHNICAL_NAMES = [techobj[10:].upper() for techobj in tech_objects]

									os.remove(f"{input_message.id}_RESPONDING_TECHS.py")

									for i, tech_name in enumerate(TECHNICAL_NAMES):
										IMPORTED_TECHNICALS[tech_name] = TECHS[i]

									string_technical_list = ", ".join(TECHNICAL_NAMES)
									await input_message.channel.send(f"✅ **Successfully imported these {len(TECHS)} technicals:** {string_technical_list}")

								except Exception as err:
									await input_message.channel.send(
									"**An error occurred while importing the technicals file!**")

									print(err)

									try: os.remove(f"{input_message.id}_RESPONDING_TECHS.py")
									except Exception: pass
				
					await self.admin_modify()

				elif option_selected == "confirm":
					# CONFIRM - Admin is confirming

					# Create start and cancel buttons
					button_view = View(timeout = None)

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

