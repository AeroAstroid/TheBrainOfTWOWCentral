import time, discord, random, statistics
import numpy as np
from Config._functions import grammar_list, word_count, elim_prize
from Config._const import ALPHABET, BRAIN, DB_LINK
from Config._db import Database

class EVENT:
	db = Database()

	# Executes when loaded
	def __init__(self):
		self.RUNNING = False
		self.info = {
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

		self.param = { # Define all the parameters necessary
			"ELIM_RATE": 0.2,
			"R_DEADLINE": 180,
			"V_DEADLINE": 150,
			"Q_DEADLINE": 60,
			"S_DEADLINE": 180,
			"P_DEADLINE": 120
		}


	# Executes when activated
	def start(self, SERVER): # Set the parameters
		self.RUNNING = True
		self.SERVER = SERVER
		self.PREFIX = SERVER["PREFIX"]
		self.MMT_C = SERVER["GAME_CHANNEL"]
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
	def force_skip(self): # Resets just about everything except the queue
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
	async def on_two_second(self):
		if len(self.info["HOST_QUEUE"]) == 0 and self.info["GAME"]["HOST"] == 0:
			await self.MMT_C.send("🎩 There are no more people in queue to host a MiniMiniTWOW.")
			self.end()
			return
		
		if self.info["GAME"]["HOST"] == 0: # When there's no host, the queue moves on
			self.info["GAME"]["HOST"] = self.info["HOST_QUEUE"][0] # Turn first person into host
			self.info["HOST_QUEUE"] = self.info["HOST_QUEUE"][1:] # Remove first person from queue

			await self.MMT_C.send(f"""🎩 <@{self.info["GAME"]["HOST"]}> is now up on the queue! Send 
			`{self.PREFIX}mmt create` to create a MiniMiniTWOW within the next {self.param["Q_DEADLINE"]} seconds, 
			or you'll be skipped from queue!""".replace("\n", "").replace("\t", ""))

			self.info["GAME"]["PERIOD_START"] = time.time() # Start the mmt create timer
			return
		
		if self.info["GAME"]["PERIOD"] == 0: # The host has to create the MiniMiniTWOW
			# How much time has passed since the start of the period
			remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

			# If there's around 30 seconds left to create the MMT
			if remain in [self.param["Q_DEADLINE"] - 30, self.param["Q_DEADLINE"] - 31]:
				await self.MMT_C.send(f"""🎩 <@{self.info["GAME"]["HOST"]}>, you have 30 seconds to create the 
				MiniMiniTWOW with `{self.PREFIX}mmt create`. Do it, or you'll be skipped from queue!
				""".replace("\n", "").replace("\t", ""))

			# If it's past the deadline
			if remain >= self.param["Q_DEADLINE"]:
				await self.MMT_C.send(f"""🎩 <@{self.info["GAME"]["HOST"]}> has been skipped for taking too long to 
				create the MiniMiniTWOW.""".replace("\n", "").replace("\t", ""))
				self.force_skip()

			return
		
		if self.info["GAME"]["PERIOD"] == 1: # The host has to start the MiniMiniTWOW
			if self.info["GAME"]["PERIOD_START"] != 0: # If it's 0, the two-player timer hasn't been triggered yet
				remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

				# If there's around 30 seconds left to start the MMT
				if remain in [self.param["S_DEADLINE"] - 30, self.param["S_DEADLINE"] - 31]:
					await self.MMT_C.send(f"""🏁 <@{self.info["GAME"]["HOST"]}>, you have 30 seconds to end signups 
					start the MiniMiniTWOW with `{self.PREFIX}mmt start`. Do it, or you'll be skipped from queue!
					""".replace("\n", "").replace("\t", ""))
					return
				
				# If it's past the deadline
				if remain >= self.param["S_DEADLINE"]:
					await self.MMT_C.send(f"""🏁 <@{self.info["GAME"]["HOST"]}> has been skipped for taking too long 
					to start the MiniMiniTWOW.""".replace("\n", "").replace("\t", ""))
					self.force_skip()
			
			return
		
		if self.info["GAME"]["PERIOD"] == 2: # The host has to pick a prompt for the MiniMiniTWOW
			remain = time.time() - self.info["GAME"]["PERIOD_START"]

			if remain < 1.95: # If the prompt decision period *just started*
				await self.MMT_C.send(f"""📰 <@{self.info["GAME"]["HOST"]}> has {self.param["P_DEADLINE"]} seconds 
				to decide on the Round {self.info["GAME"]["ROUND"]} Prompt by using `{self.PREFIX}mmt prompt`.
				""".replace("\n", "").replace("\t", ""))
				return

			# If there's around 30 seconds left to decide the prompt
			if round(remain) in [self.param["P_DEADLINE"] - 30, self.param["P_DEADLINE"] - 31]:
				await self.MMT_C.send(f"""📰 <@{self.info["GAME"]["HOST"]}>, you have 30 seconds to decide on a prompt 
				with `{self.PREFIX}mmt prompt`. Do it, or you'll be skipped from queue!
				""".replace("\n", "").replace("\t", ""))
				return

			# If it's past the deadline
			if remain >= self.param["P_DEADLINE"]:
				await self.MMT_C.send(f"""📰 <@{self.info["GAME"]["HOST"]}> has been skipped for taking too long 
				to write a prompt for the MiniMiniTWOW.""".replace("\n", "").replace("\t", ""))
				self.force_skip()
			
			return
		
		if self.info["GAME"]["PERIOD"] == 3: # The contestants have to submit to the MiniMiniTWOW
			remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

			# If everyone submitted, and the deadline *can* be shortened to 15 seconds
			if self.info["RESPONSES"].count("") == 0 and remain < self.param["R_DEADLINE"] - 15:
				await self.MMT_C.send("📝 Everyone has responded! Voting will begin in 15 seconds.")
				self.info["GAME"]["PERIOD_START"] += (time.time() - self.info["GAME"]["PERIOD_START"]
													 - self.param["R_DEADLINE"] + 15)

			# If there's around 60 seconds left to respond
			if remain in [self.param["R_DEADLINE"] - 60, self.param["R_DEADLINE"] - 61]:
				for player in self.info["PLAYERS"]:
					ind = self.info["PLAYERS"].index(player)

					if self.info["RESPONSES"][ind] == "":
						try:
							await self.SERVER["MAIN"].get_member(player).send(
							f"""📝 <@{player}>, you have 1 minute to submit to the current prompt!
							```{self.info["GAME"]["PROMPT"]}```
							If you don't respond, you'll be eliminated!""".replace("\n", "").replace("\t", ""))
						except Exception:
							pass
			
			# If it's past the deadline
			if remain >= self.param["R_DEADLINE"]:
				dnr_list = [] # Make a list of contestants who DNRd
				for player in self.info["PLAYERS"]:
					ind = self.info["PLAYERS"].index(player)

					if self.info["RESPONSES"][ind] == "":
						dnr_list.append(player)
						self.info["PLAYERS"][ind] = ""
				
				# Remove DNRers
				self.info["PLAYERS"] = [x for x in self.info["PLAYERS"] if x != ""]
				self.info["RESPONSES"] = [x for x in self.info["RESPONSES"] if x != ""]

				# Format the DNR list with pings
				dnr_list = [f"<@{x}>" for x in dnr_list]

				players = len(self.info["PLAYERS"]) # Report the new number of players

				initial = f'📝 **Round {self.info["GAME"]["ROUND"]} Responding** is over!\n'

				# Specify whether or not anyone DNRd
				if len(dnr_list) > 0:
					initial += f"""The following people did not respond: {grammar_list(dnr_list)}. We are down 
					to {players} player{'s' if players != 1 else ''}.""".replace("\n", "").replace("\t", "")
				else:
					initial += "Everyone responded."
				
				await self.MMT_C.send(initial)
				
				if players == 1: # If only one person remains, they win
					winner = self.info["PLAYERS"][0]
					await self.MMT_C.send(f"""🏆 <@{winner}> wins the MiniMiniTWOW!""")

					# Update database, increment their win count

					# Search for them in the mmtstats table
					found = self.db.get_entries("mmtstats", columns=["id"], conditions={"id": str(winner)})

					if len(found) == 0: # If they're not in the mmtstats table, add them
						self.db.add_entry("mmtstats", entry=[winner, "", 1])
					else: # Increment their win count in mmtstats
						wins = self.db.get_entries("mmtstats", columns=["wins"], conditions={"id": str(winner)})[0][0]
						self.db.edit_entry("mmtstats", entry={"wins": wins + 1}, conditions={"id": str(winner)})
						
					self.force_skip()
					return
				
				if players == 0: # If everyone DNRd
					await self.MMT_C.send(f"""🏆 Everyone is eliminated. The MiniMiniTWOW ends with no winner!""")
					self.force_skip()
					return
				
				# Switch to voting period
				self.info["GAME"]["PERIOD"] = 4

				# Prepare the voting arrays
				self.info["VOTES"]["ID"] = []
				self.info["VOTES"]["RESP"] = []
				self.info["VOTES"]["VOTE"] = []

				for spec in self.info["SPECTATORS"]:
					# Generate a random list of all or 8 of the responses as the screen
					if spec not in self.info["PLAYERS"]:
						screen = random.sample(self.info["RESPONSES"], min(8, len(self.info["RESPONSES"])))
					else: # If the voter is alive, the screen must contain the voter's response
						ind = self.info["PLAYERS"].index(spec)
						player_response = self.info["RESPONSES"][ind] # This is the response that the voter submitted
						other_responses = [resp for resp in self.info["RESPONSES"] if resp != player_response]
						screen = [player_response] + random.sample(other_responses, min(7, len(other_responses)))
						random.shuffle(screen) # So that the player's response isn't always A

					# Add the voter and the screen to the vote arrays
					self.info["VOTES"]["ID"].append(spec)
					self.info["VOTES"]["RESP"].append(screen)
					self.info["VOTES"]["VOTE"].append("")

					message = f"""🗳️ **Round {self.info["GAME"]["ROUND"]} Voting**
					```{self.info["GAME"]["PROMPT"]}```
					Cast your vote on the entries below by using `{self.PREFIX}mmt vote` followed by the letters 
					of each response ordered from best to worst in your opinion. You have {self.param["V_DEADLINE"]} 
					seconds to vote!""".replace("\n", "").replace("\t", "")

					# Format the screen properly
					screen = "\n".join([
						f"""`({ALPHABET[screen.index(resp)]})` {resp} `({word_count(resp)} 
						word{'s' if word_count(resp) != 1 else ''})`""".replace("\n", "").replace("\t", "")
						for resp in screen
					])

					message += "\n" + screen
					
					try: # Try to send the screen to the member
						await self.SERVER["MAIN"].get_member(spec).send(message)
					except Exception: # If you can't, skip them
						pass
				
				# Start the voting timer and announce voting
				self.info["GAME"]["PERIOD_START"] = time.time()
				await self.MMT_C.send(f"""🗳️ **Round {self.info["GAME"]["ROUND"]} Voting** has started! Spectators 
				have been sent the voting screens, and have {self.param["V_DEADLINE"]} seconds to vote.
				""".replace("\n", "").replace("\t", ""))
			
			return
		
		if self.info["GAME"]["PERIOD"] == 4: # The spectators have to vote
			remain = round(time.time() - self.info["GAME"]["PERIOD_START"])

			# If every spectator voted and the deadline *can* be shortened to 10 seconds
			if self.info["VOTES"]["VOTE"].count("") == 0 and remain < self.param["V_DEADLINE"] - 10:
				await self.MMT_C.send("🗳️ Every spectator has voted! Voting ends in 10 seconds.")
				self.info["GAME"]["PERIOD_START"] += (time.time() - self.info["GAME"]["PERIOD_START"]
													 - self.param["V_DEADLINE"] + 10)

			# If around 45 seconds remain to vote
			if remain in [self.param["V_DEADLINE"] - 45, self.param["V_DEADLINE"] - 46]:
				await self.MMT_C.send("🗳️ 45 seconds left to vote! There are still spectators that haven't voted.")
			
			# If it's past the deadline
			if remain >= self.param["V_DEADLINE"]:
				await self.MMT_C.send(f'🗳️ **Round {self.info["GAME"]["ROUND"]} Voting** is over!')

				# Prepare the leaderboard
				leaderboard = []

				# Add the first two columns of the leaderboard (player ping and their response), plus an array
				# for vote placements, used for calculation
				for r in range(len(self.info["RESPONSES"])):
					leaderboard.append([f'<@{self.info["PLAYERS"][r]}>', self.info["RESPONSES"][r], []])

				for vote in range(len(self.info["VOTES"]["VOTE"])): # For each vote...
					scores = self.info["VOTES"]["VOTE"][vote].split(" ") # Separate the scores
					responses = self.info["VOTES"]["RESP"][vote] # And the responses those scores correspond to

					if len(scores) < 2: # Detects placeholder vote strings (spectators that didn't vote)
						continue # Skips the vote

					for s in range(len(scores)): # For each score...
						resp = responses[s] # Identify the response
						score = float(scores[s]) # Convert score to float
						ind = self.info["RESPONSES"].index(resp) # Find the response's index on the response list

						leaderboard[ind][2].append(score) # Add the score to the response on the leaderboard
						# The response list indices and the leaderboard indices will coincide
				
				for resp in leaderboard:
					try: # Try to calculate the average
						mean = np.mean(resp[2])
					except:
						mean = "N/A"
					
					try: # Try to calculate the stdev
						stdev = statistics.stdev(resp[2])
					except:
						stdev = "N/A"

					# Add average, stdev and vote count to the leaderboard
					resp += [mean, stdev, len(resp[2])]
					del resp[2] # Delete the raw vote column
				
				leaderboard = sorted(leaderboard, key=lambda x: x[3]) # Sort by stdev ascending
				leaderboard = sorted(leaderboard, reverse=True, key=lambda x: x[2]) # Sort by score descending

				# Array for splitting up the message, yada yada
				post_leaderboard = [
				f"🏆 **Round {self.info['GAME']['ROUND']} Results**\nThe prompt: `{self.info['GAME']['PROMPT']}`.\n\n"]

				# Useful arrays to deal with eliminations and ranks
				elim_pings = []
				elim_players = []
				player_ranks = [""] * len(self.info["PLAYERS"])

				for r in range(len(leaderboard)):
					player = int(leaderboard[r][0][2:-1]) # Get their id
					# Add their placement to player_ranks, which will later be added to the database
					player_ranks[self.info["PLAYERS"].index(player)] = f"{r+1}/{len(leaderboard)}"

					if leaderboard[r][2] != "N/A": # If average is a number, turn it into a percentile
						leaderboard[r][2] = "{:.2%}".format(leaderboard[r][2])
					if leaderboard[r][3] != "N/A": # If stdev is a number, turn it into a percentile
						leaderboard[r][3] = "{:.2%}".format(leaderboard[r][3])
					# Format the vote count and add proper grammar
					leaderboard[r][4] = str(leaderboard[r][4]) + " vote" + "s" if leaderboard[r][4] != 1 else ""

					# Add brackets where necessary
					line = [f'[{r+1}]'] + leaderboard[r][:2] + [f'[{", ".join(leaderboard[r][2:])}]']

					# Determine the amount of contestants eliminated
					elim = elim_prize(len(leaderboard), elim_rate=self.param["ELIM_RATE"])[0]
					# Determine which circle emoji to use, based on if contestant is eliminated or not
					emoji = "🟡" if r == 0 else ("🟢" if len(leaderboard) - r > elim else "🔴")

					line = emoji + " " + " - ".join(line) + "\n" # Join the leaderboard line together with separators

					if len(post_leaderboard[-1] + line) > 1950: # Split into multiple messages if necessary
						post_leaderboard.append("")
					post_leaderboard[-1] += line

					# Add separators on boundaries of win, safe and elim regions
					if r == 0 or len(leaderboard) - r - 1 == elim or len(leaderboard) - r == 1:
						separator = f"`{'-' * 60}`\n"
						if len(post_leaderboard[-1] + separator) > 1950:
							post_leaderboard.append("")
						post_leaderboard[-1] += separator
					
					if emoji == "🔴": # If the person got eliminated (red circle emoji), add them to the elim arrays
						elim_pings.append(leaderboard[r][0])
						elim_players.append(int(leaderboard[r][0][2:-1]))
				
				for z in post_leaderboard: # Send leaderboard messages
					await self.MMT_C.send(z)
				
				await self.MMT_C.send(f"""❌ {grammar_list(elim_pings)} ha{'s' if len(elim_pings) == 1 else 've'} 
				been eliminated.""".replace("\n", "").replace("\t", ""))

				# Add each person's rankings to the database
				for p in range(len(self.info["PLAYERS"])):
					player = self.info["PLAYERS"][p] # `player` is an ID
					rank_str = player_ranks[p] # Their rank this round

					# Search for the player in mmtstats
					found = self.db.get_entries("mmtstats", columns=["id", "ranks"], conditions={"id": str(player)})

					if len(found) == 0: # If they're not in mmtstats, add them with the new rank value
						self.db.add_entry("mmtstats", entry=[player, rank_str, 0])
					
					else:
						# Add the new rank to their rank history
						current_rank = found[0][1]
						if self.info["GAME"]["ROUND"] == 1:
							current_rank += "\t"
						else:
							current_rank += " "
						current_rank += rank_str

						# Update mmtstats with the new rank history
						self.db.edit_entry("mmtstats", entry={"ranks": current_rank}, conditions={"id": str(player)})

				# Remove players that were eliminated
				self.info["PLAYERS"] = [x for x in self.info["PLAYERS"] if x not in elim_players]

				if len(self.info["PLAYERS"]) == 1: # If there's one player left, they win
					winner = self.info['PLAYERS'][0]
					await self.MMT_C.send(f"🏆 <@{winner}> wins the MiniMiniTWOW!")
					self.force_skip() # Skip the host since the game ended

					wins = self.db.get_entries("mmtstats", columns=["wins"], conditions={"id": str(winner)})[0][0] + 1
					# Increment the player's win count
					self.db.edit_entry("mmtstats", entry={"wins": wins}, conditions={"id": str(winner)})
					return
				
				# Turn the period into prompt decision, incremenet the round, and prepare prompt and response variables
				self.info["GAME"]["PERIOD"] = 2
				self.info["GAME"]["ROUND"] += 1
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