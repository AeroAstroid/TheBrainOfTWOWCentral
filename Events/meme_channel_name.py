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
		self.CHANNEL = MAIN_SERVER["MEMES"]
		self.RUNNING = True

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.RUNNING = False
	
	# Function that runs every hour
	async def on_one_hour(self):
		current_diacritic = self.CHANNEL.name[3]
		new_index = (self.param["CYCLE"].find(current_diacritic) + 1) % len(self.param["CYCLE"])
		await self.CHANNEL.edit(name=f"mem{self.param['CYCLE'][new_index]}s")
		return

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
