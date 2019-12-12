import discord
from Config._functions import grammar_list
from Config._const import DB_LINK, BIRTHDAY_ROLE
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql

class EVENT:
	LOADED = False
	RUNNING = False

	CHANNEL = ""
	BIRTHDAY_ROLE = ""

	param = { # Define all the parameters necessary
		"CHANNEL": "general"
	}


	# Executes when loaded
	def __init__(self):
		self.LOADED = True


	# Executes when activated
	def start(self, TWOW_CENTRAL): # Set the parameters
		self.BIRTHDAY_ROLE = discord.utils.get(TWOW_CENTRAL.roles, id=BIRTHDAY_ROLE)
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

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			day_change_tz = []
			for timezone in range(-12, 15):
				if (hour + timezone) % 24 == 0:
					tz_info = [timezone]

					tz_time = current_time + timedelta(hours=timezone)
					tz_info.append(f"{tz_time.day}/{tz_time.month}")
					tz_info.append(tz_time)
				
					day_change_tz.append(tz_info)

			for tz in day_change_tz:
				l_d = tz[2] + timedelta(days=-1)
				l_d = f"{l_d.day}/{l_d.month}"

				cursor.execute(
				sql.SQL(""" SELECT id FROM "public.birthday" WHERE birthday = {last_day} AND timezone = {timezone}
				""").format(
					last_day = sql.Literal(l_d),
					timezone = sql.Literal(tz[0])
				))
				found = cursor.fetchall()

				for member in found:
					await TWOW_CENTRAL.get_member(int(member[0])).remove_roles(self.BIRTHDAY_ROLE)

				cursor.execute(
				sql.SQL(""" SELECT id FROM "public.birthday" WHERE birthday = {birthday} AND timezone = {timezone}
				""").format(
					birthday = sql.Literal(tz[1]),
					timezone = sql.Literal(tz[0])
				))
				found = cursor.fetchall()

				if len(found) == 0:
					return
				
				for member in found:
					if self.BIRTHDAY_ROLE in TWOW_CENTRAL.get_member(int(member[0])).roles:
						print(member[0])
						found[found.index(member)] = 0
						continue

					await TWOW_CENTRAL.get_member(int(member[0])).add_roles(self.BIRTHDAY_ROLE)

				print(found)
				found = [x for x in found if x != 0]
				print(found)

				if len(found) == 0:
					return
				
				f_tz = ("+" if tz[0] > 0 else "") + str(tz[0])
		
				birthday_mentions = grammar_list([f"<@{x[0]}>" for x in found])

				#await self.CHANNEL.send(f"🎉 It's now **{tz[1]} UTC {f_tz}**! Happy birthday to {birthday_mentions}! 🎉")
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
