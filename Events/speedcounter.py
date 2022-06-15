# SPEED COUNTER
# Used for hosting the Speed Counter event, a game where you count emojis as fast as possible
# Written by Neonic - ask him if you have any questions about how the code works
###################################################################################

# Importing modules
import time, discord, random, csv, asyncio, copy, traceback, math, textwrap
from discord.ui import Select, Button, View

# Importing from other scripts within the repo
from Config._const import ALPHABET, BRAIN

# The announcement channel (where the game is hosted) and the admin channel (where the game is customisable)
EVENT_ANNOUNCE_CHANNEL = "staff-event-time"
EVENT_ADMIN_CHANNEL = "staff•commands"

# Default information that will be set to at the start of the game
DEFAULT_INFO = { # Define all the game information - This dictionary will be copied whenever there is a reset

	"CONTESTANTS": {}, # Key is user object, value is SC_Contestant object
	"DEAD_CONTESTANTS": {}, # Key is user object, value is SC_Contestant object
	"ROUND_INFO": {}, # Round information
	"SET_INFO": { # Information of the set

		"START_TIME": None,
		"END_TIME": None,
		"CORRECT_ANSWER": None,

	},
	"ROUND_NUMBER": 0, # Number of round
	"ROUND_IN_PROGRESS": False, # Whether a round is in progress or not
	"GUESSING_OPEN": False, # Whether or not guessing is currently open or not

}

# Default parameters that can be customised by admins
DEFAULT_PARAM = {

	"EMOJI_SETS": [
		["😎", "🤩", "😀", "😡", "🥶", "🤢", "😈", "💩", "😷"],
		["❤️", "⚠️", "🎶", "🟢", "🔊", "🟧", "🔕", "♀️", "⚧"],
		["⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱", "🏓"],
		["🌧️", "🌍", "🌈", "🌕", "🌺", "🦜", "🐬", "⛸️", "🔥"],
	], # Sets of emojis that will be used
	"GUESS_AMOUNT": 3, # The amount of guesses per set
	"SETS_PER_ROUND": 5, # The amount of sets per round
	"EMOJI_COUNT_RANGE": [50, 60], # The range of amount of emojis in a set
	"EMOJI_COUNTING_RANGE": [1, 1], # The range of the amount of emojis that players must count
	"EMOJI_TYPE_RANGE": [3, 5], # The range of the amount of different types of emojis that will be shown
	"ELIMINATIONS": 0, # The amount of eliminations in the round
	"PENALTY": 2, # 
	"MAX_TIME": 15, 

}

MAX_EMOJIS_PER_MESSAGE = 100

# CLASSES AND FUNCTIONS FOR SPEED COUNTER
######################################################################
class SC_Contestant:
	
	# This class is used to represent a player in a Speed Counter event.
	# Used mainly to store statistics

	def __init__(self, user):

		self.user = user
		self.alive = True
		self.rank = None

		# Information for a round
		self.round_times = []
		self.total_round_time = None

		# Information for past rounds
		self.past_rounds = []

		# Information for a set
		self.set_guesses = []
		self.correct = False
		self.guesses_left = 0

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

######################################################################
# MAIN EVENT FUNCTION

