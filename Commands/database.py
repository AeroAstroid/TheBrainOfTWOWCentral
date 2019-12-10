from Config._functions import grammar_list, is_whole, is_float
from Config._const import PREFIX, BRAIN, DB_LINK
import psycopg2, traceback
from psycopg2 import sql
from calendar import monthrange

HELP = {
	"MAIN": "Used to manage the Brain Postgres database",
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
	
	# Using a with statement on the database connection object is quite convenient. It automatically runs db.close()
	# when exiting the code through return statements, saving quite a lot of redundant lines of code
	with psycopg2.connect(DB_LINK, sslmode='require') as db:
		db.set_session(autocommit = True) # This commits to the database automatically - again, sparing the db.commit()
		cursor = db.cursor()

		if args[1].lower() == "table":

			if perms < 2: # Direct database viewing is staff-only
				await message.channel.send("You don't have permission to run this subcommand.")
				return

			if level == 2:
				# If it's just `tc/db table`, list the tables. This SQL statement grabs all tables from the 'public'
				# schema (which is where every table I use is)
				cursor.execute(""" SELECT tablename FROM pg_tables WHERE schemaname = 'public' """)
				# Automatically format the tables with bold for convenience
				table_list = [f'**{x[0].split(".")[1].upper()}**' for x in cursor.fetchall()]

				await message.channel.send(f"Here's a list of Brain Database's tables: {grammar_list(table_list)}")
				return
			
			if args[2].lower() == "add":

				# `tc/db table add` creates a table

				if level == 3:
					await message.channel.send("Include a name for the new table!")
					return
				
				if level == 4:
					await message.channel.send("Include the table's columns!")
					return
				
				# I personally prefer displaying database table names purely in uppercase when it comes to reading
				# but Postgres apparently requires table names to be lowercase. As such these two variables are
				# here to distinguish between what gets seen by the command user and what gets passed to the SQL
				name = args[3].upper()
				db_table = args[3].lower()

				if len(name) > 40:
					await message.channel.send("That table name is too long! 40 characters maximum.")
					return

				full_name = f"public.{db_table}" # Table identifiers require the schema name
				# I expect columns to be in the format `name-datatype name-datatype` and so on for each column.
				columns = [x.lower().split("-") for x in args[4:]]

				try:
					# Create the table! However, SQL-injection-proof code doesn't really allow me to write
					# statements creating tables with variable numbers of columns...
					cursor.execute(sql.SQL(""" CREATE TABLE {table_name} () """).format(
						table_name = sql.Identifier(full_name)))

					# ...so I have to add them individually, one by one, through ALTER TABLE. Dammit.
					for z in range(len(columns)):
						datatype = columns[z][1]
						if datatype not in ["text", "integer", "real"]:
							raise TypeError # These are all the data types to use. If it's not one of these, it's wrong

						# Generally in SQL-injection proof code, every single variable has to be formatted through
						# these braces with the sql.SQL() function, and specified as either sql.Identifier() or
						# sql.Literal(). Neither of these can actually be used with data types, so I resort to
						# adding the data type with python string addition. Since I've already limited the data
						# type to only three possibilities in the if statement above, this is not dangerous
						cursor.execute(sql.SQL(""" ALTER TABLE {table_name} ADD {column} """ + datatype).format(
							table_name = sql.Identifier(full_name),
							column = sql.Identifier(columns[z][0])
						))

				except Exception: # I might redo this and try to specify what the error actually is in the message
					await message.channel.send("Table creation failed! Make sure your name and columns are right.")
					return
				
				# Turn the `name-datatype` into `name datatype`, just for readability in the confirmation message
				columns = [" ".join(x) for x in columns]
				await message.channel.send(f"Table **{name}** created with columns {', '.join(columns)}")
				return

			if args[2].lower() == "remove":

				# `tc/db table remove` deletes (a.k.a. drops) a table

				if level == 3:
					await message.channel.send("Include the table you want to remove!")
					return
				
				cursor.execute(""" SELECT tablename FROM pg_tables WHERE schemaname = 'public' """)
				all_tables = [x[0].split(".")[1] for x in cursor.fetchall()]
				name = args[3].upper()
				db_table = args[3].lower()

				if db_table not in all_tables:
					await message.channel.send("There's no table with that name!")
					return

				full_name = f"public.{db_table}"
				
				# SQL command to drop a table
				cursor.execute(sql.SQL(""" DROP TABLE IF EXISTS {table_name}""").format(
					table_name = sql.Identifier(full_name)
				))
				
				await message.channel.send(f"Successfully deleted table **{name}**.")
				return
			
			if args[2].lower() == "layout":

				# `tc/db table layout` displays all columns and datatypes of a table

				if level == 3:
					await message.channel.send("Include the table you want to see the layout of!")
					return
				
				cursor.execute(""" SELECT tablename FROM pg_tables WHERE schemaname = 'public' """)
				all_tables = [x[0].split(".")[1] for x in cursor.fetchall()]
				name = args[3].upper()
				db_table = args[3].lower()

				if db_table not in all_tables:
					await message.channel.send("There's no table with that name!")
					return
				
				full_name = f"public.{db_table}"

				# This selects all columns in the entire database and their data types, and then limits them to
				# the relevant table with the WHERE statement
				cursor.execute(sql.SQL(""" SELECT column_name, data_type FROM information_schema.columns 
				WHERE table_name = {table_name}""").format(
					table_name = sql.Literal(full_name)
				))
				columns = cursor.fetchall()

				# Make them bold, in the format `name - datatype` and with arrows
				formatted = "\n> ".join([f"**{r}**" for r in [" - ".join(c) for c in columns]])

				await message.channel.send(
					f"Here are the colums and datatypes from the table **{name}**.\n> {formatted}")
				return
			
			if args[2].lower() == "entries":

				# `tc/db table entries` Displays, adds or removes entries of a table

				if level == 3:
					await message.channel.send("Include the table you want to see the layout of!")
					return
				
				cursor.execute(""" SELECT tablename FROM pg_tables WHERE schemaname = 'public' """)
				all_tables = [x[0].split(".")[1] for x in cursor.fetchall()]
				name = args[3].upper()
				db_table = args[3].lower()

				if db_table not in all_tables:
					await message.channel.send("There's no table with that name!")
					return
				
				full_name = f"public.{db_table}"
				
				get_entries = False

				# args[4] is the number of entries you want to see
				if level == 4: # If it's not specified, assume 10
					limit = 10
					get_entries = True

				elif args[4].lower() == "all": # If it's "all", just go with 99999. Better safe than sorry
					limit = 99999
					get_entries = True

				elif args[4].lower() not in ["add", "remove"]:
					# If it's not a further subcommand, interpret it as a number
					try:
						limit = int(args[4])
					except: # If it's not actually a number, just go with 10
						limit = 10
					get_entries = True
				
				# If get_entries is switched to true, that means the section above was able to extrapolate a number
				# from the command - meaning the user wants to see the table's entries, not add or remove them
				if get_entries:
					cursor.execute(sql.SQL(""" SELECT * FROM {table_name} LIMIT {limit}""").format(
						table_name = sql.Identifier(full_name),
						limit = sql.Literal(limit) # SQL can automatically return just the number of entries we want
					))
					entries = cursor.fetchall()

					# "\t".join([str(h) for h in e]) returns a single entry, with all its columns joined by tabs
					# ["\t".join([str(h) for h in e]) for e in entries] returns a list of those entry strings
					# `formatted` is set to all those entries together, separated by newlines and in arrow text
					formatted = "\n> ".join(["\t".join([str(h) for h in e]) for e in entries])

					# Gotta have correct grammar
					reported_limit = 'all' if limit >= 99999 else limit
					plural = 'ies' if limit != 1 else 'y'

					to_send = f"Here are {reported_limit} entr{plural} of **{name}**.\n> {formatted}"

					# Limit messages to 1950 characters at most. Cut them off if bigger. Getting any closer to 2000
					# can cause errors regardless for some reason, so I try to avoid it
					if len(to_send) > 1950:
						to_send = to_send[:1947] + "..."
					await message.channel.send(to_send)
					return
				
				if args[4].lower() == "add":
					# I expect arguments for this to be `value1 // value2 // value3` and so on
					arguments = " ".join(args[5:]).split(" // ")

					# Automatically detect values that are meant to be ints and floats instead of strings. Is there
					# any actual issue if someone wanting to store a number as a string can't do it? I'm not sure, but
					# I feel like dealing with that is unnecessary at the moment
					for data in range(len(arguments)):
						if is_whole(arguments[data]):
							arguments[data] = int(arguments[data])
						if is_float(arguments[data]):
							arguments[data] = float(arguments[data])

					try:
						# Using python string addition to have a variable amount of %s corresponding to arguments
						cursor.execute(sql.SQL(""" INSERT INTO {table_name} VALUES (""" 
							+ ", ".join(["%s"] * len(arguments)) + ")"
						).format(
							table_name = sql.Identifier(full_name)
						), arguments)
					except Exception: # Again, I might improve this error specification later
						await message.channel.send(
							"Failed to add entry! Make sure the columns and data types are right.")
						return
					
					await message.channel.send(f"Successfully added entry to table **{name}**!")
					return
				
				if args[4].lower() == "remove":

					if level == 5: # Specifying no arguments will delete the entire table's contents
						cursor.execute(sql.SQL(""" DELETE from {table_name} """).format(
							table_name = sql.Identifier(full_name)
						))
						await message.channel.send(f"Successfully cleared all entries from table **{name}**!")
						return
					
					# Arguments for this should be `column // value`, as a key to determine what should be deleted
					arguments = " ".join(args[5:]).split(" // ")

					cursor.execute(sql.SQL(""" SELECT column_name FROM information_schema.columns 
					WHERE table_name = {table_name}""").format(
						table_name = sql.Literal(full_name),
					))

					columns = cursor.fetchall()
					
					if (arguments[0].lower(),) not in columns: # Check that the column you're going by actually exists
						await message.channel.send(f"`{args[5].lower()}` is not a valid column for **{name}**!")
						return
					
					if len(arguments) == 1: # Can't specify a column without specifying a value for it
						await message.channel.send(f"Add a key to search the `{args[5].lower()}` column by!")
						return
					
					# So far, this command only supports deleting entries based on fulfilling one condition.
					# If I were to add support for multiple conditions, I'd also have to add support for AND
					# and OR statements with those conditions, and with variable SQL statements that'd get
					# messy real fast. Maybe one day, but for now, this is what you get.
					cursor.execute(sql.SQL(""" DELETE FROM {table_name} WHERE {column} = {value} """).format(
						table_name = sql.Identifier(full_name),
						column = sql.Identifier(arguments[0].lower()),
						value = sql.Literal(arguments[1])
					))

					await message.channel.send(f"Successfully deleted entries from table **{name}**!")
					return

	
		if args[1].lower() == "register": # Register yourself for database events like the birthday event

			if level == 2: # If it's just `tc/register`
				await message.channel.send("Choose an event to register yourself on!")
				return

			if args[2].lower() == "birthday":

				if level == 3:
					await message.channel.send("Include your birthday in `DD/MM` to register!")
					return
				
				cursor.execute(sql.SQL(""" SELECT id FROM "public.birthday" WHERE id = {person}""").format(
					person = sql.Literal(str(message.author.id))
				)) # Check if the person is in the birthday database or not
				found = cursor.fetchone()

				if found is not None: # If they are, don't bother (you can't edit it)
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
				
				birthday = "/".join([str(x) for x in birthday]) # Join the list again for the next few lines
				timezone_f = "+" if timezone > 0 else "" + str(timezone)

				# This confirmation message cannot be bypassed
				await message.channel.send(f"""Are you sure you want to record your birthday as {birthday} and your 
				timezone as UTC {timezone_f}? **You cannot edit these once recorded.** Send `confirm` in this channel 
				to confirm. """.replace("\n", "").replace("\t", ""))
				
				# Wait for a message by the same author in the same channel
				msg = await BRAIN.wait_for('message', 
				check=(lambda m: m.channel == message.channel and m.author == message.author))

				if msg.content.lower() != "confirm": # If it's not `confirm`, cancel command
					await message.channel.send("Birthday registering cancelled.")
					return
				
				# If confirmation passed, record the birthday
				cursor.execute(sql.SQL(""" INSERT INTO "public.birthday" VALUES (%s, %s, %s)"""),
				[message.author.id, birthday, timezone])

				await message.channel.send(f"Successfully recorded your birthday as **{birthday} UTC {timezone_f}**!")
				return
				
