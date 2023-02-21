import discord
from Config._servers import MAIN_SERVER

class EVENT:
	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.param = {
			"CYCLE": "éêèëĕẽēė"
		}

	# Executes when activated
	def start(self, SERVER): # Set the parameters
		self.SERVER = SERVER
		self.RUNNING = True

		self.param["MODMAIL_CATEGORY"] = discord.utils.get(SERVER["MAIN"].categories, name = "ModMail Logs")

	# Executes when deactivated
	def end(self): # Reset the parameters
		self.RUNNING = False
	
	# Function that runs on each message
	async def on_message(self, message):

		print("test")

		if self.param["MODMAIL_CATEGORY"] == None: return # Do not run if modmail category does not exist
		if message.channel == None: return # Do not run if message was not sent in channel

		if message.channel.category_id == self.param["MODMAIL_CATEGORY"].id:

			# Count amount of messages in channel
			count = 0
			async for _ in message.channel.history(limit=3):
				count += 1

			if count == 2:

				# Add reactions to message
				for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "❔"]:
					await message.add_reaction(emoji)

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
