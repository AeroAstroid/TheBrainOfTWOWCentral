import discord
from Config._functions import grammar_list
from Config._const import DB_LINK
from datetime import datetime, timedelta
from Config._db import Database

class EVENT:
	LOADED = False
	RUNNING = False

	CHANNEL = ""
	BIRTHDAY_ROLE = ""

	db = Database()

	param = { # Define all the parameters necessary
		"CHANNEL": "general"
	}


	# Executes when loaded
	def __init__(self):
		self.LOADED = True


	# Executes when activated
	def start(self, TWOW_CENTRAL, PARAMS): # Set the parameters
		self.BIRTHDAY_ROLE = discord.utils.get(TWOW_CENTRAL.roles, id=PARAMS["BIRTHDAY_ROLE"])
		self.RUNNING = True

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.param = {
			"CHANNEL": "general",
		}
		self.RUNNING = False
	
	# Function that runs every hour
	async def on_one_hour(self, TWOW_CENTRAL):
		current_time = datetime.utcnow()
		hour = current_time.hour

		self.CHANNEL = discord.utils.get(TWOW_CENTRAL.channels, name=self.param["CHANNEL"])

		day_change_tz = []
		for timezone in range(-12, 15): # For each timezone
			if (hour + timezone - 1) % 24 == 0: # If the day just changed in this timezone
				tz_info = [timezone] # Timezone is the first element of the list

				tz_time = current_time + timedelta(hours=timezone)
				tz_info.append(f"{tz_time.day}/{tz_time.month}")
				tz_info.append(tz_time) # The day is the second element of the list
			
				day_change_tz.append(tz_info)

		for tz in day_change_tz:
			l_d = tz[2] + timedelta(days=-1) # Get the last day in the timezone that just switched days
			l_d = f"{l_d.day}/{l_d.month}"

			# Find members whose birthdays just ended in that timezone
			found = self.db.get_entries("birthday", columns=["id"], conditions={"birthday": l_d, "timezone": tz[0]})
			for member in found: # Remove their birthday role
				await TWOW_CENTRAL.get_member(int(member[0])).remove_roles(self.BIRTHDAY_ROLE)

			# Now, search for members whose birthday just started
			found = self.db.get_entries("birthday", columns=["id"], conditions={"birthday": tz[1], "timezone": tz[0]})

			if len(found) == 0: # If there are none, return
				return
			
			# If there are members, cycle through each of them.
			for member in found:
				if self.BIRTHDAY_ROLE in TWOW_CENTRAL.get_member(int(member[0])).roles:
					found[found.index(member)] = 0 # If they already have the birthday role, they're being counted
					continue # again, and this is a mistake. Change their id in found to 0 and continue

				# If they don't have the birthday role, give it to them
				await TWOW_CENTRAL.get_member(int(member[0])).add_roles(self.BIRTHDAY_ROLE)

			found = [x for x in found if x != 0] # Remove those who already had their birthday counted to avoid
			# birthday ping repeats.

			if len(found) == 0:
				return # If nobody's birthday is supposed to be announced now, return
			
			# Specify the timezone the bot is covering in this message
			f_tz = ("+" if tz[0] > 0 else "") + str(tz[0])

			# Prepare pings for everyone having their birthday
			birthday_mentions = grammar_list([f"<@{x[0]}>" for x in found])

			await self.CHANNEL.send(f"🎉 It's now **{tz[1]} UTC {f_tz}**! Happy birthday to {birthday_mentions}! 🎉")
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
