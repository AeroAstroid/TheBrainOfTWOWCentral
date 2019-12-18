import discord
from Config._debug_const import MEMES

class EVENT:
	LOADED = False
	RUNNING = False

	CHANNEL = ""

	param = {
		"CYCLE": "éêèëĕẽ"
	}

	# Executes when loaded
	def __init__(self):
		self.LOADED = True


	# Executes when activated
	def start(self, TWOW_CENTRAL): # Set the parameters
		self.CHANNEL = discord.utils.get(TWOW_CENTRAL.channels, id=MEMES)
		self.RUNNING = True

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.RUNNING = False
	
	# Function that runs every hour
	async def on_two_second(self, TWOW_CENTRAL):
		current_diacritic = self.CHANNEL.name[3]
		new_index = (self.param["CYCLE"].find(current_diacritic) + 1) % 6
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
