from Config._functions import grammar_list, is_whole, is_float
from Config._const import PREFIX, BRAIN
import traceback
from calendar import monthrange

from Config._db import Database

HELP = {
	"MAIN": "Command used to interact with the Brain Postgres database",
	"FORMAT": "[subcommand]",
	"CHANNEL": 0,
	"USAGE": f"""wip
	""".replace("\n", "").replace("\t", "")
}

PERMS = 1 # Member
ALIASES = ["DB"]
REQ = []

async def MAIN(message, args, level, perms):
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return

	db = Database()

	# Staff command used to manage the database
	if args[1].lower() == "main":

		if perms < 2: # Direct database viewing is staff-only
			await message.channel.send("You don't have permission to run this subcommand.")
			return


		if level == 2: # If it's just `tc/db main`, list the tables using the get_tables() function.
			table_list = db.get_tables()
			table_list = [f'**{table.upper()}**' for table in table_list]
			await message.channel.send(f"Here's a list of Brain Database's tables: {grammar_list(table_list)}")
			return
		

		if args[2].lower() == "add": # `tc/db main add` creates a table

			if level == 3:
				await message.channel.send("Include a name for the new table!")
				return
			
			if level == 4:
				await message.channel.send("Include the table's columns!")
				return
			
			# I expect columns to be in the format `name-datatype name-datatype` and so on for each column.
			name = args[3].lower()
			columns = [x.lower().split("-") for x in args[4:]]

			db.add_table(name, columns)
			
			# Turn the `name-datatype` into `name datatype`, just for readability in the confirmation message
			columns = [" ".join(x) for x in columns]
			await message.channel.send(f"Table **{name.upper()}** created with columns {', '.join(columns)}")
			return


		if args[2].lower() == "remove": # `tc/db main remove` deletes (a.k.a. drops) a table

			if level == 3:
				await message.channel.send("Include the table you want to remove!")
				return

			name = args[3].lower()

			db.remove_table(name)
			
			await message.channel.send(f"Successfully deleted table **{name.upper()}**.")
			return
		

		if args[2].lower() == "layout": # `tc/db main layout` displays all columns and datatypes of a table

			if level == 3:
				await message.channel.send("Include the table you want to see the layout of!")
				return
		
			name = args[3].lower()

			columns = db.get_columns(name, include_type=True)

			# Make them bold, in the format `name - datatype` and with arrows
			formatted = "\n> ".join([f"**{r}**" for r in [" - ".join(c) for c in columns]])

			await message.channel.send(
				f"Here are the colums and datatypes from the table **{name.upper()}**.\n> {formatted}")
			return
		

		if args[2].lower() == "entries": # `tc/db main entries` Displays, adds or removes entries of a table

			if level == 3:
				await message.channel.send("Include the table you want to see the layout of!")
				return
			
			name = args[3].lower()
			get_entries = False

			# args[4] is the number of entries you want to see
			if level == 4: # If it's not specified, assume 10
				limit = 10
				get_entries = True

			elif args[4].lower() == "all": # If it's "all", just go with 99999. Better safe than sorry
				limit = 99999
				get_entries = True

			elif args[4].lower() not in ["add", "remove", "edit"]:
				# If it's not a further subcommand, interpret it as a number
				try:
					limit = int(args[4])
				except: # If it's not actually a number, just go with 10
					limit = 10
				get_entries = True
			
			# If get_entries is switched to true, that means the section above was able to extrapolate a number
			# from the command - meaning the user wants to see the table's entries, not add or remove them
			if get_entries:
				entries = db.get_entries(name, limit=limit)

				# "\t".join([str(h) for h in e]) returns a single entry, with all its columns joined by tabs
				# ["\t".join([str(h) for h in e]) for e in entries] returns a list of those entry strings
				# `formatted` is set to all those entries together, separated by newlines and in arrow text
				formatted = "\n> ".join(["\t".join([str(h) for h in e]) for e in entries])

				# Gotta have correct grammar
				reported_limit = 'all' if limit >= 99999 else limit
				plural = 'ies' if limit != 1 else 'y'

				to_send = [f"Here are {reported_limit} entr{plural} of **{name.upper()}**.\n> {formatted}"]

				# Limit messages to 1950 characters at most. Cut them off if bigger. Getting any closer to 2000
				# can cause errors regardless for some reason, so I try to avoid it
				if len(to_send[0]) > 1950:
					to_send.append(f"> {to_send[0][1947:3900]}")
					to_send[0] = to_send[0][:1947] + "..."

				for z in to_send:
					await message.channel.send(z)
				return
			
			
			if args[4].lower() == "add":
				# I expect arguments for this to be `value1 // value2 // value3` and so on
				arguments = " ".join(args[5:]).split(" // ")

				db.add_entry(name, arguments)
				
				await message.channel.send(f"Successfully added entry to table **{name.upper()}**!")
				return
			

			if args[4].lower() == "remove":

				if level == 5:
					await message.channel.send("Include a search column!")
					return

				if level == 6 and args[5].lower() == "all": # Delete all entries in the table
					await message.channel.send(f"""Are you sure you want to delete all entries in **{name.upper()}**? 
					Send `confirm` to transfer.""".replace("\n", "").replace("\t", ""))
					
					# Check for the next message by the same person in the same channel
					msg = await BRAIN.wait_for('message', 
					check=lambda m: (m.author == message.author and m.channel == message.channel))

					if msg.content.lower() != "confirm": # If it's not `confirm`, cancel the command
						await message.channel.send("Database command cancelled.")
						return

					db.remove_entry(name)

					await message.channel.send(f"Successfully cleared all entries from table **{name.upper()}**!")
					return
				

				# Arguments for this should be `column // value`, as a key to determine what should be deleted
				arguments = " ".join(args[5:]).split(" // ")
				
				if len(arguments) % 2 == 1: # Odd number of arguments means one key has no value
					await message.channel.send("Include a value for every updating column!")
					return
				
				conditions = {}
				for z in range(int(len(arguments) / 2)):
					conditions[arguments[z*2]] = arguments[z*2+1]
				
				db.remove_entry(name, conditions)

				await message.channel.send(f"Successfully deleted entries from table **{name.upper()}**!")
				return
			
			
			if args[4].lower() == "edit":

				if level < 8: # Requires at least 3 extra args: `upd_column // upd_key`
					await message.channel.send("Make sure to include the columns to update!")
					return
				
				if len(" ".join(args[5:]).split(" -> ")) == 2: # Split arguments into searching and updating
					searching_arguments = " ".join(args[5:]).split(" -> ")[0].split(" // ")
					updating_arguments = " ".join(args[5:]).split(" -> ")[1].split(" // ")
				else:
					searching_arguments = []
					updating_arguments = " ".join(args[5:]).split(" // ")

				if len(searching_arguments) % 2 == 1:
					await message.channel.send("Include a value for every search column!")
					return
				
				if len(updating_arguments) % 2 == 1:
					await message.channel.send("Include a value for every updating column!")
					return
				
				conditions = {}
				for z in range(int(len(searching_arguments) / 2)):
					conditions[searching_arguments[z*2]] = searching_arguments[z*2+1]
				
				entry = {}
				for z in range(int(len(updating_arguments) / 2)):
					entry[updating_arguments[z*2]] = updating_arguments[z*2+1]
				
				db.edit_entry(name, entry=entry, conditions=conditions)
				
				await message.channel.send(f"Successfully edited entries in **{name.upper()}**!")
				return


	if args[1].lower() == "register": # Register yourself for database events like the birthday event

		if level == 2: # If it's just `tc/register`
			await message.channel.send("Choose an event to register yourself on!")
			return

		if args[2].lower() == "birthday":

			if level == 3:
				await message.channel.send("Include your birthday in `DD/MM` to register!")
				return
			
			# Check if the person is in the birthday database or not
			found = db.get_entries("birthday", conditions={"id": str(message.author.id)})

			if len(found) >= 0: # If they are, don't bother (they can't edit it)
				await message.channel.send("You have already registered your birthday!")
				return
			
			birthday = args[3].split("/")

			if level == 4:
				timezone = 0

			elif not is_whole(args[4]):
				await message.channel.send("Invalid timezone! Make sure it's a whole number from -12 to 14!")
				return
			
			elif not -12 <= int(args[4]) <= 14:
				await message.channel.send("Invalid timezone! Make sure it's a whole number from -12 to 14!")
				return
			
			else:
				timezone = int(args[4])

			if len(birthday) != 2: # If it's not `n/n`
				await message.channel.send("Invalid birthday! Make sure it's in the `DD/MM` format!")
				return
			
			if not is_whole(birthday[0]) or not is_whole(birthday[1]): # If day and month aren't numbers
				await message.channel.send("Invalid birthday! Make sure the day and year are both numbers!")
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
			
			months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
			birthday_format = months[birthday[1]-1] + " " + str(birthday[0])
			birthday = "/".join([str(x) for x in birthday]) # Join the list again for the next few lines
			timezone_f = ("+" if timezone > 0 else "") + str(timezone)

			# This confirmation message cannot be bypassed
			await message.channel.send(f"""Are you sure you want to record your birthday as {birthday_format} and your 
			timezone as UTC {timezone_f}? **You cannot edit these once recorded.** Send `confirm` in this channel 
			to confirm. """.replace("\n", "").replace("\t", ""))
			
			# Wait for a message by the same author in the same channel
			msg = await BRAIN.wait_for('message', 
			check=(lambda m: m.channel == message.channel and m.author == message.author))

			if msg.content.lower() != "confirm": # If it's not `confirm`, cancel command
				await message.channel.send("Birthday registering cancelled.")
				return
			
			# If confirmation passed, record the birthday
			db.add_entry("birthday", [message.author.id, birthday, timezone])

			await message.channel.send(f"Successfully recorded your birthday as **{birthday} UTC {timezone_f}**!")
			return
			