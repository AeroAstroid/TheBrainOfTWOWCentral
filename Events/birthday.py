import discord
from Config._functions import grammar_list
from Config._const import DB_LINK
from datetime import datetime, timedelta
from Config._db import Database
from Config._servers import MAIN_SERVER

class EVENT:
	db = Database()

	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.param = { # Define all the parameters necessary
			"CHANNEL": "general"
		}


	# Executes when activated
	def start(self, SERVER): # Set the parameters
		self.SERVER = SERVER
		self.BIRTHDAY_ROLE = MAIN_SERVER["BIRTHDAY"]
		self.RUNNING = True

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.param = {
			"CHANNEL": "general",
		}
		self.RUNNING = False
	
	# Function that runs every hour
	async def on_one_hour(self):
		current_time = datetime.utcnow()
		hour = current_time.hour

		self.CHANNEL = discord.utils.get(self.SERVER["MAIN"].channels, name=self.param["CHANNEL"])

		day_change_tz = []
		for timezone in range(-12, 15): # For each timezone
			if (hour + timezone) % 24 == 0: # If the day just changed in this timezone
				tz_info = [timezone] # Timezone is the first element of the list

				tz_time = current_time + timedelta(hours=timezone)
				tz_info.append(f"{tz_time.day}/{tz_time.month}")
				tz_info.append(tz_time) # The day is the second element of the list
			
				day_change_tz.append(tz_info)

		print(day_change_tz)
		for tz in day_change_tz:
			l_d = tz[2] + timedelta(days=-1) # Get the last day in the timezone that just switched days
			n_d = tz[2] + timedelta(days=1)

			n_d = f"{n_d.day}/{n_d.month}"
			l_d = f"{l_d.day}/{l_d.month}"
			
			'''
			# All people whose birthdays were yesterday
			found = self.db.get_entries("birthday", columns=["id", "timezone"], conditions={"birthday": l_d})
			for person in found: # Cycle through all
				# person[1] < tz[0] checks if the timezone whose day just changed is greater than the person's timezone
				# since the day flips over in greater timezones first and then gradually smaller values, this checks
				# to see if the day has flipped over to the current day (tz[1]) in the person's timezone yet.
				# If person[1] < tz[0], it hasn't, and it's still l_d ("yesterday", tz[1] - 1 day) in their timezone,
				# so it's still their birthday.
				# the second boolean just checks if the person already has the birthday role. If they don't and the
				# first boolean is true, that means this person's birthday was missed, so correct that
				if person[1] < tz[0] and (self.BIRTHDAY_ROLE not in self.SERVER["MAIN"].get_member(int(person[0])).roles):
					f_tz = ("+" if person[1] > 0 else "") + str(person[1])
					await self.CHANNEL.send(
					f"""🎉 It's no longer midnight on **{l_d} UTC {f_tz}**, 
					but happy birthday to <@{person[0]}> regardless! 🎉""".replace("\n", "").replace("\t", "")
					)
					await self.SERVER["MAIN"].get_member(int(person[0])).add_roles(self.BIRTHDAY_ROLE)
			
			# All people whose birthdays are today
			found = self.db.get_entries("birthday", columns=["id", "timezone"], conditions={"birthday": tz[1]})
			for person in found: # Cycle through all
				# person[1] > tz[0] checks if the timezone whose day just changed is smaller than the person's timezone
				# since the day flips over in greater timezones first and then gradually smaller values, this checks
				# to see if the day has flipped over to the next day (tz[1] + 1 day) in the person's timezone yet.
				# If person[1] > tz[0], it hasn't, and it's still tz[1] (today) in their timezone, so it's still their
				# birthday. If person[1] == tz[0], that means it just became their birthday, and that's covered later.
				# the second boolean just checks if the person already has the birthday role. If they don't and the
				# first boolean is true, that means this person's birthday was missed, so correct that
				if person[1] > tz[0] and (self.BIRTHDAY_ROLE not in self.SERVER["MAIN"].get_member(int(person[0])).roles):
					f_tz = ("+" if person[1] > 0 else "") + str(person[1])
					await self.CHANNEL.send(
					f"""🎉 It's no longer midnight on **{tz[1]} UTC {f_tz}**, 
					but happy birthday to <@{person[0]}> regardless! 🎉""".replace("\n", "").replace("\t", "")
					)
					await self.SERVER["MAIN"].get_member(int(person[0])).add_roles(self.BIRTHDAY_ROLE)
			
			found = self.db.get_entries("birthday", columns=["id", "timezone"], conditions={"birthday": n_d})
			for person in found:
				# person[1] - 24 > tz[0] checks if the timezone whose day just changed is smaller enough than the
				# person's timezone such that there's a difference of two days between the timezone that just changed
				# and the person's. This checks to see if it's already n_d ("tomorrow", tz[1] + 1 day) somewhere and if
				# it's also at least 1 AM, so that it's possible we missed someone there.
				# If person[1] - 24 > tz[0], it is, and it's already n_d in their timezone, so it's already their
				# birthday. If person[1] == tz[0], that means it just became their birthday, and that's covered later.
				# the second boolean just checks if the person already has the birthday role. If they don't and the
				# first boolean is true, that means this person's birthday was missed, so correct that
				if person[1] - 24 > tz[0] and (self.BIRTHDAY_ROLE not in self.SERVER["MAIN"].get_member(int(person[0])).roles):
					f_tz = ("+" if person[1] > 0 else "") + str(person[1])
					await self.CHANNEL.send(
					f"""🎉 It's no longer midnight on **{n_d} UTC {f_tz}**, 
					but happy birthday to <@{person[0]}> regardless! 🎉""".replace("\n", "").replace("\t", "")
					)
					await self.SERVER["MAIN"].get_member(int(person[0])).add_roles(self.BIRTHDAY_ROLE)
			'''

			# Find members whose birthdays just ended in that timezone (one day ago, same timezone = exactly 24h ago)
			found = self.db.get_entries("birthday", columns=["id"], conditions={"birthday": l_d, "timezone": tz[0]})
			for member in found: # Remove their birthday role, as their birthday just ended
				await self.SERVER["MAIN"].get_member(int(member[0])).remove_roles(self.BIRTHDAY_ROLE)

			# Now, search for members whose birthday just started (today, in the day-changing timezone = it's midnight)
			found = self.db.get_entries("birthday", columns=["id"], conditions={"birthday": tz[1], "timezone": tz[0]})

			if len(found) == 0: # If there are none, return
				return
			
			# If there are members, cycle through each of them.
			for member in found:
				if self.BIRTHDAY_ROLE in self.SERVER["MAIN"].get_member(int(member[0])).roles:
					found[found.index(member)] = 0 # If they already have the birthday role, they're being counted
					continue # again, and this is a mistake. Change their id in found to 0 and continue

				# If they don't have the birthday role, give it to them
				await self.SERVER["MAIN"].get_member(int(member[0])).add_roles(self.BIRTHDAY_ROLE)

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
