import time, discord
from Config._const import MEMBER_ID

class EVENT:
	LOADED = False
	RUNNING = False

	MEMBER = 0 # Member role
	MUTED = 0 # Muted role
	LOGS = 0 #logs channel
	TWOW_CENTRAL = 0 # Server

	# Note: These are the rules that will get you muted by the raid protection system
	# 1. You cannot ping 5 or more people in 45 or less seconds.
	# 2. You cannot send 5 or more messages in 10 or less seconds.
	# 3. You cannot send 10 or more messages in 30 or less seconds.
	# Breaking any of these as a non-member gets you muted.

	param = { # Define all the parameters necessary 
		"PING_LIMIT": 5,
		"PING_TIME": 45,
		"MESSAGE_LIMIT": [5, 10],
		"MESSAGE_TIME": [10, 30],
		"INFO": {}
	}

	# Executes when loaded
	def __init__(self):
		self.LOADED = True
	

	# Executes when activated
	def start(self, TWOW_CENTRAL):
		self.TWOW_CENTRAL = TWOW_CENTRAL
		self.MEMBER = discord.utils.get(TWOW_CENTRAL.roles, id=MEMBER_ID)
		self.MUTED = discord.utils.get(TWOW_CENTRAL.roles, name="Mute")
		self.LOGS = discord.utils.get(TWOW_CENTRAL.channels, name="logs")
		self.RUNNING = True
	

	# Executes when deactivated
	def end(self):
		self.RUNNING = False
	

	# Function that runs on every message
	async def on_message(self, message, PERMS):
		if PERMS > 0:
			return # Only non-members are subject to raid detection

		# Make sure there's an entry for the non-member on the dict
		if message.author.id not in self.param["INFO"].keys():
			self.param["INFO"][message.author.id] = [[], []]
		
		self.param["INFO"][message.author.id][0].append(time.time())
	
		# Get total number of people pinged -- including in role pings
		mentioned = message.raw_mentions
		role_mentioned = []
		for role in message.role_mentions:
			role_mentioned += role.members
		mentioned += role_mentioned

		mention_count = len(set(mentioned))

		self.param["INFO"][message.author.id][1].append(mention_count)

		# Count messages in the last 10 and 30 seconds, as well as pings in the last 45
		msg_1 = len([x for x in self.param["INFO"][message.author.id][0] if time.time() - x < self.param["MESSAGE_TIME"][0]])
		msg_2 = len([x for x in self.param["INFO"][message.author.id][0] if time.time() - x < self.param["MESSAGE_TIME"][1]])
		msg_ping = len([x for x in self.param["INFO"][message.author.id][0] if time.time() - x < x < self.param["PING_TIME"]])
		ping = sum(self.param["INFO"][message.author.id][1][-msg_ping:])

		cause = "" # Determine the rule broken and specify it
		if msg_1 >= self.param["MESSAGE_LIMIT"][0] or msg_2 >= self.param["MESSAGE_LIMIT"][0]:
			cause = "sending messages too quickly"
		if ping >= self.param["PING_LIMIT"]:
			cause = "pinging too many people"
		
		if cause != "": # Mute the member
			try:
				if self.MUTED not in self.TWOW_CENTRAL.get_member(message.author.id).roles:
					await self.TWOW_CENTRAL.get_member(message.author.id).add_roles(self.MUTED)
					await self.LOGS.send(f"**Muted <@{message.author.id}> for {cause}.**")
			except AttributeError: # This happens when a webhook breaks the rules. Ignore that
				pass

		# Only the last 15 messages matter. This is because the maximum time the rules care about is 45 seconds
		# and any message rate above 1 per 3 seconds during more than 30 seconds will have already been muted
		if len(self.param["INFO"][message.author.id][0]) > 15:
			self.param["INFO"][message.author.id][0] = self.param["INFO"][message.author.id][0][-15:]
			self.param["INFO"][message.author.id][1] = self.param["INFO"][message.author.id][1][-15:]
	

	# Function that runs every two seconds
	async def on_two_second(self, TWOW_CENTRAL):
		keys = self.param["INFO"].keys()
		try:
			for person in keys:
				if time.time() - self.param["INFO"][person][0][-1] > 45:
					del self.param["INFO"][person]
		except RuntimeError:
			pass
			
		return True
	

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