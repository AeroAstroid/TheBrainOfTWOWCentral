import time, discord, datetime
import numpy as np
from Config._functions import grammar_list
from Config._db import Database

UPDATES_MSG_ID = 913191494159044609
SIGNUPS_CHANNEL = "twows-in-signups"

class EVENT:
	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.param = {
			"TIME_ORDER": 1
		}


	# Executes when activated
	def start(self, SERVER): # Set the parameters
		self.RUNNING = True
		self.MESSAGES = []
		self.db = Database()
		self.SERVER = SERVER
		self.CHANNEL = ""
		self.ANNOUNCE = ""
	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.param = {
			"TIME_ORDER": 1
		}
		self.RUNNING = False

	# Exclusive to this event, updates the list of TWOWs in signups
	async def update_list(self, hour=False, announce=True, update_channel=False):
		msgs = [int(x) for x in self.db.get_entries("signupmessages")[0][0].split(" ")]
		self.CHANNEL = discord.utils.get(self.SERVER["MAIN"].channels, id=msgs[0])
		self.MESSAGES = [""] * (len(msgs) - 2)
		self.ANNOUNCE = ""

		async for msg in self.CHANNEL.history(limit=100):
			if msg.id in msgs:
				if msgs.index(msg.id) != len(msgs) - 1:
					self.MESSAGES[msgs.index(msg.id) - 1] = msg
				else:
					self.ANNOUNCE = msg
			
		self.CHANNEL = discord.utils.get(self.SERVER["MAIN"].channels, name=SIGNUPS_CHANNEL)
		self.ANNOUNCE = await self.CHANNEL.fetch_message(UPDATES_MSG_ID)
		
		twow_list = self.db.get_entries("signuptwows")
		twow_list = sorted(twow_list, key=lambda m: self.param["TIME_ORDER"] * m[4])

		for ind, twow in enumerate(twow_list):
			if twow[4] <= time.time():
				twow_list[ind] = ""
		
		twow_list = [x for x in twow_list if x != ""]

		self.db.remove_entry("signuptwows")
		for twow in twow_list:
			self.db.add_entry("signuptwows", list(twow))
		
		if announce:
			try:
				new_twow_names = list(zip(*twow_list))[0]
			except IndexError:
				new_twow_names = []
			old_twow_names = [
				x.content[x.content.find("📖  **__")+7 : x.content.find("__** - Hosted by")]
				for x in self.MESSAGES
				if x.content != "\u200b"
			]

			just_added = [x for x in new_twow_names if x not in old_twow_names]
			just_removed = [x for x in old_twow_names if x not in new_twow_names]

			new_announcement_list = []
			current_time_string = f"<t:{int(time.time())}:R>"
			for x in just_added:
				new_announcement_list.append(f"{current_time_string} : Added **{x}** to the signup list")
			for x in just_removed:
				new_announcement_list.append(f"{current_time_string} : Removed **{x}** from the signup list")
			
			if self.ANNOUNCE.content != "\u200b":

				old_announcement_list = self.ANNOUNCE.content.split("\n")[2:]

				if hour:

					for z in range(len(old_announcement_list)):
                        
						time_start = old_announcement_list[z].find("<t:") + 3
						time_end = old_announcement_list[z].find(":R>")
						announcement_time = datetime.datetime.utcfromtimestamp(
							int(old_announcement_list[z][time_start:time_end])
						)
						d_days = (datetime.datetime.now() - announcement_time).days

						if d_days >= 1:
							old_announcement_list[z] = ""
				
				old_announcement_list = [x for x in old_announcement_list if x != ""]

				if new_announcement_list != []:
					old_announcement_list += new_announcement_list

				announce_msg = f"__**Recent list changes:**__\n\n" + "\n".join(old_announcement_list)
				await self.ANNOUNCE.edit(content=announce_msg)
			
			else:
				announce_msg = f"__**Recent list changes:**__\n\n" + "\n".join(new_announcement_list)
				await self.ANNOUNCE.edit(content=announce_msg)
			
			for x in just_added:
				verif = twow_list[new_twow_names.index(x)][-1]
				if verif == 1:
					print("Pinging for featured TWOW!")
					msg = await self.CHANNEL.send("<@&488451010319220766> <@&723946317839073370>")
				else:
					msg = await self.CHANNEL.send("<@&723946317839073370>")
					print("Pinging for TWOW!")
				
				await msg.delete()

		formatted_list = []
		for twow in twow_list:
			time_left = twow[4] - time.time()

			signup_warning = ""
			time_emoji = "🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚"

			if time_left <= 0:
				t_l_string = "SIGNUPS ARE OVER!"
			else:
				t_l_string = f"<t:{twow[4]}:R>"

				day = int(np.ceil(time_left / 3600) / 24)
				if day == 0:
					signup_warning = "\n⏰  **SIGNUPS ARE ALMOST OVER! JOIN SOON!**"
			
			deadline_string = f"<t:{twow[4]}:f>"
			datetime_dl = datetime.datetime.utcfromtimestamp(twow[4])
			
			try:
				chosen_emoji = time_emoji[datetime_dl.hour % 12]
			except Exception:
				chosen_emoji = time_emoji[0]

			verified_string = ""
			if twow[5] > 0:
				verified_string = "\n⭐  **FEATURED TWOW!** (<@&488451010319220766>)"
			
			descrip = twow[3].replace('\n', '\n> ')
			
			message = f"""\u200b
			\u200b{verified_string}
			📖  **__{twow[0]}__** - Hosted by **{twow[1]}**
			> {descrip}
			{signup_warning}
			{chosen_emoji}  **Signup Deadline** : **{t_l_string}** ({deadline_string})
			📥  **Server Link** : {twow[2]}""".replace("\t", "")

			formatted_list.append(message)
		
		for t in range(len(self.MESSAGES)):
			if t < len(formatted_list):
				await self.MESSAGES[-t-1].edit(content=formatted_list[t])
			elif self.MESSAGES[-t-1].content != "\u200b":
				await self.MESSAGES[-t-1].edit(content="\u200b")


	# Function that runs every hour
	async def on_one_hour(self):
		await self.update_list(hour=True)
		
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
