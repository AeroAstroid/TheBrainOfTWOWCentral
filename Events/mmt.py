import time, discord, random, statistics
import numpy as np
from Config._functions import grammar_list, word_count, elim_prize
from Config._const import GAME_CHANNEL, PREFIX, ALPHABET, BRAIN

class EVENT:
	LOADED = False
	RUNNING = False

	TWOW_CENTRAL = 0 
	MMT_C = ""

	info = {
		"HOST_QUEUE": [],

		"PLAYERS": [],
		"RESPONSES": [],

		"SPECTATORS": [],
		"VOTES": {
			"ID": [],
			"RESP": [],
			"VOTE": []
		},

		"GAME": {
			"ROUND": 0,
			"PERIOD": 0,
			"PROMPT": "",
			"HOST": 0,
			"PERIOD_START": 0,
			"END_VOTES": [],
		}
	}

	param = { # Define all the parameters necessary
		"ELIM_RATE": 0.2,
		"R_DEADLINE": 180,
		"V_DEADLINE": 150,
		"Q_DEADLINE": 60,
		"S_DEADLINE": 180,
		"P_DEADLINE": 120
	}

	# Executes when loaded
	def __init__(self):
		self.LOADED = True


	# Executes when activated
	def start(self, TWOW_CENTRAL): # Set the parameters
		self.RUNNING = True
		self.TWOW_CENTRAL = TWOW_CENTRAL
		self.MMT_C = discord.utils.get(self.TWOW_CENTRAL.channels, id=GAME_CHANNEL)
		self.info["GAME"]["PERIOD_START"] = time.time()

	
	# Executes when deactivated
	def end(self): # Reset the parameters
		self.info = {
			"HOST_QUEUE": [],
			"PLAYERS": [],
			"SPECTATORS": [],
			"RESPONSES": [],
			"VOTES": {
				"ID": [],
				"RESP": [],
				"VOTE": []
			},
			"GAME": {
				"ROUND": 0,
				"PERIOD": 0,
				"PROMPT": "",
				"HOST": 0,
				"PERIOD_START": 0,
				"END_VOTES": [],
			}
		}
		self.RUNNING = False
	
	# [Event-exclusive] Ends the current MiniMiniTWOW, moving on to the next host in queue
	def force_skip(self):
		self.info["PLAYERS"] = []
		self.info["SPECTATORS"] = []
		self.info["RESPONSES"] = []
		self.info["VOTES"] = {
			"ID": [],
			"RESP": [],
			"VOTE": []
		}
		self.info["GAME"] = {
			"ROUND": 0,
			"PERIOD": 0,
			"PROMPT": "",
			"HOST": 0,
			"PERIOD_START": 0,
			"END_VOTES": [],
		}


	# Function that runs every two seconds
	async def on_two_second(self, TWOW_CENTRAL):
		if len(self.info["HOST_QUEUE"]) == 0 and self.info["GAME"]["HOST"] == 0:
			await self.MMT_C.send("🎩 There are no more people in queue to host a MiniMiniTWOW.")
			self.end()
			return
		
		if self.info["GAME"]["HOST"] == 0: # When there's no host, the queue moves on
			self.info["GAME"]["HOST"] = self.info["HOST_QUEUE"][0]
			self.info["HOST_QUEUE"] = self.info["HOST_QUEUE"][1:]

			await self.MMT_C.send(f"""🎩 <@{self.info["GAME"]["HOST"]}> is now up on the queue! Send 
			`{PREFIX}mmt create` to create a MiniMiniTWOW within the next {self.param["Q_DEADLINE"]} seconds, 
			or you'll be skipped from queue!""".replace("\n", "").replace("\t", ""))

			self.info["GAME"]["PERIOD_START"] = time.time()
			return
		
		if self.info["GAME"]["PERIOD"] == 0: # The host has to create the MiniMiniTWOW
			remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

			if remain in [self.param["Q_DEADLINE"] - 30, self.param["Q_DEADLINE"] - 31]:
				await self.MMT_C.send(f"""🎩 <@{self.info["GAME"]["HOST"]}>, you have 30 seconds to create the 
				MiniMiniTWOW with `{PREFIX}mmt create`. Do it, or you'll be skipped from queue!
				""".replace("\n", "").replace("\t", ""))

			if remain >= self.param["Q_DEADLINE"]:
				await self.MMT_C.send(f"""🎩 <@{self.info["GAME"]["HOST"]}> has been skipped for taking too long to 
				create the MiniMiniTWOW.""".replace("\n", "").replace("\t", ""))
				self.force_skip()

			return
		
		if self.info["GAME"]["PERIOD"] == 1: # The host has to start the MiniMiniTWOW
			if self.info["GAME"]["PERIOD_START"] != 0:
				remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

				if remain in [self.param["S_DEADLINE"] - 30, self.param["S_DEADLINE"] - 31]:
					await self.MMT_C.send(f"""🏁 <@{self.info["GAME"]["HOST"]}>, you have 30 seconds to end signups 
					start the MiniMiniTWOW with `{PREFIX}mmt start`. Do it, or you'll be skipped from queue!
					""".replace("\n", "").replace("\t", ""))
					return
				
				if remain >= self.param["S_DEADLINE"]:
					await self.MMT_C.send(f"""🏁 <@{self.info["GAME"]["HOST"]}> has been skipped for taking too long 
					to start the MiniMiniTWOW.""".replace("\n", "").replace("\t", ""))
					self.force_skip()
			
			return
		
		if self.info["GAME"]["PERIOD"] == 2: # The host has to pick a prompt for the MiniMiniTWOW
			remain = time.time() - self.info["GAME"]["PERIOD_START"]

			if remain < 2:
				self.info["GAME"]["ROUND"] += 1
				await self.MMT_C.send(f"""📰 <@{self.info["GAME"]["HOST"]}> has {self.param["P_DEADLINE"]} seconds 
				to decide on the Round {self.info["GAME"]["ROUND"]} Prompt by using `{PREFIX}mmt prompt`.
				""".replace("\n", "").replace("\t", ""))
				return

			if round(remain) in [self.param["P_DEADLINE"] - 30, self.param["P_DEADLINE"] - 31]:
				await self.MMT_C.send(f"""📰 <@{self.info["GAME"]["HOST"]}>, you have 30 seconds to decide on a prompt 
				with `{PREFIX}mmt prompt`. Do it, or you'll be skipped from queue!
				""".replace("\n", "").replace("\t", ""))
				return
			
			if remain >= self.param["P_DEADLINE"]:
				await self.MMT_C.send(f"""📰 <@{self.info["GAME"]["HOST"]}> has been skipped for taking too long 
				to write a prompt for the MiniMiniTWOW.""".replace("\n", "").replace("\t", ""))
				self.force_skip()
			
			return
		
		if self.info["GAME"]["PERIOD"] == 3: # The contestants have to submit to the MiniMiniTWOW
			remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

			if self.info["RESPONSES"].count("") == 0 and remain < self.param["R_DEADLINE"] - 15:
				await self.MMT_C.send("📝 Everyone has responded! Voting will begin in 15 seconds.")
				self.info["GAME"]["PERIOD_START"] += (time.time() - self.info["GAME"]["PERIOD_START"]
													 - self.param["R_DEADLINE"] + 15)

			if remain in [self.param["R_DEADLINE"] - 60, self.param["R_DEADLINE"] - 61]:
				for player in self.info["PLAYERS"]:
					ind = self.info["PLAYERS"].index(player)

					if self.info["RESPONSES"][ind] == "":
						await self.TWOW_CENTRAL.get_member(player).send(
						f"""📝 <@{player}>, you have 1 minute to submit to the current prompt!
						```{self.info["GAME"]["PROMPT"]}```
						If you don't respond, you'll be eliminated!""".replace("\n", "").replace("\t", ""))
			
			if remain >= self.param["R_DEADLINE"]:
				dnp_list = []
				for player in self.info["PLAYERS"]:
					ind = self.info["PLAYERS"].index(player)

					if self.info["RESPONSES"][ind] == "":
						dnp_list.append(player)
						self.info["PLAYERS"][ind] = ""
				
				self.info["PLAYERS"] = [x for x in self.info["PLAYERS"] if x != ""]
				self.info["RESPONSES"] = [x for x in self.info["RESPONSES"] if x != ""]

				dnp_list = [f"<@{x}>" for x in dnp_list]

				players = len(self.info["PLAYERS"])

				initial = f'📝 **Round {self.info["GAME"]["ROUND"]} Responding** is over!\n'

				if len(dnp_list) > 0:
					initial += f"""The following people did not respond: {grammar_list(dnp_list)}. We are down 
					to {players} player{'s' if players != 1 else ''}.""".replace("\n", "").replace("\t", "")
				else:
					initial += "Everyone responded."
				
				await self.MMT_C.send(initial)
				
				if players == 1:
					await self.MMT_C.send(f"""🏆 <@{self.info["PLAYERS"][0]}> wins the MiniMiniTWOW!""")
					self.force_skip()
					return
				
				if players == 0:
					await self.MMT_C.send(f"""🏆 Everyone is eliminated. The MiniMiniTWOW ends with no winner!""")
					self.force_skip()
					return
				
				self.info["GAME"]["PERIOD"] = 4

				self.info["VOTES"]["ID"] = []
				self.info["VOTES"]["RESP"] = []
				self.info["VOTES"]["VOTE"] = []

				for spec in self.info["SPECTATORS"]:
					screen = random.sample(self.info["RESPONSES"], min(8, len(self.info["RESPONSES"])))

					self.info["VOTES"]["ID"].append(spec)
					self.info["VOTES"]["RESP"].append(screen)
					self.info["VOTES"]["VOTE"].append("")

					message = f"""🗳️ **Round {self.info["GAME"]["ROUND"]} Voting**
					```{self.info["GAME"]["PROMPT"]}```
					Cast your vote on the entries below by using `{PREFIX}mmt vote` followed by the letters 
					of each response ordered from best to worst in your opinion. You have {self.param["V_DEADLINE"]} 
					seconds to vote!""".replace("\n", "").replace("\t", "")

					screen = "\n".join([
						f"""`({ALPHABET[screen.index(resp)]})` {resp} `({word_count(resp)} 
						word{'s' if word_count(resp) != 1 else ''})`""".replace("\n", "").replace("\t", "")
						for resp in screen
					])

					message += "\n" + screen
					
					await self.TWOW_CENTRAL.get_member(spec).send(message)
				
				self.info["GAME"]["PERIOD_START"] = time.time()

				await self.MMT_C.send(f"""🗳️ **Round {self.info["GAME"]["ROUND"]} Voting** has started! Spectators 
				have been sent the voting screens, and have {self.param["V_DEADLINE"]} seconds to vote.
				""".replace("\n", "").replace("\t", ""))
			
			return
		
		if self.info["GAME"]["PERIOD"] == 4:
			remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

			if self.info["VOTES"]["VOTE"].count("") == 0 and remain < self.param["V_DEADLINE"] - 10:
				await self.MMT_C.send("🗳️ Every spectator has voted! Voting ends in 10 seconds.")
				self.info["GAME"]["PERIOD_START"] += (time.time() - self.info["GAME"]["PERIOD_START"]
													 - self.param["V_DEADLINE"] + 10)

			if remain in [self.param["V_DEADLINE"] - 45, self.param["V_DEADLINE"] - 46]:
				await self.MMT_C.send("🗳️ 45 seconds left to vote! There are still spectators that haven't voted.")
			
			if remain >= self.param["V_DEADLINE"]:
				await self.MMT_C.send(f'🗳️ **Round {self.info["GAME"]["ROUND"]} Voting** is over!')

				leaderboard = []

				for r in range(len(self.info["RESPONSES"])):
					leaderboard.append([f'<@{self.info["PLAYERS"][r]}>', self.info["RESPONSES"][r], []])

				for vote in range(len(self.info["VOTES"]["VOTE"])):
					scores = self.info["VOTES"]["VOTE"][vote].split(" ")
					if len(scores) < 2:
						continue

					for s in range(len(scores)):
						resp = self.info["VOTES"]["RESP"][vote][s]
						score = float(scores[s])
						ind = self.info["RESPONSES"].index(resp)

						leaderboard[ind][2].append(score)
				
				for resp in leaderboard:
					try:
						mean = np.mean(resp[2])
					except:
						mean = "N/A"
					
					try:
						stdev = statistics.stdev(resp[2])
					except:
						stdev = "N/A"

					resp += [mean, stdev, len(resp[2])]
					del resp[2]
				
				leaderboard = sorted(leaderboard, key=lambda x: x[3])
				leaderboard = sorted(leaderboard, reverse=True, key=lambda x: x[2])

				post_leaderboard = [
				f"🏆 **Round {self.info['GAME']['ROUND']} Results**\nThe prompt: `{self.info['GAME']['PROMPT']}`.\n\n"]

				elim_pings = []
				elim_players = []

				for r in range(len(leaderboard)):
					if leaderboard[r][2] != "N/A":
						leaderboard[r][2] = "{:.2%}".format(leaderboard[r][2])
					if leaderboard[r][3] != "N/A":
						leaderboard[r][3] = "{:.2%}".format(leaderboard[r][3])
					leaderboard[r][4] = str(leaderboard[r][4]) + " vote" + "s" if leaderboard[r][4] != 1 else ""

					line = [f'[{r+1}]'] + leaderboard[r][:2] + [f'[{", ".join(leaderboard[r][2:])}]']

					elim = elim_prize(len(leaderboard))[0]
					emoji = "🟡" if r == 0 else ("🟢" if len(leaderboard) - r > elim else "🔴")

					line = emoji + " " + " - ".join(line) + "\n"

					if len(post_leaderboard[-1] + line) > 1950:
						post_leaderboard.append("")
					post_leaderboard[-1] += line

					if r == 0 or len(leaderboard) - r - 1 == elim or len(leaderboard) - r == 1:
						separator = f"`{'-' * 60}`\n"
						if len(post_leaderboard[-1] + separator) > 1950:
							post_leaderboard.append("")
						post_leaderboard[-1] += separator
					
					if emoji == "🔴":
						elim_pings.append(leaderboard[r][0])
						elim_players.append(int(leaderboard[r][0][2:-1]))
				
				for z in post_leaderboard:
					await self.MMT_C.send(z)
				
				await self.MMT_C.send(f"""❌ {grammar_list(elim_pings)} ha{'s' if len(elim_pings) == 1 else 've'} 
				been eliminated.""".replace("\n", "").replace("\t", ""))

				self.info["PLAYERS"] = [x for x in self.info["PLAYERS"] if x not in elim_players]

				if len(self.info["PLAYERS"]) == 1:
					await self.MMT_C.send(f"🏆 <@{self.info['PLAYERS'][0]}> wins the MiniMiniTWOW!")
					self.force_skip()
					return
				
				self.info["GAME"]["PERIOD"] = 2
				self.info["GAME"]["PERIOD_START"] = time.time()
				self.info["GAME"]["PROMPT"] = ""
				self.info["RESPONSES"] = [""] * len(self.info["PLAYERS"])
				return

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