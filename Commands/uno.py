from Config._functions import grammar_list, is_whole, uno_image, uno_skip
from Config._const import PREFIX, BRAIN, ORIGINAL_DECK

HELP = {
	"MAIN": "Command for a bot implementation of UNO",
	"FORMAT": "[subcommand]",
	"CHANNEL": 0,
	
	"USAGE": f"""wip
	""".replace("\n", "").replace("\t", "")
}

PERMS = 1 # Members
ALIASES = []
REQ = ["UNO", "TWOW_CENTRAL"]

async def MAIN(message, args, level, perms, uno_info, TWOW_CENTRAL):
	if len(args) == 1:
		await message.channel.send("You must include a command mode for that command!")
		return [4, "UNO", uno_info]

	if args[1].lower() == "join":
		if uno_info["status"] != 1:
			await message.channel.send("This Uno round is not in joining period!")
			return [4, "UNO", uno_info]
		
		if message.author.id in uno_info["players"]:
			uno_info["players"].remove(message.author.id)
			grammar = "" if len(uno_info["players"]) == 1 else "s"
			await message.channel.send("**<@{}>**, you have quit this round of Uno. Now, there are **{}** player{}.".format(
			message.author.id, len(uno_info["players"]), grammar))
			return [4, "UNO", uno_info]
		
		uno_info["players"].append(message.author.id)
		grammar = "" if len(uno_info["players"]) == 1 else "s"
		await message.channel.send("**<@{}>**, you have joined this round of Uno! There are now **{}** player{}.".format(
			message.author.id, len(uno_info["players"]), grammar))

	if args[1].lower() == "config":
		if uno_info["status"] == 0:
			await message.channel.send("There's no Uno round right now!")
			return [4, "UNO", uno_info]

		if len(args) == 2:
			tag = str(time.time()).split(".")[1]
			uno_image(4, tag, config=uno_info["config"])
			await message.channel.send("These is the current game options configuration.", file=discord.File("Images/current_card_image_{}.png".format(tag)))
			os.remove("Images/current_card_image_{}.png".format(tag))
			return [4, "UNO", uno_info]

		if uno_info["host"] != message.author.id:
			await message.channel.send("Only the current host can change the round options!")
			return [4, "UNO", uno_info]

		if uno_info["status"] != 1:
			await message.channel.send("You can only change the configurations before the game has started!")
			return [4, "UNO", uno_info]
		
		if not is_whole(args[2]):
			await message.channel.send("That's not a valid option number!")
			return [4, "UNO", uno_info]

		if not 1 <= int(args[2]) <= len(uno_info["config"]):
			await message.channel.send("That's not a valid option number!")
			return [4, "UNO", uno_info]

		chosen_index = int(args[2]) - 1

		if type(uno_info["config"][list(uno_info["config"].keys())[chosen_index]]) == bool:
			uno_info["config"][list(uno_info["config"].keys())[chosen_index]] = not uno_info["config"][list(uno_info["config"].keys())[chosen_index]]
			toggle = uno_info["config"][list(uno_info["config"].keys())[chosen_index]]

			await message.channel.send("The **{}** option has been turned **{}**!".format(
				list(uno_info["config"].keys())[chosen_index], "ON" if toggle else "OFF"
			))

		elif len(args) == 3:
			await message.channel.send("You must specify a number to change this configuration to!")
			return [4, "UNO", uno_info]
		
		elif not is_whole(args[3]):
			await message.channel.send("That's not a valid card number!")
			return [4, "UNO", uno_info]

		elif 2 > int(args[3]):
			await message.channel.send("Too few cards! The minimum starting number is **2**.")
			return [4, "UNO", uno_info]
		
		elif int(args[3]) > 30:
			await message.channel.send("I see you like making things excessive. Me too, honestly, but let's just keep it at **30** maximum, that's well excessive enough")
			return [4, "UNO", uno_info]
		
		else:
			uno_info["config"][list(uno_info["config"].keys())[chosen_index]] = int(args[3])
			await message.channel.send("The **{}** option has been set to **{}**!".format(list(uno_info["config"].keys())[chosen_index], args[3]))

		return [4, "UNO", uno_info]

	if args[1].lower() == "start":
		if uno_info["host"] != message.author.id:
			await message.channel.send("Only the current host of the game can start the Uno round!")
			return [4, "UNO", uno_info]

		if uno_info["status"] != 1:
			await message.channel.send("You can only start a Uno round during joining period!")
			return [4, "UNO", uno_info]
		
		if len(uno_info["players"]) < 2:
			await message.channel.send("You can only start a Uno round with two or more players!")
			return [4, "UNO", uno_info]
		
		uno_info["status"] = 2
		await message.channel.send("**The Uno round is starting!** Currently distributing cards...")
		return [4, "UNO", uno_info]

	if args[1].lower() == "play":
		if not uno_info["running"] or uno_info["status"] != 2:
			await message.channel.send("There's no Uno round in progress!")
			return [4, "UNO", uno_info]
		
		if uno_info["order"][0] != message.author.id:
			await message.channel.send("It's not your turn to play!")
			return [4, "UNO", uno_info]
		
		if len(args) == 2:
			await message.channel.send("You must include a card or an action to play!")
			return [4, "UNO", uno_info]
		
		if is_whole(args[2]):
			if 1 <= int(args[2]) <= len(uno_info["hands"][uno_info["players"].index(message.author.id)]):
				played_card = uno_info["hands"][uno_info["players"].index(message.author.id)][int(args[2]) - 1]

				if played_card[0] == "0" or played_card[1] in ["C", "F"]:
					if len(args) == 3:
						await message.channel.send("When playing a wild card, you must include the color you want to change the game to!\nTo include a color, put another number next to the command, corresponding to the color you want.\nAdd the number 1 for red, 2 for green, 3 for blue or 4 for yellow!\nExample: `d/uno play {} 3`, will play the card and change the color to **blue.**".format(args[2]))
						return [4, "UNO", uno_info]
						
					if not is_whole(args[3]):
						await message.channel.send("That's not a valid color number!")
						return [4, "UNO", uno_info]

					if 1 <= int(args[3]) <= 4:
						if uno_info["draw_carryover"] > 0:
							await message.channel.send("Someone has played a **+2** upon you. You must play another **+2** or draw the cards!\nTo draw the cards instantly, use `d/uno play draw`.")
							return [4, "UNO", uno_info]
						if played_card[1] == "F":
							uno_info["draw_carryover"] = -4 if uno_info["draw_carryover"] > -3 else uno_info["draw_carryover"] - 4
						elif uno_info["draw_carryover"] < -3:
							await message.channel.send("Someone has played a **+4** upon you. You must play another **+4** or draw the cards!\nTo draw the cards instantly, use `d/uno play draw`.")
							return [4, "UNO", uno_info]

						uno_info["hands"][uno_info["players"].index(message.author.id)].remove(played_card)
						uno_info["last_card"] = args[3] + played_card[1]
						
						tag = str(time.time()).split(".")[1]
						uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][uno_info["players"].index(message.author.id)])
						try:
							await message.channel.send("You have successfully played a card!", file=discord.File("Images/current_card_image_{}.png".format(tag)))
						except:
							await asyncio.sleep(2)
							await message.channel.send("You have successfully played a card!", file=discord.File("Images/current_card_image_{}.png".format(tag)))
						os.remove("Images/current_card_image_{}.png".format(tag))

						uno_info["current"] = 0
						return [4, "UNO", uno_info]

					else:
						await message.channel.send("That's not a valid color number!")
						return [4, "UNO", uno_info]

				elif played_card[0] == uno_info["last_card"][0] or played_card[1] == uno_info["last_card"][1]:
					if uno_info["draw_carryover"] < -3:
						await message.channel.send("Someone has played a **+4** upon you. You must play another **+4** or draw the cards!\nTo draw the cards instantly, use `d/uno play draw`.")
						return [4, "UNO", uno_info]
					elif played_card[1] == "D":
						uno_info["draw_carryover"] = 2 if uno_info["draw_carryover"] < 2 else uno_info["draw_carryover"] + 2
					elif uno_info["draw_carryover"] > 0:
						await message.channel.send("Someone has played a **+2** upon you. You must play another **+2** or draw the cards!\nTo draw the cards instantly, use `d/uno play draw`.")
						return [4, "UNO", uno_info]

					seven_f = False
					if played_card[1] == "7" and uno_info["config"]["0-7"]:
						if len(args) == 3:
							player_list = []
							for player in range(len(uno_info["players"])):
								if uno_info["players"][player] != message.author.id:
									player_list.append("[{}] - **{}** (Card count: {})".format(player + 1, TWOW_CENTRAL.get_member(uno_info["players"][player]).name, len(uno_info["hands"][player])))

							player_list = "\n".join(player_list)

							await message.channel.send("You must pick someone to trade hands with!\n\n{}\n\nTo successfully play the card and trade hands with someone, use `d/uno play {} x`, x being the number corresponding to the player.".format(player_list, args[2]))
							return [4, "UNO", uno_info]
						
						if not is_whole(args[3]):
							await message.channel.send("That player number is invalid!")
							return [4, "UNO", uno_info]
						
						if not 1 <= int(args[3]) <= len(uno_info["players"]):
							await message.channel.send("That player number is invalid!")
							return [4, "UNO", uno_info]
						
						seven_f = True
						await uno_info["channel"].send("**{}** is trading hands with someone...".format(message.author.name))

					uno_info["last_card"] = played_card
					uno_info["hands"][uno_info["players"].index(message.author.id)].remove(played_card)

					tag = str(time.time()).split(".")[1]
					uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][uno_info["players"].index(message.author.id)])
					try:
						await message.channel.send("You have successfully played a card!", file=discord.File("Images/current_card_image_{}.png".format(tag)))
					except:
						await asyncio.sleep(2)
						await message.channel.send("You have successfully played a card!", file=discord.File("Images/current_card_image_{}.png".format(tag)))
					os.remove("Images/current_card_image_{}.png".format(tag))

					if played_card[1] == "S":
						uno_info["draw_carryover"] = -1

					if played_card[1] == "R":
						uno_info["draw_carryover"] = -3

					if played_card[1] == "0" and uno_info["config"]["0-7"]:
						uno_info["hands"] += uno_info["hands"][0:1]
						uno_info["hands"] = uno_info["hands"][1:]

						await uno_info["channel"].send("**{} has rotated everyone's hand!**".format(message.author.name))
						for player in uno_info["players"]:
							tag = str(time.time()).split(".")[1]
							uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][uno_info["players"].index(player)])
							await TWOW_CENTRAL.get_member(player).send("Everyone's hand has rotated! This is your new hand!", file=discord.File("Images/current_card_image_{}.png".format(tag)))
							os.remove("Images/current_card_image_{}.png".format(tag))
					
					if seven_f:
						provisory_hand = uno_info["hands"][int(args[3]) - 1]
						uno_info["hands"][int(args[3]) - 1] = uno_info["hands"][uno_info["players"].index(message.author.id)]
						uno_info["hands"][uno_info["players"].index(message.author.id)] = provisory_hand
						await uno_info["channel"].send("**{}** trades hands with **{}**!".format(message.author.name, TWOW_CENTRAL.get_member(uno_info["players"][int(args[3]) - 1]).name))

						tag = str(time.time()).split(".")[1]
						uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][uno_info["players"].index(message.author.id)])
						await message.channel.send("This is your new hand!", file=discord.File("Images/current_card_image_{}.png".format(tag)))
						os.remove("Images/current_card_image_{}.png".format(tag))

						tag = str(time.time()).split(".")[1]
						uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][int(args[3]) - 1])
						await TWOW_CENTRAL.get_member(uno_info["players"][int(args[3]) - 1]).send("**{}** has traded their hand with you! This is your new hand.".format(message.author.name), file=discord.File("Images/current_card_image_{}.png".format(tag)))
						os.remove("Images/current_card_image_{}.png".format(tag))

					uno_info["current"] = 0
					return [4, "UNO", uno_info]

				else:
					await message.channel.send("That card is not valid!")
					return [4, "UNO", uno_info]
			else:
				await message.channel.send("That card number is not valid!")
				return [4, "UNO", uno_info]

		elif args[2].lower() == "draw":
			if uno_info["draw_carryover"] == -2:
				await message.channel.send("You've already drawn a card this turn!")
				return [4, "UNO", uno_info]
			
			if uno_info["draw_carryover"] > 0 or uno_info["draw_carryover"] < -3:
				uno_info["hands"][uno_info["players"].index(message.author.id)] += [uno_info["deck"][:numpy.abs(uno_info["draw_carryover"])]]
				uno_info["deck"] = uno_info["deck"][numpy.abs(uno_info["draw_carryover"]):]
				
				uno_info["hands"][uno_info["players"].index(message.author.id)] = list(sorted(uno_info["hands"][uno_info["players"].index(message.author.id)]))

				uno_info["draw_carryover"] = 0

				tag = str(time.time()).split(".")[1]
				uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][uno_info["players"].index(message.author.id)])
				await message.channel.send("You draw **{}** cards!".format(numpy.abs(uno_info["draw_carryover"])), file=discord.File("Images/current_card_image_{}.png".format(tag)))
				await uno_info["channel"].send("**{}** draws **{}** cards!".format(message.author.name, numpy.abs(uno_info["draw_carryover"])))
				os.remove("Images/current_card_image_{}.png".format(tag))

				if uno_info["d-skip"]:
					await message.channel.send("Your turn is over!")
					uno_info["current"] = 0
					return [4, "UNO", uno_info]
			
			else:

				uno_info["hands"][uno_info["players"].index(message.author.id)] += [uno_info["deck"][0]]
				uno_info["deck"] = uno_info["deck"][1:]
				uno_info["draw_carryover"] = -2

				uno_info["hands"][uno_info["players"].index(message.author.id)] = list(sorted(uno_info["hands"][uno_info["players"].index(message.author.id)]))

				tag = str(time.time()).split(".")[1]
				uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][uno_info["players"].index(message.author.id)])
				await message.channel.send("You've drawn a card!", file=discord.File("Images/current_card_image_{}.png".format(tag)))
				await uno_info["channel"].send("**{}** draws a card...".format(message.author.name))
				os.remove("Images/current_card_image_{}.png".format(tag))

			for card in uno_info["hands"][uno_info["players"].index(message.author.id)]:
				if card[0] == uno_info["last_card"][0] or card[1] == uno_info["last_card"][1] or card[0] == "0":
					await message.channel.send("You have valid cards you can play! Use `d/uno play` followed by a number to play one.")
					return [4, "UNO", uno_info]

			await message.channel.send("You have no cards to play. Your turn is over!")
			await uno_info["channel"].send("**{}** has no cards to play!".format(message.author.name))
			uno_info["current"] = 0

		else:
			await message.channel.send("That card number or action is not valid!")
			return [4, "UNO", uno_info]

	if args[1].lower() == "quit":
		if not uno_info["running"]:
			await message.channel.send("There's no Uno round to quit!")
			return [4, "UNO", uno_info]
		
		if uno_info["status"] == 1:
			await message.channel.send("To quit a game during signups, use `d/uno join` again after already having joined.")
			return [4, "UNO", uno_info]
		
		if message.author.id not in uno_info["players"]:
			await message.channel.send("You're not playing in the current uno round!")
			return [4, "UNO", uno_info]
		
		player_index = uno_info["players"].index(message.author.id)

		del uno_info["players"][player_index]
		del uno_info["hands"][player_index]

		uno_info["order"].remove(message.author.id)

		await uno_info["channel"].send("**{} has quit the round!**".format(message.author.name))

		uno_info["current"] = 0

		return [4, "UNO", uno_info]

	if args[1].lower() == "end":
		if not uno_info["running"]:
			await message.channel.send("There's no Uno round to quit!")
			return [4, "UNO", uno_info]

		if message.author.id != uno_info["host"] and perms != 2:
			await message.channel.send("Only the host can end a game!")
			return [4, "UNO", uno_info]
		
		await uno_info["channel"].send("***The host has ended the round!***")
		uno_skip()
		return [4, "UNO", uno_info]

	if args[1].lower() == "create":
		if uno_info["running"]:
			await message.channel.send("There's already a Uno round in progress!")
			return [4, "UNO", uno_info]

		uno_info["running"] = True
		uno_info["status"] = 1
		uno_info["host"] = message.author.id
		uno_info["channel"] = message.channel

		await message.channel.send("**<@{}>** is creating a Uno round! Send `d/uno join` to join it.".format(message.author.id))

		skipping = True
		flag = False
		sec = 0
		while True:
			await asyncio.sleep(1)
			sec += 1

			if sec == 120:
				await message.channel.send("**<@{}>**, you have 60 seconds to start the Uno round! Use `d/uno start` to start it. If you don't do it in time, you'll be skipped as the host.".format(
					uno_info["host"]))
			

			if len(uno_info["players"]) < 2:
				sec = 0
			
			if len(uno_info["players"]) >= 2 and not flag:
				flag = True
				await message.channel.send("Two players have joined the round. **<@{}>** now has **three minutes** to start it with `d/uno start`!".format(
					uno_info["host"]))
			
			if len(uno_info["players"]) < 2 and flag:
				flag = False
				await message.channel.send("There is no longer a sufficient number of players to start. The start timer will be reset.")
			
			if sec >= 180:
				await message.channel.send("**<@{}>** has been skipped from hosting the round.".format(
					uno_info["host"]))
				uno_skip()
				return [4, "UNO", uno_info]
			
			if uno_info["status"] == 2:
				break

		uno_info["players"] = list(OrderedDict.fromkeys(uno_info["players"]))

		uno_info["order"] = uno_info["players"]

		if len(uno_info["players"]) * uno_info["config"]["start"] + 10 > len(ORIGINAL_DECK):
			multiplier = ((len(uno_info["players"]) * uno_info["config"]["start"] + 10 - len(ORIGINAL_DECK)) // len(ORIGINAL_DECK)) + 1
			uno_info["deck"] += ORIGINAL_DECK * multiplier

		random.shuffle(uno_info["deck"])
		uno_info["deck"] = uno_info["deck"][0:]

		for player in uno_info["players"]:
			uno_info["hands"].append(uno_info["deck"][:uno_info["config"]["start"]])
			uno_info["deck"] = uno_info["deck"][uno_info["config"]["start"]:]
			uno_info["hands"][-1] = list(sorted(uno_info["hands"][-1]))

			tag = str(time.time()).split(".")[1]
			uno_image(2, tag, last="QC", hand=uno_info["hands"][-1])
			await TWOW_CENTRAL.get_member(player).send("The Uno round is starting! Here's your hand:", file=discord.File("Images/current_card_image_{}.png".format(tag)))
			os.remove("Images/current_card_image_{}.png".format(tag))

		for cards in range(len(uno_info["deck"])):
			if uno_info["deck"][cards][0] == "0":
				continue
			
			uno_info["last_card"] = uno_info["deck"][cards]
			uno_info["deck"].remove(uno_info["deck"][cards])
			break
		
		await message.channel.send("The round has started! The starting card has been placed.")

		while True:
			if len(uno_info["deck"]) <= 10:
				uno_info["deck"] += ORIGINAL_DECK
				random.shuffle(uno_info["deck"])
				uno_info["deck"] = uno_info["deck"][0:]

			uno_info["players"] = list(OrderedDict.fromkeys(uno_info["players"]))

			current_player = uno_info["order"][0]
			player_index = uno_info["players"].index(current_player)
			uno_info["current"] = current_player

			tag = str(time.time()).split(".")[1]
			uno_image(1, tag, last=uno_info["last_card"], name=TWOW_CENTRAL.get_member(current_player).name)
			await message.channel.send(file=discord.File("Images/current_card_image_{}.png".format(tag)))
			os.remove("Images/current_card_image_{}.png".format(tag))

			if uno_info["draw_carryover"] > 1 or uno_info["draw_carryover"] < -3:
				await message.channel.send("Someone played a **+{}** upon **{}**!".format(numpy.abs(uno_info["draw_carryover"]), TWOW_CENTRAL.get_member(current_player).name))
				await TWOW_CENTRAL.get_member(current_player).send("Someone played a **+{}** upon you!".format(numpy.abs(uno_info["draw_carryover"])))

				defense = False
				for card in uno_info["hands"][player_index]:
					if card[1] == "F" and uno_info["draw_carryover"] < -3:
						await TWOW_CENTRAL.get_member(current_player).send("**You must play a +4 or draw the cards!**")
						defense = True
						break
					
					if card[1] == "D" and uno_info["draw_carryover"] > 1:
						await TWOW_CENTRAL.get_member(current_player).send("**You must play a +2 or draw the cards!**")
						defense = True
						break
					
				if not defense:
					dc = numpy.abs(uno_info["draw_carryover"])
					await message.channel.send("**{}** draws {} cards!".format(TWOW_CENTRAL.get_member(current_player).name, dc))

					uno_info["hands"][player_index] += uno_info["deck"][:dc]
					uno_info["hands"][player_index] = list(sorted(uno_info["hands"][player_index]))
					uno_info["deck"] = uno_info["deck"][dc:]

					tag = str(time.time()).split(".")[1]
					uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][player_index])
					await TWOW_CENTRAL.get_member(current_player).send("You drew **{}** cards!".format(dc), file=discord.File("Images/current_card_image_{}.png".format(tag)))
					os.remove("Images/current_card_image_{}.png".format(tag))

					uno_info["draw_carryover"] = 0

					if uno_info["config"]["d-skip"]:
						uno_info["order"] += uno_info["order"][0:1]
						uno_info["order"] = uno_info["order"][1:]
					continue

			tag = str(time.time()).split(".")[1]
			uno_image(0, tag, last=uno_info["last_card"], hand=uno_info["hands"][player_index])
			await TWOW_CENTRAL.get_member(current_player).send("It is now your turn to play a card!\nYou have **1 minute** to play, or you'll be skipped.", file=discord.File("Images/current_card_image_{}.png".format(tag)))
			os.remove("Images/current_card_image_{}.png".format(tag))

			sec = 0
			skip = False
			flag = True
			played = uno_info["current"]
			while True:
				await asyncio.sleep(1)
				sec += 1

				if uno_info["draw_carryover"] == -2 and flag:
					sec = 0
					await TWOW_CENTRAL.get_member(current_player).send("Since you've drawn a card, your timer has been reset. You have **1 minute** to play.")
					flag = False

				if uno_info["current"] != played:
					break

				if sec >= 59 and uno_info["current"] == played:
					if uno_info["draw_carryover"] not in [0, 2]:
						dc = numpy.abs(uno_info["draw_carryover"])
					else:
						dc = 1

					uno_info["hands"][player_index] += uno_info["deck"][:dc]
					uno_info["hands"][player_index] = list(sorted(uno_info["hands"][player_index]))
					uno_info["deck"] = uno_info["deck"][dc:]

					uno_info["draw_carryover"] = 0

					grammar = "" if dc == 1 else "s"

					tag = str(time.time()).split(".")[1]
					uno_image(2, tag, last=uno_info["last_card"], hand=uno_info["hands"][player_index])
					await TWOW_CENTRAL.get_member(current_player).send("You took too long to play! You will draw cards as punishment.", file=discord.File("Images/current_card_image_{}.png".format(tag)))
					os.remove("Images/current_card_image_{}.png".format(tag))
					await TWOW_CENTRAL.get_member(current_player).send("Your turn is over!")
					await message.channel.send("**{}** has been skipped for taking too long, drawing **{}** card{}.".format(TWOW_CENTRAL.get_member(current_player).name, dc, grammar))
					skip = True
					break
			
			if current_player not in uno_info["players"]:
				continue

			if len(uno_info["hands"][player_index]) == 1:
				await message.channel.send("**{} is at UNO!**".format(TWOW_CENTRAL.get_member(current_player).name))

			if len(uno_info["hands"][player_index]) == 0:
				tag = str(time.time()).split(".")[1]
				uno_image(3, tag, last=uno_info["last_card"], name=TWOW_CENTRAL.get_member(current_player).name)
				await message.channel.send("**{} WINS THE GAME!**".format(TWOW_CENTRAL.get_member(current_player).name), file=discord.File("Images/current_card_image_{}.png".format(tag)))
				os.remove("Images/current_card_image_{}.png".format(tag))
				break

			if len(uno_info["players"]) == 1:
				tag = str(time.time()).split(".")[1]
				uno_image(3, tag, last=uno_info["last_card"], name=TWOW_CENTRAL.get_member(uno_info["players"][0]).name)
				await message.channel.send("**{} WINS THE GAME!**".format(TWOW_CENTRAL.get_member(uno_info["players"][0]).name), file=discord.File("Images/current_card_image_{}.png".format(tag)))
				os.remove("Images/current_card_image_{}.png".format(tag))
				break

			uno_info["order"] += uno_info["order"][0:1]
			uno_info["order"] = uno_info["order"][1:]

			if uno_info["draw_carryover"] == -1:
				skipped_player = uno_info["order"][0]
				await message.channel.send("**{}** skips **{}**'s turn!".format(TWOW_CENTRAL.get_member(current_player).name, TWOW_CENTRAL.get_member(skipped_player).name))
				uno_info["order"] += uno_info["order"][0:1]
				uno_info["order"] = uno_info["order"][1:]
			
			if uno_info["draw_carryover"] == -3:
				if len(uno_info["players"]) != 2:
					uno_info["order"] = uno_info["order"][::-1]
					uno_info["order"] += [current_player]
					uno_info["order"] = uno_info["order"][1:]
				else:
					uno_info["order"] += uno_info["order"][0:1]
					uno_info["order"] = uno_info["order"][1:]

				await message.channel.send("**{}** reversed the order!".format(TWOW_CENTRAL.get_member(current_player).name))

			if uno_info["draw_carryover"] in [-1, -2, -3]:
				uno_info["draw_carryover"] = 0

		uno_skip()
		return [4, "UNO", uno_info]