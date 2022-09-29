from Helper.__config import DB_LINK
from Helper.__functions import grammar_list

from psycopg2 import connect
from psycopg2.sql import SQL, Literal, Identifier

class Database:
	'''
	Container for all database-editing functionality

	All methods have their own safety checks and error handling, meaning most sanity checks can be 
	omitted from any commands or places where this class is implemented

	This however does not include confirmations for damaging operations - those still need to be 
	implemented on a case-by-case basis wherever there is user interaction with this class
	'''

	@classmethod
	def schema(cls, debug):
		'''
		Simple shorthand for the current schema depending on whether or not we're using debug data
		'''

		return 'debug' if debug else 'public'
	
	@classmethod
	def get_schemas(cls):
		'''
		Command that returns a list of all available schemas
		'''

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				SELECT * FROM INFORMATION_SCHEMA.SCHEMATA
			"""))

			output = [sch[1] for sch in cursor.fetchall()]
		
		return output
	
	@classmethod
	def add_schema(cls, schema):
		'''
		Adds a schema to the database
		'''

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				CREATE SCHEMA {schema_name}
			""").format(
				schema_name = Identifier(schema)
			))
		
		return

	@classmethod
	def get_tables(cls, debug=False):
		'''
		Returns a list of all tables in the specified schema
		'''

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				SELECT tablename 
				FROM pg_tables 
				WHERE schemaname = {schema}
			""").format(
				schema = Literal(cls.schema(debug))
			))

			tables = [t[0].split(".")[1] for t in cursor.fetchall()]

		return tables

	@classmethod
	def add_table(cls, table, columns, debug=False):
		'''
		Adds a table to the working schema. The columns must be a list of [name, data_type] pairs.
		For conversion convenience, bot only supports "integer"/"real"/"text" (int, float, str)
		'''

		# Full table identifier with schema and table name
		table_code = f"{cls.schema(debug)}.{table.lower()}"

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				CREATE TABLE {table_name} ()
			""").format(
				table_name = Identifier(table_code)
			))

		cls.add_columns(table, columns, debug=debug)

		return

	@classmethod
	def remove_table(cls, table, debug=False):
		'''
		Removes (drops) a table from the current schema.
		'''
		
		# Check if table is in the working schema
		if table not in cls.get_tables(debug=debug):
			raise NameError(f"Table named {table} is not in the {cls.schema(debug)} schema.")
		
		# Full table identifier with schema and table name
		table_code = f"{cls.schema(debug)}.{table.lower()}"

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				DROP TABLE IF EXISTS {table_name}
			""").format(
				table_name = Identifier(table_code)
			))

		return
	
	@classmethod
	def get_columns(cls, table, include_type=False, debug=False):
		'''
		Returns a list of all columns in a table.
		If include_type is true, returns columns in [name, type] pairs
		Otherwise, returns a list of column names
		'''

		# Check if table is in the working schema
		if table not in cls.get_tables(debug=debug):
			raise NameError(f"Table named {table} is not in the {cls.schema(debug)} schema.")
		
		# Full table identifier with schema and table name
		table_code = f"{cls.schema(debug)}.{table.lower()}"

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				SELECT column_name, data_type 
				FROM information_schema.columns 
				WHERE table_name = {table_name}
			""").format(
				table_name = Literal(table_code)
			))

			# Include column name and type if include_type is true, otherwise just the name
			columns = [col if include_type else col[0] for col in cursor.fetchall()]

		return columns
	
	@classmethod
	def add_columns(cls, table, columns, debug=False):
		'''
		Add columns to the end of an existing table.
		Columns must be a list of [name, type] pairs.
		For conversion convenience, bot only supports "integer"/"real"/"text" (int, float, str)
		'''

		# Check if table is in the working schema
		if table not in cls.get_tables(debug=debug):
			raise NameError(f"Table named {table} is not in the {cls.schema(debug)} schema.")
		
		if len(columns) == 0:
			raise ValueError("No columns have been provided for the add command.")
		
		# Full table identifier with schema and table name
		table_code = f"{cls.schema(debug)}.{table.lower()}"

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			for name, data_type in columns:
				if data_type not in ["text", "real", "integer"]:
					raise TypeError(
					f"Data type provided is not text, real, nor integer, but rather {data_type}.")
				
				cursor.execute(SQL("""
					ALTER TABLE {table_name} 
					ADD {col_name} {col_type}
				""").format(
					table_name = Identifier(table_code),
					col_name = Identifier(name),
					col_type = Identifier(data_type)
				))
		
		return
	
	@classmethod
	def get_entries(cls, table, limit=None, columns=["*"], conditions={}, debug=False):
		'''
		Gets entries from a table. Returns a list of entries, where each entry is a list of its 
		values in column order.

		The limit parameter can define how many results maximum the function will return; by 
		default, the parameter is None, and so it returns all of them. The conditions parameter 
		can compare specific column values to the ones specified in the parameter, returning only 
		those that match all the conditions.
		'''

		# Check if table is in the working schema
		if table not in cls.get_tables(debug=debug):
			raise NameError(f"Table named {table} is not in the {cls.schema(debug)} schema.")
		
		if len(columns) == 0:
			raise ValueError("No columns have been provided for the get command.")
		
		table_columns = cls.get_columns(table, debug=debug)
		invalid_cols = [col for col in columns if col not in table_columns and col not in ["*"]]
		invalid_cols += [col for col in conditions.keys() if col not in table_columns]

		invalid_cols = list(set(invalid_cols))

		if len(invalid_cols) > 0:
			raise NameError(
			f"The following columns are not in {table}: {grammar_list(invalid_cols)}")
		
		# Full table identifier with schema and table name
		table_code = f"{cls.schema(debug)}.{table.lower()}"

		columns_list = ', '.join(columns)

		limit_code = "" if limit is None else f" LIMIT {limit}"

		condition_code = ""

		if len(conditions.keys()) != 0:
			typed_columns = cls.get_columns(table, debug=debug, include_type=True)

			col_indices = [table_columns.index(col) for col in conditions.keys()]
			col_types = [typed_columns[i][1] for i in col_indices]

			for i, col in enumerate(conditions.keys()):

				if col_types[i] == "text":
					conditions[col] = str(conditions[col])
				if col_types[i] == "integer":
					conditions[col] = int(conditions[col])
				if col_types[i] == "real":
					conditions[col] = float(conditions[col])

			condition_code = "WHERE " + " AND ".join([f"{col} = %s" for col in conditions.keys()])

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				SELECT {col_list} 
				FROM {table_name} 
			""" + condition_code + limit_code).format(
				col_list = SQL(columns_list),
				table_name = Identifier(table_code)
			), 
				list(conditions.values())
			)
			
			output = cursor.fetchall()
		
		return output
	
	@classmethod
	def add_entry(cls, table, entry, debug=False):
		'''
		Adds an entry to a table. The entry must be a list of values in the same order as the 
		order of columns in the table.
		'''

		# Check if table is in the working schema
		if table not in cls.get_tables(debug=debug):
			raise NameError(f"Table named {table} is not in the {cls.schema(debug)} schema.")
		
		# If the columns and value count are different
		if len(entry) != len(cls.get_columns(table, debug=debug)):
			raise IndexError(
			f"The amount of values and the amount of columns in {table} aren't equal!")
		
		# Full table identifier with schema and table name
		table_code = f"{cls.schema(debug)}.{table.lower()}"
		
		table_columns = cls.get_columns(table, include_type=True, debug=debug)

		entry = list(entry)

		for ind, col in enumerate(table_columns):
			if col[1] == "text":
				entry[ind] = str(entry[ind])
			if col[1] == "integer":
				entry[ind] = int(entry[ind])
			if col[1] == "real":
				entry[ind] = float(entry[ind])
		
		value_code = f"({', '.join(['%s'] * len(entry))})"
			
		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				INSERT INTO {table_name} 
				VALUES {value_list}
			""").format(
				table_name = Identifier(table_code),
				value_list = SQL(value_code)
			), 
				entry
			)

	@classmethod
	def remove_entry(cls, table, conditions={}, debug=False):
		'''
		Removes entries from a table. The conditions parameter can compare entries' column values 
		to the ones specified in order to limit which entries get removed. By default, removes 
		every entry from a table (!!!)
		'''

		# Check if table is in the working schema
		if table not in cls.get_tables(debug=debug):
			raise NameError(f"Table named {table} is not in the {cls.schema(debug)} schema.")
		
		table_columns = cls.get_columns(table, debug=debug)
		invalid_cols = [col for col in conditions.keys() if col not in table_columns]

		if len(invalid_cols) > 0:
			raise NameError(
			f"The following columns are not in {table}: {grammar_list(invalid_cols)}")
		
		table_code = f"{cls.schema(debug)}.{table.lower()}"

		condition_code = ""

		if len(conditions.keys()) != 0:
			typed_columns = cls.get_columns(table, debug=debug, include_type=True)

			col_indices = [table_columns.index(col) for col in conditions.keys()]
			col_types = [typed_columns[i][1] for i in col_indices]

			for i, col in enumerate(conditions.keys()):

				if col_types[i] == "text":
					conditions[col] = str(conditions[col])
				if col_types[i] == "integer":
					conditions[col] = int(conditions[col])
				if col_types[i] == "real":
					conditions[col] = float(conditions[col])

			condition_code = "WHERE " + " AND ".join([f"{col} = %s" for col in conditions.keys()])

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				DELETE FROM {table_name} 
			""" + condition_code).format(
				table_name = Identifier(table_code)
			), 
				list(conditions.values())
			)
		
		return
	
	@classmethod
	def remove_duplicates(cls, table, conditions=None, keep=1, debug=False):
		'''
		NOTE: This function can be pretty slow, especially if you're keeping many entries or the 
		table is large, so be wary of using this in any time-sensitive contexts

		Applies a remove_entry() command, but keeps the first entry in the database (by ID) that 
		matches the condition - effectively ensuring that after the operation, only one entry 
		that fulfills this condition remains. The keep parameter can be used to keep more than 1 
		entry. If no condition is specified, this command all true duplicates from the table, 
		keeping one (or more, depending on the keep parameter) of each.
		'''

		# Error handling isn't really required, the class functions below already do it for us
		if conditions is None: # No condition -> remove only true duplicates
			matches = cls.get_entries(table)

			for i, m in enumerate(matches):
				if matches[:i].count(m) >= keep:
					matches[i] = None
			
			matches = [m for m in matches if m is not None]

			cls.remove_entry(table, debug=debug)

			for m in matches:
				cls.add_entry(table, m, debug=debug)
		
		else: # Condition specified -> all entries that fulfill the condition are duplicates
			matches = cls.get_entries(table, conditions=conditions, debug=debug)

			# Removing duplicates here will do nothing
			if len(matches) <= keep:
				return

			cls.remove_entry(table, conditions=conditions, debug=debug)

			for m in matches[:keep]:
				cls.add_entry(table, m, debug=debug)
		
		return
	
	@classmethod
	def edit_entry(cls, table, columns, conditions={}, limit=None, debug=False):
		'''
		Edits one or more table entries so long as they pass the conditions specified in the 
		conditions parameter (by default, all entries pass).
		
		The columns parameter is a dict of {column: new_value} pairs (i.e. what the entries 
		that passed the conditions will have their column values edited to).
		
		The limit parameter can dictate a maximum amount of entries to edit. By default, it's 
		None, and so every entry fulfilling the conditions is edited.
		'''

		# Check if table is in the working schema
		if table not in cls.get_tables(debug=debug):
			raise NameError(f"Table named {table} is not in the {cls.schema(debug)} schema.")
		
		if len(columns.keys()) == 0:
			raise ValueError("No columns have been provided for the get command.")
		
		table_columns = cls.get_columns(table, debug=debug)
		invalid_cols = [col for col in columns.keys() if col not in table_columns]
		invalid_cols += [col for col in conditions.keys() if col not in table_columns]

		invalid_cols = list(set(invalid_cols))

		if len(invalid_cols) > 0:
			raise NameError(
			f"The following columns are not in {table}: {grammar_list(invalid_cols)}")
		
		# Full table identifier with schema and table name
		table_code = f"{cls.schema(debug)}.{table.lower()}"

		limit_code = "" if limit is None else f" LIMIT {limit}"

		condition_code = ""

		typed_columns = cls.get_columns(table, debug=debug, include_type=True)

		if len(conditions.keys()) != 0:
			col_indices = [table_columns.index(col) for col in conditions.keys()]
			col_types = [typed_columns[i][1] for i in col_indices]

			for i, col in enumerate(conditions.keys()):

				if col_types[i] == "text":
					conditions[col] = str(conditions[col])
				if col_types[i] == "integer":
					conditions[col] = int(conditions[col])
				if col_types[i] == "real":
					conditions[col] = float(conditions[col])

			condition_code = "WHERE " + " AND ".join([f"{col} = %s" for col in conditions.keys()])
		
		col_indices = [table_columns.index(col) for col in columns.keys()]
		col_types = [typed_columns[i][1] for i in col_indices]

		for i, col in enumerate(columns.keys()):

			if col_types[i] == "text":
				columns[col] = str(columns[col])
			if col_types[i] == "integer":
				columns[col] = int(columns[col])
			if col_types[i] == "real":
				columns[col] = float(columns[col])

		columns_code = ", ".join([f"{col} = %s" for col in columns.keys()])

		with connect(DB_LINK, sslmode='require') as db:
			cursor = db.cursor()

			cursor.execute(SQL("""
				UPDATE {table_name} 
				SET """ + columns_code + " " + condition_code + " " + limit_code).format(
				table_name = Identifier(table_code)
			), 
				list(columns.values()) + list(conditions.values())
			)
		
		return