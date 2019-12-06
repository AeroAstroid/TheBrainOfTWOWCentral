from Config._functions import grammar_list, is_whole, is_float
from Config._const import PREFIX, BRAIN, DB_LINK
import psycopg2, traceback
from psycopg2 import sql

HELP = {
	"MAIN": "Used to manage the Brain Postgres database",
	"FORMAT": "wip",
	"CHANNEL": 2,
	"USAGE": f"""wip
	""".replace("\n", "").replace("\t", "")
}

PERMS = 2
ALIASES = ["DB"]
REQ = []

async def MAIN(message, args, level, perms):
	if level == 1:
		await message.channel.send("Include a subcommand!")
		return
	
	with psycopg2.connect(DB_LINK, sslmode='require') as db:
		db.set_session(autocommit = True)
		cursor = db.cursor()

		if args[1].lower() == "table":

			if level == 2:
				cursor.execute(""" SELECT tablename FROM pg_tables WHERE schemaname = 'public' """)
				table_list = [f'**{x[0].split(".")[1].upper()}**' for x in cursor.fetchall()]

				await message.channel.send(f"Here's a list of Brain Database's tables: {grammar_list(table_list)}")
				return
			
			if args[2].lower() == "add":

				if level == 3:
					await message.channel.send("Include a name for the new table!")
					return
				
				if level == 4:
					await message.channel.send("Include the table's columns!")
					return
				
				name = args[3].upper()
				db_table = args[3].lower()

				if len(name) > 40:
					await message.channel.send("That table name is too long! 40 characters maximum.")
					return

				full_name = f"public.{db_table}"
				columns = [x.lower().split("-") for x in args[4:]]

				try:
					cursor.execute(sql.SQL(""" CREATE TABLE {table_name} () """).format(
						table_name = sql.Identifier(full_name)))

					for z in range(len(columns)):
						datatype = columns[z][1]

						if datatype not in ["text", "integer", "real"]:
							raise TypeError

						cursor.execute(sql.SQL(""" ALTER TABLE {table_name} ADD {column} """ + datatype).format(
							table_name = sql.Identifier(full_name),
							column = sql.Identifier(columns[z][0])
						))
				except Exception:
					await message.channel.send("Table creation failed! Make sure your name and columns are right.")
					return
				
				columns = [" ".join(x) for x in columns]
				await message.channel.send(f"Table **{name}** created with columns {', '.join(columns)}")
				return

			if args[2].lower() == "remove":

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
				
				cursor.execute(sql.SQL(""" DROP TABLE IF EXISTS {table_name}""").format(
					table_name = sql.Identifier(full_name)
				))
				
				await message.channel.send(f"Successfully deleted table **{name}**.")
				return
			
			if args[2].lower() == "layout":

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

				cursor.execute(sql.SQL(""" SELECT column_name, data_type FROM information_schema.columns 
				WHERE table_name = {table_name}""").format(
					table_name = sql.Literal(full_name)
				))
				columns = cursor.fetchall()

				formatted = "\n> ".join([f"**{r}**" for r in [" - ".join(c) for c in columns]])

				await message.channel.send(
					f"Here are the colums and datatypes from the table **{name}**.\n> {formatted}")
				return
			
			if args[2].lower() == "entries":

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

				if level == 4:
					limit = 10
					get_entries = True

				elif args[4].lower() == "all":
					limit = 99999
					get_entries = True

				elif args[4].lower() not in ["add", "remove", "edit"]:
					try:
						limit = int(args[4])
					except:
						limit = 10
					get_entries = True
				
				if get_entries:
					cursor.execute(sql.SQL(""" SELECT * FROM {table_name} LIMIT {limit}""").format(
						table_name = sql.Identifier(full_name),
						limit = sql.Literal(limit)
					))
					entries = cursor.fetchall()

					formatted = "\n> ".join(["\t".join([str(h) for h in e]) for e in entries])

					reported_limit = 'all' if limit >= 99999 else limit
					plural = 'ies' if limit != 1 else 'y'

					to_send = f"Here are {reported_limit} entr{plural} of **{name}**.\n> {formatted}"

					if len(to_send) > 1950:
						to_send = to_send[:1947] + "..."
					await message.channel.send(to_send)
					return
				
				if args[4].lower() == "add":
					arguments = " ".join(args[5:]).split(" // ")

					for data in range(len(arguments)):
						if is_whole(arguments[data]):
							arguments[data] = int(arguments[data])
						if is_float(arguments[data]):
							arguments[data] = float(arguments[data])

					try:
						cursor.execute(sql.SQL(""" INSERT INTO {table_name} VALUES (""" 
							+ ", ".join(["%s"] * len(arguments)) + ")"
						).format(
							table_name = sql.Identifier(full_name)
						), arguments)
					except Exception as e:
						print(e)
						await message.channel.send(
							"Failed to add entry! Make sure the columns and data types are right.")
						return
					
					await message.channel.send(f"Successfully added entry to table **{name}**!")
					return
				
				if args[4].lower() == "remove":

					if level == 5:
						cursor.execute(sql.SQL(""" DELETE from {table_name} """).format(
							table_name = sql.Identifier(full_name)
						))
						await message.channel.send(f"Successfully cleared all entries from table **{name}**!")
						return
					
					arguments = " ".join(args[5:]).split(" // ")

					cursor.execute(sql.SQL(""" SELECT column_name FROM information_schema.columns 
					WHERE table_name = {table_name}""").format(
						table_name = sql.Literal(full_name),
					))

					columns = cursor.fetchall()

					if (arguments[0].lower(),) not in columns:
						await message.channel.send(f"`{args[5].lower()}` is not a valid column for **{name}**!")
						return
					
					if len(arguments) == 1:
						await message.channel.send(f"Add a key to search the `{args[5].lower()}` column by!")
						return
					
					cursor.execute(sql.SQL(""" DELETE FROM {table_name} WHERE {column} = {value} """).format(
						table_name = sql.Identifier(full_name),
						column = sql.Identifier(arguments[0].lower()),
						value = sql.Literal(arguments[1])
					))

					await message.channel.send(f"Successfully deleted entries from table **{name}**!")
					return