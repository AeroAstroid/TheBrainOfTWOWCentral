# DESCRIPTION DETECTIVE GAME
# Created for description detective event
###################################################################################

import time, discord, random, statistics
from Config._functions import grammar_list, word_count, elim_prize
from Config._const import ALPHABET, BRAIN

NORMAL_POINTS = [60, 50, 40, 30, 20, 10]

class DDPlayer:
    def __init__(self, user):

		pass

class EVENT:

	# Executes when loaded
	def __init__(self):
		self.RUNNING = False

		self.info = { # Define all the game parameters

			"PLAYERS": {},

            "ROUND_NUMBER": 0,
            "TOTAL_ROUNDS": 0,

            "ROUND_IN_PROGRESS": False

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
            "ROLE": 0,
            "CSV_MESSAGE_ID": ""
		}


	# Executes when activated
	def start(self, SERVER): # Set the parameters

		# ATTEMPT TO DOWNLOAD CSV FILE FROM MESSAGE
		try:
			
			# Get message with csv file attached
			csv_message = BRAIN.get_message(int(self.param["CSV_MESSAGE_ID"]))

			# Find csv file
			if len(csv_message.attachments) == 0:
				print("This message does not have any attachments.")
				raise Exception

			attachment = csv_message.attachments[0]

			# Check if attachment is actually a csv file
			attachment_url = attachment.url
			if not attachment_url.endswith(".csv"):
				print("This message has an attachment that is not a CSV file.")
				raise Exception

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
			# Print exception and send message
			print(e)
			# Do not let the event start running
			return

		self.RUNNING = True

		self.SERVER = SERVER
		self.EVENT_ROLE = 498254150044352514 # Event participant role
		self.param["ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ROLE)
		self.param["CLUE_POSTING"] = discord.utils.get(SERVER["MAIN"].channels, name="dawthons-lair") # Post messages in here

	# Function that runs every two seconds
	async def on_two_second(self):

		pass

        # This function is used for time checking
        # Only runs if the time 
		
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
