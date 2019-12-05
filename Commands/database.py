from Config._functions import grammar_list
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

				if len(name) > 40:
					await message.channel.send("That table name is too long! 40 characters maximum.")
					return

				full_name = f"public.{name}"
				columns = [x.split("-") for x in args[4:]]

				try:
					cursor.execute(sql.SQL(""" CREATE TABLE {table_name} () """).format(
						table_name = sql.Identifier(full_name)))

					# DOESN'T WORK FOR SOME REASON
					for z in range(len(columns[0])):
						cursor.execute(sql.SQL(""" ALTER TABLE {table_name} ADD %s %s""").format(
							table_name = sql.Identifier(full_name),
						), [columns[0][z], columns[1][z]])
				except Exception as e:
					traceback.print_exc()
					await message.channel.send("Table creation failed! Make sure your name and columns are right.")
					return
				
				await message.channel.send(f"Table {name} created with columns {', '.join(columns)}")
				return

			if args[2].lower() == "remove":

				if level == 3:
					await message.channel.send("Include the table you want to remove!")
					return
				
				cursor.execute(""" SELECT tablename FROM pg_tables WHERE schemaname = 'public' """)
				all_tables = [x[0].split(".")[1] for x in cursor.fetchall()]
				name = args[3].upper()

				if name not in all_tables:
					await message.channel.send("There's no table with that name!")
					return

				full_name = f"public.{name}"
				
				cursor.execute(sql.SQL(""" DROP TABLE IF EXISTS {table_name}""").format(
					table_name = sql.Identifier(full_name)
				))
				
				await message.channel.send(f"Successfully deleted table {name}.")
				return