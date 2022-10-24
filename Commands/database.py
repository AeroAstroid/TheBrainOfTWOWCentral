from Helper.__comp import *

import os
from time import time

from Helper.__functions import is_dev, is_slash_cmd, m_line, plural
from Helper.__action_functions import confirm_action
from Helper.__db import Database as DB

def setup(BOT):
	BOT.add_cog(Database(BOT))

# TODO: Add db entries add, db entries edit, db entries remove

class Database(cmd.Cog):
	'''
	Wrapper command to edit the different database tables through the bot.

	Including the following **separate line** at the end of the command will perform the 
	operations on the debug schema instead (which has different tables and values to the public 
	one): /n/
	> `debug`

	By default, with no arguments passed, this command returns a list of every table in the 
	database. Otherwise, the first argument will dictate the mode used.

	For modes that require a multiline format, slash commands can use a literal `\\n` as a line 
	break.

	</>

	Different available modes:

	**__`{PREFIX}database add [table_name] (columns)`__** /n/
	Adds a table to the database with the specified columns and data types. `(columns)` are to be 
	specified in two-word pairs like so: /n/
	> `columnname1 datatype1` /n/
	> `columnname2 datatype2` /n/
	In this case, the data type for a column must be either **integer**, **text** or **real**.

	**__`{PREFIX}database remove [table_name]`__** /n/
	Removes (drops) a table from the database, provided proper confirmation is given by the 
	command user.

	**__`{PREFIX}database layout [table_name]`__** /n/
	Displays all columns of a table along with their data types.

	</>

	**__`{PREFIX}database entries [table_name] (conditions) (limit) ('format') ('file')`__** /n/
	Displays entries of a table that match all the conditions. The `(conditions)` **must** be 
	specified **in a multiline format** with the column name, an equals sign, and the 
	corresponding value, like so: /n/
	> `column1 = value to compare against` /n/
	> `column2 = other value to compare against` /n/
	By default, this command returns every table entry that matches the conditions given. You can 
	limit the amount of entries the command returns by including a **separate line** after the 
	conditions like such: /n/
	> `limit 10` /n/ 
	By default, returns the entries with space alignment for readability. You can make the command 
	return a tab-separated format (useful for spreadsheets) using the following **separate line** 
	at the end: /n/
	> `format` /n/
	By default, returns the entries in a Discord code block, using a file if the message is too 
	long. You can force it to return a file using the following **separate line** at the end: /n/
	> `file`

	**__`{PREFIX}database entries add [table_name] (values)`__** /n/
	Adds a single entry to a table, with the values being specified **in a multiline format** - 
	each value being its own line, like such: /n/
	> `value1` /n/
	> `value2` /n/
	> `value3` /n/
	The values must be in the same order as their respective columns in the table.

	__**`{PREFIX}database entries remove [table_name] (conditions) (limit)`**__ /n/
	Removes entries that match all the conditions from a table. These conditions **must** be 
	specified **in a multiline format**, with the column name, an equals sign, and the 
	corresponding value, like so: /n/
	> `column1 = value to compare against` /n/
	> `column2 = other value to compare against` /n/
	By default, this command deletes every table entry that matches the conditions given. You can 
	limit the amount of entries the command will delete by including a **separate line** like 
	such: /n/
	> `limit 10` /n/ 
	This command requires proper confirmation.

	**__`{PREFIX}database entries edit [table_name] (values) (conditions) (limit)`__** /n/
	Edits entries that match all the conditions specified in a table. The values to edit are 
	expressed **in separate lines** with the column name, an arrow bracket, and the corresponding 
	value, such as: /n/
	> `column1 > value to edit to` /n/
	> `column2 > other value to edit to` /n/
	The conditions themselves are also expressed in separate lines, with the column name, an 
	equals sign, and the corresponding value, like so: /n/
	> `column1 = value to compare against` /n/
	> `column2 = other value to compare against` /n/
	By default, this command changes every table entry that matches the conditions given. You can 
	limit the amount of entries the command will change by including a **separate line** like 
	such: /n/
	> `limit 10` /n/ 
	This command requires proper confirmation.
	'''

	# Extra arguments to be passed to the command
	FORMAT = "`(mode)` `(subcommand_info)` `...`"
	CATEGORY = "BRAIN"
	EMOJI = CATEGORIES[CATEGORY]
	ALIASES = ['db']

	def __init__(self, BRAIN):
		self.BRAIN = BRAIN

	# Slash version of the command due to function signature incompatibility
	@cmd.slash_command(name="database")
	@cmd.cooldown(1, 3)
	@cmd.check(is_dev)
	async def slash_database(self, ctx,
		query_subcommand = None):
		'''
		Wrapper command to edit the different database tables through the bot.
		'''

		cmd_args = query_subcommand.split(" ")

		await self.database(ctx, *cmd_args)

		return

	@cmd.command(aliases=ALIASES)
	@cmd.cooldown(1, 3)
	@cmd.check(is_dev)
	async def database(self, ctx,
		*cmd_args):

		# This block reconstructs the intended structure of the command with line breaks
		# This is important since although Discord API treats them as argument breaks like spaces,
		# they have different functions in a command like this
		if is_slash_cmd(ctx):
			original_query = "".join(
				[a + " " if a != "\\n" else "\n" for a in cmd_args]
			).strip()

		else:
			# Test for both `tc/database subcommand` AND `tc/database\nsubcommand`
			space_split = ctx.message.content.split(" ")
			line_split = ctx.message.content.splitlines()

			if len(space_split[0]) < len(line_split[0]):
				original_query = " ".join(space_split[1:])
			else:
				original_query = "\n".join(line_split[1:])

		# Make a matrix out of arguments, with space column splits and newline row splits
		arg_matrix = [l.split(" ") for l in original_query.splitlines()]

		modif = {
			"debug": False,
			"format": False,
			"file": False
		}

		for _ in range(len(modif.keys())):
			if (not len(arg_matrix) == 0 and len(arg_matrix[-1]) == 1
				and arg_matrix[-1][0].lower() in modif.keys()):
				
				modif[arg_matrix[-1][0].lower()] = True
				arg_matrix = arg_matrix[:-1]

		subcommands = ["add", "remove", "layout", "entries"]

		# No subcommand -> see all tables
		if len(arg_matrix) == 0:
			tables = DB.get_tables(debug=modif["debug"])
			tables = ", ".join([f"**{t.upper()}**" for t in tables])

			await ctx.respond(f"🗂️ **Here are all the tables in the database:**\n> {tables}")
			return
		
		# Position in the argument matrix
		line, arg_n = (0, 0)

		# This lambda function steps forward the current arg in the argument matrix
		step_forward = lambda: (
			line + 1 if arg_n + 1 >= len(arg_matrix[line]) else line,	# Current line after moving
			0 if arg_n + 1 >= len(arg_matrix[line]) else arg_n + 1,		# Current col. after moving
			arg_n + 1 >= len(arg_matrix[line])							# Did the line change? (bool)
		)

		if arg_matrix[line][arg_n].lower() not in subcommands:
			v_subcmds = ", ".join([f"**{sc.upper()}**" for sc in subcommands])

			await ctx.respond(
			f"💀 **This is not a valid subcommand!** Valid subcommands are:\n> {v_subcmds}")
			return
		
		# Add a table to the database
		if arg_matrix[line][arg_n].lower() == "add":
			line, arg_n, _ = step_forward()

			try:
				table_name = arg_matrix[line][arg_n].lower()
			except IndexError:
				await ctx.respond("💀 **You must include the name of the new table!**")
				return

			columns = []

			line, arg_n, _ = step_forward()

			while True: # Runs until there are no more columns

				try:
					column_name = arg_matrix[line][arg_n].lower()
				except IndexError:
					if len(columns) == 0:
						await ctx.respond("💀 **You must include the new table's columns!**")
						return
					else:
						break
				
				line, arg_n, _ = step_forward()

				try:
					column_type = arg_matrix[line][arg_n].lower()
				except IndexError:
					await ctx.respond(
					f"💀 **Column `{column_name.upper()}` has no specified data type!**")
					return
				
				columns.append([column_name, column_type])

				line, arg_n, _ = step_forward()
			
			DB.add_table(table_name, columns, debug=modif["debug"])

			columns_summary = "/n/".join(["> " + ": ".join(col) for col in columns])

			await ctx.respond(m_line(f"""
				✅ **Table {table_name.upper()} has been created** with the columns:/n/
				{columns_summary}"""))
			return
		
		# Drop a table from the database
		if arg_matrix[line][arg_n].lower() == "remove":
			line, arg_n, _ = step_forward()

			try:
				table_name = arg_matrix[line][arg_n].lower()
			except IndexError:
				await ctx.respond("💀 **You must include the name of the table to remove!**")
				return
			
			action_confirmed = [None]
			msg, msg_view = await confirm_action(ctx, action_confirmed, create=True)

			await msg_view.wait()

			if not action_confirmed[0]:
				return

			DB.remove_table(table_name, debug=modif["debug"])
			
			if is_slash_cmd(ctx):
				await msg.edit_original_message(view=None, content=
				f"✅ **Table {table_name.upper()} has been removed** from the database!")
			else:
				await msg.edit(view=None, content=
				f"✅ **Table {table_name.upper()} has been removed** from the database!")
			
			return

		# Print the layout of a database
		if arg_matrix[line][arg_n].lower() == "layout":
			line, arg_n, _ = step_forward()

			try:
				table_name = arg_matrix[line][arg_n].lower()
			except IndexError:
				await ctx.respond("💀 **You must include the name of the table to inspect!**")
				return
			
			layout = DB.get_columns(table_name, include_type=True, debug=modif["debug"])

			columns_summary = "\n".join(["> " + ": ".join(col) for col in layout])

			await ctx.respond(
			f"📋 **Table {table_name.upper()} has the following layout:**\n{columns_summary}")
			return
		
		# Subcommand to deal with the entries - has 4 separate submodes
		if arg_matrix[line][arg_n].lower() == "entries":
			line, arg_n, _ = step_forward()

			try:
				table_name = arg_matrix[line][arg_n].lower()
			except IndexError:
				await ctx.respond("💀 **You must include the name of the table!**")
				return
			
			submodes = ["add", "remove", "edit"]

			line, arg_n, _ = step_forward()

			try:
				submode_chosen = arg_matrix[line][arg_n].lower()
			except IndexError:
				submode_chosen = None

			# No submode: command to get entries
			if submode_chosen not in submodes:
				conditions_get = {}
				
				entry_limit = None

				if arg_matrix[-1][0].lower() == 'limit' and len(arg_matrix[-1] == 2):
					try:
						entry_limit = int(arg_matrix[-1][1])

						arg_matrix = arg_matrix[:-1]
					except ValueError:
						await ctx.respond(m_line(f"""
						💀 **Your entry limit must be a valid integer!**/n/
						> `{''.join(arg_matrix[-1])}`"""))
						return

				# None -> there are no conditions specified
				if submode_chosen is not None:

					# Loop to encounter each condition
					while True:
						full_condition = arg_matrix[line]

						if "=" not in full_condition:
							await ctx.respond(m_line(f"""
							💀 **You must separate the condition column and value with an equals 
							sign!**/n/> `{''.join(full_condition)}`"""))
							return
						
						eq_index = full_condition.index("=")
						
						condition_column = " ".join(full_condition[:eq_index])
						condition_value = " ".join(full_condition[eq_index+1:])
						
						if len(condition_column) == 0:
							await ctx.respond(m_line(f"""
							💀 **You must include a column in your condition!**/n/
							> `{''.join(full_condition)}`"""))
							return
						
						if len(condition_value) == 0:
							await ctx.respond(m_line(f"""
							💀 **You must include a value in your condition!**/n/
							> `{''.join(full_condition)}`"""))
							return

						conditions_get[condition_column] = condition_value

						line += 1
					
				entries = DB.get_entries(table_name, conditions=conditions_get, 
				debug=modif["debug"], limit=entry_limit)

				layout = DB.get_columns(table_name, include_type=True, debug=modif["debug"])
				columns_listed = [f"{col[0].upper()}:{col[1]}" for col in layout]

				if modif["format"]:
					message_lines = [f"TABLE {table_name} {'DEBUG' if modif['debug'] else ''}"]
					message_lines += ["\t".join(columns_listed)]
					message_lines += ["\t".join([str(val) for val in entry]) for entry in entries]
					message_lines += ["END TABLE"]

				else:
					message_lines = ([f"TABLE {table_name} {'DEBUG' if modif['debug'] else ''}"]
						+ [""] * (len(entries) + 1))

					for ind, arg_n in enumerate(columns_listed):
						col_data = [str(e[ind]) for e in entries]
						max_col_length = max([len(arg_n)] + [len(e) for e in col_data])

						space_align = (max_col_length + 4) - (len(arg_n))
						message_lines[1] += arg_n + " " * space_align

						for v_ind, val in enumerate(col_data):
							space_align = (max_col_length + 4) - (len(val))
							message_lines[v_ind + 2] += val + " " * space_align
					
					message_lines += ["END TABLE"]
				
				entry_count = len(message_lines) - 3
				message_lines = "\n".join(message_lines)

				if len(message_lines) > 1850 or modif["file"]:
					f_name = f'DB_{table_name}_{int(time()*1000)}.txt'

					open(f_name, 'w', encoding='utf-8').write(message_lines)

					await ctx.respond(m_line(f"""
					📋 Displaying **{entry_count}** entr{plural(entry_count, si='ies', pl='y')} 
					from table **{table_name.upper()}:**"""
					), file=dc.File(f_name))

					os.remove(f_name)
				
					return

				await ctx.respond(m_line(f"""
				📋 Displaying **{entry_count}** entr{plural(entry_count, si='ies', pl='y')} 
				from table **{table_name.upper()}:**
					
				"""
				) + f"```{message_lines}```")

		return
