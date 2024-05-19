import time, discord, traceback
from Config._functions import grammar_list

class EVENT:
	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.param = { # Define all the parameters necessary
			"CHANNEL": 481536866672443392
		}


	# Executes when activated
	def start(self, SERVER): # Set the parameters
		self.RUNNING = True

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.param = {
			"CHANNEL": 481536866672443392
		}
		self.RUNNING = False
	

	# Function that runs on each message
	async def on_message(self, message):
		if message.channel.id == self.param["CHANNEL"]:
			await message.add_reaction("🥶")
	

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
