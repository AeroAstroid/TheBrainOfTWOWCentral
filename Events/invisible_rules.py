import os
from time import time
import discord as dc
import importlib
import numpy as np

from discord.ui import Button, View

from Config._functions import m_line

def DEFAULT_PARAM():
	return { # Define all the parameters necessary
		"PLAYER_ROLE_ID": None,
		"ANNOUNCE_CHANNEL_ID": None,
		"GAME_CHANNEL_ID": None,
		"EVENT_ADMIN_ID": None,

		"PHASE_1_ROUND_TIME": 420,
		"PHASE_2_ROUND_TIME": 420,

		"PHASE_1_LEN": 5,
		"PHASE_2_LEN": 6,
		"PHASE_1_TEST_LEN": 10,
		"PHASE_2_TEST_STREAK": 8
	}

def DEFAULT_GAME():
	return { # Game variables
		"ROUND": 0,
		"PHASE": 1,

		"RULES": [],
		"RULE_DESC": [],
		"TEST_GEN": None,

		"PLAYERS": [],

		"ALL_PLAYERS": [],
		"ALL_PLAYER_TCO_POINTS": [],
		"ALL_PLAYER_AVERAGE_TIME": [],

		"INSPECTING": [],
		"TESTING": [],
		"PLAYER_TESTS": [],

		"ELIMINATIONS": [],
		"ELIM_RATE": 0,
		"ELIM_AMOUNT": 0,
		"FINAL_RANKINGS": [],

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
		self.PARAM["ANNOUNCE_CHANNEL_ID"] = 994452515594702868
		self.PARAM["GAME_CHANNEL_ID"] = 990881801641807892
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
	def generate_test_msg(self, uid, rule):
		return self.GAME["TEST_GEN"].gen_test(uid, rule)

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
					elim_msg = m_line(f"""/nOut of **{len(self.GAME['PLAYERS'])}** players, 
					**{self.GAME['ELIM_AMOUNT']}** will be eliminated./n""")

					await self.GAME["TRACKED_MSGS"][0].edit(content=m_line(
					f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!
					{elim_msg if self.GAME["PHASE"] == 2 else ''}
					Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
					messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

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

				elim_msg = m_line(f"""/nOut of **{len(self.GAME['PLAYERS'])}** players, 
				**{self.GAME['ELIM_AMOUNT']}** will be eliminated./n""")
				
				await self.GAME["TRACKED_MSGS"][0].edit(content=m_line(
				f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!
				{elim_msg if self.GAME["PHASE"] == 2 else ''}
				Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
				messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

				{self.make_timer(0)}"""))

				for t_msg in self.GAME["TRACKED_MSGS"][1:]:
					try:
						await t_msg.edit(content=m_line(
						f"""🔍 **Invisible Rules: Round {self.GAME['ROUND']} (Phase {self.GAME['PHASE']})**
						
						{self.make_timer(0, just_timestamp=True)}"""))

						# Ensures the player can see the channel
						await self.GAME_CHANNEL.set_permissions(t_msg.channel.recipient, overwrite=None)
					except Exception:
						pass
				
				for test_msg_info in self.GAME["PLAYER_TESTS"]:
					if test_msg_info[5] == 0:
						await test_msg_info[4].edit(view=None, content=
						f"📝 **Round {self.GAME['ROUND']} Rules Test!**\nThe round has ended; you've run out of time!")

				self.GAME["INSPECTING"] = []
			
			if self.GAME["PERIOD_STEP"] == 3:
				await self.ANNOUNCE_CHANNEL.send(m_line(f"""
				The **Round {self.GAME['ROUND']} Rule** was:/n
				> **```{self.GAME['RULE_DESC'][self.GAME['ROUND']-1]}```**"""))
			
			if self.GAME["PERIOD_STEP"] == 5:
				await self.ANNOUNCE_CHANNEL.send("Test results are as follows:")
			
			if self.GAME["PERIOD_STEP"] == 7:
				results_list = [
					# Username, score, time, started test, survives, TCO points gained, avg round time
					[p, 0, 9999999, False, False, 0, 0]
					for p in self.GAME["PLAYERS"]
				]

				for ind, p in enumerate(results_list):
					if p[0] not in self.GAME["TESTING"]:
						continue
					
					p_ind = self.GAME["TESTING"].index(p[0])
					p_test = self.GAME["PLAYER_TESTS"][p_ind]

					results_list[ind][2] = p_test[5] if p_test[5] != 0 else 9999999
					results_list[ind][3] = True

					
					ap_ind = self.GAME["ALL_PLAYERS"].index(p[0])
					
						
					if p_test[5] != 0:
						if self.GAME["PHASE"] == 1:
							score = p_test[3].count(True)
							
							if score >= self.PARAM["PHASE_1_TEST_LEN"]-1:
								results_list[ind][4] = True
						else:
							score = len(p_test[3])
						
						results_list[ind][1] = score

					if self.GAME["ROUND"] > 1:
						self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][0] += results_list[ind][2]
						self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][1] += 1

						results_list[ind][6] = (self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][0]
							/ self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][1])
				
				results_list = sorted(results_list, key=lambda m: -m[1])
				results_list = sorted(results_list, key=lambda m: m[6])
				results_list = sorted(results_list, key=lambda m: m[2])
				results_list = sorted(results_list, key=lambda m: -int(m[3]))
				results_list = sorted(results_list, key=lambda m: -int(m[4]))

				result_msgs = [f"🏆 **Round {self.GAME['ROUND']} Results**\n\n"]
				p_len = len(results_list)
				survivors = 0

				# Do eliminations for phase 2 (slowest players)
				if self.GAME["PHASE"] == 2:
					for ind in range(len(results_list)):
						# Highest ranks get saved from elim (provided they did the test)
						if len(results_list) - ind > self.GAME["ELIM_AMOUNT"] and results_list[ind][2] < 9999999:
							results_list[ind][4] = True

				for ind, p in enumerate(results_list):
					elim_emoji = "✅" if p[4] or self.GAME["ROUND"] == 1 else "💀"

					p_line = f"`[{ind+1}]` {elim_emoji} <@{p[0].id}> --- "

					if not p[3]:
						p_line += "Did not start test\n"
					
					elif p[2] == 9999999:
						p_line += "Did not finish test\n"

					else:
						m, s = (int(p[2] // 60), int(p[2] % 60))
						m_str = f"{m}:{s:>02}"

						p_line += f"**Finished in {m_str}** /// "

						if self.GAME["PHASE"] == 1:
							p_line += f"{p[1]}/{self.PARAM['PHASE_1_TEST_LEN']} score"
						else:
							p_line += f"{p[1]} attempts"
						
						if p[4] and self.GAME["ROUND"] != 1:
							survivors += 1

							top_percent = survivors / p_len

							ap_ind = self.GAME["ALL_PLAYERS"].index(p[0])

							if survivors == 1:
								p_line += " ///  **+4 TCO points**"
								self.GAME["ALL_PLAYER_TCO_POINTS"][ap_ind] += 4
							elif top_percent <= 0.2:
								p_line += " ///  **+3 TCO points**"
								self.GAME["ALL_PLAYER_TCO_POINTS"][ap_ind] += 3
							elif top_percent <= 0.4:
								p_line += " ///  **+2 TCO points**"
								self.GAME["ALL_PLAYER_TCO_POINTS"][ap_ind] += 2
							elif top_percent <= 0.6:
								p_line += " ///  **+1 TCO point**"
								self.GAME["ALL_PLAYER_TCO_POINTS"][ap_ind] += 1
						
						p_line += "\n"

					if len(result_msgs[-1] + p_line) >= 1950:
						result_msgs.append("")
					
					result_msgs[-1] += p_line

				for msg in result_msgs:
					await self.ANNOUNCE_CHANNEL.send(msg)

				if self.GAME["ROUND"] > 1:
					self.GAME["ELIMINATIONS"] = [p[0] for p in results_list if not p[4]]
					self.GAME["FINAL_RANKINGS"] = self.GAME["ELIMINATIONS"] + self.GAME["FINAL_RANKINGS"]

					self.GAME["PLAYERS"] = [p for p in self.GAME["PLAYERS"] if p not in self.GAME["ELIMINATIONS"]]

					for e in self.GAME["ELIMINATIONS"]:
						try:
							await self.SERVER["MAIN"].get_member(e.id).remove_roles(self.PLAYER_ROLE)
						except Exception:
							continue
			
			if self.GAME["PERIOD_STEP"] == 19:
				new_round = self.GAME["ROUND"] + 1

				if len(self.GAME["PLAYERS"]) < 2:
					if len(self.GAME["PLAYERS"]) == 1:
						winner = self.GAME["PLAYERS"][0]
						self.GAME["FINAL_RANKINGS"] = [winner] + self.GAME["FINAL_RANKINGS"]

						await self.ANNOUNCE_CHANNEL.send(f"🔍 **The winner of Invisible Rules is <@{winner.id}>!**")
					
					else:
						winner = self.GAME["FINAL_RANKINGS"][0]

						await self.ANNOUNCE_CHANNEL.send(
						f"🔍 By an average completion time tiebreaker, **the winner of Invisible Rules is <@{winner.id}>!**")
					
					final_results = []

					for p in self.GAME["FINAL_RANKINGS"]:
						ap_ind = self.GAME["ALL_PLAYERS"].index(p)
						p_pts = self.GAME["ALL_PLAYER_TCO_POINTS"][ap_ind]
						
						try:
							p_avg = self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][0]/self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][1]
						except ZeroDivisionError:
							p_avg = 9999999
						
						final_results.append([p.name, p.id, p_pts, p_avg])

					final_results = "\n".join(["\t".join([str(r) for r in row]) for row in final_results])

					with open('IR_Results.txt', 'w', encoding='utf-8') as f:
						f.write(final_results)

					# Send a log of results in a staff channel
					await self.SERVER["MAIN"].get_channel(716131405503004765).send(file=dc.File('IR_Results.txt'))

					os.remove('IR_Results.txt')
					return False
				
				elif self.GAME["ROUND"] >= len(self.GAME["RULES"]):
					await self.ANNOUNCE_CHANNEL.send("Invisible Rules has finished!")
					final_results = []
					
					self.GAME["FINAL_RANKINGS"] = self.GAME["PLAYERS"] + self.GAME["FINAL_RANKINGS"]

					for p in self.GAME["FINAL_RANKINGS"]:
						ap_ind = self.GAME["ALL_PLAYERS"].index(p)
						p_pts = self.GAME["ALL_PLAYER_TCO_POINTS"][ap_ind]
						try:
							p_avg = self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][0]/self.GAME["ALL_PLAYER_AVERAGE_TIME"][ap_ind][1]
						except ZeroDivisionError:
							p_avg = 9999999
							
						final_results.append([p.name, p.id, p_pts, p_avg])

					final_results = "\n".join(["\t".join([str(r) for r in row]) for row in final_results])

					with open('IR_Results.txt', 'w', encoding='utf-8') as f:
						f.write(final_results)

					# Send a log of results in a staff channel
					await self.SERVER["MAIN"].get_channel(716131405503004765).send(file=dc.File('IR_Results.txt'))

					os.remove('IR_Results.txt')
					return False

				if self.GAME["ROUND"] != self.PARAM["PHASE_1_LEN"]:
					await self.ANNOUNCE_CHANNEL.send(f"🔍 **Stand by! Round {new_round} begins in 20 seconds!**")
					self.GAME["PERIOD_STEP"] = -1
					self.GAME["NEXT_PERIOD"] = int(time() + 20)
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

			self.GAME["TEST_GEN"].reset()

			self.GAME["ROUND"] *= -1

			self.GAME["INSPECTING"] = self.GAME["PLAYERS"].copy()
			self.GAME["TESTING"] = []
			self.GAME["PLAYER_TESTS"] = []

			self.GAME["ELIMINATIONS"] = []

			self.GAME["NEXT_PERIOD"] = int(time() + round_t)
			self.GAME["PERIOD_STEP"] = 0
			self.GAME["ROUND_RUNNING"] = True

			if self.GAME["PHASE"] == 2:
				if self.GAME["ROUND"] == self.PARAM["PHASE_1_LEN"] + self.PARAM["PHASE_2_LEN"]:
					# Finale
					self.GAME["ELIM_AMOUNT"] = len(self.GAME["PLAYERS"]) - 1
				else:
					# Ensure at least 1 player is eliminated
					self.GAME["ELIM_AMOUNT"] = max(1, int(round(len(self.GAME["PLAYERS"]) * self.GAME["ELIM_RATE"])))

			elim_msg = m_line(f"""/nOut of **{len(self.GAME['PLAYERS'])}** players, 
			**{self.GAME['ELIM_AMOUNT']}** will be eliminated./n""")
			
			ann_timer = await self.ANNOUNCE_CHANNEL.send(m_line(
			f"""🔍 **Round {self.GAME["ROUND"]}** of Invisible Rules has started!
			{elim_msg if self.GAME["PHASE"] == 2 else ''}
			Those with the <@&{self.PARAM['PLAYER_ROLE_ID']}> role can now inspect the current rule by sending 
			messages in <#{self.PARAM['GAME_CHANNEL_ID']}>.

			{self.make_timer(round_t)}"""))


			await self.GAME_CHANNEL.send(f"🔍 **Invisible Rules: Round {self.GAME['ROUND']} (Phase {self.GAME['PHASE']})**")

			await self.GAME_CHANNEL.set_permissions(self.PLAYER_ROLE, send_messages=True)

			self.GAME["TRACKED_MSGS"] = [ann_timer]

			for p in self.GAME["PLAYERS"]:
				try:
					msg = await p.send(m_line(
					f"""🔍 **Invisible Rules: Round {self.GAME['ROUND']} (Phase {self.GAME['PHASE']})**
					
					{self.make_timer(round_t, just_timestamp=True)}
					
					Send **`ir/test`** to stop inspecting the rule and access the test!"""))

					self.GAME["TRACKED_MSGS"].append(msg)
				except Exception:
					pass

			return

		if self.GAME["ROUND"] == 0: # Intermission between phases
			message_delay = 4 # Amount of iterations (2s each) between messages

			if self.GAME["PHASE"] == 1:
				m, s = [int(self.PARAM["PHASE_1_ROUND_TIME"] // 60), int(self.PARAM["PHASE_1_ROUND_TIME"] % 60)]
				m_str = f"{m} minute{'s' if m != 1 else ''}" + (f" {s} second{'s' if s != 1 else ''}" if s != 0 else "")

				lines = [
					"🔍 **Welcome to Invisible Rules!**",

					"```diff\n+ PHASE ONE: Legal Forensics```",

					f"> For this phase, each round lasts **{m_str}**.",

					m_line(f"""> Once the round starts, everyone playing will be able to **INSPECT** the current 
					rule by sending messages in <#{self.GAME_CHANNEL.id}>. The bot will react to every message 
					with a ✅ **if it passes the rule**, or a ❌ **if it breaks the rule.** You may send as many 
					messages as you want. There is no penalty or reward for specifically sending messages that 
					break or pass the rule."""),

					m_line(f"""> A player who is confident they figured out the rule can **DM me with the command 
					`ir/test`** to stop INSPECTING and start **TESTING**. This command is **final** - you will be 
					locked out of <#{self.GAME_CHANNEL.id}> and cannot go back to INSPECTING for the remainder of 
					the round."""),

					m_line(f"""> Once they switch to **TESTING**, players will receive a **test** comprised of 
					{self.PARAM['PHASE_1_TEST_LEN']} messages. You must indicate, for each message, whether it 
					PASSES or BREAKS the current rule. You will be given no immediate feedback on whether or not 
					your answers are correct. After doing so for all {self.PARAM['PHASE_1_TEST_LEN']} messages, 
					you will be **FINISHED** with the round."""),

					m_line(f"""> By the end of the round (**{m_str}**), anyone who didn't finish their test in time, 
					as well as **anyone who scored under a {self.PARAM['PHASE_1_TEST_LEN']-1}/
					{self.PARAM['PHASE_1_TEST_LEN']}** on the test, will be **eliminated.**"""),

					m_line("""> The survivors will be ranked by how long they took to finish the round, and the 
					fastest ones will be given point bonuses."""),

					m_line(f"""> **PHASE ONE: Legal Forensics** will last for the first **{self.PARAM['PHASE_1_LEN']} 
					rounds** of the game."""),
					
					m_line("""> **Round 1** will be a practice round to get everyone up to speed on the event - it 
					will not count for **eliminations**, **average completion time**, OR **TCO points**!""")
				]
			
			elif self.GAME["PHASE"] == 2:
				m, s = [self.PARAM["PHASE_2_ROUND_TIME"] // 60, self.PARAM["PHASE_2_ROUND_TIME"] % 60]
				m_str = f"{m} minute{'s' if m != 1 else ''}" + (f" {s} second{'s' if s != 1 else ''}" if s != 0 else "")

				self.GAME["ELIM_RATE"] = 1-(1/len(self.GAME["PLAYERS"]))**(1/(self.PARAM["PHASE_2_LEN"] + 0.5))

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

					m_line(f"""> The test is considered to be passed once a player gives 
					**{self.PARAM['PHASE_2_TEST_STREAK']} correct answers IN A ROW**. Therefore, making a mistake 
					will reset your correct answer count back to 0, and make the test longer. You will be given no 
					immediate feedback on whether or not your answers are correct (that is, until you're notified 
					that you passed the test). The test has 100 messages maximum. If it's not solved by then, it is 
					considered to be unfinished."""),

					m_line(f"""> However, for this PHASE, **you may go back to INSPECTING even after starting a 
					TEST** by DMing me with **`ir/inspect`**. You will be given access to <#{self.GAME_CHANNEL.id}> 
					again and will be allowed to read/send more messages."""),

					m_line("""> You can go back to TESTING using **`ir/test`** as usual. However, leaving the test 
					to go back to INSPECTION will also reset your correct answer streak back to 0."""),

					m_line("""> Players who didn't pass the test in time are automatically placed last (and are 
					counted as taking up elimination spots). Even if there are more non-completions than elimination 
					spots, all the players who didn't pass the test in time will be eliminated."""),

					"> The survivors who finished the fastest will, once again, be given point bonuses.",

					m_line(f"""> **PHASE TWO: Investigative Journalism** will last until there's one player standing. 
					This will happen in, at most, **{self.PARAM['PHASE_2_LEN']}** rounds. If a round eliminates all 
					players, the final rankings will be tiebroken by average time necessary to complete each round.""")
				]

			# Post the messages every [message_delay] iterations
			if self.GAME["PERIOD_STEP"] % message_delay == 0:
				ind = self.GAME["PERIOD_STEP"] // message_delay

				if ind >= len(lines):
					self.GAME["ROUND"] = -1 if self.GAME['PHASE'] == 1 else -(self.PARAM['PHASE_1_LEN']+1)
					self.GAME["NEXT_PERIOD"] = int(time() + 30)
					self.GAME["PERIOD_STEP"] = 0

					await self.ANNOUNCE_CHANNEL.send(
					f"🔍 **Stand by! Phase {self.GAME['PHASE']} and Round {-self.GAME['ROUND']} begin in 30 seconds!**")
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
				self.GAME["ALL_PLAYERS"] = players
				self.GAME["ALL_PLAYER_TCO_POINTS"] = [0] * len(players)

				self.GAME["ALL_PLAYER_AVERAGE_TIME"] = []
				# Prevent the arrays from being linked to one another
				for _ in range(len(players)): self.GAME["ALL_PLAYER_AVERAGE_TIME"].append([0, 0])

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
			
			if cmd == "settestgen":
				if len(message.attachments) == 0:
					await message.channel.send(
					f"💀 **Send a file containing the rule scripts!**")
					return
				
				try:
					await message.attachments[0].save(f"{message.id}_IR_TEST_GEN.py")

					TEMP_IR_TEST_GEN = importlib.import_module(f"{message.id}_IR_TEST_GEN")
					
					await message.channel.send("Generating test cases. This can take a few minutes.")
					
					TEST_GEN = TEMP_IR_TEST_GEN.TestGenerator()

					os.remove(f"{message.id}_IR_TEST_GEN.py")

				except Exception as err:
					await message.channel.send(
					"💀 **An error occurred while importing the rules file!**")

					try: os.remove(f"{message.id}_IR_TEST_GEN.py")
					except Exception: pass

					raise err
				
				self.GAME["TEST_GEN"] = TEST_GEN

				await message.channel.send(f"✅ **Successfully generated the test cases!**")
				return

		else: # Game functions
			rnd = self.GAME["ROUND"]

			if not self.GAME["ROUND_RUNNING"]: # Only check messages if there's a round running
				return
			
			if message.channel == self.GAME_CHANNEL and message.author in self.GAME["INSPECTING"]:
				
				not_allowed = [c for c in list(msg) if ord(c) > 127 and c not in "“”‘’"]
				not_allowed += [c for c in list(msg) if c in "_*~`\\\n"]
				
				if len(not_allowed) > 0:
					return
				
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
						
						test_msgs = []
						for _ in range(10):
							test_msgs.append(self.generate_test_msg(message.author.id, self.GAME["ROUND"]))
						
						answer_sheet = [self.GAME["RULES"][rnd - 1](msg) for msg in test_msgs]

						test_view = View()

						pass_button = Button(label="Passes the rule", style=dc.ButtonStyle.green,
						emoji="✅", custom_id=f"{message.author.id} 1")
						pass_button.callback = self.step_through_test
						test_view.add_item(pass_button)

						break_button = Button(label="Breaks the rule", style=dc.ButtonStyle.red,
						emoji="❌", custom_id=f"{message.author.id} 0")
						break_button.callback = self.step_through_test
						test_view.add_item(break_button)

						test_dm_msg = await message.channel.send(
						(f"📝 **Round {rnd} Rules Test!**\nAnswer all questions to finish the test!"
						+f"\n\n{self.format_test_msg(test_msgs[0], 1)}"),
						view=test_view)

						# UserID, messages, answer sheet, player's answers, msg obj, finish time
						self.GAME["PLAYER_TESTS"].append([message.author.id, test_msgs, 
						answer_sheet, [], test_dm_msg, 0])
					
					else:
						new_msg = self.generate_test_msg(message.author.id, self.GAME["ROUND"])
						new_answer = self.GAME["RULES"][rnd - 1](new_msg)

						test_view = View()

						pass_button = Button(label="Passes the rule", style=dc.ButtonStyle.green,
						emoji="✅", custom_id=f"{message.author.id} 1")
						pass_button.callback = self.step_through_test
						test_view.add_item(pass_button)

						break_button = Button(label="Breaks the rule", style=dc.ButtonStyle.red,
						emoji="❌", custom_id=f"{message.author.id} 0")
						break_button.callback = self.step_through_test
						test_view.add_item(break_button)
							
						n = 1

						if message.author in self.GAME["TESTING"]:
							u_ind = [
								ind for ind in range(len(self.GAME["PLAYER_TESTS"]))
								if self.GAME["PLAYER_TESTS"][ind][0] == int(message.author.id)
							]

							try:
								u_ind = u_ind[0]
							except IndexError:
								return

							self.GAME["PLAYER_TESTS"][u_ind][1].append(new_msg)
							self.GAME["PLAYER_TESTS"][u_ind][2].append(new_answer)

							n = len(self.GAME["PLAYER_TESTS"][u_ind][1])
						
						test_dm_msg = await message.channel.send((f"📝 **Round {rnd} Rules Test!**\n"
						+f"Answer {self.PARAM['PHASE_2_TEST_STREAK']} questions correctly in a row to finish the test!"
						+f"\n\n{self.format_test_msg(new_msg, n)}"),
						view=test_view)

						if message.author not in self.GAME["TESTING"]:
							self.GAME["TESTING"].append(message.author)

							# UserID, messages, answer sheet, player's answers, msg obj, finish time
							self.GAME["PLAYER_TESTS"].append([message.author.id, [new_msg], 
							[new_answer], [], test_dm_msg, 0])

						else:
							self.GAME["PLAYER_TESTS"][u_ind][4] = test_dm_msg

					return

				if (msg.lower() == "ir/inspect" and message.author in self.GAME["TESTING"]
				and message.author not in self.GAME["INSPECTING"]):
					if self.GAME["PHASE"] == 1:
						await message.channel.send("You can't go back to inspecting after starting the test!")
						return

					u_ind = [
						ind for ind in range(len(self.GAME["PLAYER_TESTS"]))
						if self.GAME["PLAYER_TESTS"][ind][0] == int(message.author.id)
					]

					try:
						u_ind = u_ind[0]
					except IndexError:
						return
					
					self.GAME["INSPECTING"].append(message.author)

					self.GAME["PLAYER_TESTS"][u_ind][3].append(False)

					await self.GAME_CHANNEL.set_permissions(message.author, overwrite=None)
					await self.GAME["PLAYER_TESTS"][u_ind][4].edit(content="**Test hidden!**", view=None)

					await message.channel.send(
					m_line(f"""You have gone back to **inspecting** this round's rule! The test has been hidden 
					from you.
					
					Use **`ir/test`** to stop inspecting and go back to testing. Once you return to the test, **the 
					last question and your correct answer streak will have reset.**
					
					You are now able to see and talk in <#{self.GAME_CHANNEL.id}> again."""))

			return
	
	def format_test_msg(self, msg, n=None):
		word_count = len(msg.split(" "))
		letter_list = [c for c in list(msg.upper()) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
		letters = len(letter_list)
		letters_used = sorted(list(set(letter_list)))

		info = ""
		if n is not None:
			if self.GAME["PHASE"] == 1:
				info = f"__**TEST - Message #{n}/{self.PARAM['PHASE_1_TEST_LEN']}**__\n"
			else:
				info = f"__**TEST - Message #{n}**__\n"
			
		info += m_line(f"""
			> **```{msg}```**/n
			> Characters: `{len(msg)}`/n
			> Words: `{word_count}`/n
			> Letter Count: `{letters}`/n
			> Letters Used: `{''.join(letters_used)}`
		""")

		return info

	async def step_through_test(self, ctx):
		if not self.GAME["ROUND_RUNNING"]:
			await ctx.response.defer()
			return
		
		user, answer = ctx.data['custom_id'].split(" ")

		for i in self.GAME["INSPECTING"]:
			if i.id == int(user):
				return

		user_test_ind = [
			ind for ind in range(len(self.GAME["PLAYER_TESTS"]))
			if self.GAME["PLAYER_TESTS"][ind][0] == int(user)
		]

		try:
			user_test_ind = user_test_ind[0]
		except IndexError:
			return
		
		n = len(self.GAME["PLAYER_TESTS"][user_test_ind][3])

		if int(answer) == int(self.GAME["PLAYER_TESTS"][user_test_ind][2][n]):
			self.GAME["PLAYER_TESTS"][user_test_ind][3].append(True)
		else:
			self.GAME["PLAYER_TESTS"][user_test_ind][3].append(False)
		
		n += 1

		rnd = self.GAME['ROUND']

		if self.GAME["PHASE"] == 1:
			if n < self.PARAM["PHASE_1_TEST_LEN"]:
				new_msg = self.GAME["PLAYER_TESTS"][user_test_ind][1][n]

				t_msg = (f"📝 **Round {rnd} Rules Test!**\nAnswer all questions to finish the test!"
				+f"\n\n{self.format_test_msg(new_msg, n+1)}")

				await ctx.response.edit_message(content=t_msg)
				return
			
			else:
				self.GAME["PLAYER_TESTS"][user_test_ind][5] = (
					self.PARAM["PHASE_1_ROUND_TIME"] - (self.GAME["NEXT_PERIOD"] - time()))
				
				m, s = (
					int(self.GAME["PLAYER_TESTS"][user_test_ind][5] // 60),
					int(self.GAME["PLAYER_TESTS"][user_test_ind][5] % 60)
				)

				m_str = f"{m} minute{'s' if m != 1 else ''} {s} second{'s' if s != 1 else ''}"

				t_msg = (m_line(
				f"""📝 You have finished **Round {rnd}** in **{m_str}**!

				Your test results will be revealed once the round ends."""))

				await ctx.response.edit_message(content=t_msg, view=None)
				return
		
		else:
			required = self.PARAM["PHASE_2_TEST_STREAK"]
			last_answers = self.GAME["PLAYER_TESTS"][user_test_ind][3][-required:]

			if False in last_answers or len(last_answers) < required:
				if n < 100:
					new_msg = self.generate_test_msg(int(user), rnd)

					self.GAME["PLAYER_TESTS"][user_test_ind][1].append(new_msg)

					self.GAME["PLAYER_TESTS"][user_test_ind][2].append(
						self.GAME["RULES"][rnd - 1](new_msg))

					t_msg = (f"📝 **Round {rnd} Rules Test!**\n"
					+f"Answer {required} questions correctly in a row to finish the test!"
					+f"\n\n{self.format_test_msg(new_msg, n+1)}")

					await ctx.response.edit_message(content=t_msg)
					
				else:
					t_msg = m_line(f"""📝 **Round {rnd} Rules Test!**
					
					**You have ran out of test messages (100) without being able to finish the test!**""")

					await ctx.response.edit_message(content=t_msg, view=None)

				return
			
			else:
				self.GAME["PLAYER_TESTS"][user_test_ind][5] = (
					self.PARAM["PHASE_2_ROUND_TIME"] - (self.GAME["NEXT_PERIOD"] - time()))
				
				m, s = (
					int(self.GAME["PLAYER_TESTS"][user_test_ind][5] // 60),
					int(self.GAME["PLAYER_TESTS"][user_test_ind][5] % 60)
				)

				m_str = f"{m} minute{'s' if m != 1 else ''} {s} second{'s' if s != 1 else ''}"

				t_msg = (m_line(
				f"""📝 You have finished **Round {rnd}** in **{m_str}**!

				Your last {required} answers were all correct. 
				It took you {len(self.GAME["PLAYER_TESTS"][user_test_ind][1])} attempts."""))

				await ctx.response.edit_message(content=t_msg, view=None)
				return
