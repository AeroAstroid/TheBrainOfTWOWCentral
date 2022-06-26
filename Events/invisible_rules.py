import os
from time import time
import discord as dc
import importlib
import numpy as np
import traceback

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

			"ELIMINATIONS": [],

			"NEXT_PERIOD": 0,
			"PERIOD_STEP": 0,
			"TIMER_MSGS": []
		}

		self.PLAYER_ROLE = None
		self.ANNOUNCE_CHANNEL = None
		self.GAME_CHANNEL = None

		self.PARAM = { # Define all the parameters necessary
			"PLAYER_ROLE_ID": None,
			"ANNOUNCE_CHANNEL_ID": None,
			"GAME_CHANNEL_ID": None,
			"EVENT_ADMIN_ID": None,

			"ROUND_TIME": 540
		}
	
	def start(self, SERVER):
		self.RUNNING = True

		self.PARAM["PLAYER_ROLE_ID"] = 498254150044352514
		self.PARAM["ANNOUNCE_CHANNEL_ID"] = 716131405503004765
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

			"ELIMINATIONS": [],

			"NEXT_PERIOD": 0,
			"PERIOD_STEP": 0,
			"TIMER_MSGS": []
		}

		self.PLAYER_ROLE = None
		self.ANNOUNCE_CHANNEL = None
		self.GAME_CHANNEL = None
	
	def make_timer(self, remaining):
		p = np.ceil((remaining / self.PARAM["ROUND_TIME"]) * 10)

		if p >= 7:
			emoji = "🟩" # Green square
		elif p >= 5:
			emoji = "🟨" # Yellow square
		elif p >= 3:
			emoji = "🟧" # Orange square
		else:
			emoji = "🟥" # Red square
		
		timer_bar = emoji * p + "⬛" * (10 - p)

		msg = f"{'⌛' if p % 2 == 0 else '⏳'} **The round ends <t:{self.GAME['NEXT_PERIOD']}:R>!**"

		return msg + "\n" + timer_bar


	# Function that runs every two seconds
	async def on_two_second(self):

		if not self.GAME_STARTED:
			return
		
		rnd = self.GAME["ROUND"]
		t = self.GAME["NEXT_PERIOD"]
		p_s = self.GAME["PERIOD_STEP"]

		if time() > t:

			if rnd == 0: # Event is starting now
				m, s = [self.PARAM["ROUND_TIME"] // 60, self.PARAM["ROUND_TIME"] % 60]
				m_str = f"{m} minute{'s' if m != 1 else ''}" + (f" {s} second{'s' if s != 1 else ''}" if s != 0 else "")

				msg_delay = 6
				msgs = [
					"> 🔍 **Welcome to Invisible Rules!**",

					(f"The first round is about to start. Each round lasts **{m_str}**."),

					(f"You will be able to send messages in <#{self.PARAM['GAME_CHANNEL_ID']}>, and I will "
					+ "tell you whether or not each message passes this round's current rule with a ✅ or ❌ reaction."),

					("Once you're confident you know the rule, DM me with **`ir/test`** - you will receive a test "
					+ "comprised of [N] messages, and you must tell which ones break the rule and which don't!"),

					("Starting the test is **final** - once you do it, you'll be locked from the inspection "
					+ "channel for the remainder of the round."),

					"If you fail the test, or fail to submit it within the round's time limit, you will be eliminated.",

					"> ⏳ Stand by! **Round 1** begins in **20 seconds**."
				]
				
				if p_s < len(msgs):
					await self.ANNOUNCE_CHANNEL.send(msgs[p_s])
					
					self.GAME["PERIOD_STEP"] += 1
				
					if self.GAME["PERIOD_STEP"] != len(msgs):
						self.GAME["NEXT_PERIOD"] = int(time() + msg_delay)
					else:
						self.GAME["NEXT_PERIOD"] = int(time() + 20)
						self.GAME["ROUND"] = -1
				
				return

			if rnd < 0: # Round -N means the intermission preceding round N
				self.GAME["NEXT_PERIOD"] = int(time() + self.PARAM["ROUND_TIME"])
				self.GAME["ROUND"] *= -1
				rnd *= -1
				self.GAME["PERIOD_STEP"] = 0

				self.GAME["INSPECTING"] = self.GAME["PLAYERS"]

				full_msg = (
				f"🔍 **Round {rnd}** of Invisible Rules has started!\n\n"
				+ f"Those with the <@{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by "
				+ f"sending messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.\n\n"
				+ self.make_timer(self.PARAM["ROUND_TIME"]))

				ann_timer = await self.ANNOUNCE_CHANNEL.send(full_msg)

				game_timer = await self.GAME_CHANNEL.send(
				f"🔍 **Round {rnd}**\n\n{self.make_timer(self.PARAM['ROUND_TIME'])}")

				self.GAME["TIMER_MSGS"] = [ann_timer, game_timer]

				for p in self.GAME["PLAYERS"]:
					player_timer = await p.send((
					f"🔍 **Round {rnd}**\n\n{self.make_timer(self.PARAM['ROUND_TIME'])}"
					+ "\n\nSend **`ir/test`** to stop inspecting the rule and access the test!"))

					self.GAME["TIMER_MSGS"].append(player_timer)
			
				return

			# NEXT_PERIOD being reached in a round means the round is over
			await self.ANNOUNCE_CHANNEL.send(f"🔍 **Round {rnd}** has **ended!**")

			self.GAME["INSPECTING"] = []
			self.GAME["TESTING"] = []
			self.GAME["PLAYER_TESTS"] = []

			self.GAME["ROUND"] += 1
			self.GAME["ROUND"] *= -1

			# debug line that ensures the next round doesn't start, will remove after I code the game ending
			self.GAME["NEXT_PERIOD"] = int(time() * 2)
			#self.GAME["NEXT_PERIOD"] = int(time() + 20)
			return
		
		elif rnd > 0: # If a round is currently running, update the timers in intervals of 10 seconds
			self.GAME["PERIOD_STEP"] += 1
			self.GAME["PERIOD_STEP"] %= 5

			if self.GAME["PERIOD_STEP"] == 4:

				# Edit the message in the announcing channel
				await self.GAME["TIMER_MSGS"][0].edit(content=(
				f"🔍 **Round {rnd}** of Invisible Rules has started!\n\n"
				+ f"Those with the <@{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by "
				+ f"sending messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.\n\n"
				+ self.make_timer(self.PARAM["ROUND_TIME"])))

				# Edit the message in the game channel
				await self.GAME["TIMER_MSGS"][1].edit(content=(
				f"🔍 **Round {self.GAME['ROUND']}**\n\n{self.make_timer(self.PARAM['ROUND_TIME'])}"))

				# Edit the timers in everyone's DMs
				for ind, p_timer in enumerate(self.GAME["TIMER_MSGS"][2:]):
					if self.GAME["PLAYERS"][ind] in self.GAME["INSPECTING"]:
						last_line = "\n\nSend **`ir/test`** to stop inspecting the rule and access the test!"
					else:
						last_line = "\n\nAnswer the entire test before the time runs out!"
					
					await p_timer.edit((
					f"🔍 **Round {self.GAME['ROUND']}**\n\n{self.make_timer(self.PARAM['ROUND_TIME'])}"
					+ last_line))
				
				return

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
				announce_channel = dc.utils.get(self.SERVER["MAIN"].channels, id=int(self.PARAM["ANNOUNCE_CHANNEL_ID"]))
				game_channel = dc.utils.get(self.SERVER["MAIN"].channels, id=int(self.PARAM["GAME_CHANNEL_ID"]))

				if player_role is None:
					await message.channel.send(
					"💀 **Can't start: PLAYER_ROLE_ID doesn't point to a valid role!**")
					return
				
				if announce_channel is None:
					await message.channel.send(
					"💀 **Can't start: ANNOUNCE_CHANNEL_ID doesn't point to a valid channel!**")
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
					+ f"\n\n**Parameters:**\n{current_params}"
					+ f"\n\n**Players:** {len(players)}\n**Rounds:** {rule_count}")
					return
				
				self.PLAYER_ROLE = player_role
				self.ANNOUNCE_CHANNEL = announce_channel
				self.GAME_CHANNEL = game_channel
				self.GAME["PLAYERS"] = players
				self.GAME_STARTED = True

				await message.channel.send("✅ **Invisible Rules is now starting.**")
				return

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
				old_type = type(self.PARAM[parameter])

				self.PARAM[parameter] = old_type(value)

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

		else: # Game functions
			rnd = self.GAME["ROUND"]

			if rnd <= 0: # Only check messages if there's a round running
				return
			
			if message.channel == self.GAME_CHANNEL and message.author in self.GAME["PLAYERS"]:
				rule = self.GAME["RULES"][rnd - 1]

				passed = "✅" if rule(msg) else "❌"

				await message.add_reaction(passed)

				return
			
			if isinstance(message.channel, dc.DMChannel) and message.author in self.GAME["PLAYERS"]:
				if msg.lower() == "ir/test" and message.author in self.GAME["INSPECTING"]:
					# TODO: Maybe add a confirmation here

					self.GAME["INSPECTING"].remove(message.author)
					self.GAME["TESTING"].append(message.author)
					# update ["PLAYER_TESTS"] with a test for this round
					# lock user from seeing GAME_CHANNEL

					await message.channel.send(f"📝 **Round {rnd} Rules Test!**")
					return
