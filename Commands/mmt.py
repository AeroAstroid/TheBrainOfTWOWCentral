from Config._functions import grammar_list, elim_prize, word_count, formatting_fix, is_whole
from Config._const import GAME_CHANNEL, PREFIX, ALPHABET, BRAIN, DB_LINK
import discord, time, psycopg2
from psycopg2 import sql
import numpy as np

# I'm kind of iffy on keeping this extremely long HELP dict here, but I feel like moving it down below the function
# won't look good either, so for now I'm keeping it here
HELP = {
	"MAIN": "Allows for playing and hosting MiniMiniTWOWs",
	"FORMAT": "[subcommand]",
	"CHANNEL": 3,
	"USAGE": f"""Available subcommands: `queue`, `create`, `start`, `spectate`, `join`, `prompt`, `respond`, 
	`vote`, `transfer`, `end`. Use `{PREFIX}help mmt [subcommand]` for more info on each of these subcommands.
	""".replace("\n", "").replace("\t", ""),

	"QUEUE": {
		"MAIN": "Command for the MiniMiniTWOW hosting queue",
		"FORMAT": "(list)",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}mmt queue` adds you to the current hosting queue (or removes you from 
		the queue if you're already on it). Using `{PREFIX}mmt queue list` displays the current hosting queue. 
		Once it's your turn on the queue, you'll be notified and have to create a MiniMiniTWOW by using
		`{PREFIX}mmt create`.""".replace("\n", "").replace("\t", "")
	},
	"CREATE": {
		"MAIN": "Command to create a MiniMiniTWOW",
		"FORMAT": "",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}mmt create` will create a MiniMiniTWOW. Can only be used if you're up first 
		in the hosting queue.""".replace("\n", "").replace("\t", "")
	},
	"START": {
		"MAIN": "Command to start a MiniMiniTWOW",
		"FORMAT": "",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}mmt start` will start MiniMiniTWOW, ending signups. Can only be used if 
		you're the host, and there are 2 or more players.""".replace("\n", "").replace("\t", "")
	},
	"JOIN": {
		"MAIN": "Command to join a MiniMiniTWOW",
		"FORMAT": "",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}mmt join` will sign you up to the current MiniMiniTWOW. If you're already 
		signed up, using this command removes you from the MiniMiniTWOW. Joining a MiniMiniTWOW automatically 
		makes you a spectator.""".replace("\n", "").replace("\t", "")
	},
	"SPECTATE": {
		"MAIN": "Command to spectate a MiniMiniTWOW",
		"FORMAT": "",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}mmt spectate` will make you a spectator of the current MiniMiniTWOW. If you're 
		already a spectator, using this command makes you stop spectating. Once this command is used, starting the 
		next voting period, you'll receive voting screens.""".replace("\n", "").replace("\t", "")
	},
	"PROMPT": {
		"MAIN": "Command to spectate a MiniMiniTWOW",
		"FORMAT": "[prompt]",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}mmt prompt [prompt]` will set the current prompt. Only usable if the MiniMiniTWOW 
		is currently inbetween rounds, and if you're the host.""".replace("\n", "").replace("\t", "")
	},
	"RESPOND": {
		"MAIN": "Command to submit a MiniMiniTWOW response",
		"FORMAT": "[response]",
		"CHANNEL": 6,
		"USAGE": f"""Using `{PREFIX}mmt respond [response]` will record your response to the current prompt. Only 
		usable during submission period and if you're an alive contestant.""".replace("\n", "").replace("\t", "")
	},
	"VOTE": {
		"MAIN": "Command to cast a MiniMiniTWOW vote",
		"FORMAT": "[vote]",
		"CHANNEL": 6,
		"USAGE": f"""Using `{PREFIX}mmt vote [vote]` will record your vote to the screen you received. Only usable 
		during voting period and if you received a voting screen.""".replace("\n", "").replace("\t", "")
	},
	"TRANSFER": {
		"MAIN": "Command to transfer ownership of a MiniMiniTWOW to someone else",
		"FORMAT": "[new_host] ('confirm')",
		"CHANNEL": 4,
		"USAGE": f"""Can be used to make someone else the new host of the current MiniMiniTWOW. Using `{PREFIX}mmt 
		transfer [new_host]` prompts a message asking you to confirm the transfer. Including `confirm` as an argument 
		bypasses the confirmation message. `[new_host]` has to be a ping.""".replace("\n", "").replace("\t", "")
	},
	"END": {
		"MAIN": "Command to end or vote to end a MiniMiniTWOW",
		"FORMAT": "",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}mmt end` casts a vote to end a MiniMiniTWOW, or removes your vote if you had
		already cast one. If used by staff or the current host, the MiniMiniTWOW ends immediately. Otherwise, you 
		must be a spectator to cast an end vote. The MiniMiniTWOW is ended if the number of spectator votes is 
		higher than or equal to `ceil(s^(4/5) + 0.8)`, where `s` is the number of spectators. By virtue of this 
		formula, it's impossible to end a MiniMiniTWOW by spectator vote with less than 4 spectators.
		""".replace("\n", "").replace("\t", "")
	},
	"STATS": {
		"MAIN": "Command to display the overall MiniMiniTWOW stats",
		"FORMAT": "[stat]",
		"CHANNEL": 4,
		"USAGE": f"""Using this command allows you to view one of the statistics rankins for MMT. Available stats
		that can go under the `[stat]` argument are `nr`, `points`, `wins`, and `roundwins`.
		""".replace("\n", "").replace("\t", "")
	},
}

PERMS = 0 # Non-member
ALIASES = []
REQ = ["TWOW_CENTRAL", "EVENTS"]

async def MAIN(message, args, level, perms, TWOW_CENTRAL, EVENT):
	if not isinstance(message.channel, discord.DMChannel) and message.channel.id != GAME_CHANNEL:
		await message.channel.send(f"MiniMiniTWOW commands can only be used in <#{GAME_CHANNEL}>!")
		return
	
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	# Shorten the notation for convenience
	mmt = EVENT["MMT"]

	if args[1].lower() == "stats":

		if level == 2:
			await message.channel.send("Include the type of stat you want to see!")
			return
		
		# I've explained this with statement in the `tc/database` file
		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			# public.mmtstats contains ids, placements in each round, and MMT wins from everyone who's participated
			# in any MMT rounds so far
			cursor.execute(""" SELECT * FROM "public.mmtstats" """)
			data = cursor.fetchall()

			if data is None: # Just in case it gets reset one day
				await message.channel.send("There's no data yet!")
				return

			leaderboard = []
		
			if args[2].lower() == "points":
				for person in data: # `person` is a table entry, (id, placements, wins)
					try: # Try to find that person's username through TWOW Central
						member = TWOW_CENTRAL.get_member(int(person[0])).name
						if member is None:
							member = person[0]
					except Exception: # If you can't find them, just use the ID instead
						member = person[0]
					
					# MMT seasons are joined with tabs and MMT rounds are joined with spaces in the database
					ranks = [x.split(" ") for x in person[1].split("\t")]
					score = 0
					rounds = 0

					for twow in ranks: # For each season...
						for p_round in twow: # For each placement in a round...
							if p_round.strip() == "":
								continue
							numbers = p_round.split("/") # Get a list of [rank, contestantcount]
							# Points adds the amount of people you beat each round
							score += int(numbers[1]) - int(numbers[0])
							rounds += 1 # Keep track of the round count too
					
					leaderboard.append([member, score, rounds])
			
			elif args[2].lower() == "wins":
				for person in data:
					try:
						member = TWOW_CENTRAL.get_member(int(person[0])).name
						if member is None:
							member = person[0]
					except Exception:
						member = person[0]
					
					leaderboard.append([member, person[2]]) # person[2] is MMT season wins, so that's all we need
			
			elif args[2].lower() == "roundwins":
				for person in data:
					try:
						member = TWOW_CENTRAL.get_member(int(person[0])).name
						if member is None:
							member = person[0]
					except Exception:
						member = person[0]
					
					ranks = [x.split(" ") for x in person[1].split("\t")]
					wins = 0

					for twow in ranks:
						for p_round in twow:
							if p_round.strip() == "":
								continue

							numbers = p_round.split("/")
							if int(numbers[0]) == 1: # Count up for each `1` placement
								wins += 1
					
					leaderboard.append([member, wins]) # wins is the total number of round wins
			
			elif args[2].lower() == "nr":
				for person in data:
					try:
						member = TWOW_CENTRAL.get_member(int(person[0])).name
						if member is None:
							member = person[0]
					except Exception:
						member = person[0]
					
					ranks = [x.split(" ") for x in person[1].split("\t")]
					total = 0
					rounds = 0

					for twow in ranks:
						for p_round in twow:
							if p_round.strip() == "":
								continue

							numbers = p_round.split("/")
							# Add this round's NR to the total
							total += (int(numbers[1]) - int(numbers[0])) / (int(numbers[1]) - 1)
							rounds += 1
					
					# Format those as percentage strings
					average = "{:.2%}".format(total / rounds)
					total = "{:.2%}".format(total)
					
					leaderboard.append([member, total, average])
			
			else:
				return

			player_count = len(leaderboard)

			if args[2].lower() == "points": # Sort by points descending, then rounds ascending
				leaderboard = sorted(leaderboard, key=lambda c: c[2])
				leaderboard = sorted(leaderboard, reverse=True, key=lambda c: c[1])
			if args[2].lower() == "nr": # Sort by total NR -- remove the percentage and convert to float first
				leaderboard = sorted(leaderboard, reverse=True, key=lambda c: float(c[1][:-1]))
			if args[2].lower() in ["wins", "roundwins"]: # Just sort by wins ascending. Remove people who have none
				leaderboard = sorted(leaderboard, reverse=True, key=lambda c: c[1])
				leaderboard = [x for x in leaderboard if x[1] != 0]

			for line in range(len(leaderboard)): # Add the rank to each line of the leaderboard
				leaderboard[line] = [line+1] + leaderboard[line]

			# args[3] is the page number.
			if level == 3: # If it's not specified, assume it's the first page
				leaderboard = leaderboard[:10]
				page = 1
			
			elif not is_whole(args[3]): # If it's not a valid integer, assume it's first page also
				leaderboard = leaderboard[:10]
				page = 1
			
			elif (int(args[3]) - 1) * 10 >= len(leaderboard): # Detect if the page number is too big
				await message.channel.send(f"There is no page {args[3]} of this stat!")
				return
			
			else: # This means the user specified a valid page number
				lower = (int(args[3]) - 1) * 10
				upper = int(args[3]) * 10
				leaderboard = leaderboard[lower:upper]
				page = args[3]

			# Headers for each stat
			if args[2].lower() == "points":
				final_message = f"```diff\n---⭐ MiniMiniTWOW Point Leaderboard Page {page} ⭐---\n\n"
				final_message +=  " Rank |  Name                    |  Pts.  |  Rounds\n"
				spacing = 6
			if args[2].lower() == "nr":
				final_message = f"```diff\n---⭐ MiniMiniTWOW Normalized Rank Leaderboard Page {page} ⭐---\n\n"
				final_message +=  " Rank |  Name                    |   Total   |  Average\n"
				spacing = 9
			if args[2].lower() == "wins":
				final_message = f"```diff\n---⭐ MiniMiniTWOW Wins Leaderboard Page {page} ⭐---\n\n"
				final_message +=  " Rank |  Name                    |  Wins\n"
				spacing = 4
			if args[2].lower() == "roundwins":
				final_message = f"```diff\n---⭐ MiniMiniTWOW Round Wins Leaderboard Page {page} ⭐---\n\n"
				final_message +=  " Rank |  Name                    |  Round Wins\n"
				spacing = 5

			# Composition of each line of the leaderboard
			for line in leaderboard:
				symbol = "+" if line[0] == 1 else "-"
				spaced_rank = f"{line[0]}{' ' * (4 - len(str(line[0])))}"
				spaced_name = f"{line[1][:23]}{' '*(24 - len(str(line[1])))}"
				spaced_points = f"{line[2]}{' '*(spacing - len(str(line[2])))}"
				try: # Some stats will have two number columns...
					formatted = f"{symbol} {spaced_rank}|  {spaced_name}|  {spaced_points}|  {line[3]}\n"
				except: # ...but others will have one. This try except block detects each one.
					formatted = f"{symbol} {spaced_rank}|  {spaced_name}|  {spaced_points}\n"

				final_message += formatted # Add the line to the message
			
			final_message += "```" # Close off the code block

			await message.channel.send(final_message)
			return


	if args[1].lower() == "end":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if message.author.id == mmt.info["GAME"]["HOST"]: # Automatically end MMT if it's the host trying to end it
			await message.channel.send("**The current MiniMiniTWOW has been ended by the host! The queue moves on.**")
			mmt.force_skip()
			return
		
		if perms == 2: # Do the same if it's a staff member
			await message.channel.send("**The current MiniMiniTWOW has been ended by staff! The queue moves on.**")
			mmt.force_skip()
			return
		
		if mmt.info["GAME"]["PERIOD"] == 1: # Spectator votes have to wait until post-start, though
			await message.channel.send("You can only vote to end a MiniMiniTWOW that has already started!")
			return
		
		spect = len(mmt.info["SPECTATORS"]) # Number of spectators
		necessary = np.ceil(spect**(4/5) + 0.8) # By the formula, the number of votes necessary to end the MMT

		# If there are less than 4 spectators, you can't end an MMT by spectator vote. As such, there's not much
		# reason to bother including the amount of votes necessary if necessary > spect, so include it only if
		# necessary <= spect instead
		nec_seg = ""
		if necessary <= spect:
			nec_seg = f"/{necessary}"
		
		if message.author.id in mmt.info["GAME"]["END_VOTES"]:
			# Filter the user's ID out of the list of end voters
			mmt.info["GAME"]["END_VOTES"] = [x for x in mmt.info["GAME"]["END_VOTES"] if x != message.author.id]
			votes = len(mmt.info["GAME"]["END_VOTES"]) # Calculate the new number of votes
			await message.channel.send(f"""🚪 {message.author.mention} removes their vote to end the MiniMiniTWOW. 
			There are now **{votes}{nec_seg}** votes.""")
			return
		
		mmt.info["GAME"]["END_VOTES"].append(message.author.id) # Add user's ID to list of end votes
		votes = len(mmt.info["GAME"]["END_VOTES"]) # Calculate new number of votes
		await message.channel.send(f"""🚪 **{message.author.mention} voted to end the MiniMiniTWOW!** 
		There are now **{votes}{nec_seg}** votes.""")

		if votes >= necessary: # If the amount of votes reaches the required...
			await message.channel.send("""**The current MiniMiniTWOW has been ended 
			by public vote! The queue moves on.**""".replace("\n", "").replace("\t", ""))
			mmt.force_skip() # Function to skip a host, also used in Events/mmt.py
		
		return
		

	if args[1].lower() == "transfer":
		if not mmt.RUNNING:
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] == 0:
			await message.channel.send("Host transfers can only occur with MiniMiniTWOWs that have been created.")
			return
		
		if mmt.info["GAME"]["HOST"] != message.author.id:
			await message.channel.send("Only the host can transfer the MiniMiniTWOW to someone else!")
			return
		
		if level == 2:
			await message.channel.send("Choose a user to transfer it to!")
			return

		# You have to ping the person you wanna transfer it to
		mention = args[2]
		try:
			user_id = int(mention[2:-1])
		except:
			await message.channel.send("Invalid user! Ping the user you want to transfer the MiniMiniTWOW to!")
			return
		
		# Try to find the person in TWOW Central
		person = TWOW_CENTRAL.get_member(user_id)

		if person is None: # If they're not in TWOW Central, they can't become the new host
			await message.channel.send("Invalid user! Ping the user you want to transfer the MiniMiniTWOW to!")
			return
		
		if 'confirm' not in [x.lower() for x in args]: # Confirmation can be bypassed by including `confirm`
			await message.channel.send(f"""Are you sure you want to transfer the MiniMiniTWOW to **{person.name}**? 
			Send `confirm` to transfer.""".replace("\n", "").replace("\t", ""))
			
			# Check for the next message by the same person in the same channel
			msg = await BRAIN.wait_for('message', 
			check=lambda m: (m.author == message.author and m.channel == message.channel))

			if msg.content.lower() != "confirm": # If it's not `confirm`, cancel the command
				await message.channel.send("Transfer command cancelled.")
				return
		
		msg_send = f"Successfully transfered host position to **{person.name}**!"

		# Make the new person the host
		mmt.info["GAME"]["HOST"] = user_id

		# Reset the timers for host actions if necessary
		if mmt.info["GAME"]["PERIOD"] == 1 and mmt.info["GAME"]["PERIOD_START"] != 0:
			mmt.info["GAME"]["PERIOD_START"] = time.time()
			msg_send += f""" The timer to start the MiniMiniTWOW is reset. {mention} has {mmt.param["S_DEADLINE"]} 
			seconds to start it with `tc/mmt start`.""".replace("\n", "").replace("\t", "")
		
		if mmt.info["GAME"]["PERIOD"] == 2:
			mmt.info["GAME"]["PERIOD_START"] = time.time()
			msg_send += f""" The timer to set the prompt is reset. {mention} has {mmt.param["P_DEADLINE"]} 
			seconds to decide on the prompt with `tc/mmt prompt`.""".replace("\n", "").replace("\t", "")

		await message.channel.send(msg_send)
		return

	if args[1].lower() == "queue":
		if level == 2: # If it's just `tc/mmt queue`
			if not mmt.RUNNING: # The event is counted as off if there's nobody in queue. To check the queue, it needs
				# to be on, so being the first to join the queue will start up the event
				mmt.start(TWOW_CENTRAL)
			
			if message.author.id in mmt.info["HOST_QUEUE"]: # If you're already in queue, leaves the queue
				mmt.info["HOST_QUEUE"] = [x for x in mmt.info["HOST_QUEUE"] if x != message.author.id]
				await mmt.MMT_C.send(f"🎩 <@{message.author.id}> has been removed from queue.")
				return
			
			mmt.info["HOST_QUEUE"].append(message.author.id) # If you're not in queue, you're added to queue
			await message.channel.send(
			f"🎩 <@{message.author.id}> has been added to queue at position **{len(mmt.info['HOST_QUEUE'])}**.")
			return
		
		if args[2].lower() == "list":
			if len(mmt.info["HOST_QUEUE"]) == 0: # If the event is not running, the host queue's length is also 0
				await message.channel.send("The queue is empty!")
				return
			
			# Array I use to split the list into multiple messages if necessary
			init = ["**This is the current MiniMiniTWOW hosting queue:**\n\n"]

			for person in mmt.info["HOST_QUEUE"]: # `person` is an ID
				member = TWOW_CENTRAL.get_member(person) # Try to find the user

				if member is None: # If you can't find the user, just use their ID and format it
					member = f"`{person}`"
				else: # If you found the user, use their username
					member = member.name
				
				# Define the line that's about to be added
				line = f"🎩 [{mmt.info['HOST_QUEUE'].index(person) + 1}] - **{member}**\n"

				# If adding this line steps over the character limit, add another string to the array
				# 1950 instead of 2000 because having over 1950 can cause issues for like no reason
				if len(init[-1] + line) > 1950:
					line.append("")
				init[-1] += line # Add the line to this new string
			
			for z in init: # Send each of those strings as a separate message
				await message.channel.send(z)
			return
	
	if args[1].lower() == "create":
		if not mmt.RUNNING: # If the event isn't running
			await message.channel.send(
			f"There's no host to create a MiniMiniTWOW! Join the queue with `{PREFIX}mmt queue` to host!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 0: # If it's not time to create one
			await message.channel.send("There's already a MiniMiniTWOW running!")
			return
		
		if message.author.id != mmt.info["GAME"]["HOST"]: # If you're not host
			await message.channel.send("You can only create a MiniMiniTWOW if you're up on the queue!")
			return
		
		# Switch the period to 1 (signups)
		mmt.info["GAME"]["PERIOD"] = 1
		mmt.info["GAME"]["PERIOD_START"] = 0

		await message.channel.send(
		f"🎩 <@{message.author.id}> has created a MiniMiniTWOW! Use `{PREFIX}mmt join` to join it!")
		return
	
	if args[1].lower() == "spectate":
		if not mmt.RUNNING: # If the event isn't running
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] == 0: # If `tc/mmt create` hasn't been run
			await message.channel.send("You can only spectate a MiniMiniTWOW that has been created!")
			return
		
		if message.author.id in mmt.info["SPECTATORS"]: # If you're a spectator...
			# ...You're removed from the list of spectators
			mmt.info["SPECTATORS"] = [x for x in mmt.info["SPECTATORS"] if x != message.author.id]
			await mmt.MMT_C.send(f"👁️ <@{message.author.id}> is no longer spectating.")
			return
		
		mmt.info["SPECTATORS"].append(message.author.id) # Adds user to the list of spectators
		await mmt.MMT_C.send(f"""👁️ <@{message.author.id}> is now spectating, and will receive voting screens 
		for future rounds.""".replace("\n", "").replace("\t", ""))
		return
	
	if args[1].lower() == "join":
		if not mmt.RUNNING: # If the event is not running
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 1: # If it's not signup period
			await message.channel.send("You can only join the MiniMiniTWOW if it's in signups!")
			return
		
		if message.author.id in mmt.info["PLAYERS"]: # If you're already a player
			# Remove you both from the player list and the spectator list
			mmt.info["PLAYERS"] = [x for x in mmt.info["PLAYERS"] if x != message.author.id]
			mmt.info["SPECTATORS"] = [x for x in mmt.info["SPECTATORS"] if x != message.author.id]

			await mmt.MMT_C.send(
			f"🏁 <@{message.author.id}> left the MiniMiniTWOW. Our player count is {len(mmt.info['PLAYERS'])}.")

			if len(mmt.info['PLAYERS']) == 1: # The timer is cancelled if there's no longer 2 players
				await mmt.MMT_C.send("🏁 We no longer have two players. The three minute start timer is now reset.")
			return
		
		mmt.info["PLAYERS"].append(message.author.id) # Adds user as a player
		if message.author.id not in mmt.info["SPECTATORS"]:
			mmt.info["SPECTATORS"].append(message.author.id) # And a spectator, if they're not already one

		await mmt.MMT_C.send(
		f"🏁 **<@{message.author.id}> joined the MiniMiniTWOW!** Our player count is now {len(mmt.info['PLAYERS'])}!")
		if len(mmt.info['PLAYERS']) == 2: # If there are two players, the signup timer begins
			await mmt.MMT_C.send(f"""🏁 We have two players! <@{mmt.info["GAME"]["HOST"]}> has three minutes 
			to start the MiniMiniTWOW with `{PREFIX}mmt start`.""".replace("\n", "").replace("\t", ""))
			mmt.info["GAME"]["PERIOD_START"] = time.time()
		return
	
	if args[1].lower() == "start":
		if not mmt.RUNNING: # If the event isn't running
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 1: # If it's not signup period
			await message.channel.send("You can only start a MiniMiniTWOW if it's in signups!")
			return
		
		if message.author.id != mmt.info["GAME"]["HOST"]: # If user isn't host
			await message.channel.send("Only the host can start a MiniMiniTWOW!")
			return
		
		if len(mmt.info["PLAYERS"]) < 2: # If there aren't two contestants
			await message.channel.send("You need at least two contestants to start a MiniMiniTWOW!")
			return
		
		# Set it to round 1 with period 2 (prompt deciding)
		mmt.info["GAME"]["ROUND"] = 1
		mmt.info["GAME"]["PERIOD"] = 2
		mmt.info["GAME"]["PERIOD_START"] = time.time()

		await mmt.MMT_C.send(f"""🏁 <@{message.author.id}> has started the MiniMiniTWOW with 
		{len(mmt.info["PLAYERS"])} contestants. Nobody can sign up anymore.""".replace("\n", "").replace("\t", ""))
		
		return
	
	if args[1].lower() == "prompt":
		if not mmt.RUNNING: # If the event isn't running
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 2: # If it's not prompt decision period
			await message.channel.send("You can only set a prompt inbetween rounds!")
			return
		
		if message.author.id != mmt.info["GAME"]["HOST"]: # If user isn't host
			await message.channel.send("Only the host can set a prompt!")
			return
		
		if level == 2:
			await message.channel.send("You need to include a prompt!")
			return
		
		# Remove formatting and characters that might cause errors
		prompt = " ".join(args[2:]).replace("`", "").replace("\t", "").replace("\n", "")

		if len(prompt) > 200:
			await message.channel.send("That prompt is too long! It must be 200 characters at most.")
			return
		
		# Switch to responding period, set the rpompt, prepare the responses array
		mmt.info["GAME"]["PERIOD"] = 3
		mmt.info["GAME"]["PERIOD_START"] = time.time()
		mmt.info["GAME"]["PROMPT"] = prompt
		mmt.info["RESPONSES"] = [""] * len(mmt.info["PLAYERS"])

		await mmt.MMT_C.send(f"""📝 **Round {mmt.info["GAME"]["ROUND"]} Responding** has started! The prompt is:
		```{prompt}```
		Our contestants have {mmt.param["R_DEADLINE"]} seconds to respond to it.""".replace("\n", "").replace("\t", ""))

		for player in mmt.info["PLAYERS"]:
			try: # DM everyone the prompt
				await TWOW_CENTRAL.get_member(player).send(f"""
				📝 **Round {mmt.info["GAME"]["ROUND"]} Responding** has started! The prompt is:
				```{prompt}```
				You must respond in {mmt.param["R_DEADLINE"]} seconds using `{PREFIX}mmt respond`!
				""".replace("\n", "").replace("\t", ""))
			except Exception: # If something goes wrong, skip the person
				pass
		return
	
	if args[1].lower() == "respond":
		if not isinstance(message.channel, discord.DMChannel): # If not in DMs
			await mmt.MMT_C.send("This command can only be used in DMs!")
			return
		
		if not mmt.RUNNING: # If event isn't running
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 3: # If it's not submission period
			await message.channel.send("You can only respond during a submission period!")
			return
		
		if message.author.id not in mmt.info["PLAYERS"]: # If you're not a player
			await message.channel.send("Only alive contestants can respond!")
			return
		
		if level == 2:
			await message.channel.send("You need to include a response!")
			return

		# Run the formatting_fix function, remove characters that might cause issues and strip unnecessary whitespace
		response = formatting_fix(" ".join(args[2:]).replace("`", "").replace("\t", "").replace("\n", "")).strip()

		if len(response) > 120: # Too long
			await message.channel.send("Your response is too long! It must be 120 characters at most.")
			return
		
		if len(response) == 0: # Literally empty
			await message.channel.send("Your response evaluates to an empty string.")
			return
		
		ind = mmt.info["PLAYERS"].index(message.author.id) # Index of the user in the players array
		new = not mmt.info["RESPONSES"][ind] == "" # Detects if this is a new response or an edit

		while response in mmt.info["RESPONSES"]: # If this response has already been submitted...
			response += "\u200b" # ...distinguish between them by adding a zero-width space to the end of one
		# Keep doing so until it's unique (in the case there's more than two identical entries)

		mmt.info["RESPONSES"][ind] = response # Set the response to the one submitted

		await message.channel.send(f"""Your {'new ' if new else ''}response to the prompt has been recorded as:
		```{response}```> **Word count:** {word_count(response)}""".replace("\n", "").replace("\t", ""))
		return
	
	if args[1].lower() == "vote":
		if not isinstance(message.channel, discord.DMChannel): # If not in DMs
			await mmt.MMT_C.send("This command can only be used in DMs!")
			return
		
		if not mmt.RUNNING: # If event isn't running
			await message.channel.send("There's no MiniMiniTWOW running right now!")
			return
		
		if message.author.id not in mmt.info["VOTES"]["ID"]: # If you didn't receive a voting screen
			await message.channel.send("You can only vote if you received a voting screen!")
			return
		
		if mmt.info["GAME"]["PERIOD"] != 4: # If it's not voting period
			await message.channel.send("You can only vote during a voting period!")
			return

		if level == 2:
			await message.channel.send("You need to include a vote!")
			return
		
		vote = args[2].upper() # Always convert vote to uppercase
		ind = mmt.info["VOTES"]["ID"].index(message.author.id) # Index of user in the votes arrays
		screen = mmt.info["VOTES"]["RESP"][ind] # Check the screen the user received

		# The screen has `n` responses, so the vote should be composed of the first `n` letters of the alphabet
		# Otherwise, it's invalid
		if sorted(list(vote)) != sorted(list(ALPHABET[:len(screen)])):
			await message.channel.send("""Your vote is invalid. Make sure you're not missing or repeating any letters, 
			or including any invalid characters.""".replace("\n", "").replace("\n", ""))
			return

		# Instantly convert the vote to the score it'll give to each response
		parsed_vote = []
		for z in range(len(vote)):
			score = (len(vote) - 1 - vote.find(ALPHABET[z])) / (len(vote) - 1)
			parsed_vote.append(str(score))

		new = not mmt.info["VOTES"]["VOTE"][ind] == "" # Detect if the vote is new or an edit
		mmt.info["VOTES"]["VOTE"][ind] = " ".join(parsed_vote) # Join the list of values and record it

		# Display the vote back as the letters
		await message.channel.send(f"""Your {'new ' if new else ''}vote has been recorded as: 
		```{vote}```""".replace("\n", "").replace("\t", ""))
		return