import os
from time import time
import discord as dc
import importlib
import numpy as np

from Config._functions import m_line

def DEFAULT_PARAM():
	return { # Define all the parameters necessary
		"PLAYER_ROLE_ID": None,
		"ANNOUNCE_CHANNEL_ID": None,
		"GAME_CHANNEL_ID": None,
		"EVENT_ADMIN_ID": None,

		"PHASE_1_ROUND_TIME": 40,
		"PHASE_2_ROUND_TIME": 40,

		"PHASE_1_LEN": 5
	}

def DEFAULT_GAME():
	return { # Game variables
		"ROUND": 0,
		"PHASE": 1,

		"RULES": [],
		"RULE_DESC": [],

		"PLAYERS": [],

		"INSPECTING": [],
		"TESTING": [],
		"PLAYER_TESTS": [],

		"ELIMINATIONS": [],

		"NEXT_PERIOD": 0,
		"PERIOD_STEP": 0,
		"ROUND_RUNNING": False,
		"TRACKED_MSGS": []
	}

class EVENT:
	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.GAME_STARTED = False
		
		self.GAME = DEFAULT_GAME()

		self.PLAYER_ROLE = None
		self.ANNOUNCE_CHANNEL = None
		self.GAME_CHANNEL = None

		self.PARAM = DEFAULT_PARAM()
	
	def start(self, SERVER):
		self.RUNNING = True

		self.PARAM["PLAYER_ROLE_ID"] = 498254150044352514
		self.PARAM["ANNOUNCE_CHANNEL_ID"] = 716131405503004765
		self.PARAM["GAME_CHANNEL_ID"] = 990307784690135060

		self.PARAM["EVENT_ADMIN_ID"] = 959155078844010546
		self.EVENT_ADMIN = dc.utils.get(SERVER["MAIN"].roles, id=self.PARAM["EVENT_ADMIN_ID"])

		self.SERVER = SERVER

	def end(self):
		self.RUNNING = False
		self.GAME_STARTED = False
		
		self.GAME = DEFAULT_GAME()

		self.PLAYER_ROLE = None
		self.ANNOUNCE_CHANNEL = None
		self.GAME_CHANNEL = None
	
	def make_timer(self, remaining, just_timestamp=False):
		round_t = self.PARAM[f"PHASE_{self.GAME['PHASE']}_ROUND_TIME"]

		p = int(np.ceil((remaining / round_t) * 8))

		if p >= 7:
			emoji = ["🟩"] # Green square
		elif p >= 5:
			emoji = ["🟨"] # Yellow square
		elif p >= 3:
			emoji = ["🟧"] # Orange square
		else:
			emoji = ["🟥"] # Red square
		
		timer_bar = ["➡️"] + emoji * p + ["⬛"] * (8 - p)  + ["⬅️"]

		timer_bar = " ".join(timer_bar)

		if remaining != 0:
			msg = f"{'⌛' if p % 2 == 0 else '⏳'} **The round ends <t:{self.GAME['NEXT_PERIOD']}:R>!**"
		else:
			msg = "⌛ **The round has ended!**"
		
		if just_timestamp:
			return msg

		return msg + "\n\n" + timer_bar
	
	# Currently not fully implemented
	def generate_test_msg(self):
		return "sample test message"

	# Function that runs every two seconds
	async def on_two_second(self):

		if not self.GAME_STARTED:
			return
		
		# Within a period
		if time() <= self.GAME["NEXT_PERIOD"]:
			if self.GAME["ROUND_RUNNING"]:
				round_t = self.PARAM[f"PHASE_{self.GAME['PHASE']}_ROUND_TIME"]

				edit_delay = round_t / 32 # Amount of iterations (2s each) between timer edits

				if self.GAME["PERIOD_STEP"] % edit_delay < 1:
					await self.GAME["TRACKED_MSGS"][0].edit(content=m_line(
					f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!
					
					Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
					messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

					{self.make_timer(self.GAME["NEXT_PERIOD"] - time())}"""))

					await self.GAME["TRACKED_MSGS"][1].edit(content=m_line(
					f"""🔍 **Invisible Rules: Round {self.GAME["ROUND"]} (Phase {self.GAME['PHASE']})**

					{self.make_timer(self.GAME["NEXT_PERIOD"] - time())}"""))
				
				self.GAME["PERIOD_STEP"] += 1
			
			return
		
		if self.GAME["ROUND"] > 0: # Ending a round
			if self.GAME["ROUND_RUNNING"]:
				self.GAME["ROUND_RUNNING"] = False
				self.GAME["PERIOD_STEP"] = 0

			if self.GAME["PERIOD_STEP"] == -1:
				self.GAME["ROUND"] = -(self.GAME["ROUND"] + 1)
				return
			
			if self.GAME["PERIOD_STEP"] == 0:
				await self.ANNOUNCE_CHANNEL.send(f"🔍 **Round {self.GAME['ROUND']} has ended!**")
				await self.GAME_CHANNEL.send(f"🔍 **Round {self.GAME['ROUND']} has ended!**")

				# Ensures all players can't talk in the channel
				await self.GAME_CHANNEL.set_permissions(self.PLAYER_ROLE, send_messages=False)

				await self.GAME["TRACKED_MSGS"][0].edit(content=m_line(
				f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!
				
				Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
				messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

				{self.make_timer(0)}"""))

				await self.GAME["TRACKED_MSGS"][1].edit(content=m_line(
				f"""🔍 **Invisible Rules: Round {self.GAME["ROUND"]} (Phase {self.GAME['PHASE']})**
				
				{self.make_timer(0)}"""))

				for t_msg in self.GAME["TRACKED_MSGS"][2:]:
					await t_msg.edit(content=m_line(
					f"""🔍 **Invisible Rules: Round {self.GAME['ROUND']} (Phase {self.GAME['PHASE']})**
					
					{self.make_timer(0, just_timestamp=True)}"""))

					# Ensures the player can see the channel
					await self.GAME_CHANNEL.set_permissions(t_msg.channel.recipient, overwrite=None)

				self.GAME["INSPECTING"] = []
			
			if self.GAME["PERIOD_STEP"] == 3:
				await self.ANNOUNCE_CHANNEL.send("Results are as follows:")
			
			if self.GAME["PERIOD_STEP"] == 5:
				await self.ANNOUNCE_CHANNEL.send("trolled")
				# TODO: make it send actual results
				# TODO: perform eliminations
			
			if self.GAME["PERIOD_STEP"] == 9:
				new_round = self.GAME["ROUND"] + 1

				if new_round > len(self.GAME["RULES"]):
					await self.ANNOUNCE_CHANNEL.send("🔍 **Invisible Rules has finished!** Thank you for playing.")
					return False # End the event

				if self.GAME["ROUND"] != self.PARAM["PHASE_1_LEN"]:
					await self.ANNOUNCE_CHANNEL.send(f"🔍 **Stand by! Round {new_round} begins in 8 seconds!**") # 20
					self.GAME["PERIOD_STEP"] = -1
					self.GAME["NEXT_PERIOD"] = int(time() + 8) # 20
					self.GAME["ROUND"] = -new_round

				else:
					self.GAME["PHASE"] = 2
					self.GAME["ROUND"] = 0
					self.GAME["PERIOD_STEP"] = 0
				
				return
			
			self.GAME["PERIOD_STEP"] += 1
			return

		
		if self.GAME["ROUND"] < 0: # Ending an intermission between rounds
			round_t = self.PARAM[f"PHASE_{self.GAME['PHASE']}_ROUND_TIME"]

			self.GAME["ROUND"] *= -1

			self.GAME["INSPECTING"] = self.GAME["PLAYERS"].copy()
			self.GAME["TESTING"] = []
			self.GAME["PLAYER_TESTS"] = []

			# Control channel access here

			self.GAME["NEXT_PERIOD"] = int(time() + round_t)
			self.GAME["PERIOD_STEP"] = 0
			self.GAME["ROUND_RUNNING"] = True


			ann_timer = await self.ANNOUNCE_CHANNEL.send(m_line(
			f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!
			
			Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
			messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

			{self.make_timer(round_t)}"""))


			game_timer = await self.GAME_CHANNEL.send(m_line(
			f"""🔍 **Invisible Rules: Round {self.GAME["ROUND"]} (Phase {self.GAME['PHASE']})**
			
			{self.make_timer(round_t)}"""))

			await self.GAME_CHANNEL.set_permissions(self.PLAYER_ROLE, send_messages=True)

			self.GAME["TRACKED_MSGS"] = [ann_timer, game_timer]

			for p in self.GAME["PLAYERS"]:
				msg = await p.send(m_line(
				f"""🔍 **Invisible Rules: Round {self.GAME['ROUND']} (Phase {self.GAME['PHASE']})**
				
				{self.make_timer(round_t, just_timestamp=True)}
				
				Send **`ir/test`** to stop inspecting the rule and access the test!"""))

				self.GAME["TRACKED_MSGS"].append(msg)

			return

		if self.GAME["ROUND"] == 0: # Intermission between phases
			message_delay = 1 # 4 # Amount of iterations (2s each) between messages

			if self.GAME["PHASE"] == 1:
				m, s = [self.PARAM["PHASE_1_ROUND_TIME"] // 60, self.PARAM["PHASE_1_ROUND_TIME"] % 60]
				m_str = f"{m} minute{'s' if m != 1 else ''}" + (f" {s} second{'s' if s != 1 else ''}" if s != 0 else "")

				lines = [
					"🔍 **Welcome to Invisible Rules!**",

					"```diff\n+ PHASE ONE: Legal Forensics```",

					f"> For this phase, each round lasts **{m_str}**.",

					m_line("""> Once the round starts, everyone playing will be able to **INSPECT** the current 
					rule by sending messages in #rule-inspection. The bot will react to every message with a ✅ 
					**if it passes the rule**, or a ❌ **if it breaks the rule.** You may send as many messages 
					as you want. There is no penalty or reward for specifically sending messages that break or 
					pass the rule."""),

					m_line("""> A player who is confident they figured out the rule can **DM me with the command 
					`ir/test`** to stop INSPECTING and start **TESTING**. This command is **final** - you will be 
					locked out of #rule-inspection and cannot go back to INSPECTING for the remainder of the round.
					"""),

					m_line("""> Once they switch to **TESTING**, players will receive a **test** comprised of 10 
					messages. You must indicate, for each message, whether it PASSES or BREAKS the current rule. 
					You will be given no immediate feedback on whether or not your answers are correct.
					After doing so for all 10 messages, you will be **FINISHED** with the round."""),

					m_line(f"""> By the end of the round (**{m_str}**), anyone who didn't finish their test in time, 
					as well as **anyone who scored under a 9/10** on the test, will be **eliminated.**"""),

					m_line("""> The survivors will be ranked by how long they took to finish the round, and the 
					fastest ones will be given point bonuses."""),

					m_line(f"""> **PHASE ONE: Legal Forensics** will last for the first **{self.PARAM['PHASE_1_LEN']} 
					rounds** of the game.""")
				]
			
			elif self.GAME["PHASE"] == 2:
				m, s = [self.PARAM["PHASE_2_ROUND_TIME"] // 60, self.PARAM["PHASE_2_ROUND_TIME"] % 60]
				m_str = f"{m} minute{'s' if m != 1 else ''}" + (f" {s} second{'s' if s != 1 else ''}" if s != 0 else "")

				lines = [
					"🔍 **It's time for Phase Two!**",

					"```diff\n- PHASE TWO: Investigative Journalism```",

					m_line(f"""> For this phase, each round lasts **{m_str}**. Elimination, instead of being 
					**failure-based**, will now be **time-based**."""),

					m_line("""> The **INSPECTION** period will work the same as in PHASE ONE - you may send 
					as many messages as you want, and you'll be told whether or not they break the rule, 
					without any penalty."""),

					m_line("""> To start **TESTING**, DM me with **`ir/test`** as normal. In the PHASE TWO TEST, 
					you will be sequentially shown a series of messages, one by one, and must answer whether or not 
					they PASS or BREAK the current rule as they come."""),

					m_line("""> The test is considered to be passed once a player gives **SEVEN correct answers IN 
					A ROW**. Therefore, making a mistake will reset your correct answer count back to 0, and make 
					the test longer. You will be given no immediate feedback on whether or not your answers are 
					correct (that is, until you're notified that you passed the test)."""),

					m_line("""> However, for this PHASE, **you may go back to INSPECTING even after starting a 
					TEST** by DMing me with **`ir/inspect`**. You will be given access to #rule-inspection again 
					and will be allowed to read/send more messages."""),

					m_line("""> You can go back to TESTING using **`ir/test`** as usual. However, leaving the test 
					to go back to INSPECTION will also reset your correct answer streak back to 0."""),

					m_line("""> Players who didn't pass the test in time are automatically placed last (and are 
					counted as taking up elimination spots). Even if there are more non-completions than elimination 
					spots, all the players who didn't pass the test in time will be eliminated."""),

					"> The survivors who finished the fastest will, once again, be given point bonuses.",

					m_line("""> **PHASE TWO: Investigative Journalism** will last until there's one player standing. 
					If a round eliminates all players, the final rankings will be tiebroken by amount of points earned, 
					then by average time necessary to complete each round.""")
				]

			# Post the messages every [message_delay] iterations
			if self.GAME["PERIOD_STEP"] % message_delay == 0:
				ind = self.GAME["PERIOD_STEP"] // message_delay

				if ind >= len(lines):
					self.GAME["ROUND"] = -1 if self.GAME['PHASE'] == 1 else -(self.PARAM['PHASE_1_LEN']+1)
					self.GAME["NEXT_PERIOD"] = int(time() + 10) # 30
					self.GAME["PERIOD_STEP"] = 0

					await self.ANNOUNCE_CHANNEL.send(
					f"🔍 **Stand by! Phase {self.GAME['PHASE']} and Round {-self.GAME['ROUND']} begin in 10 seconds!**") # 30
					return
				
				await self.ANNOUNCE_CHANNEL.send(lines[ind])
			
			self.GAME["PERIOD_STEP"] += 1
			
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

			if not self.GAME["ROUND_RUNNING"]: # Only check messages if there's a round running
				return
			
			if message.channel == self.GAME_CHANNEL and message.author in self.GAME["INSPECTING"]:
			
				rule = self.GAME["RULES"][rnd - 1]

				passed = "✅" if rule(msg) else "❌"

				await message.add_reaction(passed)

				return

			if isinstance(message.channel, dc.DMChannel) and message.author in self.GAME["PLAYERS"]:
				if msg.lower() == "ir/test" and message.author in self.GAME["INSPECTING"]:

					self.GAME["INSPECTING"].remove(message.author)
					await self.GAME_CHANNEL.set_permissions(message.author, view_channel=False)

					if self.GAME["PHASE"] == 1:
						self.GAME["TESTING"].append(message.author)
						# TODO: update ["PLAYER_TESTS"] with a test for this round
						await message.channel.send(f"📝 **Round {rnd} Rules Test!**")
						# TODO: Send test
					
					else:
						if message.author not in self.GAME["TESTING"]:
							self.GAME["TESTING"].append(message.author)
							# TODO: update ["PLAYER_TESTS"] with a test for this round
							await message.channel.send(f"📝 **Round {rnd} Rules Test!**")
							# TODO: Send test

						# TODO: Edit test message to show test again

					return

				if (msg.lower() == "ir/inspect" and message.author in self.GAME["TESTING"]
				and message.author not in self.GAME["INSPECTING"]):
					if self.GAME["PHASE"] == 1:
						await message.channel.send("You can't go back to inspecting after starting the test!")
						return
					
					self.GAME["INSPECTING"].append(message.author)
					# TODO: update player's test to have a 0 streak
					await self.GAME_CHANNEL.set_permissions(message.author, overwrite=None)
					# TODO: allow player back into GAME_CHANNEL
					# TODO: edit test message to hide test

			return