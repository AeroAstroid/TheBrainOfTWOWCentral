import time, discord, datetime
import numpy as np
from Config._functions import grammar_list
from Config._db import Database

class EVENT:
	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.param = {}


	# Executes when activated
	def start(self, SERVER): # Set the parameters
		self.RUNNING = True
		self.MESSAGES = []
		self.db = Database()
		self.SERVER = SERVER
	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.param = {}
		self.RUNNING = False

	# Exclusive to this event, updates the list of TWOWs in signups
	async def update_list(self):
		if len(self.MESSAGES) == 0:
			msgs = [int(x) for x in self.db.get_entries("signupmessages")[0][0].split(" ")]
			channel = discord.utils.get(self.SERVER["MAIN"].channels, id=msgs[0])
			self.MESSAGES = [""] * (len(msgs) - 1)

			async for msg in channel.history(limit=100):
				if msg.id in msgs:
					self.MESSAGES[msgs.index(msg.id) - 1] = msg
		
		twow_list = self.db.get_entries("signuptwows")
		twow_list = sorted(twow_list, key=lambda m: m[4])

		formatted_list = []
		for twow in twow_list:
			time_left = twow[4] - time.time()

			signup_warning = ""
			time_emoji = "🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚"

			if time_left <= 0:
				t_l_string = "SIGNUPS ARE OVER!"
			else:
				abs_delta = [
					np.ceil(time_left / 3600), # Hours
					int(np.ceil(time_left / 3600) / 24)] # Days

				hr = int(abs_delta[0] % 24)
				dy = int(abs_delta[1])

				t_l_string = f"Less than"
				if dy != 0:
					t_l_string += f" {dy} day{'s' if dy!=1 else ''}"
				else:
					signup_warning = "\n⏰  **SIGNUPS ARE ALMOST OVER! JOIN SOON!**"
				if hr != 0:
					if dy != 0:
						t_l_string += ","
					
					t_l_string += f" {hr} hour{'s' if hr!=1 else ''}"
			
			datetime_dl = datetime.datetime.utcfromtimestamp(twow[4])
			deadline_string = datetime_dl.strftime("%B %d %Y %H:%M UTC")
			
			try:
				chosen_emoji = time_emoji[datetime_dl.hour % 12]
			except Exception:
				chosen_emoji = time_emoji[0]

			verified_string = ""
			if twow[5] > 0:
				verified_string = "\n⭐  **VERIFIED TWOW!**"
			
			message = f"""\u200b
			\u200b{verified_string}
			📖  **__{twow[0]}__** - Hosted by **{twow[1]}**
			> {twow[3]}
			{signup_warning}
			{chosen_emoji}  **Signup Deadline** : **{t_l_string}** `({deadline_string})`
			📥  **Server Link** : {twow[2]}""".replace("\t", "")

			formatted_list.append(message)
		
		for t in range(len(self.MESSAGES)):
			if t < len(formatted_list):
				await self.MESSAGES[-t-1].edit(content=formatted_list[t])
			elif self.MESSAGES[-t-1].content != "\u200b":
				await self.MESSAGES[-t-1].edit(content="\u200b")


	# Function that runs every hour
	async def on_one_hour(self):
		await self.update_list()
		
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