# DESCRIPTION DETECTIVE GAME
# Created for description detective event
# Written by Neonic - ask him if you have any questions about how the code works
###################################################################################

import time, discord, random, statistics, csv, asyncio
from discord.ui import Button, View
from Config._functions import grammar_list, word_count, elim_prize
from Config._const import ALPHABET, BRAIN

NORMAL_POINTS = [60, 50, 40, 30, 20, 10]
EASY_POINTS = [30, 25, 20, 15, 10, 5]
TIME_START_ROUND = 10
NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]

class DDPlayer:
	def __init__(self, user):

		self.user = user
		self.score = 0

		self.round_scores = []
		self.guesses = [None, None, None, None, None, None]
		self.guess_msg = [None, None, None, None, None, None]
		self.score_this_round = 0
		self.correct = False

class EVENT:

	# Executes when loaded
	def __init__(self):
		self.RUNNING = False

		self.GAME_STARTED = False

		self.info = { # Define all the game parameters

			"PLAYERS": {},
			"USER_IDS": [],

			"ROUND_NUMBER": 0,

			"GUESSING_OPEN": False,
			"CLUE_NUM": 0,

			# Holds the current round's data
			"CURRENT_ROUND": {
				"START_TIME": 0,
				"DIFFICULTY": "",
				"ANSWERS": [],
				"CLUE_1": "",
				"CLUE_2": "",
				"CLUE_3": "",
				"CLUE_4": "",
				"CLUE_5": "",
				"CLUE_6": "",
			},
			
			# Holds all the game rounds
			"GAME_ROUNDS": []

		}

		self.param = { # Define all the parameters necessary that could be changed
			"CLUE_TIME": 30,
			"FINAL_GUESS_TIME": 30,
			"CLUE_POSTING": 0,
			"ADMIN_CHANNEL": 0,
			"ROLE": 0,
			"CSV_MESSAGE": 0
		}

	# Executes when deactivated
	def end(self): # Reset the parameters

		self.GAME_STARTED = False

		self.info = { # Define all the game parameters

			"PLAYERS": {},
			"USER_IDS": [],

			"ROUND_NUMBER": 0,

			"GUESSING_OPEN": False,
			"CLUE_NUM": 0,

			# Holds the current round's data
			"CURRENT_ROUND": {
				"START_TIME": 0,
				"DIFFICULTY": "",
				"ANSWERS": [],
				"CLUE_1": "",
				"CLUE_2": "",
				"CLUE_3": "",
				"CLUE_4": "",
				"CLUE_5": "",
				"CLUE_6": "",
			},
			
			# Holds all the game rounds
			"GAME_ROUNDS": []

		}

		self.param = { # Define all the parameters necessary that could be changed
			"CLUE_TIME": 30,
			"FINAL_GUESS_TIME": 30,
			"CLUE_POSTING": 0,
			"ADMIN_CHANNEL": 0,
			"ROLE": 0,
			"CSV_MESSAGE": 0
		}
		self.RUNNING = False

	# Executes when activated
	def start(self, SERVER): # Set the parameters
		
		self.RUNNING = True

		self.SERVER = SERVER
		self.EVENT_ROLE = 498254150044352514 # Event participant role
		self.EVENT_ADMIN_ROLE = 959155078844010546 # Event participant role
		self.param["ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ROLE)
		self.param["ADMIN_ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ADMIN_ROLE)
		self.param["GAME_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name="tco-center-stage") # Post messages in here
		self.param["ADMIN_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name="staff•commands")

	# Begin the game
	async def start_game(self):

		event_role = self.param["ROLE"]
		clue_posting_channel = self.param["GAME_CHANNEL"]
		
		# Set up all players
		for user in event_role.members:

			# Create player object
			player_object = DDPlayer(user)
			self.info["PLAYERS"][user] = player_object
			self.info["USER_IDS"].append(user.id)

		# Send introduction to game
		await clue_posting_channel.send(
			f"""**Welcome to Description Detective!**
		
Each round, you have **20** seconds after each clue is posted in this channel to guess something in {BRAIN.user.mention}'s DMs. 
Note that there is no prefix to guessing - you just need to type the answer in DMs!
You only have one guess per clue, so make it count (and don't misspell anything!)
If you do not receive a reply from the bot, it means that your answer was incorrect.
You will receive points depending on the amount of clues posted at the time you answer correctly. (Less clues means more points.)
			
The game will start in ten seconds."""
		)

		print("Description Detective game starting!")

		await asyncio.sleep(10)

		await self.begin_round()

	# Begin each round
	async def begin_round(self):

		event_role = self.param["ROLE"]
		clue_posting_channel = self.param["GAME_CHANNEL"]

		# Reset all players' guesses
		for player in list(self.info["PLAYERS"].values()):
			player.guesses = [None, None, None, None, None, None]
			player.score_this_round = 0
			player.correct = False

		# Increment the round number
		self.info["ROUND_NUMBER"] += 1

		# Get the game round in GAME_ROUNDS
		game_round = self.info["GAME_ROUNDS"][self.info["ROUND_NUMBER"] - 1]

		# Reset clue num
		self.info["CLUE_NUM"] = 0

		# Input the data into CURRENT_ROUND
		self.info["CURRENT_ROUND"]["DIFFICULTY"] = game_round[0]
		self.info["CURRENT_ROUND"]["CLUE_1"] = game_round[1]
		self.info["CURRENT_ROUND"]["CLUE_2"] = game_round[2]
		self.info["CURRENT_ROUND"]["CLUE_3"] = game_round[3]
		self.info["CURRENT_ROUND"]["CLUE_4"] = game_round[4]
		self.info["CURRENT_ROUND"]["CLUE_5"] = game_round[5]
		self.info["CURRENT_ROUND"]["CLUE_6"] = game_round[6]
		self.info["CURRENT_ROUND"]["ANSWERS"] = []

		# Get the valid answers
		index_num = 6
		while True:

			try:
				index_num += 1
				if game_round[index_num] != "":
					self.info["CURRENT_ROUND"]["ANSWERS"].append(game_round[index_num].strip().lower())
				else:
					break
			except:
				break

		# Send message
		await clue_posting_channel.send("```ROUND {}```\nDifficulty: **{}**.\nClues will begin to be sent in {} seconds.".format(self.info["ROUND_NUMBER"], self.info["CURRENT_ROUND"]["DIFFICULTY"].title(), TIME_START_ROUND))

		# Start round in 10 seconds
		await asyncio.sleep(TIME_START_ROUND)

		# STARTING ROUND
		self.info["START_TIME"] = time.time()
		self.info["GUESSING_OPEN"] = True
		self.info["CLUE_NUM"] = 1

		# Send first clue
		await clue_posting_channel.send("1️⃣ " + self.info["CURRENT_ROUND"]["CLUE_1"])

	# End guessing
	async def end_guessing(self, all_correct = False):

		clue_posting_channel = self.param["GAME_CHANNEL"]

		self.info["GUESSING_OPEN"] = False
		if all_correct == False:
			await clue_posting_channel.send("**Round over!**\nThe answer this round was **`{}`**.".format(self.info["CURRENT_ROUND"]["ANSWERS"][0]))
		else:
			await clue_posting_channel.send("**Everyone guessed it!**\nThe answer this round was **`{}`**.".format(self.info["CURRENT_ROUND"]["ANSWERS"][0]))

		await clue_posting_channel.send("Waiting for verification from event administrators...")

		while True:
			msg = await BRAIN.wait_for('message', check=lambda m: (m.author in self.param["ADMIN_ROLE"].members and m.channel == self.param["ADMIN_CHANNEL"]))

			try:
				if msg.content.strip().lower() == "verify": break
			except:
				pass

		await self.param["ADMIN_CHANNEL"].send("Round results verified.")

		# Count how many players got it right	
		total_players = 0
		players_correct = 0

		for player in list(self.info["PLAYERS"].values()):

			total_players += 1
			# Player was correct, increment player count by 1
			if player.correct == True:
				players_correct += 1

		self.info["CLUE_NUM"] = 0

		# For every player, append their round score to round scores
		for player in list(self.info["PLAYERS"].values()):

			player.round_scores.append(player.score_this_round)
			player.score += player.score_this_round

		await self.sort_leaderboard()

		await clue_posting_channel.send(f"**{players_correct}/{total_players}** answered correctly.")

		# Wait a few seconds until prompting the host to start the next round
		await asyncio.sleep(3)

		# Check if there is a next round
		if self.info["ROUND_NUMBER"] != len(self.info["GAME_ROUNDS"]):
			# Create buttons to prompt user to start next round
			button_view = View(timeout = None)

			async def next_round_pressed(interaction):

				if interaction.user in self.param["ADMIN_ROLE"].members:

					self.GAME_STARTED = True
					await interaction.response.edit_message(content = f"**Next round started by {interaction.user}!**", view = None)

					# Start game
					await self.begin_round()

				else:

					await interaction.response.defer()

			next_round_button = Button(style = discord.ButtonStyle.blurple, label = "Start next round!")
			next_round_button.callback = next_round_pressed				
			button_view.add_item(next_round_button)

			await self.param["ADMIN_CHANNEL"].send("Press this button to start the next round.", view = button_view)
		# If there is no next round, then end game
		else:

			await clue_posting_channel.send("**All rounds have been completed!**\nThe host will post the final results shortly.\nThanks for playing!")

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

	# Function to post all the players' guesses
	async def post_guesses(self):

		try:

			# Post the current clue's guesses
			player_guess_strings = ["__**ROUND #{} CLUE #{} GUESSES**__\n\n".format(self.info["ROUND_NUMBER"], self.info["CLUE_NUM"])]

			for player in list(self.info["PLAYERS"].values()):

				player_name = player.user.name
				player_id = player.user.id
				player_guess = player.guesses[self.info["CLUE_NUM"] - 1]

				if player_guess:
					player_string = ""
					if player.correct == True:
						player_string = f"{player_id} ({player_name}) - **`{player_guess}`** ☑\n"
					else:
						player_string = f"{player_id} ({player_name}) - **`{player_guess}`**\n"

					# Check if string will go over 2000 characters
					if len(player_guess_strings[-1]) + len(player_string) > 2000:
						player_guess_strings.append("")
						
					player_guess_strings[-1] += player_string

			# Message has been split into chunks
			for string in player_guess_strings:
				await self.param["ADMIN_CHANNEL"].send(string)

		except Exception as e:

			print(e)

	# Function that runs every two seconds
	async def on_two_second(self):

		clue_posting_channel = self.param["GAME_CHANNEL"]

		# This function is used for time checking when the game is running
		if self.info["GUESSING_OPEN"] == True:

			# Check if all players have guessed correctly
			all_players_correct = True
			for player in list(self.info["PLAYERS"].values()):
				if player.correct == False:
					all_players_correct = False
					break

			if all_players_correct == True:
				
				await self.end_guessing(all_correct = True)
				return

			# Time passed since start of guessing
			time_passed = time.time() - self.info["START_TIME"] 

			# Sending clue #2
			if self.info["CLUE_NUM"] == 1 and time_passed >= self.param["CLUE_TIME"]:

				await self.post_guesses()
				await clue_posting_channel.send("2️⃣ " + self.info["CURRENT_ROUND"]["CLUE_2"])
				self.info["CLUE_NUM"] = 2

			# Sending clue #3
			elif self.info["CLUE_NUM"] == 2 and time_passed >= self.param["CLUE_TIME"] * 2:

				await self.post_guesses()
				await clue_posting_channel.send("3️⃣ " + self.info["CURRENT_ROUND"]["CLUE_3"])
				self.info["CLUE_NUM"] = 3

			# Sending clue #4
			elif self.info["CLUE_NUM"] == 3 and time_passed >= self.param["CLUE_TIME"] * 3:

				await self.post_guesses()
				await clue_posting_channel.send("4️⃣ " + self.info["CURRENT_ROUND"]["CLUE_4"])
				self.info["CLUE_NUM"] = 4

			# Sending clue #5
			elif self.info["CLUE_NUM"] == 4 and time_passed >= self.param["CLUE_TIME"] * 4:

				await self.post_guesses()
				await clue_posting_channel.send("5️⃣ " + self.info["CURRENT_ROUND"]["CLUE_5"])
				self.info["CLUE_NUM"] = 5

			# Sending clue #6 -- FINAL CLUE
			elif self.info["CLUE_NUM"] == 5 and time_passed >= self.param["CLUE_TIME"] * 5:

				await self.post_guesses()
				await clue_posting_channel.send("6️⃣ " + self.info["CURRENT_ROUND"]["CLUE_6"])
				await clue_posting_channel.send("You have **{} seconds** to get in your final guess!".format(self.param["FINAL_GUESS_TIME"]))
				self.info["CLUE_NUM"] = 6

			# Ending guessing
			elif self.info["CLUE_NUM"] == 6 and time_passed >= self.param["CLUE_TIME"] * 5 + self.param["FINAL_GUESS_TIME"]:

				await self.post_guesses()
				await self.end_guessing()

	# Function that runs on each message
	async def on_message(self, message):

		# Game has not started, meaning that messages are just for set up
		if self.GAME_STARTED == False:
			
			# Check if no CSV message has been sent
			if self.param["CSV_MESSAGE"] == 0:

				# Check for four conditions for message
				if message.channel != self.param["ADMIN_CHANNEL"]: return

				if len(message.attachments) == 0: return

				if message.content != "DESCRIPTION DETECTIVE CSV": return

				attachment = message.attachments[0]

				# Check if attachment is actually a csv file
				attachment_url = attachment.url
					
				if not attachment_url.endswith(".csv"): return

				# This is a CSV file, now attempt to read it and if any errors come up just return
				try:

					# Save the attachment
					await attachment.save("Events/descriptiondetective.csv")

					# Read CSV and get dictionary
					csv_list = []

					with open("Events/descriptiondetective.csv", 'r', encoding='UTF-8') as csv_file:
						reader = csv.reader(csv_file)
						for row in list(reader):
							csv_list.append(row)

					# Remove first row from CSV list
					csv_list.pop(0)

					# Set self.info's GAME_ROUNDS to the CSV list
					self.info["GAME_ROUNDS"] = csv_list

					print(self.info["GAME_ROUNDS"])

					self.param["CSV_MESSAGE"] = 1

				except Exception as e: 
					return
					
				# If the command has not yet returned, a valid CSV file has been sent!
				# Send message allowing player to start game

				button_view = View(timeout = None)

				# BUTTON FUNCTIONS
				async def start_button_pressed(interaction):

					self.GAME_STARTED = True
					await interaction.response.edit_message(content = "**Game of Description Detective starting!**", view = None)

					# Start game
					await self.start_game()

				async def reset_button_pressed(interaction):

					self.param["CSV_MESSAGE"] = 0
					await interaction.response.edit_message(content = "Data reset. To get this message again, submit another CSV file.", view = None)

				# Set up buttons
				start_button = Button(style = discord.ButtonStyle.green, label = "Start")
				reset_button = Button(style = discord.ButtonStyle.red, label = "Reset")

				start_button.callback = start_button_pressed
				reset_button.callback = reset_button_pressed
				
				button_view.add_item(start_button)
				button_view.add_item(reset_button)

				# Send message
				await message.channel.send("The CSV for Description Detective has been set up!\nThere are **{}** rounds.\nTo start the game or reset the CSV, just press the corresponding button on the message.".format(len(self.info["GAME_ROUNDS"])), view = button_view)

		else:

			# GAME HAS STARTED
			# CODE FOR PLAYERS GUESSING IN DMS
			# Check if game is currently in guessing
			if self.info["GUESSING_OPEN"] == True:

				try:
					
					# Check if user's message is in DMs and if not, return
					if not message.guild:

						# Check if user is in players, and if not, return
						if message.author.id in self.info["USER_IDS"]: 

							# Get member from message.author.id
							player = self.SERVER["MAIN"].get_member(message.author.id)
							# Get player object
							player_object = self.info["PLAYERS"][player]

							# Check if player has already guessed this clue and if not, return
							if not player_object.guesses[self.info["CLUE_NUM"] - 1]:

								# Check if player has already guessed correctly this round and return if so
								if player_object.correct == False: 

									# Get player's guess from the content of the message and strip it of whitespace + lowercase it
									player_guess = message.content.strip().lower()

									# Check if guess is too long
									if len(player_guess) > 70:
										return

									# Log player's guess
									player_object.guess_msg[self.info["CLUE_NUM"] - 1] = message
									player_object.guesses[self.info["CLUE_NUM"] - 1] = player_guess

									# Check if player guess is correct
									if player_guess in self.info["CURRENT_ROUND"]["ANSWERS"]:

										# Give player points
										if self.info["CURRENT_ROUND"]["DIFFICULTY"].upper() == "NORMAL": 
											points_gained = NORMAL_POINTS[self.info["CLUE_NUM"] - 1]
										elif self.info["CURRENT_ROUND"]["DIFFICULTY"].upper() == "EASY": 
											points_gained = EASY_POINTS[self.info["CLUE_NUM"] - 1]

										player_object.correct = True
										player_object.score_this_round = points_gained

										# Send message to user
										await message.reply("☑ **You got it correct on Clue {}!** ☑\nYou gain **{}** points this round!".format(self.info["CLUE_NUM"], points_gained))

									# If user did not get it correct, react with emoji
									else:

										await message.add_reaction(NUMBER_EMOJIS[self.info["CLUE_NUM"] - 1])

				except Exception as e:
					# Print exception
					print(e)

			# ADMIN COMMANDS
			# Check if message from event admin
			if message.author in self.param["ADMIN_ROLE"].members:

				if message.content.strip().lower().startswith("dd/"):

					# Check if message starts with
					args = message.content[len("dd/"):].split(" ")
					command = args[0].upper()
					level = len(args)

					if command == "MARKCORRECT":

						# Marking someone's answer correct
						if level == 1:
							await message.channel.send("You must include the user ID of a player, and the number of the guess you want to mark correctly!")

						if level == 2:
							await message.channel.send("You must include the number of the guess (what clue they guessed at) that you want to mark correctly!")

						if level == 3:
							
							# Both arguments have been given
							# Attempt to get the user
							player_to_mark = None
							try:
								player_to_mark = self.SERVER["MAIN"].get_member(int(args[1]))
							except:
								await message.channel.send(f"Could not get player with ID {args[1]}!")
								return

							# Check if player to mark is in PLAYERS keys
							if not player_to_mark in list(self.info["PLAYERS"].keys()): 
								await message.channel.send(f"Player with ID {args[1]} is not participating in event!")
								return

							# Check if number guess is an integer
							guess_clue = None
							try:
								guess_clue = int(args[2])
								if guess_clue < 1 or guess_clue > 6:
									raise Exception
							except:
								await message.channel.send("The clue guess must be an integer from 1-6!")
								return

							# Check if user sent guess or not
							player_object = self.info["PLAYERS"][player_to_mark]
							if not player_object.guess_msg[guess_clue - 1]:
								await message.channel.send(f"The player with ID {args[1]} did not send a guess at Clue #{guess_clue}!")
								return

							# Give player points
							if self.info["CURRENT_ROUND"]["DIFFICULTY"].upper() == "NORMAL": 
								points_gained = NORMAL_POINTS[guess_clue - 1]
							elif self.info["CURRENT_ROUND"]["DIFFICULTY"].upper() == "EASY": 
								points_gained = EASY_POINTS[guess_clue - 1]

							player_object.correct = True
							player_object.score_this_round = points_gained

							# Send message to user
							await player_object.guess_msg[guess_clue - 1].reply("☑ **Your guess for Clue {} was marked manually correct (not by a bot)!** ☑\nYou gain **{}** points this round!".format(guess_clue, points_gained))
							await self.param["ADMIN_CHANNEL"].send(f"☑ Guess on **Clue #{guess_clue}** ({player_object.guesses[guess_clue - 1]}) marked correct for player {player_object.user.mention}! (Marked correct by {message.author.mention})")
		
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

