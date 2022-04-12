# DESCRIPTION DETECTIVE GAME
# Created for description detective event
###################################################################################

import time, discord, random, statistics
from Config._functions import grammar_list, word_count, elim_prize
from Config._const import ALPHABET, BRAIN

CSV_MSG_ID = 963026403236925481

NORMAL_POINTS = [60, 50, 40, 30, 20, 10]

class DDPlayer:
	def __init__(self, user):

		self.user = user
		self.score = 0

		self.round_scores = []
		self.guesses = [
			None,
			None,
			None,
			None,
			None,
			None
		]

class EVENT:

	# Executes when loaded
	def __init__(self):
		self.RUNNING = False

		self.GAME_STARTED = False

		self.info = { # Define all the game parameters

			"PLAYERS": {},

			"ROUND_NUMBER": 0,
			"TOTAL_ROUNDS": 0,

			"ROUND_IN_PROGRESS": False,

			# Holds the current round's data
			"CURRENT_ROUND": {
				"START_TIME": 0,
				"ANSWERS": [],
				"CATEGORY": "",
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
			"CLUE_TIME": 20,
			"CLUE_POSTING": 0,
			"ADMINISTRATION_CHANNEL": 0,
			"ROLE": 0,
			"CSV_MESSAGE": 0
		}

	# Executes when deactivated
	def end(self): # Reset the parameters

		self.GAME_STARTED = False

		self.info = { # Define all the game parameters

			"PLAYERS": {},

			"ROUND_NUMBER": 0,
			"TOTAL_ROUNDS": 0,

			"ROUND_IN_PROGRESS": False,

			# Holds the current round's data
			"CURRENT_ROUND": {
				"START_TIME": 0,
				"ANSWERS": [],
				"CATEGORY": "",
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
			"CLUE_TIME": 20,
			"CLUE_POSTING": 0,
			"ADMINISTRATION_CHANNEL": 0,
			"ROLE": 0,
			"CSV_MESSAGE": 0
		}
		self.RUNNING = False

	# Executes when activated
	def start(self, SERVER): # Set the parameters
		
		self.RUNNING = True

		self.SERVER = SERVER
		self.EVENT_ROLE = 498254150044352514 # Event participant role
		self.param["ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ROLE)
		self.param["CLUE_POSTING"] = discord.utils.get(SERVER["MAIN"].channels, name="dawthons-lair") # Post messages in here
		self.param["ADMINISTRATION_CHANNEL"] = discord.utils.get(SERVER["MAIN"].channels, name="staff•commands")

	# Function that runs every two seconds
	async def on_two_second(self):

		# Wait for game to start from initiation
		pass

		# This function is used for time checking when the game is running
		# Only runs if the time 

	# Function that runs on each message
	async def on_message(self, message):

		# Game has not started, meaning that messages are just for set up
		if self.GAME_STARTED == False:
			
			# Check if no CSV message has been sent
			if self.param["CSV_MESSAGE"] == 0:

				print(message.content)
				print(self.param["ADMINISTRATION_CHANNEL"])

				# Check for four conditions for message
				if message.channel != self.param["ADMINISTRATION_CHANNEL"]: return

				print("test 1")

				if len(message.attachments) == 0: return

				print("test 2")

				if message.content != "DESCRIPTION DETECTIVE CSV": return

				print("test 3")

				attachment = csv_message.attachments[0]

				# Check if attachment is actually a csv file
				attachment_url = attachment.url
				if not attachment_url.endswith(".csv"): return

				print("test 4")

				# This is a CSV file, now attempt to read it and if any errors come up just return
				try:

					# Save the attachment
					attachment.save("Events/descriptiondetective.csv")

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

					raise Exception

				except Exception as e: 
					print(e)
					return
					
				# If the command has not yet returned, a valid CSV file has been sent!
				# Send message allowing player to start game

				



		
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

