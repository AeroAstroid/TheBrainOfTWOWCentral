from Config._const import BRAIN
from Config._db import Database
import random, discord
from datetime import datetime, timezone
from calendar import monthrange
from Config._functions import is_whole

def HELP(PREFIX):
	return {
		"COOLDOWN": 1,
		"MAIN": "The command for birthday registering and viewing",
		"FORMAT": "(subcommand) (complements)",
		"CHANNEL": 0,
		"USAGE": f"""Using `{PREFIX}birthday` without a subcommand displays your own registered birthday. 
		Using `{PREFIX}birthday next` will show you the next birthday from now chronologically. Using 
		`{PREFIX}birthday user [username/id]` allows you to see that person's birthday, if they've registered one. 
		Using `{PREFIX}birthday register [dd/mm] (timezone)` will allow you to register or edit your birthday. 
		Using `{PREFIX}birthday month (month_number/month_name)` allows you to see all the birthdays in a given 
		month if you've specified one, or the current one if you didn't specify a month.
		""".replace("\n", "").replace("\t", ""),
		"CATEGORY" : "Community"
	}

PERMS = 0 # Non-members
ALIASES = ["BD"]
REQ = []

async def MAIN(message, args, level, perms, SERVER):
	db = Database()

	months = ["January", "February", "March", "April", "May", "June",
	"July", "August", "September", "October", "November", "December"]

	if level == 1: # If just tc/bd, return info on their birthday
		found = db.get_entries("birthday", conditions={"id": str(message.author.id)})

		if found == []:
			await message.channel.send(f"""You are yet to register your birthday!
			You can register by using **{SERVER["PREFIX"]}birthday register `DD/MM` `timezone`**""".replace("\t", ""))
			return

		birthday, tz = found[0][1:]
		birthday = birthday.split("/")

		birthday_format = months[int(birthday[1])-1] + " " + str(birthday[0])
		timezone_f = ("+" if tz > 0 else "") + str(tz)

		await message.channel.send(
		f"""**{message.author.name}**'s birthday is set as **{birthday_format}** in **UTC {timezone_f}**.""")
		return
	
	if args[1].lower() == "month":
		if level == 2:
			chosen_month = datetime.now(timezone.utc).month

		elif is_whole(args[2]):
			if int(args[2]) > 12 or int(args[2]) < 1:
				await message.channel.send(
					"Invalid month number. If you're picking a month number, choose one between 1 and 12!")
				return
			
			chosen_month = int(args[2])

		else:
			possible_months = [x for x in months if x.lower().startswith(args[2].lower())]

			if len(possible_months) == 0:
				new_possible = [x for x in months if args[2].lower() in x.lower()]

				if len(new_possible) == 0:
					await message.channel.send("There's no valid month with that name!")
					return
				
				if len(new_possible) > 1:
					await message.channel.send(
						f"""There are multiple months fitting that search key. Please specify which one you mean!
						`({', '.join(new_possible)})`""".replace("\t", ""))
					return
				
				possible_months = new_possible
			
			if len(possible_months) > 1:
				await message.channel.send(
					f"""There are multiple months fitting that search key. Please specify which one you mean!
					`({', '.join(possible_months)})`""".replace("\t", ""))
				return
			
			chosen_month = months.index(possible_months[0]) + 1
		
		found = db.get_entries("birthday")
		found = [k for k in found if int(k[1].split("/")[1]) == chosen_month]
		month_name = months[chosen_month - 1]

		if len(found) == 0:
			await message.channel.send(f"There are no registered birthdays in {month_name}!")
			return
		
		found = sorted(found, key=lambda k: int(k[1].split("/")[0]))

		messages = [f"Here are all the birthdays registered in {month_name}:\n\n"]

		for bd in found:
			try:
				username = f"**{SERVER['MAIN'].get_member(int(bd[0])).name}**"
			except Exception:
				username = f"**`[{bd[0]}]`**"
			
			day = bd[1].split("/")[0]
			tz = ("+" if bd[2] > 0 else "") + str(bd[2])

			line = f"> {username} - {month_name} {day}, UTC {tz}\n"

			if len(messages[-1]) + len(line) > 1900:
				messages.append("")
			
			messages[-1] += line
		
		for m in messages:
			await message.channel.send(m)
		
		return

	if args[1].lower() == "next":
		found = db.get_entries("birthday")
		found = sorted(found, key=lambda k: int(k[1].split("/")[0]))
		found = sorted(found, key=lambda k: int(k[1].split("/")[1]))

		day, month = datetime.now(timezone.utc).day, datetime.now(timezone.utc).month

		for bd in found:
			if int(bd[1].split("/")[1]) > month:
				next_bd = bd
				break
			elif int(bd[1].split("/")[1]) == month and int(bd[1].split("/")[0]) > day:
				next_bd = bd
				break
		else:
			next_bd = found[0]
		
		next_id, birthday, tz = next_bd
		birthday = birthday.split("/")
		birthday_format = months[int(birthday[1])-1] + " " + str(int(birthday[0]))
		timezone_f = ("+" if tz > 0 else "") + str(tz)

		try:
			username = SERVER["MAIN"].get_member(int(next_id)).name
		except AttributeError:
			username = next_id
		
		await message.channel.send(f"The next birthday is **{username}**'s, on **{birthday_format}** in **UTC {timezone_f}**.")
		return
	
	if args[1].lower() == "user":
		if level == 2:
			await message.channel.send("Include the username or ID of the person whose birthday you want to check.")
			return
		
		rest = " ".join(args[2:])

		if rest.startswith("<@") and rest.endswith(">"):
			rest = rest[2:-1]
		
		if is_whole(rest):
			found = db.get_entries("birthday", conditions={"id": rest})

			try:
				username = SERVER["MAIN"].get_member(int(rest)).name
			except:
				username = rest
			
			if found == []:
				await message.channel.send(f"**{username}** has not registered a birthday yet!")
				return
			
			user_bd = found[0]
			birthday, tz = user_bd[1:]
			birthday = birthday.split("/")
			birthday_format = months[int(birthday[1])-1] + " " + str(int(birthday[0]))
			timezone_f = ("+" if tz > 0 else "") + str(tz)

			await message.channel.send(f"**{username}**'s birthday is on **{birthday_format}** in **UTC {timezone_f}**.")
			return
		
		else:
			user = discord.utils.get(SERVER["MAIN"].members, name=rest)
			
			if user is None:
				await message.channel.send("That user is not in the server!")
				return
			
			found = db.get_entries("birthday", conditions={"id": str(user.id)})

			if found == []:
				await message.channel.send(f"**{rest}** has not registered a birthday yet!")
				return
			
			user_bd = found[0]
			birthday, tz = user_bd[1:]
			birthday = birthday.split("/")
			birthday_format = months[int(birthday[1])-1] + " " + str(int(birthday[0]))
			timezone_f = ("+" if tz > 0 else "") + str(tz)

			await message.channel.send(f"**{rest}**'s birthday is on **{birthday_format}** in **UTC {timezone_f}**.")
			return
	
	if args[1].lower() == "remove":
		found = db.get_entries("birthday", conditions={"id": str(message.author.id)})

		if found == []:
			await message.channel.send("You haven't registered a birthday yet to remove it!")
			return
		
		await message.channel.send(f"""Are you sure you want to remove your birthday from the database? Send `confirm` 
		in this channel to confirm. Send anything else to cancel.""".replace("\n", "").replace("\t", ""))

		# Wait for a message by the same author in the same channel
		msg = await BRAIN.wait_for('message', 
		check=(lambda m: m.channel == message.channel and m.author == message.author))

		if msg.content.lower() != "confirm": # If it's not `confirm`, cancel command
			await message.channel.send("Birthday registering cancelled.")
			return
		
		db.remove_entry("birthday", conditions={"id": str(message.author.id)})
		await message.channel.send("Your birthday has been removed from the database.")
		return

	if args[1].lower() == "register":
		if level == 2:
			await message.channel.send("Include your birthday in `DD/MM` to register!")
			return
			
		# Check if the person is in the birthday database or not
		found = db.get_entries("birthday", conditions={"id": str(message.author.id)})
		
		birthday = args[2].split("/")

		if level == 3:
			tz = 0

		elif not is_whole(args[3]):
			await message.channel.send("Invalid timezone! Make sure it's a whole number from -12 to 14!")
			return
		
		elif not -12 <= int(args[3]) <= 14:
			await message.channel.send("Invalid timezone! Make sure it's a whole number from -12 to 14!")
			return
		
		else:
			tz = int(args[3])

		if len(birthday) != 2: # If it's not `n/n`
			await message.channel.send("Invalid birthday! Make sure it's in the `DD/MM` format!")
			return
		
		if not is_whole(birthday[0]) or not is_whole(birthday[1]): # If day and month aren't numbers
			await message.channel.send("Invalid birthday! Make sure the day and month are both numbers!")
			return
		
		# Transform into integers for these next two checks
		birthday[0] = int(birthday[0])
		birthday[1] = int(birthday[1])
		
		if not 1 <= birthday[1] <= 12: # If month is invalid
			await message.channel.send("Invalid month! Make sure it's between 1 and 12.")
			return
		
		if not 1 <= birthday[0] <= monthrange(2020, birthday[1])[1]: # monthrange checks days in the month
			await message.channel.send( # 2020 months because it's a leap year, and 29/02 should be available
			f"Invalid day! Make sure it's between 1 and {monthrange(2020, birthday[1])[1]} for that month.")
			return
		
		birthday_format = months[birthday[1]-1] + " " + str(birthday[0])
		birthday = "/".join([str(x) for x in birthday]) # Join the list again for the next few lines
		timezone_f = ("+" if tz > 0 else "") + str(tz)

		# This confirmation message cannot be bypassed
		await message.channel.send(f"""Are you sure you want to record your birthday as {birthday_format} and your 
		timezone as UTC {timezone_f}? Send `confirm` in this channel to confirm.
		""".replace("\n", "").replace("\t", ""))
		
		# Wait for a message by the same author in the same channel
		msg = await BRAIN.wait_for('message', 
		check=(lambda m: m.channel == message.channel and m.author == message.author))

		if msg.content.lower() != "confirm": # If it's not `confirm`, cancel command
			await message.channel.send("Birthday registering cancelled.")
			return
		
		# If confirmation passed, record the birthday
		if found == []:
			is_new = ""
			db.add_entry("birthday", [message.author.id, birthday, tz])
		else:
			is_new = "new "
			db.edit_entry("birthday", entry={"birthday": birthday, "timezone": tz},
				conditions={"id": str(message.author.id)})

		await message.channel.send(f"Successfully recorded your {is_new}birthday as **{birthday} UTC {timezone_f}**!")
		return