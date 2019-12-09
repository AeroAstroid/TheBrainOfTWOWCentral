import discord
from Config._functions import grammar_list
from Config._const import DB_LINK
from datetime import datetime
import psycopg2
from psycopg2 import sql

class EVENT:
	LOADED = False
	RUNNING = False

	CHANNEL = ""

	param = { # Define all the parameters necessary
		"CHANNEL": "general"
	}


	# Executes when loaded
	def __init__(self):
		self.LOADED = True


	# Executes when activated
	def start(self, TWOW_CENTRAL): # Set the parameters
		self.RUNNING = True

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.param = {
			"CHANNEL": "general",
		}
		self.RUNNING = False
	
	# Function that runs every day
	async def on_one_day(self, TWOW_CENTRAL, CURRENT_DAY):
		current_date = f"{CURRENT_DAY}/{datetime.utcnow().month}"
		self.CHANNEL = discord.utils.get(TWOW_CENTRAL.channels, name=self.param["CHANNEL"])

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor() 

			cursor.execute(sql.SQL(""" SELECT id FROM "public.birthday" WHERE birthday = {birthday}""").format(
				birthday = sql.Literal(current_date)
			))
			found = cursor.fetchall()

			if found is None:
				return
			
			birthday_mentions = grammar_list([f"<@{x[0]}>" for x in found])

			await self.CHANNEL.send(f"🎉 It is now **{current_date}**. Happy birthday to {birthday_mentions}! 🎉")
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