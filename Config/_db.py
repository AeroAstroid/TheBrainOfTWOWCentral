import psycopg2
from psycopg2 import sql
try:
	from Config._const import DB_LINK
	from Config._functions import grammar_list
except ModuleNotFoundError:
	from _const import DB_LINK
	from _functions import grammar_list

class Database:
	def __init__(self):
		pass

	# Retrieve a list of tables. Example: db.get_tables()
	def get_tables(self):
		# Using a with statement on the database connection object is quite convenient. It automatically runs db.close()
		# when exiting the code through return statements, saving quite a lot of redundant lines of code
		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			# This SQL statement grabs all tables from the 'public' schema (which is where every table I use is)
			cursor.execute(""" SELECT tablename FROM pg_tables WHERE schemaname = 'public' """)
			return [x[0].split(".")[1] for x in cursor.fetchall()] # Return just the table's names, without the schema


	# Retrieve a table's columns. Setting include_type to True includes data types. Example: db.get_columns("birthday")
	def get_columns(self, table, include_type=False):
		if table not in self.get_tables():
			raise NameError(f"The table {table} is not in the database.")

		full_name = f"public.{table.lower()}" # Schema name

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			# information_schema.columns holds all of the columns of the entire database.
			cursor.execute(sql.SQL(""" SELECT column_name, data_type FROM information_schema.columns 
			WHERE table_name = {table_name} """).format( # Include the datatypes by default, too
				table_name = sql.Literal(full_name) # Filter these columns to only the table we want
			))
			columns = cursor.fetchall()

			if not include_type: # include_type is False, drop the datatypes from each column
				columns = [x[0] for x in columns]
			return columns
	
	# Add a column to the end of a table. columns is a list of [name, type] matchups. Example: db.add_columns("serverdata", [["prefix", "text"], ["members", "integer"]])
	def add_columns(self, table, columns):
		if table not in self.get_tables():
			raise NameError(f"The table {table} is not in the database.")

		if len(columns) == 0:
			raise ValueError("No columns have been specified to be added.")
		
		full_name = f"public.{table.lower()}" # Schema name

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			for i in range(len(columns)): # Add the columns one by one (so we can check them each individually for
				datatype = columns[i][1] # code that might be harmful)

				if datatype not in ["text", "integer", "real"]: # The three datatypes we use
					raise TypeError(f"The only SQL data types available are text, integer and real - not {datatype}.")

				# If the datatype is right, add the column. I have to use regular string addition for the datatype, but
				# since we made sure it's one of the three data types above, there's no harm in doing this
				cursor.execute(sql.SQL(""" ALTER TABLE {table_name} ADD {column} """ + datatype).format(
					table_name = sql.Identifier(full_name),
					column = sql.Identifier(columns[i][0])
				))
			
			return


	# Gets entries from a table. You can specify the limit - if not, it's 10. You can specify the columns to get - if
	# not, returns all of them. You can specify the conditions on which to gather them - if not, gathers all of them.
	# Example: db.get_entries("birthday", limit=50, columns=["date"], conditions={"timezone": 0})
	def get_entries(self, table, limit=None, columns=[], conditions={}):
		if table not in self.get_tables():
			raise NameError(f"The table {table} is not in the database.")
		
		if len(columns) != 0: # If there are specific columns to search for
			table_columns = self.get_columns(table) # Make sure they exist
			invalid_columns = [x for x in columns if x not in table_columns]

			if len(invalid_columns) > 0: # If there are invalid columns...
				raise NameError(f"The following columns are not in {table}: {grammar_list(invalid_columns)}")
		
		else: # If no columns were specified, gather all of them.
			columns = ["*"]

		full_name = f"public.{table.lower()}" # Schema name

		# Entry includes all columns specified and braces to format in the table name
		sql_query = f" SELECT {', '.join(columns)} FROM " + "{} "

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			if len(conditions.keys()) == 0: # If there are no conditions, select every entry in the columns
				if limit is not None:
					sql_query += f" LIMIT {limit} "

				cursor.execute(sql.SQL(sql_query).format(
					sql.Identifier(full_name)
				))
			
			else: # If there are conditions, use WHERE and formatting to specify them.
				sql_query += "WHERE " + ' AND '.join([f"{col} = %s" for col in conditions.keys()])
				
				if limit is not None:
					sql_query += f" LIMIT {limit} "

				cursor.execute(sql.SQL(sql_query).format(
					sql.Identifier(full_name)
				), list(conditions.values()))
			
			output = cursor.fetchall()
			return output
	

	# Adds a table. Example: db.add_table("bigredbutton", [["button", "integer"], ["info", "text"]])
	def add_table(self, table, columns):
		full_name = f"public.{table}" # Define the name with the schema included

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			# Create the table but with no columns
			cursor.execute(sql.SQL(""" CREATE TABLE {table_name} () """).format(
				table_name = sql.Identifier(full_name)
			))

			for i in range(len(columns)): # Add the columns one by one (so we can check them each individually for
				datatype = columns[i][1] # code that might be harmful)

				if datatype not in ["text", "integer", "real"]: # The three datatypes we use
					raise TypeError(f"The only SQL data types available are text, integer and real - not {datatype}.")

				# If the datatype is right, add the column. I have to use regular string addition for the datatype, but
				# since we made sure it's one of the three data types above, there's no harm in doing this
				cursor.execute(sql.SQL(""" ALTER TABLE {table_name} ADD {column} """ + datatype).format(
					table_name = sql.Identifier(full_name),
					column = sql.Identifier(columns[i][0])
				))
			return
	
	# Removes a table from the database. Example: db.remove_table("birthday")
	def remove_table(self, table):
		if table not in self.get_tables():
			raise NameError(f"The table {table} is not in the database.")

		full_name = f"public.{table}" # Schema name

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			cursor.execute(sql.SQL(""" DROP TABLE IF EXISTS {table_name}""").format(
				table_name = sql.Identifier(full_name) # Drop (a.k.a. remove) the table
			))
			return

	
	# Adds an entry to the table. Example: db.add_entry("birthday", ["184768535107469314", "12/12", -3])
	def add_entry(self, table, entry):
		if table not in self.get_tables():
			raise NameError(f"The table {table} is not in the database.")
		
		if len(entry) != len(self.get_columns(table)): # If the columns and value count are different
			raise IndexError(f"The amount of values and the amount of columns in {table} aren't equal!")

		full_name = f"public.{table}" # Schema name
		table_columns = self.get_columns(table, include_type=True)

		for c in table_columns: # Automatically convert values to column datatypes
			if c[1] == "text": # Text -> Str
				entry[table_columns.index(c)] = str(entry[table_columns.index(c)])
			if c[1] == "integer": # Integer -> Int
				entry[table_columns.index(c)] = int(entry[table_columns.index(c)])
			if c[1] == "real": # Real -> Float
				entry[table_columns.index(c)] = float(entry[table_columns.index(c)])

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			# Insert all the values in the database
			cursor.execute(sql.SQL(""" INSERT INTO {table_name} VALUES (""" 
				+ ", ".join(["%s"] * len(entry)) + ")" # Use python string addition to insert a variable amount of %s
			).format(
				table_name = sql.Identifier(full_name)
			), entry)

			return


	# Removes entries from table. If there are no conditions, will delete every entry in the table.
	# Example: db.remove_entry("birthday", conditions={"timezone": 0})
	def remove_entry(self, table, conditions={}):
		if table not in self.get_tables():
			raise NameError(f"The table {table} is not in the database.")
		
		if len(conditions.keys()) != 0: # If there are condition columns
			table_columns = self.get_columns(table) # Make sure those columns exist
			invalid_columns = [x for x in conditions.keys() if x not in table_columns]

			if len(invalid_columns) > 0: # If there are invalid columns...
				raise NameError(f"The following columns are not in {table}: {grammar_list(invalid_columns)}")
		
		full_name = f"public.{table}" # Schema name

		sql_query = " DELETE FROM {} " # Specify only the table until it's checked that there are conditionals

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			if len(conditions.keys()) == 0: # If there are no conditions, delete everything
				cursor.execute(sql.SQL(sql_query).format(
					sql.Identifier(full_name)
				))
			
			else: # If there are conditions, express them through the WHERE function
				sql_query += "WHERE " + ' AND '.join([f"{col} = %s" for col in conditions.keys()])

				cursor.execute(sql.SQL(sql_query).format(
					sql.Identifier(full_name)
				), list(conditions.values()))
			
			return


	# Edits entries of a table. Parameter entry specifies which columns to change into what, and conditions specifies
	# which entries should undergo the change. If there are no conditions, the entire table is changed. There must be
	# at least one column in entry.
	# Example: db.edit_entry("birthday", entry={"timezone": -4}, conditions={"id": 183331874670641152})
	def edit_entry(self, table, entry={}, conditions={}):
		if table not in self.get_tables():
			raise NameError(f"The table {table} is not in the database.")
		
		if len(entry.keys()) == 0: # There must be at least one column you want to edit
			raise IndexError("You haven't selected any columns to edit.")
		
		full_name = f"public.{table}" # Schema name
		table_columns = self.get_columns(table) # Detect invalid columns even if there are none in conditions
		# Because there's guaranteed to be columns in entry
		invalid_columns = [x for x in list(conditions.keys()) + list(entry.keys()) if x not in table_columns]

		if len(invalid_columns) > 0: # If there are invalid columns...
			raise NameError(f"The following columns are not in {table}: {grammar_list(invalid_columns)}")
		
		entry_edits = []
		for column in entry.keys():
			entry_edits.append(f"{column} = %s")

		# Query for unconditional editing
		sql_query = " UPDATE {} SET " + ", ".join(entry_edits)

		with psycopg2.connect(DB_LINK, sslmode='require') as db:
			db.set_session(autocommit = True)
			cursor = db.cursor()

			if len(conditions.keys()) == 0: # If there are no conditions, edit everything
				cursor.execute(sql.SQL(sql_query).format(
					sql.Identifier(full_name)
				), list(entry.values()))
			
			else: # If there are conditions, express them through the WHERE statement
				sql_query += "WHERE " + ' AND '.join([f"{col} = %s" for col in conditions.keys()])

				cursor.execute(sql.SQL(sql_query).format(
					sql.Identifier(full_name)
				), list(entry.values()) + list(conditions.values()))
			
			return