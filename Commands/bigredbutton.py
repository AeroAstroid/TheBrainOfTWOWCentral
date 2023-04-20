from Config._const import DB_LINK
from Config._functions import key_generator, strip_alpha, is_whole, number_key
import random, time, asyncio, discord
import numpy as np

from Config._db import Database

def HELP(PREFIX):
	return {
		"COOLDOWN": 2,
		"MAIN": "Command for the Big Red Button game",
		"FORMAT": "('press'/'top')",
		"CHANNEL": 4,
		"USAGE": f"""Using `{PREFIX}bigredbutton` will give you information on the current Big Red Button, such as its 
		chance of exploding, serial number and inspector code. Using `{PREFIX}bigredbutton press` will press the button. 
		If it doesn't explode, you gain points equal to its chance of exploding. If it explodes, the button cannot be 
		pressed for 5 minutes. You also lose points, and cannot press any buttons for 6 hours. Once a button's pressed, 
		a new one is generated with new info. If the last digit of your user ID appears in the serial number, the button 
		has a 0.67x chance of exploding when YOU press it. If the first letter of your username appears in the serial 
		number, the button has a 2x chance of exploding.""".replace("\n", "").replace("\t", ""),
		"USAGE2": """Upon explosion, you lose half of your points. If the factory inspector's code shares two digits with 
		your discriminator, the button's explosion only takes away a quarter of your points. If it shares all three digits 
		with your discriminator, it only takes away one tenth of your points upon exploding. Shared digits can only be 
		paired once; an inspector code of 770 and a discriminator of 7316 only counts as one shared digit (because the 
		first 7 pairs with the 7 in the discriminator, but the other 7 has no other 7 to pair with. This is so 
		discriminators or inspector codes with repeating digits don't provide any advantage or disadvantage.)
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Fun"
	}

PERMS = 1 # Member
ALIASES = ["BUTTON"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):

	if isinstance(message.channel, discord.DMChannel): # Everyone should be able to see button presses
		await message.channel.send("This command cannot be used in DMs!")
		return

	db = Database()

	if level == 1: # `tc/button` will check the current button

		try:
			# "public.bigredbutton" always has a single entry unless there has never been a button. If len(button_info)
			# is 0, that's the case, and this will throw an error caught by the try except block.
			button_info = db.get_entries("bigredbutton", columns=["button", "info"])[0]
		except IndexError:
			button_info = db.get_entries("bigredbutton", columns=["button", "info"])

		if len(button_info) == 0: # If there is no button, create one
			button_number = 1 # It'd be the first ever button
			serial_number = key_generator(random.randrange(8, 15)) # Generate serial
			exploding_chance = random.randrange(15, 51) # 15 to 50% chance of exploding
			inspector = number_key(3) # Factory inspector code

			db.add_entry("bigredbutton", [1, f"{serial_number} {exploding_chance} {inspector}", "", ""])
			# Insert the new button info. Now there is a button, so skip to [*]

		elif button_info[1] == "PRESSED": # This is the 3 second interval after a button is pressed and before
			return # the outcome is announced. Ignore button checks for this period

		elif len(button_info[1].split(" ")) == 1: # [#]
			# Button, when in cooldown, has a single code for its info column, representing when it was pressed and
			# if it blew up or not. This code, unlike the normal `serial exp_chance` information, has no space in
			# it. This section detects that code

			pressing_time = int(button_info[1][2:]) # Time at which the button was pressed

			if button_info[1].startswith("0-"): # `0-time` means button didn't blow up
				left = int((pressing_time + 15) - time.time()) # Time left for button to come back

				if left < 0: # If it's negative, the button should've returned by now but didn't
					# So generate the button on the spot
					button_number = button_info[0] + 1 # Increment button number
					serial_number = key_generator(random.randrange(8, 15)) # Generate serial
					exploding_chance = random.randrange(15, 51) # 15 to 50% chance of exploding
					inspector = number_key(3) # Factory inspector code

					n_info = f"{serial_number} {exploding_chance} {inspector}"
					db.edit_entry("bigredbutton", entry={"button": button_number, "info": n_info})
					# Update with the new button

				else: # If it's not negative, and the timer hasn't ended, report the amount of time remaining
					await message.channel.send(f"The new button is currently being prepared! {left}s remain!")
					return
			
			if button_info[1].startswith("1-"): # `1-time` means the button blew up
				left = int((pressing_time + 300) - time.time()) # Time left for button to come back

				if left < 0: # Read above about the timer being negative
					button_number = button_info[0] + 1
					serial_number = key_generator(random.randrange(8, 15))
					exploding_chance = random.randrange(15, 51)
					inspector = number_key(3)

					n_info = f"{serial_number} {exploding_chance} {inspector}"
					db.edit_entry("bigredbutton", entry={"button": button_number, "info": n_info})
					# Update with new button

				else: # Report the actual timer if it hasn't ended yet
					mn = int(left / 60) # Extract minutes
					sc = left % 60 # Extract seconds
					await message.channel.send(f"The new button is being reconstructed. {mn}min {sc}s remain!")
					return

		else: # If there's a button and that's it
			button_number = button_info[0] # Report the button number...
			serial_number = button_info[1].split(" ")[0] # Its serial...
			exploding_chance = button_info[1].split(" ")[1] # ...Its explosion chance
			inspector = button_info[1].split(" ")[2] # And its inspector
		
		# [*] Report the current button
		await message.channel.send(
			f"""<:bigredbutton:654042578617892893> This is **Big Red Button #{button_number}**
			
			It has a **{exploding_chance}%** chance of exploding. The serial number is `{serial_number}`.
			It was inspected and approved by Factory Inspector #{inspector}.
			Use `tc/bigredbutton press` to press this button!""".replace("\t", ""))

		return

	if args[1].lower() == "forcegenerate" and perms >= 2:
		
		try:
			# "public.bigredbutton" always has a single entry unless there has never been a button. If len(button_info)
			# is 0, that's the case, and this will throw an error caught by the try except block.
			button_info = db.get_entries("bigredbutton", columns=["button", "info"])[0]
		except IndexError:
			button_info = db.get_entries("bigredbutton", columns=["button", "info"])
		
		button_number = button_info[0]
		serial_number = key_generator(random.randrange(8, 15))
		exploding_chance = random.randrange(15, 51)
		inspector = number_key(3)

		db.edit_entry("bigredbutton", entry={"button": button_number + 1, 
		"info": f"{serial_number} {exploding_chance} {inspector}"})
		
		await message.channel.send(
		f"""<:bigredbutton:654042578617892893> This is **Big Red Button #{button_number + 1}**

		It has a **{exploding_chance}%** chance of exploding. The serial number is `{serial_number}`.
		It was inspected and approved by Factory Inspector #{inspector}.
		Use `tc/bigredbutton press` to press this button!""".replace("\t", ""))
		
		return
			
	if args[1].lower() == "top": # Points leaderboard

		unformatted_points = db.get_entries("bigredbutton", columns=["points"])[0]
		unformatted_points = [x.split("-") for x in unformatted_points[0].split(" ")]
		# unformatted_points might include empty strings from how the points value is formatted
		points = [] # This variable will be the clean version

		for x in unformatted_points:
			try:
				x[0] = int(x[0])
				x[1] = int(x[1])
				points.append(x) # If it passed the int tests, append it to points
			except ValueError: # If it fails to convert to integers, it's an empty string and is ignored
				continue
		
		points = sorted(points, reverse=True, key=lambda x: x[1]) # Sort the leaderboard

		player_info = [x for x in points if x[0] == message.author.id][0]
		player_ind = points.index(player_info)

		# args[2] is the page number.
		if level == 2: # If it's not specified, assume it's the first page
			points = points[:10]
			page = 1
		
		elif not is_whole(args[2]): # If it's not a valid integer, assume it's first page also
			points = points[:10]
			page = 1
		
		elif (int(args[2]) - 1) * 10 >= len(points): # Detect if the page number is too big
			await message.channel.send(f"There is no page {args[2]} on Big Red Button!")
			return
		
		else: # This means the user specified a valid page number
			lower = (int(args[2]) - 1) * 10
			upper = int(args[2]) * 10
			points = points[lower:upper]
			page = int(args[2])
		
		# Top of the message
		beginning = f"```diff\n---⭐ Big Red Button Points Leaderboard Page {page} ⭐---\n"
		beginning += "\n Rank |  Name                  |  Points\n"

		for person in points:
			r = points.index(person) + 1 + (page - 1) * 10
			if r == 1: # + if the person is first
				line = f"+ {r}{' ' * (4 - len(str(r)))}|  "
			else: # - otherwise
				line = f"- {r}{' ' * (4 - len(str(r)))}|  "
			
			try: # Try to gather a username from the ID
				member = SERVER["MAIN"].get_member(int(person[0])).name
			except: # If you can't, just display the ID
				member = str(person[0])

			line += f"{member[:20]}{' ' * (22 - len(member[:20]))}|  " # Trim usernames to 20 characters long
			line += str(person[1]) + "\n" # Add points value and newline
		
			beginning += line # Add this line to the final message
		
		beginning += f"\nYour rank is {player_ind+1}, with {player_info[1]} points."
		beginning += "```" # Close off code block
		
		await message.channel.send(beginning)
		return


	if args[1].lower() == "press": # Press the button!

		button_info = db.get_entries("bigredbutton")[0]

		# This segment is almost an exact repeat of [#] up above
		if len(button_info[1].split(" ")) == 1 and button_info[1] != "PRESSED":
			pressing_time = int(button_info[1][2:])

			if button_info[1].startswith("0-"):
				left = int((pressing_time + 15) - time.time())

				if left < 0:
					button_number = button_info[0] + 1
					serial_number = key_generator(random.randrange(8, 15))
					exploding_chance = random.randrange(15, 51)
					inspector = number_key(3)

					n_info = f"{serial_number} {exploding_chance} {inspector}"
					db.edit_entry("bigredbutton", entry={"button": button_number, "info": n_info})

					await message.channel.send(f"""Big Red Button #{button_number} has arrived from inspection 
					by Factory Inspector #{inspector}, now with a {exploding_chance}% chance to explode and a 
					serial number of `{serial_number}`!""".replace("\n", "").replace("\t", ""))
					return

				else:
					await message.channel.send(f"The new button is currently being prepared! {left}s remain!")
					return
			
			if button_info[1].startswith("1-"):
				left = int((pressing_time + 300) - time.time())

				if left < 0:
					button_number = button_info[0] + 1
					serial_number = key_generator(random.randrange(8, 15))
					exploding_chance = random.randrange(15, 51)
					inspector = number_key(3)

					n_info = f"{serial_number} {exploding_chance} {inspector}"
					db.edit_entry("bigredbutton", entry={"button": button_number, "info": n_info})

					await message.channel.send(f"""Big Red Button #{button_number} has arrived from inspection 
					by Factory Inspector #{inspector}, now with a {exploding_chance}% chance to explode and a 
					serial number of `{serial_number}`!""".replace("\n", "").replace("\t", ""))
					return

				else:
					mn = int(left / 60)
					sc = left % 60
					await message.channel.send(f"The new button is being reconstructed. {mn}min {sc}s remain!")
					return

		# We already checked button_info[1], check two others now
		button_number = button_info[0]
		incapacitated = button_info[2]

		if str(message.author.id) in incapacitated: # If you're incapacitated
			incapacitated = incapacitated.split(" ")

			ind = 0 # Find the author in the incapacitated list and extract their explosion time
			for incap in incapacitated:
				if incap.split("-")[0] == str(message.author.id):
					ind = incapacitated.index(incap)
					explosion_t = int(incap.split("-")[1])
					break

			# Calculate how long it'll be before they can recover
			delta = (explosion_t + 21600) - time.time()

			if delta < 0: # If it's negative, then they already recovered and can go on
				del incapacitated[ind] # Delete the entry for this person

				incapacitated = " ".join(incapacitated) # Join the list

				# Update with the new incapacitated list
				db.edit_entry("bigredbutton", entry={"incapacitated": incapacitated})
			
			else: # If it's not negative, they still have to wait a little
				abs_delta = [
					int(delta), # Seconds
					int(delta / 60), # Minutes
					int(delta / (60 * 60))] # Hours
				
				sc = abs_delta[0] % 60
				mn = abs_delta[1] % 60
				hr = abs_delta[2]

				await message.channel.send(f"You are still incapacitated! Wait {hr}h {mn}min {sc}s to press again.")
				return

		if strip_alpha(message.author.name) == "":
			return # Don't try to cheese it by having no letters

		if button_info[1] == "PRESSED": # If it's currently being pressed, ignore this press
			return
		else: # Mark this button as being pressed so nobody else presses it during the 3 second interval
			db.edit_entry("bigredbutton", entry={"info": "PRESSED"})

		# Gather serial_number and exploding_chance for calculations
		serial_number = button_info[1].split(" ")[0]
		exploding_chance = int(button_info[1].split(" ")[1])
		inspector = list(button_info[1].split(" ")[2])
		
		new_chance = exploding_chance # Clean slate variable
		if str(message.author.id)[-1] in serial_number:
			new_chance *= 0.67 # If last digit of ID is in serial...
		
		if strip_alpha(message.author.name)[0].upper() in serial_number:
			new_chance *= 2 # If first letter of username is in serial...
		
		point_retention = 0.5
		share_count = 0
		disc = list(str(message.author.discriminator))
		for x in range(len(list(inspector))):
			if inspector[x] in disc:
				share_count += 1
				disc.remove(inspector[x])
				inspector[x] = "-"

		if share_count == 2:
			point_retention = 0.75
		if share_count == 3:
			point_retention = 0.9
		
		seed = random.uniform(0, 100) # Has to be above the explosion chance otherwise it explodes

		await message.channel.send(f"**{message.author.name}** presses the button, and...")
		await asyncio.sleep(3) # Suspense!

		if seed <= new_chance: # If it's under the explosion chance, it blows up
			n_button_info = f"1-{int(time.time())}" # Remember, `1-time` is the explosion flag
			new_inc = f" {message.author.id}-{n_button_info[2:]}" # Add this person to the incapacitated list
			points = button_info[3].split(" ") # Get the points list

			new_points = 0

			ind = -1 # Find the player in the points list and halve their point count
			for player in points:
				if player.split("-")[0] == str(message.author.id):
					ind = points.index(player)
					new_points = int(int(player.split("-")[1]) * point_retention)
					points[ind] = f"{message.author.id}-{new_points}"
			
			if ind == -1: # If ind is still -1, then the player wasn't found in the points list so create a new
				points.append(f"{message.author.id}-{new_points}") # entry for them with 0 points
			
			points = " ".join(points)

			db.edit_entry("bigredbutton", 
			entry={"info": n_button_info, "points": points, "incapacitated": incapacitated + new_inc})
			# Update with the explosion info, the new incapacitated list, and the new points list

			await message.channel.send(
			f"""<:bigredbutton:654042578617892893> ***The #{button_number} Big Red Button blew up!***

			<@{message.author.id}> has been incapacitated. Their point total is now **{new_points}**.
			They cannot press any more buttons for 6 hours.
			The button is broken. It'll take **5 minutes** to rebuild it.""".replace("\t", ""))

			await asyncio.sleep(300) # Five minutes until the button is back
		
		else: # If seed > new_chance, it doesn't blow up
			points = button_info[3].split(" ") # Get points list to add points
			n_button_info = f"0-{int(time.time())}" # `0-time` means no explosion

			ind = -1 # Find player in points list and add the new points
			for player in points:
				if player.split("-")[0] == str(message.author.id):
					ind = points.index(player)
					# Note: the points they gain is ALWAYS the nominal value for the exploding chance, not the
					# modified serial number chance that was used to calculate explosions
					new_points = int(player.split("-")[1]) + exploding_chance
					points[ind] = f"{message.author.id}-{new_points}"
			
			if ind == -1: # If they're not in the points list, add them with the new point value
				points.append(f"{message.author.id}-{exploding_chance}")
			
			points = " ".join(points)
			
			db.edit_entry("bigredbutton", 
			entry={"info": n_button_info, "points": points})
			# Update with the pressing info and the new points list

			await message.channel.send(f"""
			<:bigredbutton:654042578617892893> The #{button_number} Big Red Button did nothing.

			<@{message.author.id}> gained {exploding_chance} points. Another button arrives in **15 seconds**.
			""".replace("\t", ""))

			await asyncio.sleep(15) # Fifteen seconds until the button is back

		# Generate new serial_number and exploding_chance
		button_number += 1
		serial_number = key_generator(random.randrange(8, 15))
		exploding_chance = random.randrange(15, 51)
		inspector = number_key(3)

		n_info = f"{serial_number} {exploding_chance} {inspector}"
		db.edit_entry("bigredbutton", entry={"button": button_number, "info": n_info})
		# Update table with the new button

		# Announce the new button
		await message.channel.send(f"""Big Red Button #{button_number} has arrived from inspection 
		by Factory Inspector #{inspector}, now with a {exploding_chance}% chance to explode and a 
		serial number of `{serial_number}`!""".replace("\n", "").replace("\t", ""))
		return