class EVENT:

	# Executes when loaded
	def __init__(self):
		self.RUNNING = False

		self.GAME_STARTED = False

		# Setting game information and parameters
		self.info = DEFAULT_INFO
		self.param = DEFAULT_PARAM

	# Executes when deactivated
	def end(self): # Reset the parameters

		self.GAME_STARTED = False

		# Resetting all game information and parameters
		self.info = DEFAULT_INFO
		self.param = DEFAULT_PARAM

		# Stop event from running
		self.RUNNING = False

	# Executes when activated
	def start(self, SERVER): # Set the parameters
		
		self.RUNNING = True

		self.SERVER = SERVER
		self.EVENT_ROLE = 498254150044352514 # Event participant role
		self.EVENT_ADMIN_ROLE = 959155078844010546 # Event administrator role

		self.param["ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ROLE)
		self.param["ADMIN_ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ADMIN_ROLE)
		self.param["GAME_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name=EVENT_ANNOUNCE_CHANNEL) # Post messages in here
		self.param["ADMIN_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name=EVENT_ADMIN_CHANNEL) # Make administration run here

	# Function that runs on each message
	async def on_message(self, message):

		user = message.author
		channel = message.channel

		# Game has not started, meaning that messages are just for set up
		if self.GAME_STARTED == False:

			# Check if message is in administration channel
			if channel == self.param["ADMIN_CHANNEL"]:

				# Check if user wants to start game or not
				if message.content.upper() == "START":

					# Send message with buttons saying to start
					await channel.send("There are **{}** participants. Type `confirm` to start the game or type anything else to cancel.".format(len(self.param["ROLE"].members)))
			
					msg = await BRAIN.wait_for('message', check=lambda m: (m.author == user and m.channel == channel))

					if msg.content.upper() == "CONFIRM":

						# Start game
						await self.start_game()

					else:

						# Cancel start
						await channel.send("Start cancelled. Send `START` to prompt the start.")

		# Game has started
		else:

			print("TEST 1 - Game started is True")

			# Check if guessing is open for contestants
			if self.info["GUESSING_OPEN"] == True:
				
				print("TEST 2 - Guessing is open")

				# Check if message occured in DMs
				if isinstance(channel, discord.channel.DMChannel):

					print("TEST 3 - Message is in DMs")

					# Only users who are current contestants
					if user in self.info["CONTESTANTS"].keys():

						print("TEST 4 - User is considered a player")

						# Check if this is a guess from the player (check if content of message is integer)
						user_answer = None
						try:
							user_answer = int(message.content)
						except:
							pass

						if user_answer:

							print("TEST 5 - Able to convert user's answer into integer")

							# This is an answer from the user
							# Get user's player object
							player_object = self.info["CONTESTANTS"][user]
							# Check if user has already used up all guesses
							if player_object.guesses_left == 0: return

							print("TEST 6 - User still has guesses left")

							# Check if user has already answered correctly before
							if player_object.correct == True: return

							print("TEST 7 - User has not answered correctly yet")

							# User is able to answer, so add their answers to the guess list
							player_object.set_guesses.append(user_answer)
							# Check if user answered correctly
							if user_answer == self.info["SET_INFO"]["CORRECT_ANSWER"]:

								player_object.correct = True
								# Find timestamp of guess message
								guess_timestamp = message.created_at.timestamp()
								# Check how much time it took user to guess correctly
								guess_time = guess_timestamp - self.info["SET_INFO"]["START_TIME"]
								# Add any penalties
								penalty_amount = len(player_object.set_guesses) - 1
								penalty_total = penalty_amount * self.param["PENALTY"]
								final_guess_time = round(guess_time + penalty_total, 2)
								# Make sure final guess time does not go over max
								if final_guess_time > self.param["MAX_TIME"]:
									final_guess_time = self.param["MAX_TIME"]

								# Add time to round times
								player_object.round_times.append(final_guess_time)

								# Send message with reply, saying they got it correct
								if penalty_amount == 0:
									await message.reply(content = "☑️ **Correct!** ☑️\nYou answered in **`{0:.2f}`** seconds.")
								elif penalty_amount == 1:
									await message.reply(content = "☑️ **Correct!** ☑️\nYou answered in **`{0:.2f}`** seconds (including **`{1}`** penalty worth **`{2}`** extra seconds).".format(final_guess_time, penalty_amount, penalty_total))
								else:
									await message.reply(content = "☑️ **Correct!** ☑️\nYou answered in **`{0:.2f}`** seconds (including **`{1}`** penalties worth **`{2}`** extra seconds).".format(final_guess_time, penalty_amount, penalty_total))

							# Check if user answered wrongly
							else:

								# Remove one guess from user's guess amount
								player_object.guesses_left -= 1

								# If user has no more guesses then give them maximum time
								if player_object.guesses_left == 0:

									player_object.round_times.append(self.param["MAX_TIME"])
									await channel.send("❌ **You used up all your guesses!** ❌\nYour time for this set is automatically set to **`{0:.2f}`**.".format(self.param["MAX_TIME"]))

							# Check if all contestants have answered correctly or have run out of guesses
							set_finished = True
							for contestant in list(self.info["CONTESTANT"].values()):

								if contestant.correct == False and contestant.guesses_left > 0:
									set_finished = False

							# If set finished is true, end set
							if set_finished == True:
								await self.end_set()

	# Function that starts the game
	async def start_game(self):

		self.GAME_STARTED = True

		# Go through each person in the participation role and make them a contestant
		for contestant in self.param["ROLE"].members:

			# Create user's contestant instance and add them to contestant list
			contestant_object = SC_Contestant(contestant)
			self.info["CONTESTANTS"][contestant] = contestant_object

		contestant_amount = len(self.info["CONTESTANTS"])
		# Send message in announcement channel
		await self.param["GAME_CHANNEL"].send("```SPEED COUNTER```\nWelcome to **Speed Counter!** There are **{}** contestants competing. Round 1 will start shortly.".format(contestant_amount))

		# Allow for admin modification of Round 1
		self.info["ROUND_NUMBER"] += 1

		try:
			await self.admin_modify()
		except Exception: # Detect errors when commands are used
			traceback.print_exc() # Print the error

	# Function that starts a round
	async def start_round(self):

		# Reset current round data
		self.info["ROUND_INFO"] = {
			"SET_NUMBER": 0,
		}

		# Send message saying round has started
		round_number = self.info["ROUND_NUMBER"]
		current_contestants, eliminations = len(self.info["CONTESTANTS"]), self.param["ELIMINATIONS"]
		sets = self.param["SETS_PER_ROUND"]

		await self.param["GAME_CHANNEL"].send(f"```ROUND {round_number}```\nThere are **{current_contestants}** contestants entering this round.\nThere are **{sets}** sets.\nThe slowest **{eliminations}** contestant(s) across this round are eliminated.")

		# Reset each player's round data
		for player_object in self.info["CONTESTANTS"].values():

			player_object.round_times = []
			player_object.total_round_time = 0

		# Begin the sets
		await self.setup_set()

	# Function at the start of a set - resetting all variables
	async def setup_set(self):

		# Reset current set data
		self.info["SET_INFO"] = {
			"START_TIME": 0,
			"END_TIME": 0,
			"CORRECT_ANSWER": None,
		}
		self.info["ROUND_INFO"]["SET_NUMBER"] += 1

		# Reset current player set data
		for player_object in self.info["CONTESTANTS"].values():
			player_object.set_guesses = [] # The guesses that they've used in the set
			player_object.correct = False
			player_object.guesses_left = self.param["GUESS_AMOUNT"] # The amount of guesses they have left

		# Wait for user to start the set
		# Create start button
		button_view = View(timeout = None)

		# BUTTON FUNCTION - START
		########################################################
		async def start_button_pressed(interaction):

			if interaction.user not in self.param["ADMIN_ROLE"].members:
				await interaction.response.defer()
				return

			# BEGIN THE ROUND
			await interaction.response.edit_message(content = "**Set {} has been started!**".format(self.info["ROUND_INFO"]["SET_NUMBER"]), view = None)

			# Start game
			await self.run_set()

		# Creating button objects
		start_button = Button(style = discord.ButtonStyle.primary, label = "Start set")
		start_button.callback = start_button_pressed				
		button_view.add_item(start_button)

		await self.param["ADMIN_CHANNEL"].send("**Round {} - Set {}**\nPress the button to begin the set.".format(self.info["ROUND_NUMBER"], self.info["ROUND_INFO"]["SET_NUMBER"]), view = button_view)
	
	# Function that runs when a set starts
	async def run_set(self):

		set_number = self.info["ROUND_INFO"]["SET_NUMBER"]
		set_total = self.param["SETS_PER_ROUND"]

		# RANDOMIZING STRING OF EMOJIS
		################################################################
		# Choose a random emoji set
		emoji_set = copy.deepcopy(random.choice(self.param["EMOJI_SETS"]))

		# Set amounts depending on ranges
		emoji_count = random.randint(self.param["EMOJI_COUNT_RANGE"][0], self.param["EMOJI_COUNT_RANGE"][1])
		emoji_type_amount = random.randint(self.param["EMOJI_TYPE_RANGE"][0], self.param["EMOJI_TYPE_RANGE"][1])
		
		# Randomize which emojis to use
		emojis_in_set = []
		for i in range(emoji_type_amount):
			# Choose a random emoji from the emoji set
			random_emoji_num = random.randint(0, len(emoji_set) - 1)
			emoji_chosen = emoji_set[random_emoji_num]
			emojis_in_set.append(emoji_chosen)
			# Remove emoji from emoji set
			emoji_set.pop(random_emoji_num)

		# Choose which emojis that the player must count
		emojis_counting = []
		# Shuffle the emojis in set list
		random.shuffle(emojis_in_set)

		# Decide how many emojis the players must count
		emoji_counting_types = random.randint(self.param["EMOJI_COUNTING_RANGE"][0], self.param["EMOJI_COUNTING_RANGE"][1])

		for i in range(emoji_counting_types):
			emojis_counting.append(emojis_in_set[i])

		# Create the random string of emojis
		emoji_str = ""
		correct_emoji_count = 0
		for i in range(emoji_count):

			# Get a random emoji from the emojis in set list
			random_emoji = random.choice(emojis_in_set)
			emoji_str += random_emoji

			# Check if emoji is in the counting list, and add it to the correct emoji counter if so
			if random_emoji in emojis_counting:
				correct_emoji_count += 1

		# Make emoji strings into list - only max of 100 emojis per message

		chunks = [emoji_str[i:i + MAX_EMOJIS_PER_MESSAGE] for i in range(0, len(emoji_str), MAX_EMOJIS_PER_MESSAGE)]
		################################################################

		# Send set title to discord, along with what emoji they are counting
		set_string = "__**SET #{}/{}**__\n\n".format(set_number, set_total)
		if emoji_counting_types > 1:
			set_string += "You are counting the emojis " + " ".join(emojis_counting) + ". Your answer should be the sum of these."
		elif emoji_counting_types == 1:
			set_string += f"You are counting the emoji {emojis_counting[0]}."

		await self.param["GAME_CHANNEL"].send(set_string)

		# Wait a few seconds
		await asyncio.sleep(3)

		# Send "Ready?" string to prompt players
		await self.param["GAME_CHANNEL"].send("***Ready?***")

		# Wait a few seconds
		await asyncio.sleep(random.randint(20, 40) / 10)

		# Set correct answer
		self.info["SET_INFO"]["CORRECT_ANSWER"] = correct_emoji_count

		# Open guessing
		self.info["GUESSING_OPEN"] = True

		# Send GO! and emoji string
		await self.param["GAME_CHANNEL"].send("***GO!***")
		latest_emoji_msg = None
		for emoji_str_chunk in chunks:
			latest_emoji_msg = await self.param["GAME_CHANNEL"].send(emoji_str_chunk)

		# Set timestamps
		self.info["SET_INFO"]["START_TIME"] = latest_emoji_msg.created_at.timestamp()
		self.info["SET_INFO"]["END_TIME"] = latest_emoji_msg.created_at.timestamp() + self.param["MAX_TIME"]

	# Function that ends the set
	async def end_set(self):

		set_number = self.info["ROUND_INFO"]["SET_NUMBER"]
		set_total = self.param["SETS_PER_ROUND"]

		# Close guessing
		self.info["GUESSING_OPEN"] = False

		# Send message saying that set has ended
		self.param["GAME_CHANNEL"].send("**Set #{}/{} has ended!**\nThe correct answer was `**{}**`.".format(set_number, set_total, self.info["SET_INFO"]["CORRECT_ANSWER"]))

		await asyncio.sleep(5)

		# Check if that was the final set
		if set_number == set_total:

			# End round
			await self.end_round()

		else:
			# That was not the final set, so do not end round and start new set
			await self.setup_set()

	# Function that ends the round
	async def end_round(self):

		# Finalize players' total times
		for contestant in list(self.info["CONTESTANTS"].values()):
			contestant.total_round_time = sum(contestant.round_times)

		# Sort players in a list from fastest total time to lowest time
		contestant_list = list(self.info["CONTESTANTS"].keys())
		sorted_contestant_list = sorted(contestant_list, key=lambda userobj: (self.info["CONTESTANTS"][userobj].total_round_time))

	# Function that allows user to modify parameters
	async def admin_modify(self):

		# Create embed
		admin_embed = discord.Embed(title="Round {} - {} Contestants Remain".format(self.info["ROUND_NUMBER"], len(self.info["CONTESTANTS"])), description="Select a parameter to change for the round the dropdown menu, or select `Confirm` to start the round.", color=0x31d8b1)

		# Add fields to the embed
		admin_embed.add_field(name="😀 Emoji sets", value="\n".join(["".join(emoji_set) for emoji_set in self.param["EMOJI_SETS"]]), inline=False)
		admin_embed.add_field(name="🔢 Emoji count range", value=str(self.param["EMOJI_COUNT_RANGE"][0]) + " to " + str(self.param["EMOJI_COUNT_RANGE"][1]), inline=True)
		admin_embed.add_field(name="🐑 Emojis to count range", value=str(self.param["EMOJI_COUNTING_RANGE"][0]) + " to " + str(self.param["EMOJI_COUNTING_RANGE"][1]), inline=True)
		admin_embed.add_field(name="⌨️ Emoji type range", value=str(self.param["EMOJI_TYPE_RANGE"][0]) + " to " + str(self.param["EMOJI_TYPE_RANGE"][1]), inline=True)
		admin_embed.add_field(name="💨 Sets per round", value=str(self.param["SETS_PER_ROUND"]) + " sets", inline=False)
		admin_embed.add_field(name="❌ Amount of guesses", value=str(self.param["GUESS_AMOUNT"]) + " guesses", inline=True)
		admin_embed.add_field(name="❗ Wrong guess penalty", value=str(self.param["PENALTY"]) + " seconds", inline=True)
		admin_embed.add_field(name="⏱️ Maximum time", value=str(self.param["MAX_TIME"]) + " seconds", inline=True)
		admin_embed.add_field(name="⚔️ Eliminations", value=str(self.param["ELIMINATIONS"]) + " contestants", inline=False)

		# Creating dropdown menu for admins to use
		select_view = View(timeout = None)

		options_list = [
			discord.SelectOption(label = "Modify emoji sets", value = "emoji_sets", emoji = "😀"),
			discord.SelectOption(label = "Modify emoji count range", value = "emoji_count_range", emoji = "🔢"),
			discord.SelectOption(label = "Modify emojis to count range", value = "emoji_counting_range", emoji = "🐑"),
			discord.SelectOption(label = "Modify emoji type range", value = "emoji_type_range", emoji = "⌨️"),
			discord.SelectOption(label = "Modify sets per round", value = "sets_per_round", emoji = "💨"),
			discord.SelectOption(label = "Modify amount of guesses", value = "guess_amount", emoji = "❌"),
			discord.SelectOption(label = "Modify wrong guess penalty", value = "penalty", emoji = "❗"),
			discord.SelectOption(label = "Modify maximum time", value = "max_time", emoji = "⏱️"),
			discord.SelectOption(label = "Modify eliminations", value = "eliminations", emoji = "⚔️"),
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
				if option_selected == "emoji_sets":
					# EMOJI SETS - Get user to change emoji sets
					await self.admin_modify()

				elif option_selected == "emoji_count_range":
					# EMOJI_COUNT_RANGE - Ask user for range of amount of emojis bot will post in one set
					await self.param["ADMIN_CHANNEL"].send("Set a MINIMUM amount of emojis that the bot will post in a set, or say `cancel` to go back.")
					minimum = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if minimum != "cancel":
						# Ask user for minimum
						await self.param["ADMIN_CHANNEL"].send("Set a MAXIMUM amount of emojis that the bot will post in a set, or say `cancel` to go back.")
						maximum = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
						if maximum != "cancel":
							self.param["EMOJI_COUNT_RANGE"][0] = minimum
							self.param["EMOJI_COUNT_RANGE"][1] = maximum

					await self.admin_modify()

				elif option_selected == "emoji_counting_range":
					# EMOJI_COUNTING_RANGE - Ask user for range of amount of emoji types that contestants must count
					await self.param["ADMIN_CHANNEL"].send("Set a MINIMUM amount of emoji types that contestants must count, or say `cancel` to go back.")
					minimum = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if minimum != "cancel":
						# Ask user for minimum
						await self.param["ADMIN_CHANNEL"].send("Set a MAXIMUM amount of emoji types that contestants must count, or say `cancel` to go back.")
						maximum = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
						if maximum != "cancel":
							self.param["EMOJI_COUNTING_RANGE"][0] = minimum
							self.param["EMOJI_COUNTING_RANGE"][1] = maximum

					await self.admin_modify()

				elif option_selected == "emoji_type_range":
					# EMOJI_TYPE_RANGE - Ask user for range of types of emojis that will be used in a set
					await self.param["ADMIN_CHANNEL"].send("Set a MINIMUM amount of types of emojis that will be posted in a set, or say `cancel` to go back.")
					minimum = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if minimum != "cancel":
						# Ask user for minimum
						await self.param["ADMIN_CHANNEL"].send("Set a MAXIMUM amount of types of emojis that will be posted in a set, or say `cancel` to go back.")
						maximum = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
						if maximum != "cancel":
							self.param["EMOJI_TYPE_RANGE"][0] = minimum
							self.param["EMOJI_TYPE_RANGE"][1] = maximum
						
					await self.admin_modify()

				elif option_selected == "sets_per_round":
					# SETS_PER_ROUND - Ask user for amount of sets in a round
					await self.param["ADMIN_CHANNEL"].send("Set the amount of sets that will be used next round, or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if admin_input != "cancel":
						self.param["SETS_PER_ROUND"] = admin_input
					await self.admin_modify()

				elif option_selected == "guess_amount":
					# GUESS_AMOUNT - Ask user for amount of guesses user has before automatically being given the lowest possible score
					await self.param["ADMIN_CHANNEL"].send("Set the maximum amount of guesses contestants have before automatically getting the lowest possible score, or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if admin_input != "cancel":
						self.param["GUESS_AMOUNT"] = admin_input
					await self.admin_modify()

				elif option_selected == "penalty":
					# PENALTY - Ask user for the time penalty contestants are given for each wrong guess
					await self.param["ADMIN_CHANNEL"].send("Set the time penalty (in seconds) that contestants are given for each wrong guess, or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if admin_input != "cancel":
						self.param["PENALTY"] = admin_input
					await self.admin_modify()

				elif option_selected == "max_time":
					# MAX_TIME - Ask user for the time in seconds that users have to guess correctly
					await self.param["ADMIN_CHANNEL"].send("Set the time (in seconds) that users have per set to guess correctly, or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if admin_input != "cancel":
						self.param["MAX_TIME"] = admin_input
					await self.admin_modify()

				elif option_selected == "eliminations":
					# ELIMINATIONS - Ask user for the amount of contestants to eliminate this round
					await self.param["ADMIN_CHANNEL"].send("Set the amount of contestants that will be eliminated this round, or say `cancel` to go back.")
					admin_input = await get_positive_integer(interaction.user, self.param["ADMIN_CHANNEL"])
					if admin_input != "cancel":
						self.param["ELIMINATIONS"] = admin_input
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

						# BEGIN THE ROUND
						await interaction.response.edit_message(content = "**Round {} will begin now!**".format(self.info["ROUND_NUMBER"]), view = None)

						# Start game
						await self.start_round()

					async def cancel_button_pressed(interaction):

						if interaction.user not in self.param["ADMIN_ROLE"].members:
							await interaction.response.defer()
							return

						# BEGIN THE RESPONDING PERIOD
						await interaction.response.edit_message(content = "You will now return to the admin modification menu.", view = None)

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

					await self.param["ADMIN_CHANNEL"].send("✅ **Parameters confirmed!** Press the Start button to start the next round. If you would like to cancel, press the Cancel button.", view = button_view)

			else:

				# Defer interaction
				await interaction.response.defer()

		##########################################################################
		##########################################################################

		modification_menu.callback = mod_menu_press
		select_view.add_item(modification_menu)

		await self.param["ADMIN_CHANNEL"].send(embed = admin_embed, view = select_view)


