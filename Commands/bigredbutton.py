from Config._const import PREFIX, DB_LINK
from Config._functions import key_generator, strip_alpha
import psycopg2, random, time, asyncio, discord
import numpy as np
from psycopg2 import sql

HELP = {
	"MAIN": "Command for the Big Red Button game",
	"FORMAT": "('press'/'top')",
	"CHANNEL": 4,
	"USAGE": f"""Using `{PREFIX}bigredbutton` will give you information on the current Big Red Button, such as its 
	chance of exploding and serial number. Using `{PREFIX}bigredbutton press` will press the button. If it doesn't 
	explode, you gain points equal to its chance of exploding. If it explodes, the button breaks and cannot be pressed 
	for 5 minutes, and you're incapacitated and cannot press any buttons for 6 hours. Once a button's pressed, a new 
	one is generated with a new serial number and chance of exploding. If the last digit of your user ID appears in 
	the serial number, the chances of the button exploding when you press it are multiplied by 0.67. If the first 
	letter of your username appears in the serial number, the chances of the button exploding when you press it are 
	multiplied by 2.""".replace("\n", "").replace("\t", "")
}

PERMS = 1 # Member
ALIASES = ["BUTTON"]
REQ = ["TWOW_CENTRAL"]

async def MAIN(message, args, level, perms, TWOW_CENTRAL):

	if isinstance(message.channel, discord.DMChannel):
		await message.channel.send("This command cannot be used in DMs!")
		return

	if level == 1:
		with psycopg2.connect(DB_LINK, sslmode="require") as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			cursor.execute(sql.SQL(""" SELECT button, info FROM "public.bigredbutton" LIMIT 1 """))
			button_info = cursor.fetchone()

			if button_info is None:
				button_number = 1
				serial_number = key_generator(random.randrange(8, 15))
				exploding_chance = random.randrange(15, 50)

				cursor.execute(sql.SQL(""" INSERT INTO "public.bigredbutton" VALUES (1, {serial}, '', '') """).format(
					serial = sql.Literal(f"{serial_number} {exploding_chance}")
				))

			elif len(button_info[1].split(" ")) == 1:
				pressing_time = int(button_info[1][2:])

				if button_info[1].startswith("0-"):
					left = int((pressing_time + 15) - time.time())
					await message.channel.send(f"The new button is currently being prepared! {left}s remain!")
					return
				
				if button_info[1].startswith("1-"):
					left = int((pressing_time + 300) - time.time())
					mn = int(left / 60)
					sc = left % 60
					await message.channel.send(f"The new button is being reconstructed. {mn}min {sc}s remain!")
					return

			else:
				button_number = button_info[0]
				serial_number = button_info[1].split(" ")[0]
				exploding_chance = button_info[1].split(" ")[1]
			
			await message.channel.send(
				f"""<:bigredbutton:654042578617892893> This is **Big Red Button #{button_number}**
				
				It has a **{exploding_chance}%** chance of exploding. The serial number is `{serial_number}`.
				Use `tc/bigredbutton press` to press this button!""".replace("\t", ""))

			return
	
	if args[1].lower() == "top":
		with psycopg2.connect(DB_LINK, sslmode="require") as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			cursor.execute(sql.SQL(""" SELECT points FROM "public.bigredbutton" LIMIT 1 """))
			unformatted_points = [x.split("-") for x in cursor.fetchone()[0].split(" ")]
			points = []
			
			for x in unformatted_points:
				try:
					x[0] = int(x[0])
					x[1] = int(x[1])
					points.append(x)
				except ValueError:
					continue
			
			points = sorted(points, reverse=True, key=lambda x: x[1])

			# args[2] is the page number.
			if level == 2: # If it's not specified, assume it's the first page
				points = points[:10]
				page = 1
			
			elif not is_whole(args[3]): # If it's not a valid integer, assume it's first page also
				points = points[:10]
				page = 1
			
			elif (int(args[2]) - 1) * 10 >= len(points): # Detect if the page number is too big
				await message.channel.send(f"There is no page {args[2]} on Big Red Button!")
				return
			
			else: # This means the user specified a valid page number
				lower = (int(args[2]) - 1) * 10
				upper = int(args[2]) * 10
				points = points[lower:upper]
				page = args[2]
			
			beginning = f"```diff\n---⭐ Big Red Button Points Leaderboard Page {page} ⭐---\n"
			beginning += "\n Rank |  Name                    |  Points\n"

			for person in points:
				r = points.index(person) + 1
				if r == 1:
					line = f"+ {r}{' ' * (4 - len(str(r)))}|  "
				else:
					line = f"- {r}{' ' * (4 - len(str(r)))}|  "
				
				try:
					member = TWOW_CENTRAL.get_member(int(person[0])).name
				except:
					member = str(person[0])

				line += f"{member[:20]}{' ' * (22 - len(member[:20]))}|  "
				line += str(person[1]) + "\n"
			
				beginning += line
			
			beginning += "```"
			
			await message.channel.send(beginning)
			return

	if args[1].lower() == "press":
		with psycopg2.connect(DB_LINK, sslmode="require") as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			cursor.execute(sql.SQL(""" SELECT * FROM "public.bigredbutton" LIMIT 1 """))
			button_info = cursor.fetchone()

			if len(button_info[1].split(" ")) == 1 and button_info[1] != "PRESSED":
				pressing_time = int(button_info[1][2:])

				if button_info[1].startswith("0-"):
					left = int((pressing_time + 15) - time.time())
					await message.channel.send(f"The new button is currently being prepared! {left}s remain!")
					return
				
				if button_info[1].startswith("1-"):
					left = int((pressing_time + 300) - time.time())
					mn = int(left / 60)
					sc = left % 60
					await message.channel.send(f"The new button is being reconstructed. {mn}min {sc}s remain!")
					return

			button_number = button_info[0]
			incapacitated = button_info[2]

			if str(message.author.id) in incapacitated:
				incapacitated = incapacitated.split(" ")

				ind = 0
				for incap in incapacitated:
					if incap.split("-")[0] == str(message.author.id):
						ind = incapacitated.index(incap)
						explosion_t = int(incap.split("-")[1])
						break

				delta = (explosion_t + 21600) - time.time()

				if delta < 0:
					del incapacitated[ind]

					incapacitated = " ".join(incapacitated)

					cursor.execute(sql.SQL(""" UPDATE "public.bigredbutton" SET incapacitated = {n_inc} """).format(
						n_inc = sql.Literal(incapacitated)
					))
				
				else:
					abs_delta = [
						int(delta), # Seconds
						int(delta / 60), # Minutes
						int(delta / (60 * 60))] # Hours
					
					sc = abs_delta[0] % 60
					mn = abs_delta[1] % 60
					hr = abs_delta[2]

					await message.channel.send(f"You are still incapacitated! Wait {hr}h {mn}min {sc}s to press again.")
					return

			if button_info[1] == "PRESSED":
				return
			else:
				cursor.execute(sql.SQL(""" UPDATE "public.bigredbutton" SET info = 'PRESSED' """))

			serial_number = button_info[1].split(" ")[0]
			exploding_chance = int(button_info[1].split(" ")[1])
			
			new_chance = exploding_chance
			if str(message.author.id)[-1] in serial_number:
				new_chance *= 0.67
			if strip_alpha(message.author.name)[0].upper() in serial_number:
				new_chance *= 2
			
			seed = random.uniform(0, 100)

			await message.channel.send(f"**{message.author.name}** presses the button, and...")
			await asyncio.sleep(3)

			if seed <= exploding_chance:
				n_button_info = f"1-{int(time.time())}"
				new_inc = f" {message.author.id}-{n_button_info[2:]}"
				points = button_info[3].split(" ")

				half_points = 0

				ind = -1
				for player in points:
					if player.split("-")[0] == str(message.author.id):
						ind = points.index(player)
						new_points = int(int(player.split("-")[1]) / 2)
						half_points = new_points
						points[ind] = f"{message.author.id}-{new_points}"
				
				if ind == -1:
					points.append(f"{message.author.id}-0")
				
				points = " ".join(points)

				cursor.execute(sql.SQL(
				""" UPDATE "public.bigredbutton" SET info = {n_info}, incapacitated = {n_inc}, 
				points = {n_points}""").format(
						n_info = sql.Literal(n_button_info),
						n_inc = sql.Literal(incapacitated + new_inc),
						n_points = sql.Literal(points)
				))

				await message.channel.send(
				f"""<:bigredbutton:654042578617892893> ***The #{button_number} Big Red Button blew up!***

				<@{message.author.id}> been incapacitated. Their point total is now **{half_points}**.
				They cannot press any more buttons for 6 hours.
				The button is broken. It'll take **5 minutes** to rebuild it.""".replace("\t", ""))

				await asyncio.sleep(300)
			
			else:
				points = button_info[3].split(" ")
				n_button_info = f"0-{int(time.time())}"

				ind = -1
				for player in points:
					if player.split("-")[0] == str(message.author.id):
						ind = points.index(player)
						new_points = int(player.split("-")[1]) + exploding_chance
						points[ind] = f"{message.author.id}-{new_points}"
				
				if ind == -1:
					points.append(f"{message.author.id}-{exploding_chance}")
				
				points = " ".join(points)
				
				cursor.execute(sql.SQL(
				""" UPDATE "public.bigredbutton" SET info = {n_info}, points = {n_points}
				""").format(
						n_info = sql.Literal(n_button_info),
						n_points = sql.Literal(points)
				))

				await message.channel.send(f"""
				<:bigredbutton:654042578617892893> The #{button_number} Big Red Button did nothing.

				<@{message.author.id}> gained {exploding_chance} points. Another button arrives in **15 seconds**.
				""".replace("\t", ""))

				await asyncio.sleep(15)

			serial_number = key_generator(random.randrange(8, 15))
			exploding_chance = random.randrange(15, 50)

			cursor.execute(
			sql.SQL(""" UPDATE "public.bigredbutton" SET button = button + 1, info = {n_info} """).format(
					n_info = sql.Literal(f"{serial_number} {exploding_chance}"),
			))

			await message.channel.send(f"""Big Red Button #{button_number+1} has arrived, now with a 
			{exploding_chance}% chance to explode and a serial number of `{serial_number}`!
			""".replace("\n", "").replace("\t", ""))

			return