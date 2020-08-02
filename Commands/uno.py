from Config._functions import is_whole, uno_image, uno_skip
from Config._const import BRAIN, ORIGINAL_DECK
import asyncio, os, numpy, random, time, discord
from collections import OrderedDict

def HELP(PREFIX): 
	return {
		"COOLDOWN": 2,
		"MAIN": "Command for a bot implementation of UNO",
		"FORMAT": "[subcommand]",
		"CHANNEL": 0,
		"CATEGORY" : "Games",
		
		"USAGE": f"""Available subcommands: `create`, `config`, `join`, `start`, `play`, `quit`, `end`. Use `{PREFIX}help 
		uno [subcommand]` for more info on each of these subcommands.""".replace("\n", "").replace("\t", ""),

		"CREATE": {
			"MAIN": "Creates a Uno round",
			"FORMAT": "",
			"CHANNEL": 0,
			"USAGE": f"""Using `{PREFIX}uno create` will create a Uno round, provided there isn't one currently running.
			""".replace("\n", "").replace("\t", "")
		},
		"CONFIG": {
			"MAIN": "Shows or modifies the adjustable settings for the Uno rounds",
			"FORMAT": "(config_number) (new_number)",
			"CHANNEL": 0,
			"USAGE": f"""Using `{PREFIX}uno config` show you the current settings for the Uno round. The host can change
			these settings provided it's currently joining period, by using `{PREFIX}uno config n` to toggle ON/OFF 
			configurations by their code number, and `{PREFIX}uno config n x` to change the value in number configurations.
			""".replace("\n", "").replace("\t", "")
		},
		"JOIN": {
			"MAIN": "Join or leave a Uno round",
			"FORMAT": "",
			"CHANNEL": 0,
			"USAGE": f"""Using `{PREFIX}uno join` will add you to the Uno round, or remove you if you're already in it. 
			The host has three minutes to start the Uno round after two people join.""".replace("\n", "").replace("\t", "")
		},
		"START": {
			"MAIN": "Starts a Uno round",
			"FORMAT": "",
			"CHANNEL": 0,
			"USAGE": f"""Using `{PREFIX}uno start` will start the Uno round. Only usable if you're the round host, and if 
			there are two or more players.""".replace("\n", "").replace("\t", "")
		},
		"PLAY": {
			"MAIN": "Plays or draws cards",
			"FORMAT": "[number/'draw'] (color)",
			"CHANNEL": 0,
			"USAGE": f"""Using `{PREFIX}uno play n` will play the `n`th card in your hand (card numbers are shown right 
			above each card). When playing wild cards, you must include the `(color)` parameter - a number from 1 through 
			4 denoting what color you want to switch to. Using `{PREFIX}uno play draw` will draw a card.
			""".replace("\n", "").replace("\t", "")
		},
		"QUIT": {
			"MAIN": "Quits the Uno round",
			"FORMAT": "",
			"CHANNEL": 0,
			"USAGE": f"""Using `{PREFIX}uno quit` will remove you from the Uno round. Only usable after the game has 
			started - to quit during joining period, use `{PREFIX}uno join` again.""".replace("\n", "").replace("\t", "")
		},
		"END": {
			"MAIN": "Ends the Uno round",
			"FORMAT": "",
			"CHANNEL": 0,
			"USAGE": f"""Using `{PREFIX}uno end` will end the Uno round automatically. Only the host or staff members 
			can end a round.""".replace("\n", "").replace("\t", "")
		}
	}

PERMS = 1 # Members
ALIASES = []
REQ = ["UNO"]

