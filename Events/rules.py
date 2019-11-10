import time, discord, re, asyncio
from Config._functions import grammar_list

class EVENT:
	LOADED = False
	RUNNING = False
	START = 0

	param = { # Define all the parameters necessary
		"FINAL_5": False,
		"MESSAGES": 0,
		"LOGGING": 0,
		"ROLE": 0,
		"PLAYER_IDS": [],
		"PLAYER_INFO": []
	}

	# Executes when loaded
	def __init__(self):
		self.LOADED = True

	# Executes when activated
	def start(self, TWOW_CENTRAL): # Set the parameters
		self.RUNNING = True
		self.START = time.time()

		self.param["FINAL_5"] = False # When there's <5 players, Rule 1 won't ever be halved (intentional)
		self.param["ROLE"] = discord.utils.get(TWOW_CENTRAL.roles, name="Participating")
		self.param["MESSAGES"] = discord.utils.get(TWOW_CENTRAL.channels, name="events")
		self.param["LOGGING"] = discord.utils.get(TWOW_CENTRAL.channels, name="tournament-time")

		self.param["PLAYER_IDS"] = [x.id for x in self.param["ROLE"].members]
		self.param["PLAYER_INFO"] = [[x, [], time.time()] for x in self.param["PLAYER_IDS"]]

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.param = {
			"FINAL_5": False,
			"MESSAGES": 0,
			"LOGGING": 0,
			"ROLE": 0,
			"PLAYER_IDS": [],
			"PLAYER_INFO": []
		}
		self.RUNNING = False
		self.START = 0


	# [Event-specific] Function that checks for each rule
	def rule_check(self, message, context):
		broken = []

		# Rule 2. Do not send the same message twice throughout the entirety of the event.
		if message in context:
			broken.append("2")

		# Rule 3. Do not send any messages that start and end with the same character.
		if message[0] == message[-1]:
			broken.append("3")

		# Rule 4. Do not use the letter X.
		if "x" in message.lower():
			broken.append("4")

		# Rule 5. Do not send any messages containing four characters or less.
		if len(message) <= 4:
			broken.append("5")

		# Rule 6. Do not use any digits.
		if re.search('[0-9]', message) is not None:
			broken.append("6")

		# Rule 7. Do not use any words that have exactly seven characters.
		lengths = [len(x) for x in message.split(" ")]
		if 7 in lengths:
			broken.append("7")

		# Rule 8. Do not send any messages where the character count is a multiple of 8.
		if len(message) % 8 == 0:
			broken.append("8")
		
		return broken
	

	# Function that runs on each message
	async def on_message(self, message):
		if message.author.id not in self.param["PLAYER_IDS"] or message.channel != self.param["MESSAGES"]:
			return # Filters for messages that are valid for the event

		pl_index = self.param["PLAYER_IDS"].index(message.author.id)
		self.param["PLAYER_INFO"][pl_index][2] = time.time() # Resets the contestant's message timer (Rule 1)

		# Runs rule_check to find any broken rules
		broken = self.rule_check(message.content, self.param["PLAYER_INFO"][pl_index][1])

		if len(broken) > 0:
			# Remove role, announce elimination, mark player as eliminated
			await message.author.remove_roles(self.param["ROLE"])
			await self.param["LOGGING"].send(f"""<@{message.author.id}> has been eliminated for breaking
			Rule{'s' if len(broken) != 1 else ''} {grammar_list(broken)}.""".replace("\t", "").replace("\n", " "))

			self.param["PLAYER_INFO"][pl_index][0] = 0
			self.param["PLAYER_IDS"][pl_index] = 0

		else:
			# Add message to the player's message history (Rule 2)
			self.param["PLAYER_INFO"][player_list_index][1].append(message.content)
	

	# Function that runs every two seconds
	async def on_two_second(self, TWOW_CENTRAL):
		for player_info in self.param["PLAYER_INFO"]:
			pl_index = self.param["PLAYER_INFO"].index(player_info)

			# The two different cases of Rule 1
			if self.param["FINAL_5"]: t = 120
			else: t = 240

			if time.time() - player_info[2] > t: # If the player went too long without sending messages...
				# Remove role, announce elimination, mark player as eliminated
				await TWOW_CENTRAL.get_member(player_info[0]).remove_roles(self.param["ROLE"])
				await self.param["LOGGING"].send(f"<@{player_info[0]}> has been eliminated for breaking Rule 1.")

				self.param["PLAYER_INFO"][pl_index][0] = 0
				self.param["PLAYER_IDS"][pl_index] = 0
			
				# If the final 5 has been reached
				if len([p for p in self.param["PLAYER_IDS"] if p != 0]) == 5:
					self.param["FINAL_5"] = True

					for p in self.param["PLAYER_INFO"]:
						p[2] = time.time
					
					await self.param["LOGGING"].send("**Five players remain.** The threshold for Rule 1 is now halved.")
		
		# Remove eliminated players from the lists
		self.param["PLAYER_IDS"] = [p for p in self.param["PLAYER_IDS"] if p != 0]
		self.param["PLAYER_INFO"] = [p for p in self.param["PLAYER_INFO"] if p[0] != 0]

		if len(self.param["PLAYER_IDS"]) == 1: # Crown a winner
			await self.param["LOGGING"].send(f'<@{self.param["PLAYER_IDS"][0]}> is the winner of the event!')
			self.RUNNING = False

		if len(self.param["PLAYER_IDS"]) == 0: # End the game with no winner
			await self.param["LOGGING"].send("Everyone has been eliminated! The event is over.")
			self.RUNNING = False
		
		return self.RUNNING # Serves as a check of whether or not the event has ended