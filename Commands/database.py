from Config._functions import grammar_list
from Config._const import PREFIX, BRAIN, DB_LINK
import psycopg2

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
    
    with psycopg2.connect(host=DB_LINK) as db:
        cursor = db.cursor()

		if args[1].lower() == "table":

			if level == 2:
        		cursor.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'public'")
				table_list = [f'**{x[0].upper()}**' for x in cursor.fetchall()]

				await message.channel.send(f"Here's a list of Brain Database's tables: {grammar_list(tables)}")
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
				
				columns = [x.replace("-", " ") for x in args[4:]]

				try:
					cursor.execute("CREATE TABLE {} (%s)".format(psycopg2.sql.Identifier(f'public.{name}')),
					[", ".join(columns)])
				except Exception:
					await message.channel.send("Table creation failed! Make sure your name and columns are right.")
					return
				
				db.commit()
				await message.channel.send(f"Table {name} created with columns {', '.join(columns)}")
				return