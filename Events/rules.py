import time, discord, re
from Config._functions import grammar_list

class EVENT:
	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.param = { # Define all the parameters necessary
			"FINAL_5": False,
			"MESSAGES": 0,
			"LOGGING": 0,
			"ROLE": 0,
			"PLAYER_IDS": [],
			"PLAYER_INFO": []
		}


	# Executes when activated
	def start(self, SERVER): # Set the parameters
		self.RUNNING = True

		self.SERVER = SERVER
		self.EVENT_ROLE = 498254150044352514 # Event participant role
		self.param["FINAL_5"] = False
		self.param["ROLE"] = discord.utils.get(SERVER["MAIN"].roles, id=self.EVENT_ROLE)
		self.param["MESSAGES"] = discord.utils.get(SERVER["MAIN"].channels, name="dawthons-lair") # Take messages from here
		self.param["LOGGING"] = discord.utils.get(SERVER["MAIN"].channels, name="event-time") # Log eliminations here

		self.param["PLAYER_IDS"] = [x.id for x in self.param["ROLE"].members] # Set the players as the people with role
		# Set [id, history, last_message] parameters for the message history and timer rules
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


	# [Event-specific] Function that checks for each rule
	def rule_check(self, msg, context):
		message = msg.content
		print(message)
		broken = []

		# Rule 2. Vowels are essential to many English words! Every message you send must have at least one vowel in it (including the letter “y”)
		vowels = ["a", "e", "i", "o", "u", "y"]
		c = 0
		for chr in list(message.lower()):
			if chr in vowels: c += 1
		if c == 0:
			broken.append("2")
		
		# Rule 3. I don’t like the verbosity meta in TWOW right now; you can only use words that are 8 characters or less!
		lengths = [len(x) for x in message.split(" ")]
		if max(lengths) > 8 :
			broken.append("3")

		# Rule 4. The number 3 sucks lmfao; Your message cannot be exactly 3 words.
		if len(message.split(" ")) == 3:
			broken.append("4")

		# Rule 5. Do not send any embeds, images or files.
		if msg.attachments:
			broken.append("5")

		# Rule 6. Once again, the number 3 sucks lmfao; You can’t use the letter C.
		if "c" in message.lower():
			broken.append("6")
		
		# Rule 7. You have to be obedient to everything. No negative answers. You can’t use the words: “no”, “nope”, “never”, “nah”, “disagree”, “na”
		banned_words = ["no", "nope", "never", "nah", "disagree"]
		for word in banned_words:
			if word in message.lower().split(" "):
				broken.append("7")
				break

		# Rule 8. Don’t you dare deface us staff members. You’re not allowed to say the name of a staff member.
		banned_words = ["alley", "alleywr", "cause", "cause key", "dark", "dawthon", "epik", "anepik", "kitten", "kittenruler", "sinistershovel", "neonic", "neonicplasma", "thenamesh", "h", "purple", "purplegaze", "harrysoaps", "blandy", "trojan", "plasmictrojan"]
		for word in banned_words:
			if word in message.lower().split(" "):
				broken.append("8")
				break
		
		# Rule 9. You can’t have a character count that’s above 60 characters. Once again, the verbosity meta sucks.
		if 60 < len(message):
			broken.append("9")
		
		# Rule 10. You can’t use more than 9 vowels in your message.
		if c > 9:
			broken.append("10")
		
		print(broken)
		return broken
	

	# Function that runs on each message
	async def on_message(self, message):
		if message.author.id not in self.param["PLAYER_IDS"] or message.channel != self.param["MESSAGES"]:
			return # Filters for messages that are valid for the event

		# Resets the contestant's message timer (Rule 1)
		pl_index = self.param["PLAYER_IDS"].index(message.author.id)
		self.param["PLAYER_INFO"][pl_index][2] = time.time()

		# Runs rule_check to find any broken rules
		broken = self.rule_check(message, self.param["PLAYER_INFO"][pl_index][1])

		if len(broken) > 0:
			# Remove role, announce elimination, mark player as eliminated

			emojis = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟")
			
			await message.author.remove_roles(self.param["ROLE"])
			await self.param["LOGGING"].send(f"""<@{message.author.id}> has been eliminated for breaking
			Rule{'s' if len(broken) != 1 else ''} {grammar_list(broken)}.""".replace("\t", "").replace("\n", " "))

			for rule in broken:
				await message.add_reaction(emojis[int(rule) - 1])

			self.param["PLAYER_INFO"][pl_index][0] = 0
			self.param["PLAYER_IDS"][pl_index] = 0

		else:
			# Add message to the player's message history (Rule 2)
			self.param["PLAYER_INFO"][pl_index][1].append(message.content)
	

	# Function that runs every two seconds
	async def on_two_second(self):
		for player_info in self.param["PLAYER_INFO"]:
			pl_index = self.param["PLAYER_INFO"].index(player_info)

			# The two different cases of Rule 1
			if self.param["FINAL_5"]: t = 45
			else: t = 90

			if time.time() - player_info[2] > t: # If the player went too long without sending messages...
				# Remove role, announce elimination, mark player as eliminated
				await self.SERVER["MAIN"].get_member(player_info[0]).remove_roles(self.param["ROLE"])
				await self.param["LOGGING"].send(f"<@{player_info[0]}> has been eliminated for breaking Rule 1.")

				self.param["PLAYER_INFO"][pl_index][0] = 0
				self.param["PLAYER_IDS"][pl_index] = 0
			
		# If the final 5 has been reached
		if len([p for p in self.param["PLAYER_IDS"] if p != 0]) <= 5 and not self.param["FINAL_5"]:
			self.param["FINAL_5"] = True

			for p in self.param["PLAYER_INFO"]:
				p[2] = time.time()
			
			await self.param["LOGGING"].send("**Five players remain.** The threshold for Rule 1 is now multiplied by 0.5.")
		
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
	

	# Change a parameter of the event
	async def edit_event(self, message, new_params):
		incorrect = []
		correct = []
		for parameter in new_params.keys():
			try:
				self.param[parameter] == new_params[parameter]
				correct.append(parameter)
			except KeyError:
				incorrect.append(parameter)
		
		if len(correct) > 0:
			await message.channel.send(f"Successfully changed the parameters: {grammar_list(correct)}")
		if len(incorrect) > 0:
			await message.channel.send(f"The following parameters are invalid: {grammar_list(incorrect)}")
		
		return
