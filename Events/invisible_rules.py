import os
import time
import discord as dc
import importlib

class EVENT:
	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.GAME_STARTED = False
		
		self.GAME = { # Game variables
			"ROUND": 0,

			"RULES": [],
			"RULE_DESC": [],

			"PLAYERS": [],

			"INSPECTING": [],
			"TESTING": [],
			"PLAYER_TESTS": [],

			"NEXT_PERIOD": 0
		}

		self.PLAYER_ROLE = None
		self.GAME_CHANNEL = None

		self.PARAM = { # Define all the parameters necessary
			"PLAYER_ROLE_ID": None,
			"GAME_CHANNEL_ID": None,
			"EVENT_ADMIN_ID": None,

			"ROUND_TIME": 540
		}
	
	def start(self, SERVER):
		self.RUNNING = True

		self.PARAM["PLAYER_ROLE_ID"] = 498254150044352514
		self.PARAM["GAME_CHANNEL_ID"] = 716131405503004765

		self.PARAM["EVENT_ADMIN_ID"] = 959155078844010546
		self.EVENT_ADMIN = dc.utils.get(SERVER["MAIN"].roles, id=self.PARAM["EVENT_ADMIN_ID"])

		self.SERVER = SERVER

	def end(self):
		self.RUNNING = False
		self.GAME_STARTED = False
		
		self.GAME = { # Game variables
			"ROUND": 0,

			"RULES": [],
			"RULE_DESC": [],

			"PLAYERS": [],

			"INSPECTING": [],
			"TESTING": [],
			"PLAYER_TESTS": [],

			"NEXT_PERIOD": 0
		}

		self.PLAYER_ROLE = None
		self.GAME_CHANNEL = None
	
	# Function that runs on each message
	async def on_message(self, message):
		msg = message.content

		if not self.GAME_STARTED:

			# Pre-game setup is limited solely to commands
			if not msg.lower().startswith("ir/"):
				return
			
			# Commands are limited solely to event administrators
			if message.author not in self.EVENT_ADMIN.members:
				return

			args = msg.split(" ")
			cmd = args[0][3:].lower()

			if cmd == "begin":
				player_role = dc.utils.get(self.SERVER["MAIN"].roles, id=int(self.PARAM["PLAYER_ROLE_ID"]))
				game_channel = dc.utils.get(self.SERVER["MAIN"].channels, id=int(self.PARAM["GAME_CHANNEL_ID"]))

				if player_role is None:
					await message.channel.send(
					"💀 **Can't start: PLAYER_ROLE_ID doesn't point to a valid role!**")
					return
				
				if game_channel is None:
					await message.channel.send(
					"💀 **Can't start: GAME_CHANNEL_ID doesn't point to a valid channel!**")
					return
				
				players = player_role.members

				if len(players) == 0:
					await message.channel.send("💀 **Can't start: the player role has no members!**")
					return
				
				rule_count = len(self.GAME["RULES"])
				
				if rule_count == 0:
					await message.channel.send("💀 **Can't start: no rules have been registered!**")
					return
				
				if len(args) == 1 or args[1].lower() != "confirm":
					current_params = "\n".join([f"**{k}**: {v}" for k, v in self.PARAM.items()])
					await message.channel.send(
					f"❓ **Do you wish to start the game?** Send `ir/begin confirm` to start!"
					+ "\n\n**Parameters:**\n{current_params}"
					+ f"\n\n**Players:** {players}\n**Rounds:** {rule_count}")
					return
				
				self.PLAYER_ROLE = player_role
				self.GAME_CHANNEL = game_channel
				self.GAME["PLAYERS"] = players
				self.GAME_STARTED = True

			if cmd == "modify": # Change parameters or view them
				if len(args) == 1:
					current_params = "\n".join([f"**{k}**: {v}" for k, v in self.PARAM.items()])
				
					await message.channel.send("📑 **Here are the current event parameters:**\n\n"
					+ current_params)
					return
				
				parameter = args[1].upper()

				if parameter not in self.PARAM.keys():
					await message.channel.send(
					"❌ **That parameter is not available for this event!**")
					return
				
				if len(args) == 2:
					await message.channel.send(
					f"💀 **You must include a new value for the {parameter} parameter!**")
					return
				
				value = " ".join(args[2:])
				old_value = self.PARAM[parameter]

				self.PARAM[parameter] = value

				await message.channel.send(
				f"✅ **Successfully edited {parameter}** from\n> `{old_value}`\nto\n> `{value}`")
				return
			
			if cmd == "setrules":
				if len(message.attachments) == 0:
					await message.channel.send(
					f"💀 **Send a file containing the rule scripts!**")
					return
				
				try:
					await message.attachments[0].save(f"{message.id}_IR_RULES.py")

					TEMP_IR_RULES = importlib.import_module(f"{message.id}_IR_RULES")

					rule_funcs = [attr for attr in dir(TEMP_IR_RULES) if not attr.startswith("__")]

					RULES = [getattr(TEMP_IR_RULES, func) for func in rule_funcs]
					RULE_DESC = [f.__doc__.strip() for f in RULES]

					os.remove(f"{message.id}_IR_RULES.py")

				except Exception as err:
					await message.channel.send(
					"💀 **An error occurred while importing the rules file!**")

					try: os.remove(f"{message.id}_IR_RULES.py")
					except Exception: pass

					raise err
				
				self.GAME["RULES"] = RULES
				self.GAME["RULE_DESC"] = RULE_DESC

				await message.channel.send(f"✅ **Successfully imported {len(RULES)} rules!**")
				return


				