async def MAIN(message, args, level, perms, SERVER, UNO_INFO):
	if level == 1: # If the command is just `tc/uno`
		await message.channel.send("You must include a command mode for that command!")
		return


	if args[1].lower() == "join":
		if UNO_INFO["status"] != 1: # If it's not joining period
			await message.channel.send("This Uno round is not in joining period!")
			return
		
		if message.author.id in UNO_INFO["players"]: # If the person is already a player
			UNO_INFO["players"].remove(message.author.id) # Remove them from the player list

			# Report the new player count
			await message.channel.send(f"""**<@{message.author.id}>**, you have quit this round of Uno. 
			Now, there are **{len(UNO_INFO["players"])}** 
			player{"s" if len(UNO_INFO["players"]) != 1 else ""}.""".replace("\n", "").replace("\t", ""))

			return [4, "UNO", UNO_INFO] # Return a flag to change the UNO PARAMS entry
		
		# If the person is not already a player...
		UNO_INFO["players"].append(message.author.id) # Add them to the player list

		# Report the new player count
		await message.channel.send(f"""**<@{message.author.id}>**, you have joined this round of Uno! 
		There are now **{len(UNO_INFO["players"])}** 
		player{"s" if len(UNO_INFO["players"]) != 1 else ""}.""".replace("\n", "").replace("\t", ""))

		return [4, "UNO", UNO_INFO]


	if args[1].lower() == "config":
		if UNO_INFO["status"] == 0: # If there's no Uno round right now
			await message.channel.send("There's no Uno round right now!")
			return

		if level == 2: # `tc/config` shows you the current configurations
			tag = str(time.time()).split(".")[1] # Get a pretty much random sequence of digits
			uno_image(4, tag, SERVER['PREFIX'], config=UNO_INFO["config"]) # Generate the image with the [4] (config menu) flag

			await message.channel.send("These is the current game options configuration.",
			file=discord.File(f"Images/current_card_image_{tag}.png")) # Send the image

			os.remove(f"Images/current_card_image_{tag}.png") # And then promptly delete it

			return

		# If there are more than 2 arguments, that means the command is to change a configuration
		if UNO_INFO["host"] != message.author.id: # If the command isn't coming from the host
			await message.channel.send("Only the current host can change the round options!")
			return

		if UNO_INFO["status"] != 1: # If the game is already goings
			await message.channel.send("You can only change the configurations before the game has started!")
			return
		
		if not is_whole(args[2]): # Options are numbered on the menu, args[2] represents the number you want
			await message.channel.send("That's not a valid option number!")
			return

		if not 1 <= int(args[2]) <= len(UNO_INFO["config"]): # If it's not a valid number...
			await message.channel.send("That's not a valid option number!")
			return

		chosen_index = int(args[2]) - 1 # Index in the list of dict keys

		config_key = list(UNO_INFO["config"].keys())[chosen_index] # Get the key of chosen_index

		config_value = UNO_INFO["config"][config_key] # The current value of the option chosen

		if type(config_value) == bool: # If config_value is a boolean
			current_state = UNO_INFO["config"][config_key] # Toggle the value
			UNO_INFO["config"][config_key] = not current_state

			await message.channel.send( # Report the toggled value
			f"The **{config_key}** option has been turned **{'ON' if current_state else 'OFF'}**!")
			return [4, "UNO", UNO_INFO]

		elif level == 3: # If it's not a boolean, this config parameter needs an extra argument to be changed
			await message.channel.send("You must specify a number to change this configuration to!")
			return
		
		elif not is_whole(args[3]): # So far, the only extra argument is an integer for card number
			await message.channel.send("That's not a valid card number!")
			return

		elif 2 > int(args[3]): # Currently this is quite a bit hardcoded
			await message.channel.send("Too few cards! The minimum starting number is **2**.")
			return
		
		elif int(args[3]) > 30: # So maybe I'll change it in the future
			await message.channel.send("""I see you like making things excessive. Me too, honestly, but let's just 
			keep it at **30** maximum, that's well excessive enough""".replace("\n", "").replace("\t", ""))
			return
		
		else:
			UNO_INFO["config"][config_key] = int(args[3]) # Set the card number to the number specified
			await message.channel.send(f"The **{config_key}** option has been set to **{args[3]}**!")
			return [4, "UNO", UNO_INFO]


	if args[1].lower() == "start": # Command to start the round
		if UNO_INFO["host"] != message.author.id: # If it's not from the host
			await message.channel.send("Only the current host of the game can start the Uno round!")
			return

		if UNO_INFO["status"] != 1: # If it's not joining period
			await message.channel.send("You can only start a Uno round during joining period!")
			return
		
		if len(UNO_INFO["players"]) < 2: # If there are less than two playerss
			await message.channel.send("You can only start a Uno round with two or more players!")
			returns
		
		UNO_INFO["status"] = 2 # Change the game status and distribute cards
		await message.channel.send("**The Uno round is starting!** Currently distributing cards...")
		return [4, "UNO", UNO_INFO]


	if args[1].lower() == "play":
		if not UNO_INFO["running"] or UNO_INFO["status"] != 2: # If there's no Uno round being played right now
			await message.channel.send("There's no Uno round in progress!")
			return
		
		if UNO_INFO["order"][0] != message.author.id: # If it's not you who's ups
			await message.channel.send("It's not your turn to play!")
			return
		
		if level == 2: # `tc/uno play` by itself does nothing
			await message.channel.send("You must include a card or an action to play!")
			return
		
		player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)]

		if is_whole(args[2]): # If there's a number as args[2], interpret it as a card index

			if not 1 <= int(args[2]) <= len(player_hand): # If it's a number of cards you don't have
				await message.channel.send("That card number is not valid!")
				return

			played_card = player_hand[int(args[2]) - 1] # The card code for the card that was played

			if played_card[0] == "0": # 0C and OF are wild cards
				if level == 3: # If you just played a wild card without specifying the color you want
					await message.channel.send( # Warn about the color and how you can pick it
					f"""When playing a wild card, you must include the color you want to change the game to!
					To include a color, put another number next to the command, corresponding to the color you want.
					Add the number 1 for red, 2 for green, 3 for blue or 4 for yellow!
					Example: `{SERVER['PREFIX']}uno play {args[2]} 3`, will play the card and change the color to **blue.**
					""".replace("\t", ""))
					return
					
				if not is_whole(args[3]): # The color should be an integer
					await message.channel.send("That's not a valid color number!")
					return

				if not 1 <= int(args[3]) <= 4: # If the color is not 1 through 4
					await message.channel.send("That's not a valid color number!")
					return

				if UNO_INFO["carryover"] > 0: # If the carryover is positive, there are cards to be drawn made up
					await message.channel.send( # of one or more +2s.
					f"""Someone has played a **+2** upon you. You must play another **+2** or draw the cards!
					To draw the cards instantly, use `{SERVER['PREFIX']}uno play draw`.""".replace("\t", ""))
					return
				
				if UNO_INFO["carryover"] < -3 and played_card != "0F": # If the carryover is negative and below -3,
					await message.channel.send( # There are cards to be drawn made up of one or more +4s
					f"""Someone has played a **+4** upon you. You must play another **+4** or draw the cards!
					To draw the cards instantly, use `{SERVER['PREFIX']}uno play draw`.""".replace("\t", ""))
					return

				if played_card == "0F": # If a +4 was played, make the carryover -4 if there weren't any
					# cards to be drawn prior, or increment by 4 any current card total to be drawn
					UNO_INFO["carryover"] = -4 if UNO_INFO["carryover"] > -3 else UNO_INFO["carryover"] - 4

				# Remove the card from the player's hand
				UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)].remove(played_card)
				UNO_INFO["last_card"] = args[3] + played_card[1] # args[3] is chosen color, card code includes color

				player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] # Redefine player_hand
				
				tag = str(time.time()).split(".")[1] # Make the updated image for the player's hand
				uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=player_hand)

				# Send the image then promptly delete it
				await message.channel.send("You have successfully played a card!",
				file=discord.File(f"Images/current_card_image_{tag}.png"))
				os.remove(f"Images/current_card_image_{tag}.png")

				UNO_INFO["current"] = 0
				return [4, "UNO", UNO_INFO]

			elif (not played_card[0] == UNO_INFO["last_card"][0] and 
			not played_card[1] == UNO_INFO["last_card"][1]): # If neither the color nor the number match
				await message.channel.send("That card is not valid!")
				return
			
			if UNO_INFO["carryover"] < -3: # If the carryover is negative and below -3,
				await message.channel.send( # There are cards to be drawn made up of one or more +4s
				f"""Someone has played a **+4** upon you. You must play another **+4** or draw the cards!
				To draw the cards instantly, use `{SERVER['PREFIX']}uno play draw`.""".replace("\t", ""))
				return
			
			if UNO_INFO["carryover"] > 0 and played_card[1] != "D": # If the carryover is positive, there are cards
				await message.channel.send( # to be drawn made up of one or more +2s.
				f"""Someone has played a **+2** upon you. You must play another **+2** or draw the cards!
				To draw the cards instantly, use `{SERVER['PREFIX']}uno play draw`.""".replace("\t", ""))
				return
			
			if played_card[1] == "D": # If a +2 was played, make the carryover 2 if there weren't any
				# cards to be drawn prior, or increment by 2 any current card total to be drawn
				UNO_INFO["carryover"] = 2 if UNO_INFO["carryover"] < 2 else UNO_INFO["carryover"] + 2

			seven_f = False # Variable for the case where the player switches hands with someone using special 7

			if played_card[1] == "7" and UNO_INFO["config"]["0-7"]: # If you played a 7 under the 0-7 rule

				if level == 3: # You need to specify a player to trade withs
					player_list = []
					for player in range(len(UNO_INFO["players"])): # For each player that isn't you
						if UNO_INFO["players"][player] != message.author.id:
							player_name = SERVER["MAIN"].get_member(UNO_INFO["players"][player]).name
							player_hand_size = len(UNO_INFO["hands"][player])

							player_list.append(
							f"[{player + 1}] - **{player_name}** (Card count: {player_hand_size})")

					player_list = "\n".join(player_list) # Format the list of available players to switch hands with

					await message.channel.send(
					f"""You must pick someone to trade hands with!
					
					{player_list}
					
					To successfully play the card and trade hands with someone, use `{SERVER['PREFIX']}uno play {args[2]} x`
					*(x being the number corresponding to the player)*
					""".replace("\t", ""))

					return
				
				if not is_whole(args[3]): # If the player number is not a whole number
					await message.channel.send("That player number is invalid!")
					return
				
				if not 1 <= int(args[3]) <= len(UNO_INFO["players"]): # If the number isn't in the amount of players
					await message.channel.send("That player number is invalid!")
					return
				
				if UNO_INFO["players"][int(args[3]) - 1] == message.author.id: # If you chose yourself
					await message.channel.send("You can't trade hands with yourself!")
					return
				
				seven_f = True # Set the variable to true for later
				await UNO_INFO["channel"].send(f"**{message.author.name}** is trading hands with someone...")

			UNO_INFO["last_card"] = played_card # Make the card played the last one, remove it from the player's hand
			UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)].remove(played_card)

			player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] # Redefine player_hand

			tag = str(time.time()).split(".")[1] # Make the updated image for the player's new hand
			uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=player_hand)

			await message.channel.send("You have successfully played a card!", # Send the image
			file=discord.File(f"Images/current_card_image_{tag}.png"))
			os.remove(f"Images/current_card_image_{tag}.png") # Then promptly delete it

			if played_card[1] == "S": # If it's a skip...
				UNO_INFO["carryover"] = -1 # -1 carryover means skip

			if played_card[1] == "R": # If it's a reverse card...
				UNO_INFO["carryover"] = -3 # -3 carryover means reverse

			if played_card[1] == "0" and UNO_INFO["config"]["0-7"]: # If it's 0 under the 0-7 rule...
				UNO_INFO["hands"] += UNO_INFO["hands"][0:1] # A zero rotates everyone's hands around
				UNO_INFO["hands"] = UNO_INFO["hands"][1:]

				# Report that the hands were rotated
				await UNO_INFO["channel"].send(f"**{message.author.name} has rotated everyone's hand!**")

				for player in UNO_INFO["players"]: # Send every single person their new hand
					tag = str(time.time()).split(".")[1] # Make the image for their new hand
					uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"],
					hand=UNO_INFO["hands"][UNO_INFO["players"].index(player)])

					await SERVER['MAIN'].get_member(player).send( # Send the new hand
					"Everyone's hand has rotated! This is your new hand!", 
					file=discord.File(f"Images/current_card_image_{tag}.png"))
					os.remove(f"Images/current_card_image_{tag}.png") # Delete the images
			
			if seven_f: # If it's a 7 under 0-7...
				provisory_hand = UNO_INFO["hands"][int(args[3]) - 1] # Just a variable to hold the other player's hand
				UNO_INFO["hands"][int(args[3]) - 1] = player_hand # Make the other player's hand your own

				# Make your own hand the other player's
				UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] = provisory_hand

				player_member = SERVER["MAIN"].get_member(UNO_INFO["players"][int(args[3]) - 1])
				player_name = player_member.name
				await UNO_INFO["channel"].send( # Report the trade
				f"**{message.author.name}** trades hands with **{player_name}**!")

				player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)]

				tag = str(time.time()).split(".")[1] # Report your new hand
				uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=player_hand)
				await message.channel.send("This is your new hand!", 
				file=discord.File(f"Images/current_card_image_{tag}.png"))
				os.remove(f"Images/current_card_image_{tag}.png")

				tag = str(time.time()).split(".")[1] # Show the other player their new hand
				uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=UNO_INFO["hands"][int(args[3]) - 1])
				await SERVER["MAIN"].get_member(player_member).send(
				f"**{message.author.name}** has traded their hand with you! This is your new hand.", 
				file=discord.File(f"Images/current_card_image_{tag}.png"))
				os.remove(f"Images/current_card_image_{tag}.png")

			UNO_INFO["current"] = 0 # Signals that the turn is over
			return [4, "UNO", UNO_INFO]
			
		elif args[2].lower() == "draw":
			if UNO_INFO["carryover"] == -2: # carryover being -2 indicates you've already drawn
				await message.channel.send("You've already drawn a card this turn!")
				return
			
			if UNO_INFO["carryover"] > 0 or UNO_INFO["carryover"] < -3: # If there are cards to be drawn
				card_n = numpy.abs(UNO_INFO["carryover"]) # Add the card number to the player's hand
				UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] += UNO_INFO["deck"][:card_n]
				UNO_INFO["deck"] = UNO_INFO["deck"][card_n:]

				player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] # Redefine player_hand

				# Sort the player's hand to show cards in the correct order
				UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] = list(sorted(player_hand))

				player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)]

				UNO_INFO["carryover"] = 0 # Reset the carryover

				tag = str(time.time()).split(".")[1] # Report the new hand
				uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=player_hand)
				await message.channel.send(f"You draw **{card_n}** cards!", 
				file=discord.File(f"Images/current_card_image_{tag}.png"))
				
				await UNO_INFO["channel"].send(f"**{message.author.name}** draws **{card_n}** cards!")
				os.remove(f"Images/current_card_image_{tag}.png")

				if UNO_INFO["config"]["d-skip"]: # d-skip is whether or not drawing by +2 or +4 skips you. If it skips you...
					await message.channel.send("Your turn is over!")
					UNO_INFO["current"] = 0 # Signals that the turn is over

				return [4, "UNO", UNO_INFO]
			
			else: # If there's no carryover, just draw a card normally

				# Add the card to the player's hands
				UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] += [UNO_INFO["deck"][0]]
				UNO_INFO["deck"] = UNO_INFO["deck"][1:] # Remove the first card from the deck
				UNO_INFO["carryover"] = -2 # -2 carryover indicates drawing

				player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] # Redefine player_hand

				# Sorts the player's hand
				UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)] = list(sorted(player_hand))

				player_hand = UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)]

				tag = str(time.time()).split(".")[1] # Report the new hand
				uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=player_hand)

				await message.channel.send("You've drawn a card!",
				file=discord.File(f"Images/current_card_image_{tag}.png"))

				await UNO_INFO["channel"].send(f"**{message.author.name}** draws a card...")
				os.remove(f"Images/current_card_image_{tag}.png")

			for card in UNO_INFO["hands"][UNO_INFO["players"].index(message.author.id)]:
				if card[0] == UNO_INFO["last_card"][0] or card[1] == UNO_INFO["last_card"][1] or card[0] == "0":
					await message.channel.send(
					f"You have valid cards you can play! Use `{SERVER['PREFIX']}uno play` followed by a number to play one.")
					return [4, "UNO", UNO_INFO]

			await message.channel.send("You have no cards to play. Your turn is over!")
			if UNO_INFO["config"]["no-cards"]: # no-cards is whether or not to publicly announce you have no cards
				await UNO_INFO["channel"].send(f"**{message.author.name}** has no cards to play!")
			UNO_INFO["current"] = 0 # Signals that the turn is overs
			return [4, "UNO", UNO_INFO]

		else: # If it's not "draw" or a card
			await message.channel.send("That card number or action is not valid!")
			return

	if args[1].lower() == "quit":
		if not UNO_INFO["running"]: # If there's no round
			await message.channel.send("There's no Uno round to quit!")
			return
		
		if UNO_INFO["status"] == 1: # Redirect to tc/uno join
			await message.channel.send(
			f"To quit a game during signups, use `{SERVER['PREFIX']}uno join` again after already having joined.")
			return
		
		if message.author.id not in UNO_INFO["players"]: # If you're not a player
			await message.channel.send("You're not playing in the current uno round!")
			return
		
		player_index = UNO_INFO["players"].index(message.author.id) # Find the index of the player

		del UNO_INFO["players"][player_index] # Delete the player from the players list
		del UNO_INFO["hands"][player_index] # Delete their hand too

		UNO_INFO["order"].remove(message.author.id) # Remove them from the order

		await UNO_INFO["channel"].send(f"**{message.author.name} has quit the round!**")

		UNO_INFO["current"] = 0

		return [4, "UNO", UNO_INFO]

	if args[1].lower() == "end":
		if not UNO_INFO["running"]: # If there's no round
			await message.channel.send("There's no Uno round to end!")
			return

		if message.author.id != UNO_INFO["host"] and perms != 2: # Only the host and staff can end the game
			await message.channel.send("Only the host can end a game!")
			return
		
		await UNO_INFO["channel"].send("***The host has ended the round!***")
		UNO_INFO = uno_skip() # I've got a function for this, wow!
		return [4, "UNO", UNO_INFO]

	if args[1].lower() == "create":
		if UNO_INFO["running"]: # If a round has already been created
			await message.channel.send("There's already a Uno round in progress!")
			return

		UNO_INFO["running"] = True # There is now a round
		UNO_INFO["status"] = 1 # Joining period
		UNO_INFO["host"] = message.author.id # Set the host
		UNO_INFO["channel"] = message.channel # The channel in which the game started is used for game updates

		await message.channel.send(
		f"<@{message.author.id}> is creating a Uno round! Send `{SERVER['PREFIX']}uno join` to join it.")

		flag = False # Whether or not the timer is currently active
		sec = 0 # Variable to handle timers
		while True: # The signup while loop
			await asyncio.sleep(1) # Wait one second per iteration
			sec += 1

			if sec == 120: # If 2 out of 3 minutes have passed, warn the host to start quickly
				await message.channel.send(
				f"""<@{UNO_INFO["host"]}>, you have 60 seconds to start the Uno round! Use `{SERVER['PREFIX']}uno start` 
				to start it. If you don't do it in time, you'll be skipped as the host.
				""".replace("\n", "").replace("\t", ""))

			if len(UNO_INFO["players"]) < 2: # If there are less than two players there is no timer
				sec = 0
			
			if len(UNO_INFO["players"]) >= 2 and not flag: # If the timer is not active but it should be
				flag = True
				await message.channel.send(
				f"""Two players have joined the round. <@{UNO_INFO["host"]}> now has **three minutes** to start it 
				with `{SERVER['PREFIX']}uno start`!""".replace("\n", "").replace("\t", ""))
			
			if len(UNO_INFO["players"]) < 2 and flag: # If the timer is active but it shouldn't be
				flag = False
				await message.channel.send(
				"There is no longer a sufficient number of players to start. The start timer will be reset.")
			
			if sec >= 180: # If the host ran out of time
				await message.channel.send(f"**<@{UNO_INFO['host']}>** has been skipped from hosting the round.")
				UNO_INFO = uno_skip()
				return [4, "UNO", UNO_INFO]
			
			if UNO_INFO["status"] == 2: # Represents that the game has started
				break

		UNO_INFO["players"] = list(OrderedDict.fromkeys(UNO_INFO["players"]))
		UNO_INFO["order"] = UNO_INFO["players"] # Prepare the order

		start_cards = UNO_INFO["config"]["start"] # Amount of cards each person starts with
		
		if len(UNO_INFO["players"]) * start_cards + 10 > len(ORIGINAL_DECK): # If there are not enough cards on the
			# deck to suit the player count and/or starting card number

			# How many times to multiply the original deck and add it to the original to suit the card demand?
			multiplier = ((len(UNO_INFO["players"]) * start_cards + 10 - len(ORIGINAL_DECK)) // len(ORIGINAL_DECK)) + 1
			UNO_INFO["deck"] += ORIGINAL_DECK * multiplier

		random.shuffle(UNO_INFO["deck"]) # Shuffle the deck
		UNO_INFO["deck"] = UNO_INFO["deck"][0:]

		for player in UNO_INFO["players"]: # For each player
			UNO_INFO["hands"].append(UNO_INFO["deck"][:start_cards]) # Give the player their cards
			UNO_INFO["deck"] = UNO_INFO["deck"][start_cards:] # Remove those cards from the deck
			UNO_INFO["hands"][-1] = list(sorted(UNO_INFO["hands"][-1])) # Sort that hand

			tag = str(time.time()).split(".")[1] # Give the person their starting cards
			uno_image(2, tag, SERVER['PREFIX'], last="QC", hand=UNO_INFO["hands"][-1])
			await SERVER['MAIN'].get_member(player).send(
			"The Uno round is starting! Here's your hand:", 
			file=discord.File(f"Images/current_card_image_{tag}.png"))
			os.remove(f"Images/current_card_image_{tag}.png")

		for cards in range(len(UNO_INFO["deck"])): # Go through the deck
			if UNO_INFO["deck"][cards][0] == "0":
				continue # Find the first card that isn't a wild card
			
			UNO_INFO["last_card"] = UNO_INFO["deck"][cards] # Make that card the starting card
			UNO_INFO["deck"].remove(UNO_INFO["deck"][cards]) # Remove it from the deck
			break
		
		# Start it off
		await message.channel.send("The round has started! The starting card has been placed.")

		while True: # This is the handler for the entire game. Each iteration is a player's turn

			if len(UNO_INFO["deck"]) <= 10: # If there are too few cards
				UNO_INFO["deck"] += ORIGINAL_DECK # Add the original deck to the current one
				random.shuffle(UNO_INFO["deck"]) # Reshuffle
				UNO_INFO["deck"] = UNO_INFO["deck"][0:]

			UNO_INFO["players"] = list(OrderedDict.fromkeys(UNO_INFO["players"]))

			current_player = UNO_INFO["order"][0] # Get the current player having their turn
			player_index = UNO_INFO["players"].index(current_player) # This becomes useful later on
			UNO_INFO["current"] = current_player # Record the current player
			player_member = SERVER['MAIN'].get_member(current_player)
			player_name = player_member.name # Their username

			tag = str(time.time()).split(".")[1] # Make the image reporting that it's the player's turn
			uno_image(1, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], name=player_name)
			await message.channel.send(file=discord.File(f"Images/current_card_image_{tag}.png"))
			os.remove(f"Images/current_card_image_{tag}.png")

			if UNO_INFO["carryover"] > 1 or UNO_INFO["carryover"] < -3: # If there's cards to be drawn
				await message.channel.send( # Report so
				f"Someone played a **+{numpy.abs(UNO_INFO['carryover'])}** upon **{player_name}**!")
				await player_member.send(f"Someone played a **+{numpy.abs(UNO_INFO['carryover'])}** upon you!")

				defense = False # Can the player defend against the cards?
				for card in UNO_INFO["hands"][player_index]:
					if card[1] == "F" and UNO_INFO["carryover"] < -3: # If it's made of +4s and the player has one
						await SERVER['MAIN'].get_member(current_player).send("**You must play a +4 or draw the cards!**")
						defense = True
						break
					
					if card[1] == "D" and UNO_INFO["carryover"] > 1: # If it's made of +2s and the player has one
						await SERVER['MAIN'].get_member(current_player).send("**You must play a +2 or draw the cards!**")
						defense = True
						break
					
				if not defense: # If they can't defend, they have to draw
					dc = numpy.abs(UNO_INFO["carryover"]) # Report that the player drew the cards
					await message.channel.send(f"**{player_name}** draws {dc} cards!")

					UNO_INFO["hands"][player_index] += UNO_INFO["deck"][:dc] # Add the cards to the player's hand
					UNO_INFO["hands"][player_index] = list(sorted(UNO_INFO["hands"][player_index])) # Sort the hand
					UNO_INFO["deck"] = UNO_INFO["deck"][dc:] # Remove those cards from the deck

					tag = str(time.time()).split(".")[1] # Send the player their new hand
					uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=UNO_INFO["hands"][player_index])
					await player_member.send(f"You drew **{dc}** cards!",
					file=discord.File(f"Images/current_card_image_{tag}.png"))
					os.remove(f"Images/current_card_image_{tag}.png")

					UNO_INFO["carryover"] = 0 # Reset the carryovers

					if UNO_INFO["config"]["d-skip"]: # d-skip is whether players who drew from +2 or +4 are skipped
						UNO_INFO["order"] += UNO_INFO["order"][0:1]
						UNO_INFO["order"] = UNO_INFO["order"][1:]
					continue # Do another iteration. If they weren't skipped, it's still their turn

			tag = str(time.time()).split(".")[1] # Show the player their cards
			uno_image(0, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=UNO_INFO["hands"][player_index])
			await player_member.send("""It is now your turn to play a card!
			You have **1 minute** to play, or you'll be skipped.""",
			file=discord.File(f"Images/current_card_image_{tag}.png"))
			os.remove(f"Images/current_card_image_{tag}.png")

			sec = 0 # Second number
			played = UNO_INFO["current"] # Memory for what the current player is supposed to be
			while True: # Handler that waits for a card to be played
				await asyncio.sleep(1) # One second per iteration
				sec += 1

				if UNO_INFO["carryover"] == -2 and flag: # If the player has drawn 
					sec = 0 # Reset their timer
					await player_member.send(
					"Since you've drawn a card, your timer has been reset. You have **1 minute** to play.")
					flag = False

				if UNO_INFO["current"] != played:
					break # If the current player has been changed it means the turn ended

				if sec >= 60 and UNO_INFO["current"] == played: # If the 1 minute timer ran out, the player draws cards
					if UNO_INFO["carryover"] not in [0, 2]: # They draw the cards to be drawn if there are any
						dc = numpy.abs(UNO_INFO["carryover"])
					else: # Otherwise they draw one
						dc = 1

					UNO_INFO["hands"][player_index] += UNO_INFO["deck"][:dc] # Add the cards to the player's hand
					UNO_INFO["hands"][player_index] = list(sorted(UNO_INFO["hands"][player_index])) # Sort the hand
					UNO_INFO["deck"] = UNO_INFO["deck"][dc:] # Remove those cards from the deck

					UNO_INFO["carryover"] = 0 # Reset the carryover

					grammar = "" if dc == 1 else "s"

					tag = str(time.time()).split(".")[1] # Report their new hand
					uno_image(2, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], hand=UNO_INFO["hands"][player_index])

					await player_member.send(
					"You took too long to play! You will draw cards as punishment.",
					file=discord.File(f"Images/current_card_image_{tag}.png"))
					os.remove(f"Images/current_card_image_{tag}.png")
					await player_member.send("Your turn is over!")

					await message.channel.send(
					f"""**{player_name}** has been skipped for taking too long, drawing **{dc}** 
					card{'' if dc == 1 else 's'}.""".replace("\n", "").replace("\t", ""))
					break # Finish the while loop, turn ended
			
			if current_player not in UNO_INFO["players"]:
				continue

			if len(UNO_INFO["hands"][player_index]) == 1: # If the player has only one card... UNO!
				await message.channel.send(f"**{player_name} is at UNO!**")

			if (len(UNO_INFO["hands"][player_index]) == 0 or
			len(UNO_INFO["players"]) == 1): # If they have no cards, they win! Or also if everyone else quit
				tag = str(time.time()).split(".")[1] # Report the victory
				uno_image(3, tag, SERVER['PREFIX'], last=UNO_INFO["last_card"], name=player_name)
				await message.channel.send(f"**{player_name} WINS THE GAME!**", 
				file=discord.File(f"Images/current_card_image_{tag}.png"))
				os.remove(f"Images/current_card_image_{tag}.png")
				break # End the while loop of the whole game

			# If the game didn't end, increment the order
			UNO_INFO["order"] += UNO_INFO["order"][0:1]
			UNO_INFO["order"] = UNO_INFO["order"][1:]

			if UNO_INFO["carryover"] == -1: # -1 carryover means a skip card
				skipped_player = UNO_INFO["order"][0] # The next player over is skipped
				await message.channel.send(
				f"**{player_name}** skips **{SERVER['MAIN'].get_member(skipped_player).name}**'s turn!")
				UNO_INFO["order"] += UNO_INFO["order"][0:1] # Increment order again
				UNO_INFO["order"] = UNO_INFO["order"][1:]
			
			if UNO_INFO["carryover"] == -3: # -3 carryover means a reverse card
				if len(UNO_INFO["players"]) != 2: # Normal reverse card behavior
					UNO_INFO["order"] = UNO_INFO["order"][::-1] # Reverse the order list
					UNO_INFO["order"] += [current_player] # Add player to the end
					UNO_INFO["order"] = UNO_INFO["order"][1:] # Increment order
				else: # If there are only two people, reverse is identical to skip
					UNO_INFO["order"] += UNO_INFO["order"][0:1]
					UNO_INFO["order"] = UNO_INFO["order"][1:]

				await message.channel.send(f"**{player_name}** reversed the order!")

			if UNO_INFO["carryover"] in [-1, -2, -3]: # These three drawovers last for one turn only
				UNO_INFO["carryover"] = 0 # They're reset right after

		UNO_INFO = uno_skip() # The game is over! Reset the uno_info dict.
		return [4, "UNO", UNO_INFO]